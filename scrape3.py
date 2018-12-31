#!/usr/bin/python

#############################################################################
# Given video ids this code scrapes the top level comments from each video
#############################################################################

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
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),CLIENT_SECRETS_FILE))

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  # Trusted testers can download this discovery document from the developers page
  # and it should be in the same directory with the code.
  with open("youtube-v3-discoverydocument.json", "r") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))


# Call the API's commentThreads.list method to list the existing comment threads.
#####################################################
# gets Top level comments not replies
#####################################################
def get_comment_threads(youtube, video_id):
  results = youtube.commentThreads().list(
    part="snippet,replies", # returns replies as well
    videoId=video_id,
    textFormat="plainText"
  ).execute()

  cvec = []
  for item in results["items"]:
    comment = item["snippet"]["topLevelComment"]
    author = comment["snippet"]["authorDisplayName"]
    text = comment["snippet"]["textDisplay"]
    print
    print "%s, %s" % (author, text)
    cvec.append((author, text))

  print
  print "###############################################"
  print

  return results["items"], cvec

if __name__ == "__main__":

  args = argparser.parse_args()
  youtube = get_authenticated_service(args)

  # Load video Ids
  path = 'vdIds/'
  fnames = os.listdir(path)
  fnames.sort()
  print
  print fnames
  print

  idx = 1
  for name in fnames:

	print
	print "######################################################"
	print name
	print "######################################################"
	print

	f = open(path+name,'r')

	ln = 1
	all_com = []
	for line in f:
		print str(ln) +": "+ line
		if ln == 2:
			tmp = line.split(" ")
			chId = tmp[2]
		elif ln >= 4:
			videoid = line

			# All the available methods are used in sequence just for the sake of an example.
			try:
				video_comment_threads, cvec = get_comment_threads(youtube, videoid)

			except HttpError, e:
			    	print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
			else:
				all_com = all_com + cvec

		ln += 1

	f.close()

	# write comments
	fc = open("comments/" + str(idx) + "_"+ (chId).encode('utf-8').strip() +".txt",'w')
	for x in range(len(all_com)):
		fc.write(((chId).encode('utf-8').strip() +","+ all_com[x][0] +","+all_com[x][1]+"\n").encode('utf-8'))

	idx += 1

