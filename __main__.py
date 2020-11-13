from lyricsGenius import LyricsGenius
from networkConstructor import NetworkConstructor
from billboard import downloadBillboard
from decouple import config
import collections
import io

import pandas as pd

mapperoni = {
    "2012": {
        "15": {
            "1": {
                "title": "cool song feat. nono", "artist": "cool artist"
            },
            "2": {
                "title": "uncool song featuring smart man", "artist": "uncool artist & smart man"
            }
        },
        "16": {
            "1": {
                "title": "new week", "artist": "nono"
            }
        }
    },
    "2013": {
        "1": {
            "1": {
                "title": "new year featuring cool artist, lil wayne & uncool artist", "artist": "nono"
            }
        },
        "2": {
            "1": {
                "title": "uncool song", "artist": "uncool artist"
            }
        }
    }
}


token = config('ACCESS_TOKEN')
hey2 = LyricsGenius(token)

mapperoni = downloadBillboard('2018-01-01','2018-01-15')
mapperoni[2018]['01'] = {k:v for k,v in mapperoni[2018]['01'].items() if k < 10}
mapperoni[2018]['02'] = {k:v for k,v in mapperoni[2018]['02'].items() if k < 10}

print(mapperoni)

hey = NetworkConstructor(mapperoni, token)
print(hey.network.nodes(data=True))
print()
print(hey.network.edges())
degree_sequence = sorted([d for n, d in hey.network.degree()], reverse=True)  # degree sequence
degreeCount = collections.Counter(degree_sequence)
deg, cnt = zip(*degreeCount.items())
print()
print((deg, cnt))

print()
print(hey.network.edges(data=True))