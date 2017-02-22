######################################################################
#  CliNER - print_cliner_dir.py                                      #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: print value that should be assigned to CLINER_DIR        #
######################################################################


import os
import sys


def back(p):
    return os.path.dirname(p)


def main():
    # Assumes this file never moves
    base = back(back(back(os.path.abspath(__file__))))

    if 'CliNER' not in os.path.basename(base):
        print("\n\tERROR: Do not move file print_cliner_dir.py\n",
              file=sys.stderr)
        exit(1)
    else:
        print(base)


if __name__ == '__main__':
    main()
