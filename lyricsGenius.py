from bs4 import BeautifulSoup
import requests
import urllib
from requests.exceptions import HTTPError, Timeout
import time
import re
import io
import datetime


class LyricsGenius():
    APIRoot = 'https://api.genius.com/'

    def __init__(self, access_token=None):
        self._session = requests.Session()
        self.access_token = access_token
        self.access_token = 'Bearer ' + self.access_token if self.access_token else None
        self.authorizationHeader = {'authorization': self.access_token}

    def _makeRequest_(self, path, params=None, web=False, **kwargs):
        if(not web):
            uri = self.APIRoot
            header = self.authorizationHeader
        else:
            uri = ""
            header = None
        uri = uri + path

        params = params if params else {}
        response = None
        sleep = 0.2
        response = self._session.request(
                'GET', uri, params=params, headers=header, **kwargs)
        if response.status_code == 429:
            time.sleep(int(response.headers["Retry-After"]))
            # Try to download again after suggested time
            return self._makeRequest_(path, params=params, web=web, kwargs=kwargs)
        elif response.status_code == 503:
            time.sleep(1)
            self._makeRequest_(path, params=params, web=web, kwargs=kwargs)
        else:
            # Raise if other type
            response.raise_for_status()
        time.sleep(sleep)

        if(web):
            return response.text
        elif response.status_code == 200:
            res = response.json()
            return res.get('response', res)
        else:
            return response.status

    def lyrics(self, title, year, artist=""):
        """Finds genius song id by title and artist, then 
        scrapes the genius webpage for the lyrics. The function
        is a modified version of the lyrics function from
        https://github.com/johnwmillr/LyricsGenius/blob/master/lyricsgenius/genius.py

        Args:
            title (str):
                Song title
            artist (str):
                Song artist

        Returns:
            str \\| None:
                'str' If it can find the lyrics, otherwise 'None'

        """

        # Get the song url (search filtered by artist)

        path = "search?q=" + title + " " + artist
        searchResponse = self._makeRequest_(path)
        hits = searchResponse['hits']
        hitResults = [hit['result'] for hit in hits if hit['type'] == "song"]
        songUrls = [song['url']
                    for song in hitResults if artist.lower() in song['primary_artist']['name'].lower()]
        if(len(songUrls) == 0):
            return ""
        songUrl = songUrls[0]

        # Get the song lyrics by scraping song url
        div = None
        html = BeautifulSoup(
            self._makeRequest_(songUrl, web=True).replace('<br/>', '\n'),
            "html.parser"
        )
        div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
        if div is None:
            div = html.find("div", class_=re.compile("LyricsPlaceholder__Container"))
            if div is None:
                print("dumping html")
                f = open("hallo.txt", "w", encoding='utf-8')
                f.write(str(html))
                f.close()
                return "Error with song url: {}".format(songUrl)
            else:
                return ""
        lyrics = div.get_text()

        lyrics = re.sub(r'(\[.*?\])*', '', lyrics)
        lyrics = re.sub('\n{2}', '\n', lyrics)

        return lyrics

    def lyricsShortcut(self, songUrl):
        # Get the song lyrics by scraping song url
        div = None
        try:
            html = BeautifulSoup(
                self._makeRequest_(songUrl, web=True).replace('<br/>', '\n'),
                "html.parser"
            )
        except HTTPError as e:
            print(e)
            return ""
        div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
        if div is None:
            div = html.find("div", class_=re.compile("LyricsPlaceholder__Container"))
            if div is None:
                print("dumping html")
                f = open("hallo.txt", "w", encoding='utf-8')
                f.write(str(html))
                f.close()
                return "Error with song url: {}".format(songUrl)
            else:
                return ""
        lyrics = div.get_text()

        lyrics = re.sub(r'(\[.*?\])*', '', lyrics)
        lyrics = re.sub('\n{2}', '\n', lyrics)

        return lyrics

    def _cleanString_(self, s):
        return s.strip().replace('\u200b', '').replace('\u200c', '')

    def _checkRelease_(self, song, year):
        release = song['release_date_for_display'] or None
        if(release is None):
            return False
        releaseYear = re.findall(r'\d{4}',release)
        if(len(releaseYear)==0):
            return False
        if (int(releaseYear[0]) > int(year)):
            return False
        else:
            return True

    def artist(self, title, artist, year):
        artist = urllib.parse.quote(artist)
        title = urllib.parse.quote(title)
        path = "search?q=" + title + " " + artist
        searchResponse = self._makeRequest_(path)
        hits = searchResponse['hits']
        hitResults = [hit['result'] for hit in hits if hit['type'] == "song"]
        songIds = [song['id'] for song in hitResults]
        if(len(songIds) == 0):
            return ([], [])
        
        songId = songIds[0]
        path = "songs/" + str(songId)
        songResponse = self._makeRequest_(path)
        song = songResponse['song']

        if(self._checkRelease_(song, year) == False):
            return([],[])

        primaryArtists = re.split('&', song['primary_artist']['name'])
        primaryArtists = [artist.strip() for artist in primaryArtists]
        featuringArtists = song['featured_artists']
        featuringArtists = [artist['name'].strip()
                            for artist in featuringArtists]
        return([self._cleanString_(p) for p in primaryArtists], [self._cleanString_(f) for f in featuringArtists])

    def fullInfo(self, title, artist, year):
        artist = urllib.parse.quote(artist)
        title = urllib.parse.quote(title)
        path = "search?q=" + title + " " + artist
        searchResponse = self._makeRequest_(path)
        hits = searchResponse['hits']
        hitResults = [hit['result'] for hit in hits if hit['type'] == "song"]
        songIds = [song['id'] for song in hitResults]
        songUrls = [song['url'] for song in hitResults]
        if(len(songIds) == 0):
            return ([], [], "")
        
        songId = songIds[0]
        path = "songs/" + str(songId)
        songResponse = self._makeRequest_(path)
        song = songResponse['song']

        if(self._checkRelease_(song, year) == False):
            return([],[],"")

        lyrics = ""
        if(songUrls[0] is not None):
            lyrics = self.lyricsShortcut(songUrls[0])

        primaryArtists = re.split('&', song['primary_artist']['name'])
        primaryArtists = [artist.strip() for artist in primaryArtists]
        featuringArtists = song['featured_artists']
        featuringArtists = [artist['name'].strip()
                            for artist in featuringArtists]
        return([self._cleanString_(p) for p in primaryArtists], [self._cleanString_(f) for f in featuringArtists], lyrics)
