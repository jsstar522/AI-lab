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

  # # Add each result to the appropriate list, and then display the lists of
  # # matching videos, channels, and playlists.
  # for search_result in search_response.get('items', []):
  #   if search_result['id']['kind'] == 'youtube#video':
  #     videos.append('%s (%s)' % (search_result['snippet']['title'],
  #                                search_result['id']['videoId']))
  #   elif search_result['id']['kind'] == 'youtube#channel':
  #     channels.append('%s (%s)' % (search_result['snippet']['title'],
  #                                  search_result['id']['channelId']))
  #   elif search_result['id']['kind'] == 'youtube#playlist':
  #     playlists.append('%s (%s)' % (search_result['snippet']['title'],
  #                                   search_result['id']['playlistId']))

  # print 'Videos:\n', '\n'.join(videos), '\n'
  # print 'Channels:\n', '\n'.join(channels), '\n'
  # print 'Playlists:\n', '\n'.join(playlists), '\n'


# if __name__ == '__main__':
#   parser = argparse.ArgumentParser()
#   parser.add_argument('--q', help='Search term', default='toppoki')
#   parser.add_argument('--max-results', help='Max results', default=25)
#   args = parser.parse_args()

#   try:
#     youtube_search(args)
#   except HttpError, e:
#     print 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)