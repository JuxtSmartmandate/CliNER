
import sys
import os
import pickle as pickle

from features_dir.umls_dir.interpret_umls import obtain_concept_ids

sys.path.append((os.environ["CLINER_DIR"] + "/cliner/features_dir/umls_dir"))
#sys.path.append((os.environ["CLINER_DIR"] + "/cliner/normalization/spellCheck"))

#from spellChecker import getPWL
from umls_cache import UmlsCache

pwl = None
umls_cache = UmlsCache()


def disambiguate(output, txtFile, cui_freq):
    """
    obtains concept ids for each phrase indicated by the span generated from prediction
    """

    txtFile = open(txtFile, "r")

    txtFile = txtFile.read()

    cuisToInsert = []

    output = output.split('\n')

    output.pop()

    for index, line in enumerate(output):

        phrase = ""
        spans = line.split("|")

        if len(spans) != 19:
            print("ERROR: the format of this line is not correct.")
            print("LINE: line")
            exit()

        spans = spans[1]
        spans = spans.split(',')
        spans = [s.split('-') for s in spans]

        # get the phrase  for each span
        for span in spans:

            string = txtFile[int(span[0]):int(span[1]) + 1]

            phrase += string

        cuiToInsert = {}

        cuiToInsert["phrase"] = phrase
        cuiToInsert["index"] = index
        cuiToInsert["cui"] = None

        cuisToInsert.append(cuiToInsert)

    phrases = [cuiToInsert["phrase"] for cuiToInsert in cuisToInsert]

    # perform cui lookup for all concepts detected in file

    cuis = []

    for phrase in phrases:
        cuis.append(obtain_concept_ids(
            umls_cache, phrase, PyPwl=pwl, cui_freq=cui_freq))

    for cui, cuiToInsert in zip(cuis, cuisToInsert):
        cuiToInsert["cui"] = cui

    for cuiToInsert in cuisToInsert:
        # replace CUI-less with concept id obtained
        string = output[cuiToInsert["index"]].split('|')

        string = string[0:2] + [cuiToInsert["cui"]] + string[3:]

        output[cuiToInsert["index"]] = '|'.join(string)

    resultingOutput = "\n".join(output)

    return resultingOutput


def calcFreqOfCuis(training_list):

    cui_freq = {}

    total_cui_count = 0.0

    for _, con in training_list:
        con_file = open(con, "r")
        con_text = con_file.read()
        con_file.close()

        con_text = con_text.split('\n')

        while "" in con_text:
            con_text.remove("")

        for line in con_text:

            # get cui
            cui = line.split('|')[2]

            # TODO: I do not consider CUI-Less. since if metamap returns no cui then there is only one choice.
            # for now frequency of a cui is used when metamap returns multiple concept ids.
            #            -potential frequencies to record:
            #                          -record the frequency of a phrase having a certain cui?
            if cui == "CUI-less":
                continue

            if cui in cui_freq:
                cui_freq[cui] += 1.0
                total_cui_count += 1.0

            else:
                cui_freq[cui] = 1.0
                total_cui_count += 1.0

    # get frequencies
    for cui in cui_freq:
        cui_freq[cui] = (cui_freq[cui] / total_cui_count)

    return cui_freq
