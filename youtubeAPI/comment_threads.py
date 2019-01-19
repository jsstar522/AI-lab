# -*- coding: utf-8 -*- 
#!/usr/bin/python

# Usage example:
# python comment_threads.py --channelid='<channel_id>' --videoid='<video_id>' --text='<text>'

import httplib2
import os
import sys

from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains

# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
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

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  # Trusted testers can download this discovery document from the developers page
  # and it should be in the same directory with the code.
  with open("youtube-v3-discoverydocument.json", "r") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))


# Call the API's commentThreads.list method to list the existing comments.
def get_comments(youtube, video_id, channel_id, page_token):
  results = youtube.commentThreads().list(
    part="snippet,replies",
    maxResults = 100,
    videoId=video_id,
    # channelId=channel_id,
    pageToken=page_token,
    textFormat="plainText"
  ).execute()
  return results

num = 0
def load_comments(match):
  global num
  for item in match["items"]:
    # comment = item["snippet"]["topLevelComment"]
    comment = item
    print comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    num += 1
    print num
    if "replies" in comment.keys():
      for reply in item["replies"]["comments"]:
        print reply["snippet"]["textDisplay"]
        num += 1
        print num

    # author = comment["snippet"]["authorDisplayName"]
    # text = comment["snippet"]["textDisplay"]
    # print "Comment by %s: %s" % (author, text)

if __name__ == "__main__":
  # The "channelid" option specifies the YouTube channel ID that uniquely
  # identifies the channel for which the comment will be inserted.
  # The "videoid" option specifies the YouTube video ID that uniquely
  # identifies the video for which the comment will be inserted.
  argparser.add_argument("--videoid",
    help="Required; ID for video for which the comment will be inserted.")
  # The "text" option specifies the text that will be used as comment.
  args = argparser.parse_args()

  if not args.videoid:
    exit("Please specify videoid using the --videoid= parameter.")

  youtube = get_authenticated_service(args)
  try:
    match = get_comments(youtube, args.videoid, None, None)
    next_page_token = match["nextPageToken"]
    load_comments(match)
    # maxResult 이상부터 loop 가동
    while next_page_token:
      match = get_comments(youtube, args.videoid, None, next_page_token)
      load_comments(match)
      # match["nextPageToken"]을 찾을 수 없는 에러가 나오면 loop 중지
      if "nextPageToken" in match.keys():
        next_page_token = match["nextPageToken"]
      else:
        next_page_token = None

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  else:
    print "Inserted, listed and updated top-level comments."