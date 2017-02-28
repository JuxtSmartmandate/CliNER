

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

import glob

class BagOfWords(object):

    def __init__(self, tfidf=True):

       # print "called constructor for BagOfWords obj"

        self._fitted = False

        if tfidf is True:
        #    print "using TfidfVectorizer"
            self._count_vect = TfidfVectorizer(lowercase=True)
        else:
         #   print "using CountVectorizer()"
            self._count_vect = CountVectorizer(lowercase=True)

        self._vocab = {}

    def fit(self, corpus):

        """
        example corpus input:

        doc1 = "doc1 = "blah blah blah. this is a test corpus"
        doc2 = "yea this is also a test corpus blah blah"

        corpus = [doc1, doc2]
        """

        self._count_vect.fit(corpus)

        self._vocab = self._count_vect.vocabulary_

        self._fitted = True

    def get_vocab(self):
        return self._vocab

    def is_fitted(self):
        return self._fitted

    def transform(self, corpus):

        """
        takes in same input formatting as fit()

        returns a list of dicts. each dict is the freq of each word occuring.
        Term Frequency Inverse Document Frequency normalization is used.
        """

        transformed_corpus = None

        d = []

        if self.is_fitted() is False:
            exit("bow model error: cannot transformed data when model is not fitted yet")
        else:
            transformed_corpus = self._count_vect.transform(corpus)

        V = self.get_vocab()

        for transformed_doc, doc in zip(transformed_corpus, corpus):

            word_freq_map = {}

            transformed_doc = transformed_doc.toarray()[0]

            for word in V:
                freq = transformed_doc[V[word]]
                word_freq_map[word] = freq

            d.append(word_freq_map)

        return d

def tokenize(doc):
    #print "called tokenize()"

    #print "doc: ", doc

    tokens = []

    for line in doc.split('\n'):
        tokens += line.split()

    #print tokens

    return tokens


if __name__ == "__main__":

    doc1 = "blah blah blah. this is a test corpus"
    doc2 = "yea this is also a test corpus blah blah"

    corpus = [doc1, doc2]

    bow_model = BagOfWords()
    bow_model.fit(corpus)

    transformed_corpus = bow_model.transform(["This is a test\n sentence.",
                                              "corpus corpus test"])

    print(transformed_corpus)


