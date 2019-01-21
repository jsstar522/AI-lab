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

  with open("youtube-v3-discoverydocument.json", "r") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

# Call the API's commentThreads.list method to list the existing comments.
def get_comments(youtube, video_id, page_token):
  results = youtube.commentThreads().list(
    part="id,snippet,replies",
    maxResults = 100,
    videoId=video_id,
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
    
  if match["nextPageToken"]:
    next_page_token = match["nextPageToken"]
    print next_page_token
    match = get_comments(youtube, args.videoid, next_page_token)
    load_comments(match)
  else:
    return 0

    # author = comment["snippet"]["authorDisplayName"]
    # text = comment["snippet"]["textDisplay"]
    # print "Comment by %s: %s" % (author, text)

if __name__ == "__main__":
  argparser.add_argument("--videoid",
    help="Required; ID for video for which the comment will be inserted.")
  args = argparser.parse_args()

  if not args.videoid:
    exit("Please specify videoid using the --videoid= parameter.")

  youtube = get_authenticated_service(args)

  try:
    match = get_comments(youtube, args.videoid, None)
    load_comments(match)

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  else:
    print "Inserted, listed and updated top-level comments."