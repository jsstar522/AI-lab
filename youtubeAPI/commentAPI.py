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

# # client secrets file
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

num = 0
## "최상위 댓글"의 전체 payload를 get_comments로 가져왔으므로 속성별로 나누는 메서드
def load_comments(match):
  global num
  for item in match["items"]:
    print item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    num += 1
    print num
    ## 현재 "최상위 댓글"의 id 전달, 대댓글 확인
    id = item["snippet"]["topLevelComment"]["id"]
    load_replies(id)
  if "nextPageToken" in match:
    match = get_comments(youtube, args.videoid, match["nextPageToken"])
    load_comments(match)

## "대댓글"의 전체 payload를 get_replies로 가져왔으므로 속성별로 나누는 메서드
def load_replies(id):
  global num
  match = get_replies(youtube, id)
  for item in match["items"]:
    print item["snippet"]["textDisplay"]
    num += 1
    print num

## vedeoid를 인자로 받아서 댓글 추출
def get_allComments(videoid):
  ## videoid를 인자로 받아서 args 새롭게 생성
  argparser.add_argument("--videoid")
  args = argparser.parse_args()
  args.videoid = videoid

  global youtube
  youtube = get_authenticated_service(args)

  try:
    match = get_comments(youtube, args.videoid, None)
    load_comments(match)
    
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  else:
    print "################### All Comments of One Video ###################"
