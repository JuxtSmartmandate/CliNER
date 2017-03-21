#####################################################################
#  CliCon - sentence_features.py                                     #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
# Purpose: Isolate the model's sentence - level features               #
######################################################################

import sys
import os
import re

from cliner.features_dir.utilities import load_pos_tagger
from cliner.features_dir import word_features as feat_word

# What modules are available
from cliner.features_dir.read_config import enabled_modules

__author__ = 'Willie Boag'
__date__ = 'Apr. 27, 2014'

CLINER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          *["..", ".."])

# Import feature modules
enabled = enabled_modules()
if enabled.get('GENIA', False):
    from .genia_dir.genia_features import GeniaFeatures

if enabled.get("BROWN", False):
    from .BrownCluster import BrownCluster
    bc = BrownCluster(enabled.get("BROWN", False))

# Only create UMLS cache if module is available
if enabled.get('UMLS', False):
    from cliner.features_dir.umls_dir import interpret_umls
    from cliner.features_dir.umls_dir import umls_features as feat_umls

    from .umls_dir.umls_cache import UmlsCache

    umls_cache = UmlsCache()


nltk_tagger = load_pos_tagger()

# Feature Enabling
enabled_concept_features = frozenset(["UMLS", "grammar_features"])

if enabled.get('GENIA', False):
    feat_genia = None

if enabled.get("WORD2VEC", False):
    from cliner.features_dir.word2vec_dir.clustering import\
        predict_sequence_cluster

enabled_IOB_nonprose_sentence_features = []
# enabled_IOB_nonprose_sentence_features.append('pos')
# enabled_IOB_nonprose_sentence_features.append('pos_context')
enabled_IOB_nonprose_sentence_features.append('prev')
enabled_IOB_nonprose_sentence_features.append('next')
enabled_IOB_nonprose_sentence_features.append('unigram_context')
enabled_IOB_nonprose_sentence_features.append('UMLS')

enabled_IOB_prose_sentence_features = []
enabled_IOB_prose_sentence_features.append('unigram_context')
enabled_IOB_prose_sentence_features.append('pos')
enabled_IOB_prose_sentence_features.append('pos_context')
enabled_IOB_prose_sentence_features.append('prev')
enabled_IOB_prose_sentence_features.append('prev2')
enabled_IOB_prose_sentence_features.append('next')
enabled_IOB_prose_sentence_features.append('next2')
enabled_IOB_prose_sentence_features.append('GENIA')
enabled_IOB_prose_sentence_features.append('UMLS')

dependency_parser = None

if enabled.get("PY4J", False):
    stanford_dir = os.path.join(CLINER_DIR,
                                *["cliner", "lib", "java", "stanford_nlp"])
    sys.path.append(stanford_dir)

    from stanfordParse import DependencyParser
    from IPython.core.debugger import Tracer  # NOQA
    Tracer()()
    dependency_parser = DependencyParser()


def display_enabled_modules():
    print()
    for module, status in list(enabled.items()):
        if status:
            print('\t', module, '\t', ' ENABLED')
        else:
            print('\t', module, '\t', 'DISABLED')
    print()


def sentence_features_preprocess(data):
    global feat_genia
    tagger = enabled.get('GENIA', False)
    # Only run GENIA tagger if module is available
    if tagger:
        feat_genia = GeniaFeatures(tagger, data)


