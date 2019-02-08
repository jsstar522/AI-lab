#!/usr/bin/python

from googleapiclient.discovery import build

DEVELOPER_KEY = #<Put your API Key>#
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

videos = []

def youtube_search(page_token, resultSize, keyword):

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    part='snippet',
    q=keyword,
    maxResults=50,
    pageToken=page_token,
    # order=options.order,
  ).execute()

  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append(search_result)
    ## 원하는 비디오 리스트 개수만큼 나오면 중지
    if len(videos) == resultSize:
      return videos

  ## 비디오 리스트 다음페이지가 없을 때까지 재귀호출
  if "nextPageToken" in search_response:
    print(search_response["nextPageToken"])
    youtube_search(search_response["nextPageToken"], resultSize)

  return videos

#!/usr/bin/python

from googleapiclient.discovery import build

DEVELOPER_KEY = #<Put your API Key>#
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

videos = []

def youtube_search(page_token, resultSize, keyword):

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    part='snippet',
    q=keyword,
    maxResults=50,
    pageToken=page_token,
    # order=options.order,
  ).execute()

  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append(search_result)
    ## 원하는 비디오 리스트 개수만큼 나오면 중지
    if len(videos) == resultSize:
      return videos

  ## 비디오 리스트 다음페이지가 없을 때까지 재귀호출
  if "nextPageToken" in search_response:
    print(search_response["nextPageToken"])
    youtube_search(search_response["nextPageToken"], resultSize)

  return videos

if __name__ == "__main__":
  youtube_search(None)
