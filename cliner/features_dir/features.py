######################################################################
#  CliCon - clicon_features.py                                       #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate the model's features from model.py               #
######################################################################


__author__ = 'Willie Boag'
__date__ = 'Jan. 27, 2014'

import cliner.features_dir.sentence_features as feat_sent

# display enabled modules to user
feat_sent.display_enabled_modules()


def IOB_prose_features(nested_prose_data):
    """
    IOB_prose_features()

    @param data      A list of split sentences (1 sent = 1 line from file)
    @param Y         A list of list of IOB (1:1 mapping with data)
    @return          tuple: list of IOB_prose_features, list of IOB

    """
    # Genia preprocessing
    feat_sent.sentence_features_preprocess(nested_prose_data)

    prose_feats = []
    for sentence in nested_prose_data:
        prose_feats.append(feat_sent.IOB_prose_features(sentence))
    return prose_feats


def IOB_nonprose_features(nonprose_data):
    """
    IOB_nonprose_features()

    @param data      A list of split sentences (1 sent = 1 line from file)
    @param Y         A list of list of IOB (1:1 mapping with data)
    @return          tuple: list of IOB_prose_features, list of IOB

    """
    nonprose_feats = []
    for sentence in nonprose_data:
        nonprose_feats.append(feat_sent.IOB_nonprose_features(sentence))
    return nonprose_feats


def concept_features(sentence, chunk_inds):
    """
    concept_features()

    @param sentence.   a list of chunks
    @param chunk_inds. a list of important indices of the sentence
    @return            a list of dictionaries of features

    >>> concept_features(['this', 'is', 'an', 'important', 'test'],
                         [3, 4]) is not None
    True
    """
    # FIXME - move all of this work to SentenceFeatures object

    '''
    # VERY basic feature set for sanity check tests during development
    features_list = []
    for i,ind in enumerate(chunk_inds):
        features = {('phrase',sentence[ind]) : 1}
        features_list.append(features)
    return features_list
    '''

    # Create a list of feature sets (one per chunk)
    features_list = feat_sent.concept_features_for_sentence(sentence,
                                                            chunk_inds)
    return features_list


def extract_third_pass_features(chunks, inds, bow=None):

    unvectorized_X = []

    for lineno, indices in enumerate(inds):

        features = feat_sent.third_pass_features(chunks[lineno], indices,
                                                 bow_model=bow)

        unvectorized_X += features

    return unvectorized_X
