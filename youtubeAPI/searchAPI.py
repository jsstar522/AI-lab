#!/usr/bin/python

import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


## API KEY https://cloud.google.com/console
DEVELOPER_KEY = 'AIzaSyCyJotl20tvJ7iW2ERC8rWy8llyFEmVeds'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search():
  parser = argparse.ArgumentParser()
  parser.add_argument('--q', help='Search term', default='merry_nee')
  parser.add_argument('--max-results', help='Max results', default=25)
  args = parser.parse_args()
  # parser.add_argumnet('--order', help='Order', default='date')


  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    part='id,snippet',
    q=args.q,
    maxResults=args.max_results,
    # order=options.order,
  ).execute()

  videos = []

  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append(search_result)
  return videos

if __name__ == "__main__":
  print(youtube_search(args))