def IOB_prose_features(sentence, data=None):
    """
    IOB_prose_features

    @param sentence. A list of strings
    @return          A list of dictionaries of features

    """
    features_list = []

    # Initialize feat_genia if not done so already
    global feat_genia
    if data and enabled.get('GENIA', False) and not feat_genia:
        # Only run GENIA tagger if module is available
        tagger = enabled.get('GENIA', False)
        feat_genia = GeniaFeatures(tagger, data)

    # Get a feature set for each word in the sentence
    for i, word in enumerate(sentence):
        features_list.append(feat_word.IOB_prose_features(sentence[i]))

    # Feature: Bag of Words unigram conext (window=3)
    if 'unigram_context' in enabled_IOB_prose_sentence_features:
        window = 3
        n = len(sentence)

        # Previous unigrams
        for i in range(n):
            end = min(i, window)
            unigrams = sentence[i - end:i]
            for j, u in enumerate(unigrams):
                features_list[i][('prev_unigrams - %d' % j, u)] = 1

        # Next     unigrams
        for i in range(n):
            end = min(i + window, n - 1)
            unigrams = sentence[i + 1:end + 1]
            for j, u in enumerate(unigrams):
                features_list[i][('next_unigrams - %d' % j, u)] = 1

    # Only POS tag once
    if 'pos' in enabled_IOB_prose_sentence_features:
        pos_tagged = nltk_tagger.tag(sentence)

    # Allow for particular features to be enabled
    for feature in enabled_IOB_prose_sentence_features:

        # Feature: Part of Speech
        if feature == 'pos':
            for (i, (_, pos))in enumerate(pos_tagged):
                features_list[i].update({('pos', pos): 1})

        # Feature: POS context
        if 'pos_context' in enabled_IOB_prose_sentence_features:
            window = 3
            n = len(sentence)

            # Previous POS
            for i in range(n):
                end = min(i, window)
                for j, p in enumerate(pos_tagged[i - end:i]):
                    pos = p[1]
                    features_list[i][('prev_pos_context - %d' % j, pos)] = 1

            # Next POS
            for i in range(n):
                end = min(i + window, n - 1)
                for j, p in enumerate(pos_tagged[i + 1:i + end + 1]):
                    pos = p[1]
                    features_list[i][('prev_pos_context - %d' % j, pos)] = 1

        # GENIA features
        if (feature == 'GENIA')and enabled.get('GENIA', False):

            # Get GENIA features
            genia_feat_list = feat_genia.features(sentence)

            '''
            print '\t', sentence

            print '\n\n'
            for gf in genia_feat_list:
                print '\t', gf
                print
            print '\n\n'
            '''

            for i, feat_dict in enumerate(genia_feat_list):
                features_list[i].update(feat_dict)

        # Feature: UMLS Word Features (only use prose ones)
        if (feature == "UMLS") and enabled.get("UMLS", False):
            umls_features = feat_umls.IOB_prose_features(sentence)
            for i in range(len(sentence)):
                features_list[i].update(umls_features[i])

    # Used for 'prev' and 'next' features
    ngram_features = [{} for i in range(len(features_list))]
    if "prev" in enabled_IOB_prose_sentence_features:
        prev = lambda f: {("prev_" + k[0], k[1]): v
                          for k, v in list(f.items())}
        prev_list = list(map(prev, features_list))
        for i in range(len(features_list)):
            if i == 0:
                ngram_features[i][("prev", "*")] = 1
            else:
                ngram_features[i].update(prev_list[i - 1])

    if "prev2" in enabled_IOB_prose_sentence_features:
        prev2 = lambda f: {
            ("prev2_" + k[0], k[1]): v / 2.0 for k, v in list(f.items())}
        prev_list = list(map(prev2, features_list))
        for i in range(len(features_list)):
            if i == 0:
                ngram_features[i][("prev2", "*")] = 1
            elif i == 1:
                ngram_features[i][("prev2", "*")] = 1
            else:
                ngram_features[i].update(prev_list[i - 2])

    if "next" in enabled_IOB_prose_sentence_features:
        next = lambda f: {("next_" + k[0], k[1]): v
                          for k, v in list(f.items())}
        next_list = list(map(next, features_list))
        for i in range(len(features_list)):
            if i < len(features_list) - 1:
                ngram_features[i].update(next_list[i + 1])
            else:
                ngram_features[i][("next", "*")] = 1

    if "next2" in enabled_IOB_prose_sentence_features:
        next2 = lambda f: {
            ("next2_" + k[0], k[1]): v / 2.0 for k, v in list(f.items())}
        next_list = list(map(next2, features_list))
        for i in range(len(features_list)):
            if i < len(features_list) - 2:
                ngram_features[i].update(next_list[i + 2])
            elif i == len(features_list) - 2:
                ngram_features[i][("next2", "**")] = 1
            else:
                ngram_features[i][("next2", "*")] = 1

    merged = lambda d1, d2: dict(list(d1.items()) + list(d2.items()))
    features_list = [merged(features_list[i], ngram_features[i])
                     for i in range(len(features_list))]

    '''
    for f in features_list:
        print sorted(f.items())
        print
    print '\n\n\n'
    '''

    return features_list


