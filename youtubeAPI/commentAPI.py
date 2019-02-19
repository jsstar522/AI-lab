# -*- coding: utf-8 -*-
#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from googleapiclient.discovery import build

# # aws db mapping
ENV = "AWS"

environment = {
    "AWS": {
        "status": "production",
        "db": "dynamodb",
    }
}
environment = environment[ENV]

## client secrets file
CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# # if missing client secrets file.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com
For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# # client key와 discoverydocument.json 파일 읽어옴
# # discoverydocument.json이 있어야 commentThreads() 메서드를 사용할 수 있다.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
                                  message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  with open("youtube-v3-discoverydocument.json", "r") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

# # 조건에 맞는 "최상위 댓글"의 전체 list를 가져오는 method
# ## part: snippet = 댓글 객체, replies = 댓글 객체 안에 있는 대댓글(대댓글을 뽑아내는 함수는 따로 정의할 예정이므로 사용하지 않도록 한다.)
# ## maxResult: 개수 1~100까지만 한번에 뽑아낼 수 있다.
# ## videoId: vodeoId
# ## pageToken: 다음 페이지가 있을 경우(100개 이상)에만 return 된다.
def get_comments(youtube, video_id, page_token):
  results = youtube.commentThreads().list(
    part="snippet",
    maxResults=100,
    videoId=video_id,
    pageToken=page_token,
    textFormat="plainText"
  ).execute()
  return results

# # 조건에 맞는 "대댓글"의 전체 list를 가져오는 method
# ## 최상위 댓글 id == 대댓글 parent_id
# ## 해당 parent_id를 가진 대댓글이 모두 나타난다.
# ## 최상위 댓글 id를 넣어서 결과가 나오지 않으면 대댓글이 없는 것.
def get_replies(youtube, parent_id):
  results = youtube.comments().list(
    part="snippet",
    maxResults=100,
    parentId=parent_id,
    textFormat="plainText"
  ).execute()
  return results

## 비디오 통계치(좋아요, 조회수...) 추출
def get_videoStatistics(youtube, video_id):
  results = youtube.videos().list(
    part='statistics',
    id=video_id
  ).execute()
  return results

## "최상위 댓글"의 전체 payload를 get_comments로 가져왔으므로 속성별로 나누는 메서드
## 댓글 개수 print(num)
num = 0
def load_comments(match):

  global num
  for item in match["items"]:
    ## 유형
    type = "topLevelComment"
    ## 최상위 댓글
    commentDisplay = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    ## 부모댓글 = 없음
    parentId = None

    ## 최상위 댓글 id
    id = item["snippet"]["topLevelComment"]["id"]
    ## 최상위 댓글 작성자
    commentAuthor = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
    commentAuthorId = item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"]
    ## 작성날짜
    commentDate = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
    ## 좋아요
    commentLikeCount = item["snippet"]["topLevelComment"]["snippet"]["likeCount"]

    ## db 추가
    comments.add_comments(type, id, parentId, commentDisplay, commentAuthor, commentAuthorId, commentDate, commentLikeCount)
    print(commentDisplay)

    ## 개수
    num += 1
    print (num)

    ## 현재 "최상위 댓글"의 id 전달, 대댓글 확인
    load_replies(id)
  if "nextPageToken" in match:
    match = get_comments(youtube, args.videoid, match["nextPageToken"])
    load_comments(match)

## "대댓글"의 전체 payload를 get_replies로 가져왔으므로 속성별로 나누는 메서드
def load_replies(id):
  global num
  match = get_replies(youtube, id)
  for item in match["items"]:
    ## 유형
    type = "reply"
    ## 대댓글
    commentDisplay = item["snippet"]["textDisplay"]
    ## 부모댓글 id
    parentId = item["snippet"]["parentId"]
    ## 대댓글 id
    id = item["id"]
    ## 대댓글 작성자
    commentAuthor = item["snippet"]["authorDisplayName"]
    commentAuthorId = item["snippet"]["authorChannelId"]["value"]
    ## 작성날짜
    commentDate = item["snippet"]["publishedAt"]
    ## 좋아요
    commentLikeCount = item["snippet"]["likeCount"]

    ## db 추가 
    comments.add_comments(type, id, parentId, commentDisplay, commentAuthor, commentAuthorId, commentDate, commentLikeCount)
    print(commentDisplay)

    ## 개수
    num += 1
    print (num)

## vedeoid를 인자로 받아서 댓글 추출
def get_allComments(videoid, keyword):
  ## video ID
  args.videoid = videoid

  global youtube
  youtube = get_authenticated_service(args)
  
  ## infromation of video
  title = video["snippet"]["title"]
  print('<<', title, '>>')
  author = video["snippet"]["channelTitle"]
  createAt = video["snippet"]["publishedAt"]
  #discription = video["snippet"]["discription"]
  channelId = video["snippet"]["channelId"]
  ## 비디오 통계치
  ## 좋아요, 싫어요를 표시하지 않는 경우도 있다.
  statistics = get_videoStatistics(youtube, args.videoid)
  viewCount = statistics["items"][0]["statistics"]["viewCount"]
  if "likeCount" in statistics["items"][0]["statistics"]:
    likeCount = statistics["items"][0]["statistics"]["likeCount"]
    dislikeCount = statistics["items"][0]["statistics"]["dislikeCount"]
  else:
    likeCount = "Unknown"
    dislikeCount = "Unknown"

  ## db 테이블 생성
  comments.init()
  comments.set_info(dict(videoID=args.videoid, searchKeyword=keyword, title=title, author=author, createdAt=createAt, channelId=channelId, viewCount=int(viewCount), likeCount=int(likeCount), dislikeCount=int(dislikeCount)))

  ## 본격적인 댓글 추출 시작
  try:
    match = get_comments(youtube, args.videoid, None)
    load_comments(match)
    comments.set_contents()
    
  except HttpError as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
  else:
    print ("################### All Comments of One Video ###################")

if __name__ == "__main__":
  import searchAPI
  from comments import Comments

  ## videoid를 인자로 받아서 args 새롭게 생성
  argparser.add_argument("--keyword",
    help="Required; KEYWORD for search videos")
  argparser.add_argument("--resultSize", type = int,
    help="Required; Number of searched video lists")
  argparser.add_argument("--videoid")
  args = argparser.parse_args()
  print(args)

  if not args.keyword:
    exit("Please specify keword for search videos using the --keyword='<parameter>'.")
  if not args.resultSize:
    exit("Please specify number of searched video lists using the --resultSize='<parameter>'.")

  ## db handling 메서드 가져오기
  comments = Comments(_status=environment["status"], _chosen_db=environment["db"])

  for video in searchAPI.youtube_search(None, args.resultSize, args.keyword):
    ## 존재하는 videoID이면 건너뛰기
    if comments.is_exist(dict(videoID=video["id"]["videoId"])):
      continue
    ## 댓글 추출 시작
    ## 검색 키워드, 검색 국가를 테이블 생성시 쓸 수 있도록 인자로 전달
    get_allComments(video['id']['videoId'], args.keyword)

