import networkx as nx
import re
from lyricsGenius import LyricsGenius


class NetworkConstructor():

    def __init__(self, billboardMap, access_token=None):
        self.__network = nx.MultiDiGraph()
        self.__lyricsGenius = LyricsGenius(access_token=access_token)
        for year in billboardMap.keys():
            for week in billboardMap[year].keys():
                for (rank, data) in billboardMap[year][week].items():
                    artist = re.split(
                        'featuring|ft.|feat.|feat|&|and', data['artist'].lower())[0]
                    title = data['title']
                    print("fetching artists")
                    (primary, featuring) = self.__lyricsGenius.artist(title, artist)
                    print(rank)
                    print(title)
                    self._addEdges_(title, primary, featuring)
                    self._addSong_(title, primary, year, week, rank)

    @property
    def network(self):
        return self.__network

    def _addEdges_(self, title, artists, featuring):
        labels = [(f, a, t) for (f, a, _), t in nx.get_edge_attributes(
            self.__network, 'label').items()]
        for primaryArtist in artists:
            self.__network.add_node(primaryArtist)
            edgeList = [(artist, primaryArtist) for artist in featuring]
            for (f, p) in edgeList:
                print((f, p, title))
                print(labels)
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
