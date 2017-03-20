

from sklearn.feature_extraction import DictVectorizer

from cliner.features_dir import features as feat_obj

from cliner.features_dir.utilities import load_pickled_obj, is_prose_sentence
from cliner.features_dir.BagOfWords import BagOfWords
from cliner.features_dir.read_config import enabled_modules

from cliner.machine_learning import sci
from cliner.machine_learning import crf

from cliner.notes.note import concept_labels, reverse_concept_labels
from cliner.notes.note import IOB_labels,     reverse_IOB_labels
from cliner.tools import flatten, save_list_structure, reconstruct_list

from collections import defaultdict

# Stores the verbosity
from . import globals_cliner
import numpy as np
from functools import reduce

if enabled_modules().get('WORD2VEC', False):

    from .features_dir.word2vec_dir import clustering
    from .features_dir.word2vec_dir.ngrams import get_char_gram_mappings
    from .features_dir.word2vec_dir.clustering import get_sequence_vector_clusters


class Model:

    @staticmethod
    def load(filename='awesome.model'):
        model = load_pickled_obj(filename)
        model.filename = filename

        return model

    def __init__(self, is_crf=True):

        # Use python-crfsuite
        self._crf_enabled = is_crf

        # DictVectorizers
        self._first_prose_vec = None
        self._first_nonprose_vec = None
        self._second_vec = None
        self.third_vec = None

        # Classifiers
        self._first_prose_clf = None
        self._first_nonprose_clf = None
        self._second_clf = None
        self.third_clf = None

        self.cui_freq = None
        self.bow = None

        # clustered vectors
        self.skipgram_mappings = None
        self.seq_clusters = None
        self.seq_lex_clusters = None

    def set_cui_freq(self, cui_freq):
        self.cui_freq = cui_freq

    def get_cui_freq(self):
        assert self.cui_freq is not None
        return self.cui_freq

    def train(self, notes, do_grid=False, do_third=False):
        """
        Model::train()

        Purpose: Train a Machine Learning model on annotated data

        @param notes. A list of Note objects (containing text and annotations)
        @return       None
        """

        # Extract formatted data
        tokenized_sentences, iob_labels = first_pass_data_and_labels(notes)
        chunks, indices, con_labels = second_pass_data_and_labels(notes)

        if enabled_modules().get('WORD2VEC', False):

            self.set_char_gram_maps(tokenized_sentences)

            clustering.skipgram_mappings = self.skipgram_mappings

            self.set_clusters(chunks, indices)

            # setting as globals within module so they don't have to be passed
            # as parameters...
            clustering.lexical_cluster = self.seq_lex_clusters
            clustering.embedding_clusters = self.seq_clusters

        # Train classifiers for 1st pass and 2nd pass
        self.__first_train(tokenized_sentences, iob_labels, do_grid)
        self.__second_train(chunks, indices, con_labels, do_grid)

        if do_third is True:
            self.__third_train(tokenized_sentences, notes, do_grid)

    def set_char_gram_maps(self, tokenized_sentences):

        self.skipgram_mappings = get_char_gram_mappings(
            tokenized_sentences, 200)

        return

    def set_clusters(self, chunked_sentences, chunked_indices):

        self.seq_clusters, self.seq_lex_clusters = get_sequence_vector_clusters(
            chunked_sentences, chunked_indices)

        return

    def predict(self, note, do_third=False):
        """
        Model::predict()

        Purpose: Predict concept annotations for a given note

        @param note. A Note object (containing text and annotations)
        @return      <list> of Classification objects
        """

        if enabled_modules().get('WORD2VEC', False):

            # setting as globals within module so they don't have to be passed
            # as parameters...
            clustering.lexical_cluster = self.seq_lex_clusters
            clustering.embedding_clusters = self.seq_clusters
            clustering.skipgram_mappings = self.skipgram_mappings

        # First pass (IOB Chunking)
        if globals_cliner.verbosity > 0:
            print('first pass')

        # Extract formatted data
        tokenized_sentences = first_pass_data(note)

        # Predict IOB labels
        iobs = self.__first_predict(tokenized_sentences)
        note.setIOBLabels(iobs)

        # Second pass (concept labels)
        if globals_cliner.verbosity > 0:
            print('second pass')

        # Extract formatted data
        chunked_sentences, inds = second_pass_data(note)

        # Predict concept labels
        classifications = self.__second_predict(chunked_sentences, inds)

        result = classifications

        # TODO: make third pass work other formattings.
        if note.format == "semeval":
            # Third pass enabled?
            if do_third is True:

                if globals_cliner.verbosity > 0:
                    print('third pass')
                clustered = self.__third_predict(
                    chunked_sentences, classifications, inds)
                result = clustered

            else:
                # Treat each as its own set of spans (each set containing one
                # tuple)
                clustered = [(c[0], c[1], [(c[2], c[3])])
                             for c in classifications]
                result = clustered

        return result

    #########################################################################
    ##           Mid-level reformats data and sends to lower level         ##
    #########################################################################

    def __first_train(self, tokenized_sentences, Y, do_grid=False):
        """
        Model::__first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param tokenized_sentences. <list> of tokenized sentences
        @param Y.                   <list-of-lists> of IOB labels for words
        @param do_grid.             <boolean> whether to perform a grid search

        @return          None
        """

        if globals_cliner.verbosity > 0:
            print('first pass')
        if globals_cliner.verbosity > 0:
            print('\textracting  features (pass one)')

        # Seperate into prose v nonprose
        nested_prose_data,    nested_prose_Y = list(zip(
            *[line_iob_tup for line_iob_tup in zip(tokenized_sentences, Y) if is_prose_sentence(line_iob_tup[0])]))
        nested_nonprose_data, nested_nonprose_Y = list(zip(
            *[line_iob_tup for line_iob_tup in zip(tokenized_sentences, Y) if not is_prose_sentence(line_iob_tup[0])]))

        # extract features
        nested_prose_feats = feat_obj.IOB_prose_features(nested_prose_data)
        nested_nonprose_feats = feat_obj.IOB_nonprose_features(
            nested_nonprose_data)

        # Flatten lists (because classifier will expect flat)
        prose_Y = flatten(nested_prose_Y)
        nonprose_Y = flatten(nested_nonprose_Y)

        # rename because code uses it
        pchunks = prose_Y
        nchunks = nonprose_Y
        prose = nested_prose_feats
        nonprose = nested_nonprose_feats

        # Train classifiers for prose and nonprose
        pvec, pclf = self.__generic_first_train(
            'prose',    prose, pchunks, do_grid)
        nvec, nclf = self.__generic_first_train(
            'nonprose', nonprose, nchunks, do_grid)

        # Save vectorizers
        self._first_prose_vec = pvec
        self._first_nonprose_vec = nvec

        # Save classifiers
        self._first_prose_clf = pclf
        self._first_nonprose_clf = nclf

    def __second_train(self, chunked_data, inds_list, con_labels, do_grid=False):
        """
        Model::__second_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      <list> of tokenized sentences after collapsing chunks
        @param inds_list <list-of-lists> of indices
                           - assertion: len(data) == len(inds_list)
                           - one line of 'inds_list' contains a list of indices
                               into the corresponding line for 'data'
        @param con_labels <list> of concept label strings
                           - assertion: there are sum(len(inds_list)) labels
                              AKA each index from inds_list maps to a label
        @param do_grid   <boolean> indicating whether to perform a grid search

        @return          None
        """

        if globals_cliner.verbosity > 0:
            print('second pass')

        # Extract features
        if globals_cliner.verbosity > 0:
            print('\textracting  features (pass two)')

        text_features = [feat_obj.concept_features(
            s, inds) for s, inds in zip(chunked_data, inds_list)]

        flattened_text_features = flatten(text_features)

        if globals_cliner.verbosity > 0:
            print('\tvectorizing features (pass two)')

        # Vectorize labels
        numeric_labels = [concept_labels[y] for y in con_labels]

        # Vectorize features
        self._second_vec = DictVectorizer()
        vectorized_features = self._second_vec.fit_transform(
            flattened_text_features)

        if globals_cliner.verbosity > 0:
            print('\ttraining  classifier (pass two)')

        # Train the model
        self._second_clf = sci.train(
            vectorized_features, numeric_labels, do_grid)

    def __third_train(self, tokenized_sentences, notes, do_grid):

        print('third pass')

        print('\textracting  features (pass three)')
        # Get data and annotations of which spans actaully should be grouped
        classifications = []
        chunks = []
        for note in notes:

            # Annotations for groups
            seen = len(chunks)
            non_offset = note.getNonContiguousSpans()
            offset = [(c[0], c[1] + seen, c[2]) for c in non_offset]
            classifications += offset

            # Chunked text
            chunks += note.getChunkedText()

        self.bow = BagOfWords()

        fit_bag_of_words(self.bow, chunks)

        indices = [note.getConceptIndices() for note in notes]

        inds = reduce(concat, indices)

        # Useful for encoding annotations
        # query line number & chunk index to get list of shared chunk indices
        relations = defaultdict(lambda: defaultdict(lambda: []))
        for concept, lineno, spans in classifications:
            for i in range(len(spans)):
                key = spans[i]
                for j in range(len(spans)):
                    if i == j:
                        continue
                    relations[lineno][key].append(spans[j])

        # Extract features between pairs of chunks
        unvectorized_X = feat_obj.extract_third_pass_features(
            chunks, inds, bow=self.bow)

        print('\tvectorizing features (pass three)')

        # Construct boolean vector of annotations
        Y = []

        for lineno, indices in enumerate(inds):
            # Cannot have pairwise relationsips with either 0 or 1 objects
            if len(indices) < 2:
                continue

            # Build (n choose 2) booleans
            bools = []
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    # Does relationship exist between this pair?
                    if indices[j] in relations[lineno][indices[i]]:
                        # print indices[i], indices[j]
                        shared = 1
                    else:
                        shared = 0
                    # Positive or negative result for training
                    bools.append(shared)

            Y += bools

        self.third_vec = DictVectorizer()

        # Vectorize features
        X = self.third_vec.fit_transform(unvectorized_X)

        print('\ttraining classifier  (pass three)')

        # Train classifier
        self.third_clf = sci.train(X, Y, do_grid, default_label=0)

    def __first_predict(self, data):
        """
        Model::__first_predict()

        Purpose: Predict IOB chunks on data

        @param data.  A list of split sentences    (1 sent = 1 line from file)
        @return       A list of list of IOB labels (1:1 mapping with data)
        """

        if globals_cliner.verbosity > 0:
            print('\textracting  features (pass one)')

        # Seperate into
        nested_prose_data = [line for line in data if is_prose_sentence(line)]
        nested_nonprose_data = [
            line for line in data if not is_prose_sentence(line)]

        # Parition into prose v. nonprose
        nested_prose_feats = feat_obj.IOB_prose_features(nested_prose_data)
        nested_nonprose_feats = feat_obj.IOB_nonprose_features(
            nested_nonprose_data)

        # rename because code uses it
        prose = nested_prose_feats
        nonprose = nested_nonprose_feats

        # Predict labels for IOB prose and nonprose text
        nlist = self.__generic_first_predict(
            'nonprose', nonprose, self._first_nonprose_vec, self._first_nonprose_clf)
        plist = self.__generic_first_predict(
            'prose',    prose, self._first_prose_vec, self._first_prose_clf)

        # Stitch prose and nonprose data back together
        # translate IOB labels into a readable format
        prose_iobs = []
        nonprose_iobs = []
        iobs = []
        num2iob = lambda l: reverse_IOB_labels[int(l)]
        for sentence in data:
            if sentence == []:
                iobs.append([])
            elif is_prose_sentence(sentence):
                prose_iobs.append(plist.pop(0))
                prose_iobs[-1] = list(map(num2iob, prose_iobs[-1]))
                iobs.append(prose_iobs[-1])
            else:
                nonprose_iobs.append(nlist.pop(0))
                nonprose_iobs[-1] = list(map(num2iob, nonprose_iobs[-1]))
                iobs.append(nonprose_iobs[-1])

        # list of list of IOB labels
        return iobs

    def __second_predict(self, chunked_sentences, inds_list):

        # If first pass predicted no concepts, then skip
        # NOTE: Special case because SVM cannot have empty input
        if sum([len(inds) for inds in inds_list]) == 0:
            print("first pass predicted no concepts, skipping second pass")
            return []

        # Create object that is a wrapper for the features
        if globals_cliner.verbosity > 0:
            print('\textracting  features (pass two)')

        print('\textracting  features (pass two)')

        # Extract features
        text_features = [feat_obj.concept_features(
            s, inds) for s, inds in zip(chunked_sentences, inds_list)]
        flattened_text_features = flatten(text_features)

        print('\tvectorizing features (pass two)')

        if globals_cliner.verbosity > 0:
            print('\tvectorizing features (pass two)')

        # Vectorize features
        vectorized_features = self._second_vec.transform(
            flattened_text_features)

        if globals_cliner.verbosity > 0:
            print('\tpredicting    labels (pass two)')

        # Predict concept labels
        out = sci.predict(self._second_clf, vectorized_features)

        # Line-by-line processing
        o = list(out)
        classifications = []
        for lineno, inds in enumerate(inds_list):

            # Skip empty line
            if not inds:
                continue

            # For each concept
            for ind in inds:

                # Get next concept
                concept = reverse_concept_labels[o.pop(0)]

                # Get start position (ex. 7th word of line)
                start = 0
                for i in range(ind):
                    start += len(chunked_sentences[lineno][i].split())

                # Length of chunk
                length = len(chunked_sentences[lineno][ind].split())

                # Classification token
                classifications.append(
                    (concept, lineno + 1, start, start + length - 1))

        # Return classifications
        return classifications

    def __third_predict(self, chunks, classifications, inds):

        print('\textracting  features (pass three)')

        # Extract features between pairs of chunks
        unvectorized_X = feat_obj.extract_third_pass_features(
            chunks, inds, bow=self.bow)

        print('\tvectorizing features (pass three)')

        # Vectorize features
        X = self.third_vec.transform(unvectorized_X)

        print('\tpredicting    labels (pass three)')

        # Predict concept labels
        predicted_relationships = sci.predict(self.third_clf, X)

        classifications_cpy = list(classifications)

        # Stitch SVM output into clustered token span classifications
        clustered = []
        for indices in inds:

            # Cannot have pairwise relationsips with either 0 or 1 objects
            if len(indices) == 0:
                continue

            elif len(indices) == 1:
                # Contiguous span (adjust format to (length-1 list of tok
                # spans)
                tup = list(classifications_cpy.pop(0))
                tup = (tup[0], tup[1], [(tup[2], tup[3])])
                clustered.append(tup)

            else:

                # Number of classifications on the line
                tups = []
                for _ in range(len(indices)):
                    tup = list(classifications_cpy.pop(0))
                    tup = (tup[0], tup[1], [(tup[2], tup[3])])
                    tups.append(tup)

                # Pairwise clusters
                clusters = {}

                # ASSUMPTION: All classifications have same label
                concept = tups[0][0]
                lineno = tups[0][1]
                spans = [t[2][0] for t in tups]

                # Keep track of non-clustered spans
                singulars = list(tups)

                # Get all pairwise relationships for the line
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        pair = predicted_relationships.pop(0)
                        if pair == 1:
                            tup = (concept, lineno, [spans[i], spans[j]])
                            clustered.append(tup)

                            # No longer part of a singular span
                            if tups[i] in singulars:
                                singulars.remove(tups[i])
                            if tups[j] in singulars:
                                singulars.remove(tups[j])

                clustered += singulars

        return clustered

    ##########################################################################
    ###               Lowest-level (interfaces to ML modules)                ###
    ##########################################################################

    def __generic_first_train(self, p_or_n, text_features, iob_labels, do_grid=False):
        '''
        Model::__generic_first_train()

        Purpose: Train that works for both prose and nonprose

        @param p_or_n.        <string> either "prose" or "nonprose"
        @param text_features. <list-of-lists> of feature dictionaries
        @param iob_labels.    <list> of "I", "O", and "B" labels
        @param do_grid.       <boolean> indicating whether to perform grid search
        '''

        # Must have data to train on
        if len(text_features) == 0:
            raise Exception('Training must have %s training examples' % p_or_n)

        # Vectorize IOB labels
        Y_labels = [IOB_labels[y] for y in iob_labels]

        # Save list structure to reconstruct after vectorization
        offsets = save_list_structure(text_features)

        if globals_cliner.verbosity > 0:
            print('\tvectorizing features (pass one) ' + p_or_n)

        #X = reconstruct_list(flatten(text_features), offsets)
        #Y = reconstruct_list(        Y_labels      , offsets)
        # for a,b in zip(X,Y):
        #    for x,y in zip(a,b):
        #        print y
        #        #print filter(lambda t:t[0]=='word', x.keys())
        #        print x.keys()
        #        print
        #    print '\n\n\n'

        # Vectorize features
        dvect = DictVectorizer()
        X_feats = dvect.fit_transform(flatten(text_features))

        # CRF needs reconstructed lists
        if self._crf_enabled:
            X_feats = reconstruct_list(list(X_feats), offsets)
            Y_labels = reconstruct_list(Y_labels, offsets)
            lib = crf
        else:
            lib = sci

        if globals_cliner.verbosity > 0:
            print('\ttraining classifiers (pass one) ' + p_or_n)

        # for i,X in enumerate(X_feats):
        #    for j,x in enumerate(X):
        #        print x, '\t', Y_labels[i][j]
        #    print
        # exit()

        # Train classifier
        clf = lib.train(X_feats, Y_labels, do_grid)

        return dvect, clf

    def __generic_first_predict(self, p_or_n, text_features, dvect, clf, do_grid=False):
        '''
        Model::__generic_first_predict()

        Purpose: Train that works for both prose and nonprose

        @param p_or_n.        <string> either "prose" or "nonprose"
        @param text_features. <list-of-lists> of feature dictionaries
        @param dvect.         <DictVectorizer>
        @param clf.           scikit-learn classifier
        @param do_grid.       <boolean> indicating whether to perform grid search
        '''

        # If nothing to predict, skip actual prediction
        if len(text_features) == 0:
            print('\tnothing to predict (pass one) ' + p_or_n)
            return []

        # Save list structure to reconstruct after vectorization
        offsets = save_list_structure(text_features)

        if globals_cliner.verbosity > 0:
            print('\tvectorizing features (pass one) ' + p_or_n)

        # Vectorize features
        X_feats = dvect.transform(flatten(text_features))

        if globals_cliner.verbosity > 0:
            print('\tpredicting    labels (pass one) ' + p_or_n)

        # CRF requires reconstruct lists
        if self._crf_enabled:
            X_feats = reconstruct_list(list(X_feats), offsets)
            lib = crf
        else:
            lib = sci

        # for X in X_feats:
        #    for x in X:
        #        print x
        #    print
        # print '\n'

        # Predict IOB labels
        out = lib.predict(clf, X_feats)

        # Format labels from output
        predictions = reconstruct_list(out, offsets)
        return predictions


