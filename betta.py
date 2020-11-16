from networkConstructor import NetworkConstructor
from decouple import config
import io
import json

token = config('ACCESS_TOKEN')
for i in range(2003,2021):
    with open('./billboard/' + str(i) + '.txt', 'r') as read_file:
        billboardMap = json.load(read_file)
    netC = NetworkConstructor(billboardMap, token, networkPath='network/' + str(i) + '.gpickle', songMemPath='./bettaSongMem.txt', lyricsMemPath='./bettaLyricsMem.txt')