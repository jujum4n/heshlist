###############################################################################
__version__ = '0.1'
__author__ = "Justin 'juju' Chase"
__contact__ = 'jujowned@gmail.com'
###############################################################################

import requests
import json
import time 
import sys
import os
import isodate
import pickle
from oauth2client.client import flow_from_clientsecrets, HttpAccessTokenRefreshError
import httplib2
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.file import Storage
from oauth2client import tools
import dateutil.parser
import operator
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser


CREDENTIALS_FILE = 'oauth.json'
APPLICATION_NAME = 'Heshlist'
CLIENT_SECRET_FILE = 'client_secrets.json'
SCOPES = 'https://www.googleapis.com/auth/youtube'

redirect_uri = 'https://yourredirect'

def get_credentials():
    store = Storage(CREDENTIALS_FILE)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = flow_from_clientsecrets(
        './hl/client_secrets.json',
        scope='https://www.googleapis.com/auth/youtube',
        redirect_uri=redirect_uri)
            
        auth_uri = flow.step1_get_authorize_url()
        print('Goto: ', auth_uri)
        auth_code = input()
        credentials = flow.step2_exchange(auth_code)
        store.put(credentials)
        print('Storing credentials to: ' + CREDENTIALS_FILE)
    return credentials


def authorize():
    flow = flow_from_clientsecrets(
        './hl/client_secrets.json',
        scope='https://www.googleapis.com/auth/youtube',
        redirect_uri=redirect_uri)
    
    auth_uri = flow.step1_get_authorize_url()
    print('Goto: ', auth_uri)
    auth_code = input()
    credentials = flow.step2_exchange(auth_code)
    http_auth = credentials.authorize(httplib2.Http())
    return build('youtube', 'v3', http=http_auth)



def get_uploadid_from_channelid(channel_id):
    results = youtube.channels().list(
        part="contentDetails",
        id=channel_id
      ).execute()
    return results['items'][0]['contentDetails']['relatedPlaylists']['uploads']



def playlist_items_from_uploadid_next(uploads_playlist_id, videoids, nextPageTokent):
    results = youtube.playlistItems().list(
    part="snippet",
    maxResults=50,
    playlistId=uploads_playlist_id,
    pageToken=nextPageTokent
    ).execute()
    
    vidids = videoids
    
    for item in results['items']:
        vidids.append([item['snippet']['resourceId']['videoId'], 
                        item['snippet']['publishedAt'], 
                        item['snippet']['title'], 
                        'https://www.youtube.com/watch?v=' + 
                        item['snippet']['resourceId']['videoId']])
    try:
        if results['nextPageToken']:
            print('going in a recursive call with: ' + \
                results['nextPageToken'] + \
                ' current videolistlength: ' + str(len(vidids)))
            playlist_items_from_uploadid_next(uploads_playlist_id, 
                vidids, results['nextPageToken'])
    except KeyError:
            return vidids
    return vidids

def playlist_items_from_uploadid(uploadid):
    results = youtube.playlistItems().list(
    part="snippet",
    maxResults=50,
    playlistId=uploadid
    ).execute()
    videoids = []
    
    for item in results['items']:
        videoids.append([item['snippet']['resourceId']['videoId'], 
                        item['snippet']['publishedAt'], 
                        item['snippet']['title'], 
                        'https://www.youtube.com/watch?v=' + 
                        item['snippet']['resourceId']['videoId']])
    if results['nextPageToken']:
        videoids = playlist_items_from_uploadid_next(uploadid, videoids, 
                                                    results['nextPageToken'])
        return videoids

def get_video_object_from_videoid(videoid):
    """Given a Video ID, gets the duration from the video"""
    results = youtube.videos().list(
                                    part="contentDetails",
                                    id=videoid[0]
                                    ).execute()
    duration = results['items'][0]['contentDetails']['duration']
    return [videoid[0], videoid[1], videoid[2], videoid[3], duration]

def parse_time(TIME_VALUE):
    """isodate format PT2M50S"""
    dur = isodate.parse_duration(TIME_VALUE)
    return dur


def parse_date(TIME_VALUE):
    """RFC 3339 format 2012-04-16T05:17:30.000Z"""
    return dateutil.parser.parse(TIME_VALUE)


def sort_by_date(video_list):
    sorted_list = sorted(video_list, key=operator.itemgetter(1))
    return sorted_list


################################################################################
# Testing Purposes
################################################################################
# Open our channel id json file, has all the relevenat skateboarding channels
def testing():
    try:
        credentials = get_credentials()
    except HttpAccessTokenRefreshError:
        credentials.refresh()
    
    http_auth = credentials.authorize(httplib2.Http())
    youtube = build('youtube', 'v3', http=http_auth)
    channel_data = None
    with open('./templates/data/chanids.json') as data_file:
        channel_data = json.load(data_file)
    contentList = channel_data['contentList']
    
    #For testing purposes Setup a channel_id (lurknyc channel)
    lurknyc = contentList[1]
    lurknyc_channel_id = lurknyc[1]
    
    print('Getting Uploadid from Channelid...')
    upload_id = get_uploadid_from_channelid(lurknyc_channel_id)
    print('Getting Videoid list from uploadid...')
    videoids = playlist_items_from_uploadid(upload_id)
    
    
    print('Sorting Videos by date...')
    videoids = sort_by_date(videoids)
    
    video_list = []
    print('Getting video durations for all videos')
    for vid in videoids:
        video_obj = get_video_object_from_videoid(vid)
        to_append = SkateVideo(video_obj[0], video_obj[1], video_obj[2], video_obj[3], video_obj[4], 'lurknyc')
        video_list.append(to_append)
        
    pickle.dump(video_list, open( "testdata.p", "wb" ))
    
    video_list = pickle.load(open("testdata.p", "rb"))
    
    for video in video_list:
        print(video.posted_date, video.video_name, video.duration)