def extract_concept_features(chunked_sentences, inds_list, feat_obj):
    ''' extract conept (2nd pass) features from textual data '''
    X = []
    for s, inds in zip(chunked_sentences, inds_list):
        X += feat_obj.concept_features(s, inds)
    return X


def first_pass_data_and_labels(notes):
    '''
    first_pass_data_and_labels()

    Purpose: Interface with notes object to get text data and labels

    @param notes. List of Note objects
    @return <tuple> whose elements are:
              0) list of tokenized sentences
              1) list of labels for tokenized sentences

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> con = os.path.join(base_dir, 'single.con')
    >>> note_tmp = Note('i2b2')
    >>> note_tmp.read(txt, con)
    >>> notes = [note_tmp]
    >>> first_pass_data_and_labels(notes)
    ([['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']], [['B', 'I', 'I', 'I', 'I', 'I', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']])
    '''

    # Get the data and annotations from the Note objects
    l_tokenized_sentences = [note.getTokenizedSentences() for note in notes]
    l_iob_labels = [note.getIOBLabels() for note in notes]

    tokenized_sentences = flatten(l_tokenized_sentences)
    iob_labels = flatten(l_iob_labels)

    return tokenized_sentences, iob_labels


def second_pass_data_and_labels(notes):
    '''
    second_pass_data_and_labels()

    Purpose: Interface with notes object to get text data and labels

    @param notes. List of Note objects
    @return <tuple> whose elements are:
              0) list of chunked sentences
              0) list of list-of-indices designating chunks
              1) list of labels for chunks

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> con = os.path.join(base_dir, 'single.con')
    >>> note_tmp = Note('i2b2')
    >>> note_tmp.read(txt, con)
    >>> notes = [note_tmp]
    >>> second_pass_data_and_labels(notes)
    ([['The score stood four to two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']], [[0]], ['problem'])
    '''

    # Get the data and annotations from the Note objects
    l_chunked_sentences = [note.getChunkedText() for note in notes]
    l_inds_list = [note.getConceptIndices() for note in notes]
    l_con_labels = [note.getConceptLabels() for note in notes]

    chunked_sentences = flatten(l_chunked_sentences)
    inds_list = flatten(l_inds_list)
    con_labels = flatten(l_con_labels)

    # print 'labels: ', len(con_labels)
    # print 'inds:   ', sum(map(len,inds_list))
    # exit()

    return chunked_sentences, inds_list, con_labels


