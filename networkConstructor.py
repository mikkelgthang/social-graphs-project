import networkx as nx
import re
import json
import pathlib
from lyricsGenius import LyricsGenius


class NetworkConstructor():

    def __init__(self, billboardMap, access_token=None, networkPath=None, songMemPath=None):
        loadNet = pathlib.Path(networkPath)
        if(not loadNet.exists() and networkPath is not None):
            self.__network = nx.MultiDiGraph()
            nx.write_gpickle(self.__network, networkPath)

        loadMem = pathlib.Path(songMemPath)
        if(not loadMem.exists() and songMemPath is not None):
            f = open(songMemPath, 'a')
            f.write("{}")
            f.close()

        self.__network = nx.MultiDiGraph() if networkPath is None else nx.read_gpickle(networkPath)
        self.__songMem = {}
        if(songMemPath is not None):
            with open(songMemPath) as jsonFile:
                self.__songMem = json.load(jsonFile)
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
                        (primary, featuring) = self.__lyricsGenius.artist(title, artist)
                        self.__songMem[str((title, artist))] = (primary, featuring)
                        # Write songMem to path
                        if(songMemPath is not None):
                            f = open(songMemPath, 'w')
                            json.dump(self.__songMem, f, indent=4)
                            f.close()
                    else:
                        (primary, featuring) = self.__songMem[str((title, artist))]
                    self._addEdges_(title, primary, featuring)
                    self._addSong_(title, primary, year, week, rank)
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

    def _addSong_(self, title, artists, year, week, rank):
        for artist in artists:
            if('songs' not in self.network.nodes[artist]):
                self.network.nodes[artist]['songs'] = {}
            if(title not in self.network.nodes[artist]['songs']):
                self.network.nodes[artist]['songs'][title] = []
            self.network.nodes[artist]['songs'][title].append(
                {'rank': rank, 'year': year, 'week': week})
