from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError, Timeout
import time
import re
import io


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
        try:
            response = self._session.request(
                'GET', uri, timeout=5, params=params, headers=header, **kwargs)
            response.raise_for_status()
            time.sleep(sleep)
        except TimeoutError as e:
            raise TimeoutError("Request timed out:\n{e}".format(e=e))

        if(web):
            return response.text
        elif response.status_code == 200:
            res = response.json()
            return res.get('response', res)
        else:
            return response.status

    def lyrics(self, title, artist=""):
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
        songUrl = songUrls[0]

        # Get the song lyrics by scraping song url
        div = None
        html = BeautifulSoup(
            self._makeRequest_(songUrl, web=True).replace('<br />', '\n'),
            "html.parser"
        )
        div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
        if div is None:
            print("dumping html")
            f = open("hallo.txt", "w", encoding='utf-8')
            f.write(str(html))
            f.close()
            return "Error with song url: {}".format(songUrl)
        lyrics = div.get_text()

        lyrics = re.sub(r'(\[.*?\])*', '', lyrics)
        lyrics = re.sub('\n{2}', '\n', lyrics)

        return lyrics.strip("\n")

    def artist(self, title, artist):
        path = "search?q=" + title + " " + artist
        searchResponse = self._makeRequest_(path)
        hits = searchResponse['hits']
        hitResults = [hit['result'] for hit in hits if hit['type'] == "song"]
        songIds = [song['id'] for song in hitResults]
        songId = songIds[0]
        path = "songs/" + str(songId)
        songResponse = self._makeRequest_(path)
        song = songResponse['song']
        primaryArtists = re.split('&',song['primary_artist']['name'])
        primaryArtists = [artist.strip() for artist in primaryArtists]
        featuringArtists = song['featured_artists']
        featuringArtists = [artist['name'].strip() for artist in featuringArtists]
        return(primaryArtists, featuringArtists)
