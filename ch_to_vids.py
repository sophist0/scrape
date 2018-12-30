#!/usr/bin/python


########################################################################################
# Grabs all video ids from a list of Youtube video channels
# Google to resolve import and auth. issues
########################################################################################

import os
import sys
import httplib2

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from apiclient.discovery import build_from_document
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

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

#def get_authenticated_service():
#  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
#  credentials = flow.run_console()
#  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

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


# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]

      # For properties that have array values, convert a name like
      # "snippet.tags[]" to snippet.tags, and set a flag to handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True

      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs

################################################################

def get_videoIds(response):

  vec = []
  tmp1 = response.items()
  for el in tmp1:
	
	if el[0] == 'items':

		# get video ids
		for x in range(len(el[1])):	
			tmp2 = el[1][x]["id"]
			if "videoId" in tmp2:
				vd = tmp2["videoId"]
				vec.append(vd)
	
	nToken = None
	if "nextPageToken" in response:
		nToken = response["nextPageToken"]

  return nToken, vec


def search_list_by_keyword(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.search().list(
    **kwargs
  ).execute()

  #return print_response(response)
  return get_videoIds(response)


def get_chId(response):
	tmp1 = response["items"]
	return tmp1[0]["id"]


def channels_list_by_username(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.channels().list(
    **kwargs
  ).execute()

  return get_chId(response)

#################################################################

if __name__ == '__main__':

  args = argparser.parse_args()

  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service(args)

  ##################################################
  vidchannels = open("pet_channels_2.txt")

  ln = 1
  for line in vidchannels:
    	if ln >= 10:
		line2 = line.split("/")

		if line2[3] == "user":
  			chTitle = line2[4] 
  			chId = channels_list_by_username(client,
    				part='snippet,contentDetails,statistics',
    				forUsername=chTitle)

  			print
  			print "###############################################################"
  			print
  			print("Line " + str(ln) +": " + chTitle + " Channel Id: " + chId)
		else:
			chId = line2[4]
  			print
  			print "###############################################################"
  			print
  			print("Line " + str(ln) +": Channel Id: " + chId)

	##################################################
	  
		nextToken = ""
		maxReturn = 50
		vec = []
		avec = []
		while True:
			print
			print("nextToken: ",nextToken)
			print("vec: ",vec)
			print
			nextToken, vec = search_list_by_keyword(client,
				part='snippet',
				maxResults=maxReturn, # If undefined max 50 results returned https://developers.google.com/youtube/v3/docs/search/list
				channelId=chId,
				pageToken=nextToken,
				type='')

			avec = avec + vec
			if (len(vec) < maxReturn) or (nextToken == None):
				break

		ftmp = open("vdIds/videoIds_"+chId+".txt","w")
		ftmp.write("Channel Id: "+chId+"\n") 
		ftmp.write("\n")
		  
		for vdid in avec:
			ftmp.write(vdid)
			ftmp.write("\n")
		ftmp.close()

	# NEXT LINE
 	ln += 1

	###################################################
