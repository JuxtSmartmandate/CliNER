######################################################################
#  CliNER - predict.py                                               #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Use trained model to predict concept labels for data.    #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Oct. 5, 2014'


import os
import sys
import glob
import argparse
from cliner import helper
import re
import string
import time
import itertools
import pickle as pickle
import copy

from cliner.model import Model
from cliner.notes.note import Note
from multiprocessing import Pool

sys.path.append(os.path.join(*[os.environ["CLINER_DIR"], "cliner", "features_dir"]))

from read_config import enabled_modules

# Import feature modules
enabled = enabled_modules()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "input",
        help = "The input files to predict",
    )

    parser.add_argument("-o",
        dest = "output",
        help = "The directory to write the output",
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The model to use for prediction",
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )",
    )

    parser.add_argument("-crf",
        dest = "with_crf",
        help = "Specify where to find crfsuite",
        default = None
    )

    parser.add_argument("-discontiguous_spans",
        dest = "third",
        help = "A flag indicating whether to have third/clustering pass",
        action = "store_true"
    )

    parser.add_argument("-umls_disambiguation",
        dest = "disambiguate",
        help = "A flag indicating whether to disambiguate CUI ID for identified entities in semeval",
        action = "store_true"
    )

    args = parser.parse_args()

    # Error check: Ensure that file paths are specified
    if not args.input:
        print('\n\tError: Must provide text files\n', file=sys.stderr)
        exit(1)
    if not args.output:
        print('\n\tError: Must provide output directory\n', file=sys.stderr)
        exit(1)
    if not args.model:
        print('\n\tError: Must provide path to model\n', file=sys.stderr)
        exit(1)
    if not os.path.exists(args.model):
        print('\n\tError: Model does not exist: %s\n' % args.model, file=sys.stderr)
        exit(1)


    # Parse arguments
    files = glob.glob(args.input)
    helper.mkpath(args.output)

    third = args.third

    if args.format:
        format = args.format
    else:
        print('\n\tERROR: must provide "format" argument\n')
        exit()

    if third is True and args.format == "i2b2":
        exit("i2b2 formatting does not support disjoint spans")

    # Tell user if not predicting
    if not files:
        print("\n\tNote: You did not supply any input files\n", file=sys.stderr)
        exit()

    # Predict
    predict(files, args.model, args.output, format=format, third=third, disambiguate=args.disambiguate)




def predict(files, model_path, output_dir, format, third=False, disambiguate=False):

    # Must specify output format
    if format not in Note.supportedFormats():
        print('\n\tError: Must specify output format', file=sys.stderr)
        print('\tAvailable formats: ', ' | '.join(Note.supportedFormats()), file=sys.stderr)
        print('', file=sys.stderr)
        exit(1)


    # Load model
    model = Model.load(model_path)


    # Tell user if not predicting
    if not files:
        print("\n\tNote: You did not supply any input files\n", file=sys.stderr)
        exit()

    if enabled["UMLS"] is not None and disambiguate is True:
        from .disambiguation import cui_disambiguation

    # For each file, predict concept labels
    n = len(files)
    for i,txt in enumerate(sorted(files)):

        note = Note(format)
        note.read(txt)

        # Output file
        extension = note.getExtension()
        fname = os.path.splitext(os.path.basename(txt))[0] + '.' + extension
        out_path = os.path.join(output_dir, fname)
        #if os.path.exists(out_path):
        #    print '\tWARNING: prediction file already exists (%s)' % out_path
        #    continue

        if format == "semevaL":
            note.setFileName(os.path.split(txt)[-1])

        # Predict concept labels
        labels = model.predict(note, third)

        # Get predictions in proper format
        output = note.write(labels)

        # TODO: make a flag to enable or disable looking up concept ids.
        if format == "semeval":

            print("\nencoding concept ids")
            if enabled["UMLS"] is not None and disambiguate is True:
                output = cui_disambiguation.disambiguate(output, txt, model.get_cui_freq())

        # Output the concept predictions
        print('\n\nwriting to: ', out_path)
        with open(out_path, 'w') as f:
            print(output, file=f)
        print()


if __name__ == '__main__':
    main()
