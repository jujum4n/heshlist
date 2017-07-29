from django.shortcuts import render
from random import shuffle
import time
import json
import pickle

from .YoutubeHelper import get_credentials, get_uploadid_from_channelid,playlist_items_from_uploadid, sort_by_date, get_video_object_from_videoid
import pickle
from oauth2client.client import HttpAccessTokenRefreshError
import httplib2
from apiclient.discovery import build


magazine_data = None
with open('templates/data/magazines.json') as data_file:    
    magazine_data = json.load(data_file)

messageboard_data = None
with open('templates/data/messageboards.json') as loaded:    
    messageboard_data = json.load(loaded)

skatepark_data = None
with open('templates/data/skateparks.json') as loaded:    
    skatepark_data = json.load(loaded)

charities_data = None
with open('templates/data/charities.json') as loaded:    
    charities_data = json.load(loaded)

resources_data = None
with open('templates/data/resources.json') as loaded:    
    resources_data = json.load(loaded)

podcast_data = None
with open('templates/data/podcasts.json') as loaded:    
    podcast_data = json.load(loaded)

shop_data = None
with open('templates/data/shops.json') as loaded:    
    shop_data = json.load(loaded)

video_data = None
with open('templates/data/videos.json') as loaded:    
    video_data = json.load(loaded)

def old_index(request):
    rendertimets = int(time.time())
    rendertime = str(time.strftime("%d %b %Y, %I:%M %p", time.localtime(rendertimets)))
    finshedrendertime = int(time.time())
    differencetime = finshedrendertime - rendertimets
    
    videos = video_data["contentList"]
    magazines = magazine_data["contentList"]
    messageboards = messageboard_data["contentList"]
    skateparks = skatepark_data["contentList"]
    charities = charities_data["contentList"]
    resources = resources_data["contentList"]
    podcasts = podcast_data["contentList"]
    shops = shop_data["contentList"]
    
    shuffle(magazines)
    shuffle(messageboards)
    shuffle(skateparks)
    shuffle(charities)
    shuffle(resources)
    shuffle(podcasts)
    shuffle(shops)
    shuffle(videos)
    return render(request, 'index.html',
                  {
                      'videos': videos,
                      'shops': shops,
                      'podcasts': podcasts,
                      'charities': charities,
                      'resources': resources,
                      'skateparks': skateparks,
                      'rendertime': rendertime,
                      'differencetime': differencetime,
                      'magazines': magazines,
                      'messageboards': messageboards,
                  })

def index(request):
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
    
    return render(request, 'hl.html',
              {
                  'video_list': video_list,
              })