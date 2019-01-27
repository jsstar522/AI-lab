#!/usr/bin/python

import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


## API KEY https://cloud.google.com/console
DEVELOPER_KEY = 'AIzaSyCyJotl20tvJ7iW2ERC8rWy8llyFEmVeds'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    part='id,snippet',
    q=options.q,
    maxResults=options.max_results,
    # order=options.order,
  ).execute()

  videos = []

  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append(search_result['id']['videoId'])

  return videos