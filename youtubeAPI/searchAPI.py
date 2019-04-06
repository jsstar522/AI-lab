#!/usr/bin/python

from googleapiclient.discovery import build

DEVELOPER_KEY = #<Put your API Key>#
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

videos = []

def youtube_search(page_token, resultSize, keyword, region_code):

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  ## search 메서드 사용
  search_response = youtube.search().list(
    part='snippet',
    q=keyword,
    maxResults=50,
    pageToken=page_token,
    regionCode=region_code,
    # order=options.order,
  ).execute()

  ## snippet 형태에서 video 검색결과만 videos 배열에 추가
  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append(search_result)
    ## 원하는 비디오 리스트 개수만큼 나오면 중지
    if len(videos) == resultSize:
      return videos

  ## 비디오 리스트 다음페이지가 없을 때까지 재귀호출
  if "nextPageToken" in search_response:
    print(search_response["nextPageToken"])
    youtube_search(search_response["nextPageToken"], resultSize, keyword, region_code)

  return videos

if __name__ == "__main__":
  youtube_search(None)
