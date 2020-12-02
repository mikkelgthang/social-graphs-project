from nltk.corpus import stopwords
from lyricsGenius import LyricsGenius
import io
import pickle
import networkx as nx
import pandas as pd
import nltk
nltk.download('stopwords')
nltk.download('punkt')
stopwords = set(stopwords.words("english"))


network = nx.read_gpickle("./fullNetwork.gpickle")

# labMTWordlist = pd.read_csv(
#     'https://journals.plos.org/plosone/article/file?type=supplementary&id=info:doi/10.1371/journal.pone.0026752.s001',
#     sep='\t',
#     skip_blank_lines=True,
#     header=2
# )


labMTWordlist = pd.read_csv("semantics.csv")


def tokenize(text):
    tokens = nltk.word_tokenize(text)
    tokens = [token for token in tokens if token not in stopwords]
    tokens = [token for token in tokens if token.isalnum()]
    tokens = [token.lower() for token in tokens]
    return tokens


def calcSentiment(text):
    tokens = tokenize(text)
    df = pd.DataFrame(tokens, columns=['word'])
    df = df.merge(labMTWordlist, left_on='word', right_on='word')
    return df['happiness_average'].mean()

# h = network.nodes(data=True)['Drake']['songs']['One Dance']
# print(h)
# h['hey'] = 5
# print(network.nodes(data=True)['Drake']['songs']['One Dance'])


tot = len(network.nodes())
i = 1
for node in network.nodes(data=True):
    print("{i} / {tot}".format(i=i, tot=tot))
    i = i + 1
    if 'songs' in node[1]:
        for k, v in node[1]['songs'].items():
            if(not v['lyrics'] == "404 Error"):
                v['sVal'] = calcSentiment(v['lyrics'])

nx.write_gpickle(network, './fullNetworkSentiment.gpickle')