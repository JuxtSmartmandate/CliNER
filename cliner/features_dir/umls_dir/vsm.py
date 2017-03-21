
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.tag import _POS_TAGGER
from nltk.corpus import wordnet
from nltk.data import load

pos_tagger = load(_POS_TAGGER)

import time
import numpy as np
import os
import pickle as pickle


class VSM(object):

    def __init__(self, documents):

        self.lemmatizer = WordNetLemmatizer()
        self.pos_tagger = pos_tagger

        # list of strings
        self.original_documents = documents
        self.documents = self.preprocess(documents)
        self.documents = documents

        self.tfidf_vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.documents)

    def get_wordnet_pos_tag(self, treebank_tag):
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

    def preprocess(self, listOfStrings):

        retVal = []

        for string in listOfStrings:

            pos_tags = self.pos_tagger.tag(string.split(' '))

            tokens = []

            print(pos_tags)

            for t in pos_tags:

                token = t[0]
                pos_tag = self.get_wordnet_pos_tag(t[1])

                if pos_tag == '':
                    tokens.append(token)

                else:
                    lemma = self.lemmatizer.lemmatize(token, pos_tag)
                    tokens.append(lemma)

                    print(lemma)
                    print(token)

            retVal.append(" ".join(tokens))

        return retVal

    def vectorize_query(self, listOfStrings):
        return self.tfidf_vectorizer.transform(listOfStrings)

    def get_cosine_similarity(self, featVecs):
        return cosine_similarity(featVecs, self.tfidf_matrix)

    def get_closest_documents(self, listOfStrings):

        #        featVects = self.vectorize_query(self.preprocess(listOfStrings))
        featVects = self.vectorize_query(listOfStrings)

        similarity_scores = self.get_cosine_similarity(featVects)

        print(similarity_scores)

        similarDocuments = []

        for list_of_similarity_scores, string in zip(similarity_scores, listOfStrings):

            maxIndex = np.argmax(list_of_similarity_scores)
            maxValue = list_of_similarity_scores[maxIndex]

            similarDocuments.append([self.original_documents[
                                    index] for index, value in enumerate(list_of_similarity_scores) if value > 0])

        return similarDocuments


def vsmTest():
    """
    TODO: cleanup code
    """

    my_phrase = ('diseased',)

    documents = (
        "C1290398|ENG|P|L0699962|PF|S0834867|Cerebral arterial aneurysm|3|",
        "C1290398|ENG|S|L1698352|PF|S7493290|Cerebral artery aneurysm|0|",
        "C1290398|ENG|S|L1698352|VCW|S1911784|Aneurysm;artery;cerebral|3|",
        "C1290398|ENG|S|L1698352|VC|S6658532|cerebral artery aneurysm|0|",
        "C1290398|ENG|S|L1698352|VO|S9215778|aneurysm of cerebral artery|3|",
        "C1290398|ENG|S|L2826210|PF|S3213211|Cerebral arterial aneurysm (disorder)|9|",
        "C1290398|ENG|S|L2826213|PF|S3377307|Intracranial arterial aneurysm|9|",
        "C1290398|ENG|S|L6979163|PF|S9215777|aneurysm of cerebral artery (diagnosis)|3|",
        "Disease",
        "disease",
        "Diseases",
        "Disease, NOS",
        "diseases",
        "Disease (disorder)",
        "disease/disorder",
        "Diseases and Disorders",
        "Disease [Disease/Finding]")
    init_time = time.time()

    vectorSpacedModel = VSM(documents=documents)
#    print vectorSpacedModel.get_closest_documents(my_phrase)

    print(vectorSpacedModel.preprocess(["diseased"]))

    print(time.time() - init_time)

if __name__ == "__main__":
    vsmTest()

# EOF
