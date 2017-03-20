######################################################################
#  CliNER - train.py                                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Build model for given training data.                     #
######################################################################


__author__ = 'Willie Boag'
__date__ = 'Oct. 5, 2014'


import os
import os.path
import glob
import argparse
import pickle as pickle
import sys

from cliner import helper
from cliner.model import Model
from cliner.notes.note import Note
from cliner.notes.utilities_for_notes import NoteException

sys.path.append(os.path.join(
    *[os.environ["CLINER_DIR"], "cliner", "features_dir"]))

from read_config import enabled_modules

# Import feature modules
enabled = enabled_modules()

if enabled.get('UMLS', False):

    from .disambiguation import cui_disambiguation


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
                        dest="txt",
                        help="The files that contain the training examples",
                        )

    parser.add_argument("-c",
                        dest="con",
                        help="The files that contain the labels for the training examples",
                        )

    parser.add_argument("-m",
                        dest="model",
                        help="Path to the model that should be generated",
                        )

    parser.add_argument("-f",
                        dest="format",
                        help="Data format ( " +
                        ' | '.join(Note.supportedFormats()) + " )",
                        )

    parser.add_argument("-g",
                        dest="grid",
                        help="A flag indicating whether to perform a grid search",
                        action="store_true"
                        )

    parser.add_argument("-no-crf",
                        dest="nocrf",
                        help="A flag indicating whether to use crfsuite for pass one.",
                        action="store_true"
                        )

    parser.add_argument("-discontiguous_spans",
                        dest="third",
                        help="A flag indicating whether to have third/clustering pass",
                        action="store_true"
                        )

    parser.add_argument("-umls_disambiguation",
                        dest="umls_disambiguation",
                        action="store_true",
                        help="A flag indicating wheter to disambiguate CUI id for detected entities in semeval format",
                        )

    """
    parser.add_argument("-unlabeled",
        dest = "unlabeled",
        help = "Path to dir containing unlabelled data used for unsupervised methods",
    )
    """

    # Parse the command line arguments
    args = parser.parse_args()
    is_crf = not args.nocrf
    third = args.third

    # Error check: Ensure that file paths are specified
    if not args.txt:
        print('\n\tError: Must provide text files', file=sys.stderr)
        print('', file=sys.stderr)
        exit(1)
    if not args.con:
        print('\n\tError: Must provide annotations for text files', file=sys.stderr)
        print('', file=sys.stderr)
        exit(1)
    if not args.model:
        print('\n\tError: Must provide valid path to store model', file=sys.stderr)
        print('', file=sys.stderr)
        exit(1)
    modeldir = os.path.dirname(args.model)
    if (not os.path.exists(modeldir)) and (modeldir != ''):
        print('\n\tError: Model dir does not exist: %s' %
              modeldir, file=sys.stderr)
        print('', file=sys.stderr)
        exit(1)

    if "PY4J_DIR_PATH" not in os.environ and args.third is True:
        exit("please set environ var PY4J_DIR_PATH to the dir of the folder containg py4j<version>.jar")

    # A list of text    file paths
    # A list of concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)

    # data format
    if args.format:
        format = args.format
    else:
        print('\n\tERROR: must provide "format" argument\n')
        exit()

    if third is True and args.format == "i2b2":
        exit("i2b2 formatting does not support disjoint spans")

    # Must specify output format
    if format not in Note.supportedFormats():
        print('\n\tError: Must specify output format', file=sys.stderr)
        print('\tAvailable formats: ', ' | '.join(
            Note.supportedFormats()), file=sys.stderr)
        print('', file=sys.stderr)
        exit(1)

    # Collect training data file paths
    # ex. {'record-13': 'record-13.con'}
    txt_files_map = helper.map_files(txt_files)
    con_files_map = helper.map_files(con_files)

    # ex. training_list =  [ ('record-13.txt', 'record-13.con') ]
    training_list = []
    for k in txt_files_map:
        if k in con_files_map:
            training_list.append((txt_files_map[k], con_files_map[k]))

    # Train the model
    train(training_list, args.model, format, is_crf=is_crf,
          grid=args.grid, third=third, disambiguate=args.umls_disambiguation)


def train(training_list, model_path, format, is_crf=True, grid=False, third=False, disambiguate=False):
    """
    train()

    Purpose: Train a model for given clinical data.

    @param training_list  list of (txt,con) file path tuples (training instances)
    @param model_path     string filename of where to pickle model object
    @param format         concept file data format (ex. i2b2, semeval)
    @param is_crf         whether first pass should use CRF classifier
    @param grid           whether second pass should perform grid search
    @param third          whether to perform third/clustering pass
    """

    # Read the data into a Note object
    notes = []
    for txt, con in training_list:

        note_tmp = Note(format)   # Create Note
        note_tmp.read(txt, con)   # Read data into Note
        notes.append(note_tmp)    # Add the Note to the list

    # file names
    if not notes:
        print('Error: Cannot train on 0 files. Terminating train.')
        return 1

    # Create a Machine Learning model
    model = Model(is_crf=is_crf)

    # disambiguation
    if format == "semeval" and disambiguate is True and enabled.get('UMLS', False) != None:
        model.set_cui_freq(cui_disambiguation.calcFreqOfCuis(training_list))

    # Train the model using the Note's data
    model.train(notes, grid, do_third=third)

    # Pickle dump
    print('\nserializing model to %s\n' % model_path)
    with open(model_path, "wb") as m_file:
        pickle.dump(model, m_file)

    # return trained model
    return model


if __name__ == '__main__':
    main()
