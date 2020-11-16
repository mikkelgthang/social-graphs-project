from lyricsGenius import LyricsGenius
from networkConstructor import NetworkConstructor
from billboard import storeBillboardData, storeSpecificBillboardData, patchHoles
from decouple import config
import collections
import io
import pickle
import json
import networkx as nx

import pandas as pd


token = config("ACCESS_TOKEN")
for i in range(1963, 1983):
    with open('./billboard/' + str(i) + '.txt','r') as read_file:
        billboardMap = json.load(read_file)
    networkConstructor = NetworkConstructor(billboardMap, token, networkPath="./network/" + str(i) + ".gpickle", songMemPath="./network/songMem/songMem.txt", lyricsMemPath="./network/lyricsMem/lyricsMem.txt")

# allNetworks = []
# for i in range(1958, 2021):
#     network = nx.read_gpickle("./network/" + str(i) + ".gpickle")
#     allNetworks.append(network)
# fullNetwork = nx.compose_all(allNetworks)
# nx.write_gpickle(fullNetwork, "./network/full.gpickle")

# network = nx.read_gpickle('./network/full.gpickle')
# print("Nodes: {}".format(len(network.nodes())))
# print("Edges: {}".format(len(network.edges())))
# print("Isolates: {}".format(len(list(nx.isolates(network)))))
# topLinked = sorted(network.degree, key=lambda x: x[1], reverse=True)[100]
# print(topLinked)
# allEdges = network.edges(data=True)
# lilwaynein = [(a,c['label']) for (a,b,c) in list(allEdges) if b.lower()=='lil wayne']
# lilwayneout = [(a,c['label']) for (a,b,c) in list(allEdges) if a.lower()=='lil wayne']
# print([(a,b,c['label']) for (a,b,c) in list(allEdges) if a.lower()=='Michael Jackson'])

# for i in range(1966,1967):
#     print(i)
#     patchHoles(str(i))

# m = {
#     "2012": {
#         "01": {
#             "1": {
#                 "title": "Life is Good",
#                 "artist": "Future Featuring Drake"
#             },
#             "2": {
#                 "title": "Circles",
#                 "artist": "Post Malone"
#             }
#         },
#         "02": {
#             "1": {
#                 "title": "Circles",
#                 "artist": "Post Malone"
#             }
#         }
#     }
# }
# networkConstructor = NetworkConstructor(m, token, networkPath="./network/testtest.gpickle", songMemPath="./network/songMem/songMem.txt", lyricsMemPath="./network/lyricsMem/lyricsMem.txt")
# network = networkConstructor.network
# network = nx.read_gpickle('./network/testtest.gpickle')
# print(network.nodes(data=True))
# print(network.edges(data=True))
# print(len(network.nodes(data=True)))
# print(len(network.edges(data=True)))
# print(network.nodes(data=True)['Post Malone']['songs']['Circles']['lyrics'])



# network = nx.read_gpickle('./network/1988.gpickle')
# print([[(a,len(b)) for a,b in v.items()] for k,v in network.nodes(data=True)['Rick Astley'].items()])

# mapperoni = {
#     "2012": {
#         "15": {
#             "1": {
#                 "title": "cool song feat. nono", "artist": "cool artist"
#             },
#             "2": {
#                 "title": "uncool song featuring smart man", "artist": "uncool artist & smart man"
#             }
#         },
#         "16": {
#             "1": {
#                 "title": "new week", "artist": "nono"
#             }
#         }
#     },
#     "2013": {
#         "1": {
#             "1": {
#                 "title": "new year featuring cool artist, lil wayne & uncool artist", "artist": "nono"
#             }
#         },
#         "2": {
#             "1": {
#                 "title": "uncool song", "artist": "uncool artist"
#             }
#         }
#     }
# }


# token = config('ACCESS_TOKEN')
# hey2 = LyricsGenius(token)

# mapperoni = downloadBillboard('2018-01-01','2018-01-15')
# mapperoni[2018]['01'] = {k:v for k,v in mapperoni[2018]['01'].items() if k < 10}
# mapperoni[2018]['02'] = {k:v for k,v in mapperoni[2018]['02'].items() if k < 10}

# print(mapperoni)

# hey = NetworkConstructor(mapperoni, token)
# print(hey.network.nodes(data=True))
# print()
# print(hey.network.edges())
# degree_sequence = sorted([d for n, d in hey.network.degree()], reverse=True)  # degree sequence
# degreeCount = collections.Counter(degree_sequence)
# deg, cnt = zip(*degreeCount.items())
# print()
# print((deg, cnt))

# print()
# print(hey.network.edges(data=True))
