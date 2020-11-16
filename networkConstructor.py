import networkx as nx
import re
import json
import pathlib
from lyricsGenius import LyricsGenius


class NetworkConstructor():

    def __init__(self, billboardMap, access_token=None, networkPath=None, songMemPath=None, lyricsMemPath=None):
        loadNet = pathlib.Path(networkPath)
        if(not loadNet.exists() and networkPath is not None):
            self.__network = nx.MultiDiGraph()
            nx.write_gpickle(self.__network, networkPath)

        loadMem = pathlib.Path(songMemPath)
        if(not loadMem.exists() and songMemPath is not None):
            f = open(songMemPath, 'a')
            f.write("{}")
            f.close()

        loadLyricsMem = pathlib.Path(lyricsMemPath)
        if(not loadLyricsMem.exists() and lyricsMemPath is not None):
            f = open(lyricsMemPath, 'a')
            f.write("{}")
            f.close()

        self.__network = nx.MultiDiGraph() if networkPath is None else nx.read_gpickle(networkPath)
        self.__songMem = {}
        self.__lyricsMem = {}
        if(songMemPath is not None):
            with open(songMemPath) as jsonFile:
                self.__songMem = json.load(jsonFile)
        self.__lyricsMemPath = lyricsMemPath
        if(self.__lyricsMemPath is not None):
            with open(self.__lyricsMemPath) as jsonFile:
                self.__lyricsMem = json.load(jsonFile)

        self.__lyricsGenius = LyricsGenius(access_token=access_token)
        for year in billboardMap.keys():
            for week in billboardMap[year].keys():
                for (rank, data) in billboardMap[year][week].items():
                    print("Processing year: {year}    week: {week}    rank: {rank}".format(
                        year=year, week=week, rank=rank))
                    artist = re.split(
                        'featuring|ft.|feat.|feat|&|and', data['artist'].lower())[0]
                    title = data['title']
                    if(str((title, artist)) not in self.__songMem):
                        (primary, featuring, lyrics) = self.__lyricsGenius.fullInfo(title, artist, year)
                        self.__songMem[str((title, artist))] = (primary, featuring)
                        self.__lyricsMem[str((title, artist))] = lyrics
                        # Write songMem to path
                        if(songMemPath is not None):
                            f = open(songMemPath, 'w')
                            json.dump(self.__songMem, f, indent=4)
                            f.close()
                        # Write lyricsMem to path
                        if(lyricsMemPath is not None):
                            f = open(lyricsMemPath, 'w')
                            json.dump(self.__lyricsMem, f, indent=4)
                            f.close()
                    else:
                        (primary, featuring) = self.__songMem[str((title, artist))]
                        if(len(primary) > 0):
                            lyrics = self.__lyricsMem[str((title, artist))]
                        else:
                            lyrics = ""
                    self._addEdges_(title, primary, featuring)
                    self._addSongShort_(title, primary, lyrics, year, week, rank)
        ## Save current network to path
        if(networkPath is not None):
            nx.write_gpickle(self.__network, networkPath)


    @property
    def network(self):
        return self.__network

    def _addEdges_(self, title, artists, featuring):
        labels = [(f, a, t) for (f, a, _), t in nx.get_edge_attributes(
            self.__network, 'label').items()]
        for a in artists:
            otherArtists = [artist for artist in artists if not artist == a]
            for oa in otherArtists:
                if(not (a, oa, title) in labels):
                    self.network.add_edge(a, oa, label=title, collab=True)
        for primaryArtist in artists:
            self.__network.add_node(primaryArtist)
            edgeList = [(artist, primaryArtist) for artist in featuring]
            for (f, p) in edgeList:
                if(not (f, p, title) in labels):
                    self.network.add_edge(f, p, label=title)

    def _addSongShort_(self, title, artists, lyrics, year, week, rank):
        if(len(artists) == 0):
            return
        for artist in artists:
            if('songs' not in self.network.nodes[artist]):
                self.network.nodes[artist]['songs'] = {}
            if(title not in self.network.nodes[artist]['songs']):
                self.network.nodes[artist]['songs'][title] = {'lyrics': lyrics, 'placements': []}

            self.network.nodes[artist]['songs'][title]['placements'].append(
                {'rank': rank, 'year': year, 'week': week})


    def _addSong_(self, title, artists, year, week, rank):
        if(len(artists) == 0):
            return
        primaryArtist = artists[0]
        for artist in artists:
            if('songs' not in self.network.nodes[artist]):
                self.network.nodes[artist]['songs'] = {}
            if(title not in self.network.nodes[artist]['songs']):
                self.network.nodes[artist]['songs'][title] = {}

                if(str((title, primaryArtist)) not in self.__lyricsMem):
                    lyrics = self.__lyricsGenius.lyrics(title, year, artist=primaryArtist)
                    self.__lyricsMem[str((title, primaryArtist))] = lyrics
                    # Write songMem to path
                    if(self.__lyricsMemPath is not None):
                        f = open(self.__lyricsMemPath, 'w')
                        json.dump(self.__lyricsMem, f, indent=4)
                        f.close()
                else:
                    lyrics = self.__lyricsMem[str((title, primaryArtist))]

                self.network.nodes[artist]['songs'][title] = {'lyrics': lyrics, 'placements': []}

            self.network.nodes[artist]['songs'][title]['placements'].append(
                {'rank': rank, 'year': year, 'week': week})
