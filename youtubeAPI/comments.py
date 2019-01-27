#!/usr/bin/python
#-*- coding: utf-8 -*-

import argparse

import searchAPI
import commentAPI

parser = argparse.ArgumentParser()
parser.add_argument('--q', help='Search term', default='merry_nee')
parser.add_argument('--max-results', help='Max results', default=25)
# parser.add_argument('--order', help='Order', default='date')
args = parser.parse_args()

for videoid in searchAPI.youtube_search(args):
  print (commentAPI.get_allComments(videoid))