def IOB_nonprose_features(sentence):
    """
    IOB_nonprose_features

    @param sentence. A list of strings
    @return          A list of dictionaries of features

    """

    # Get a feature set for each word in the sentence
    features_list = []
    for i, word in enumerate(sentence):
        word_feats = feat_word.IOB_nonprose_features(sentence[i])
        features_list.append(word_feats)

    # Feature: Bag of Words unigram conext (window=3)
    if 'unigram_context' in enabled_IOB_nonprose_sentence_features:
        window = 3
        n = len(sentence)

        # Previous unigrams
        for i in range(n):
            end = min(i, window)
            unigrams = sentence[i - end:i]
            for j, u in enumerate(unigrams):
                features_list[i][('prev_unigrams - %d' % j, u)] = 1

        # Next     unigrams
        for i in range(n):
            end = min(i + window, n - 1)
            unigrams = sentence[i + 1:end + 1]
            for u in unigrams:
                features_list[i][('next_unigrams - %d' % j, u)] = 1

    # Feature: UMLS Word Features (only use nonprose ones)
    if enabled.get('UMLS', False) and 'UMLS' in enabled_IOB_nonprose_sentence_features:
        umls_features = feat_umls.IOB_nonprose_features(sentence)
        for i in range(len(sentence)):
            features_list[i].update(umls_features[i])

    if 'pos' in enabled_IOB_nonprose_sentence_features:
        pos_tagged = nltk_tagger.tag(sentence)

    # Allow for particular features to be enabled
    for feature in enabled_IOB_nonprose_sentence_features:

        # Feature: Part of Speech
        if feature == 'pos':
            for (i, (_, pos))in enumerate(pos_tagged):
                features_list[i][('pos', pos)] = 1

        # Feature: POS context
        if 'pos_context' in enabled_IOB_nonprose_sentence_features:
            window = 3
            n = len(sentence)

            # Previous POS
            for i in range(n):
                end = min(i, window)
                for j, p in enumerate(pos_tagged[i - end:i]):
                    pos = p[1]
                    features_list[i][('prev_pos_context - %d' % j, pos)] = 1

            # Next POS
            for i in range(n):
                end = min(i + window, n - 1)
                for j, p in enumerate(pos_tagged[i + 1:i + end + 1]):
                    pos = p[1]
                    features_list[i][('prev_pos_context - %d' % j, pos)] = 1

    ngram_features = [{} for _ in range(len(features_list))]
    if "prev" in enabled_IOB_nonprose_sentence_features:
        prev = lambda f: {("prev_" + k[0], k[1]):
                          v for k, v in list(f.items())}
        prev_list = list(map(prev, features_list))
        for i in range(len(features_list)):
            if i == 0:
                ngram_features[i][("prev", "*")] = 1
            else:
                ngram_features[i].update(prev_list[i - 1])

    if "next" in enabled_IOB_nonprose_sentence_features:
        next = lambda f: {("next_" + k[0], k[1]): v
                          for k, v in list(f.items())}
        next_list = list(map(next, features_list))
        for i in range(len(features_list)):
            if i == len(features_list) - 1:
                ngram_features[i][("next", "*")] = 1
            else:
                ngram_features[i].update(next_list[i + 1])

    merged = lambda d1, d2: dict(list(d1.items()) + list(d2.items()))
    features_list = [merged(features_list[i], ngram_features[i])
                     for i in range(len(features_list))]

    return features_list


