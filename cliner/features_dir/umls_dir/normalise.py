
from nltk.stem import WordNetLemmatizer

from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.tag import _POS_TAGGER
from nltk.corpus import wordnet
from nltk.data import load

pos_tagger = load(_POS_TAGGER)
lemmatizer = WordNetLemmatizer()


def get_wordnet_pos_tag(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''


def preprocess(string):

    tokens = []

    pos_tags = pos_tagger.tag(string.split(' '))

    for t in pos_tags:

        token = t[0]
        pos_tag = get_wordnet_pos_tag(t[1])

        if pos_tag == '':
            tokens.append(token)

        else:
            lemma = lemmatizer.lemmatize(token, pos_tag)
            tokens.append(lemma)

    return " ".join(tokens)

if __name__ == "__main__":

    print(preprocess("he was running very fast"))
