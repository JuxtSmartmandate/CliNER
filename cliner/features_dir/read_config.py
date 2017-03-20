######################################################################
#  CliCon - read_config.py                                           #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Read a configuration file to determine what features     #
#               are available on the system                          #
######################################################################


import os.path as op
import sys
from configparser import ConfigParser

CLINER_DIR = op.join(op.dirname(op.abspath(__file__)), *["..", ".."])


def enabled_modules():
    """
    enabled_modules()

    @return a dictionary of {name, resource} pairs.

    ex. {'UMLS': None, 'GENIA': 'genia/geniatagger-3.0.1/geniatagger'}

    >>> enabled_modules() is not None
    True
    """
    config_path = op.join(CLINER_DIR, "config.ini")
    cfparser = ConfigParser()
    cfparser.read(config_path)
    specs = cfparser['DEFAULT']

    # check if paths are actually valid
    if "GENIA" in specs:

        if op.isfile(specs["GENIA"]) is False:
            sys.exit("Invalid path to genia executable.")

    if "UMLS" in specs:

        if op.isdir(specs["UMLS"]) is False:
            sys.exit("Invalid path to directory containing UMLS database tables.")

    if "BROWN" in specs:

        if op.isfile(specs["BROWN"]) is False:
            sys.exit("Invalid path to generated brown clusters.")

    if "PY4J" in specs:

        if op.isfile(specs["PY4J"]) is False:
            sys.exit(
                "Invalid path to py4j0.x.jar, consult https://www.py4j.org/install.html to locate it.")

    if "WORD2VEC" in specs:

        if op.isfile(specs["WORD2VEC"]) is False:
            sys.exit("Invalid path to <word2vec_embeddings>.bin")

    return specs

if __name__ == "__main__":
    print(enabled_modules())