def concept_features_for_sentence(sentence, chunk_inds):
    """
    concept_features()

    @param  sentence.   A sentence in list of chunk format
    @param  chunk_inds. A list of indices for non - None - labeled chunks
    @return             A list of feature dictionaries
    """

    global dependency_parser

    # Get a feature set for each word in the sentence
    features_list = []
    for ind in chunk_inds:
        features_list.append(
            feat_word.concept_features_for_chunk(sentence, ind))

    dependencies = None

    if dependency_parser is not None:
        dependencies = dependency_parser.get_collapsed_dependencies(sentence)

    # Allow for particular features to be enabled
    for feature in enabled_concept_features:

        # Features: UMLS features
        if (feature == "UMLS")and enabled.get('UMLS', False):
            umls_features = feat_umls.concept_features_for_chunks(
                sentence, chunk_inds)
            for i in range(len(chunk_inds)):
                features_list[i].update(umls_features[i])

        if (feature == "grammar_features" and enabled.get("PY4J", False)):
            print("getting grammar features")
            for i, target_index in enumerate(chunk_inds):
                if dependencies is not None:
                    try:
                        features_list[i].update(dependency_parser.get_related_tokens(
                            target_index, sentence, dependencies))
                    except Exception as err:
                        from IPython.core.debugger import Tracer  # NOQA
                        Tracer()()

    if enabled.get("WORD2VEC", False):
        print("getting vectors...")
        for i, chunk_index in enumerate(chunk_inds):

            chunk = sentence[chunk_index]
            cluster = predict_sequence_cluster(chunk)

            features_list[i].update({("cluster", cluster): 1})

    return features_list


def getTypesOfRel(start, end, dependencies):
    """
    returns a list of list of tokens indicating the types of relations between

    dependencies.
    """

    global dependency_parser

    lOflOfRelations = []

    # list of list of strings
    paths = dependency_parser.follow_dependency_path(start, end, dependencies)

    for l in paths:
        # get relations from ordered token list
        indices = list(range(1, len(l), 2))
        tmpL = [l[i] for i in indices]

        lOflOfRelations.append(tmpL)

    return getShortestList(lOflOfRelations)


def getTokens(start, end, dependencies):
    """ get the tokens between two words within a dependency path """

    lOflOftokens = []

    from IPython.core.debugger import Tracer  # NOQA
    Tracer()()
    paths = dependency_parser.follow_dependency_path(start, end, dependencies)

    for l in paths:
        # get relations from ordered token list
        indices = list(range(0, len(l), 2))
        tmpL = [l[i] for i in indices]

        # only want the tokens between the start and end.
        lOflOftokens.append(tmpL[1: - 1])

    return getShortestList(lOflOftokens)


def getNumOfObjects(lOfObjects):
    return len(lOfObjects)


def getShortestList(lists):

    shortestList = []

    for l in lists:

        if len(shortestList)is 0:
            shortestList = l
        elif len(l) < len(shortestList):
            shortestList = l

    return shortestList


