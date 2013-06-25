# -*- coding: utf-8 -*-
import xbmcaddon

import urllib, urllib2, simplejson
import xbmc, xbmcgui, xbmcplugin
import time, socket

socket.setdefaulttimeout(10)

class multiImagesSession:

    def addLink(self,name,url):
        liz=xbmcgui.ListItem(name, iconImage="DefaultImage.png")
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=str(url),listitem=liz,isFolder=False)

    def LIBRARY_FANARTS(self):
        retval = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": ["fanart"] }, "id": 1}')
        result = simplejson.loads(retval)
        images = result['result']['artists']
        for img in images:
            title = img.get('label','')
            row = img.get('fanart','')
            if not self.addLink(title,urllib2.unquote(row[8:-1])): break
        return True

    def SEARCH_FANARTS(self,query):
        url = 'http://pipes.yahoo.com/pipes/pipe.run?_id=c2fa95340901afd0957744024c8a3372&mbid='+query+'&_render=json'
        search_results = urllib.urlopen(url)
        json = simplejson.loads(search_results.read())
        search_results.close()
        images = json['value']['items']
        for img in images:
            title = img.get('title','')
            if not self.addLink(title,img.get('link','')): break
        return True


## XBMC Plugin stuff starts here --------------------------------------------------------            
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
                            
    return param

def get_mbid_artist(artist):
    artist_url = 'http://search.musicbrainz.org/ws/2/artist/?&fmt=json&query=artist:"'+artist+'"'
    search_results = urllib.urlopen(artist_url)
    json = simplejson.loads(search_results.read())
    search_results.close()
    if json['artist-list']['count'] == 0:
        return None
    else:
        mbid = json['artist-list']['artist'][0]['id']
        return mbid

def get_mbid(artist, song):
    artist=urllib.quote_plus(artist)
    song=urllib.quote_plus(song)
    recording_url = 'http://search.musicbrainz.org/ws/2/recording/?&fmt=json&query=artist:"'+artist+'"%20AND%20recording:"'+song+'"'
    tries = 0
    trylimit = 5
    gotit = False
    while tries < trylimit and not gotit:
        ret = GetStringFromUrl(recording_url)
        if 'requests are exceeding the allowable rate limit' in ret:
            time.sleep(1)
            tries = tries + 1
        else:
            gotit = True
    if not gotit:
        return -1
    json = simplejson.loads(ret)
    if json['recording-list']['count'] == 0:
        return get_mbid_artist(artist)
    else:
        recordings = json['recording-list']['recording']
        for recording in recordings:
            mbid = recording['artist-credit']['name-credit'][0]['artist']['id']
        return mbid

def artist_mbid():
        embedmbit=None
        try:
            json_mbid = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["musicbrainzartistid"], "playerid": 0 }, "id": "AudioGetItem"}')
            result = simplejson.loads(json_mbid)
            embedmbit=result['result']['item']['musicbrainzartistid']
        except:
            pass
        if not embedmbit:
            print "i will search mbid"
            artist=xbmc.Player().getMusicInfoTag().getArtist()
            song=xbmc.Player().getMusicInfoTag().getTitle()
            if len(artist) > 0 and len(song) > 0:
                multiartist=artist.split(' / ')
                if (len(multiartist)) >= 2:
                    artist=multiartist[0]
                return get_mbid(artist, song)
            if len(artist) == 0 and len(song) > 0:
                artistsong=song.split(' - ')
                if (len(artistsong))==2:
                    artist=artistsong[0]
                    song=artistsong[1]
                    return get_mbid(artist, song)
            else:
                return None
        else:
            print "embed mbid"
            multimbid=embedmbit.split('/')
            if (len(multimbid)) >= 2:
                embedmbit=multimbid[0]
            return embedmbit


def GetStringFromUrl(encurl):
    f = urllib.urlopen( encurl)
    doc = f.read()
    f.close()
    return str(doc)

### Do plugin stuff --------------------------------------------------------------------------
def doPlugin():
    params=get_params()

    mode=None
    name=None

    if xbmc.Player().isPlayingAudio()==False:
        url=None 
    else:
        url=artist_mbid()
    try:
            url=urllib.unquote_plus(params["url"])
    except:
            pass
    try:
            name=urllib.unquote_plus(params["name"])
            xbmcaddon.Addon(id='script.cu.lrclyrics').setSetting(id='song', value='%s' % (str(name)))
    except:
            pass
    try:
            mode=int(params["mode"])
    except:
            pass

    print "Mode: "+str(mode)
    print "URL: "+str(url)
    print "Name: "+str(name)


    update_dir = True
    success = True
    cache = True

    mis = multiImagesSession()
    
#    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TRACKNUM)
    
    if mode==None and url==None or len(url)<1:
        mis.LIBRARY_FANARTS()
    else:
        mis.SEARCH_FANARTS(query=url)

    xbmcplugin.endOfDirectory(int(sys.argv[1]),succeeded=success,updateListing=update_dir,cacheToDisc=cache)

doPlugin()