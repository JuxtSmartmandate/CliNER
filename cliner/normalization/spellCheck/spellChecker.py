import pickle as pickle
import enchant
import os
import sys
import difflib
import time

umls_spell_check_dir = os.path.join(*[os.environ["CLINER_DIR"], "clicon", "normalization", "spellCheck"])
umls_words_file_path = os.path.join(*[umls_spell_check_dir, "umls_words.txt"])

def getPWL():

    print("loading personal word list")
    pwl = enchant.DictWithPWL(None, umls_words_file_path)
    print("finished loading pwl")

    return pwl

def spellCheck(string, strLen=0, PyPwl=None):
    """
    takes a string, breaks on white space
    and then corrects each string of character count greater than strLen

    strLen is how long the string needs to be before it is checked for spelling.

    PyPwl is a pyenchant personal word list object.
    """

    print("spell correcting: ", string)

    if PyPwl is None:
        print("NOT using personal word list")
        spellChecker = enchant.Dict("en_US")
    else:
        print("using personal word list")

    spellChecker = PyPwl

#    tokenizedString = string.split(' ')

#    spellCheckedTokens = []

    suggestions = None

    if spellChecker.is_added(string):
        return string

    else:
        suggestions = spellChecker.suggest(string)
        suggestions = difflib.get_close_matches(string, suggestions, cutoff=.80)

#        print suggestions

        """
        for token in tokenizedString:

            # token may be spelled wrong.
            if len(token) > strLen:

                try:
                    suggestions = spellChecker.suggest(token)
                    suggestions = difflib.get_close_matches(token, suggestions, cutoff=.80)

                except:

                    suggestions = []

                if string in suggestions:
                    suggestions.remove(string)

                if len(suggestions) > 0:
                    # correct potential misspelling
                    spellCheckedTokens.append( suggestions[0] )
                else:
                    # token may be spelled wrong but cannot get a correction to spelling
                    spellCheckedTokens.append(token)

            else:
                spellCheckedTokens.append(token)
        """

    return suggestions
#    return ' '.join(spellCheckedTokens)

if __name__ == "__main__":

    pwl = getPWL()

    init_time = time.time()

    print(spellCheck( "diseased", PyPwl=pwl))

    print(time.time() - init_time)