def third_pass_features(line, indices, bow_model=None):
    """ extract third pass features
        running this assumes all the dependencies are properly installed.
    """

    global dependency_parser

    # only instantiate once.
    if dependency_parser is None:

        sys.path.append(os.path.join(
            *[os.environ["CLINER_DIR"], "cliner", "lib", "java", "stanford_nlp"]))
        from stanfordParse import DependencyParser

        from IPython.core.debugger import Tracer  # NOQA
        Tracer()()
        dependency_parser = DependencyParser()

    heads = []

    tagged_line = None
    sentence = " ".join(line)

    # Cannot have pairwise relationsips with either 0 or 1 objects
    if len(indices) < 2:
        return []

    else:

        # get dependency paths for tokens in line.
        if len(line) <= 100:
            from IPython.core.debugger import Tracer  # NOQA
            Tracer()()
            heads = dependency_parser.getNounPhraseHeads(sentence)

            #  the parser takes way too long to run for really long strings.
            from IPython.core.debugger import Tracer  # NOQA
            Tracer()()
            dependencies = dependency_parser.get_collapsed_dependencies(
                " ".join(line))
        else:
            dependencies = []

        tagged_line = nltk_tagger.tag(line)

    features_list = []

    # Build (n choose 2)booleans
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):

            feats = {}

            start = line[indices[i]].lower()
            end = line[indices[j]].lower()

            between_tokens = line[(indices[i] + 1): indices[j]]
            bow = bow_model.transform([' '.join(between_tokens)])[0]

            for _, pos in tagged_line[(indices[i] + 1): indices[j]]:
                feats[('pos', pos)] = 1

            for key in bow:
                feats[('bow', key)] = bow[key]

            start_tokens = start.split()
            start_tokens = [re.sub("[^A - Za - z0 - 9]", "", token)
                            for token in start_tokens]
            start_tokens = [token for token in start_tokens if token != '']

            if enabled.get("BROWN", False):

                for token in start_tokens:
                    cluster_str = bc.get_first_n_bits(token, -1)

                    feats[("brown_cluster_first_2_bits_start_word",
                           token)] = cluster_str[:2]
                    feats[("brown_cluster_first_4_bits_start_word",
                           token)] = cluster_str[:4]
                    feats[("brown_cluster_first_6_bits_start_word",
                           token)] = cluster_str[:6]
                    feats[("brown_cluster_first_8_bits_start_word",
                           token)] = cluster_str[:8]

                end_tokens = end.split()
                end_tokens = [re.sub("[^A - Za - z0 - 9]", "", token)
                              for token in end_tokens]
                end_tokens = [token for token in end_tokens if token != '']

                for token in end_tokens:
                    cluster_str = bc.get_first_n_bits(token, -1)

                    feats[("brown_cluster_first_2_bits_end_word", token)
                          ] = cluster_str[:2]
                    feats[("brown_cluster_first_4_bits_end_word", token)
                          ] = cluster_str[:4]
                    feats[("brown_cluster_first_6_bits_end_word", token)
                          ] = cluster_str[:6]
                    feats[("brown_cluster_first_8_bits_end_word", token)
                          ] = cluster_str[:8]

            if len(heads) > 0:

                contains = 0
                for head in heads:
                    if head in start:
                        contains = 1
                        break

                feats[('contains_NP_head', start)] = contains

                contains = 0
                for head in heads:
                    if head in end:
                        contains = 1
                        break

                feats[('contains_NP_head', end)] = contains

            get_cui = interpret_umls.obtain_concept_ids

            start_cui = get_cui(umls_cache, start, PyPwl=None)
            end_cui = get_cui(umls_cache, end, PyPwl=None)
            disjoint_cui = get_cui(
                umls_cache, "{} {}".format(start, end), PyPwl=None)

            feats[('start_cui', start_cui)] = 1
            feats[('end_cui', end_cui)] = 1
            feats[('disjoint_cui', disjoint_cui)] = 1

            # Features of pair relationship
            lOfRels = getTypesOfRel(start, end, dependencies)

            feats[('dependency_relation', None)] = (len(lOfRels) > 0)

            numOfRels = getNumOfObjects(lOfRels)

            lOfTokes = getTokens(start, end, dependencies)

            numOfTokes = getNumOfObjects(lOfTokes)

            feats[('rels_btwn_depen', None)] = numOfRels
            feats['num_of_depen_tokes'] = numOfTokes

            # feats[("tokes_that_exists_in_umls_db", None)] = interface_umls.substrs_that_exists([start, end], pwl)

            # Feature: Left Unigrams
            for tok in line[indices[i]].split():
                tok = tok.lower()
                feats[('left_unigram', tok)] = 1

            # Feature: Right Unigrams
            for tok in line[indices[j]].split():
                tok = tok.lower()
                feats[('right_unigram', tok)] = 1

            # Feature: Unigrams between spans
            for tok in ' '.join(line[indices[i + 1]:indices[j]]).split():
                tok = tok.lower()
                feats[('inner_unigram', tok)] = 1

            # Feature: Number of chunks between spans
            feats[('span_dist', None)] = len(line[indices[i + 1]:indices[j]])

            # Add pair features to list of data points
            features_list.append(feats)

    return features_list