def first_pass_data(note):
    '''
    first_pass_data()

    Purpose: Interface with notes object to get first pass data

    @param note. Note objects
    @return      <list> of tokenized sentences

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> note = Note('i2b2')
    >>> note.read(txt)
    >>> first_pass_data(note)
    [['The', 'score', 'stood', 'four', 'to', 'two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']]
    '''

    return note.getTokenizedSentences()


def second_pass_data(note):
    '''
    second_pass_data()

    Purpose: Interface with notes object to get second pass data

    @param notes. List of Note objects
    @return <tuple> whose elements are:
              0) list of chunked sentences
              0) list of list-of-indices designating chunks

    >>> import os
    >>> from notes.note import Note
    >>> base_dir = os.path.join(os.getenv('CLINER_DIR'), 'tests', 'data')
    >>> txt = os.path.join(base_dir, 'single.txt')
    >>> note = Note('i2b2')
    >>> note.read(txt, con)
    >>> second_pass_data(note)
    ([['The score stood four to two', ',', 'with', 'but', 'one', 'inning', 'more', 'to', 'play', ',']], [[0]])
    '''

    # Get the data and annotations from the Note objects
    chunked_sentences = note.getChunkedText()
    inds = note.getConceptIndices()

    return chunked_sentences, inds


def fit_bag_of_words(bow_obj, data, unlabeled_data=None):

    global bow

    """ needs to be a list of strings """

    corpus = data

    if unlabeled_data is not None:

        corpus += unlabeled_data

    if bow_obj.is_fitted() is False:

        docs = [' '.join(chunk) for chunk in corpus]

        bow_obj.fit(docs)


def concat(a, b):
    return a + b
