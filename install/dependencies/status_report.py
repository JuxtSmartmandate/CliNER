######################################################################
#  CliNER - dependencies.py                                          #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Determine which python modules are installed.            #
######################################################################


import sys



# Modules used by cliner (package name -> module name)
required = {
             'scipy'           : 'import scipy'      ,
             'numpy'           : 'import numpy'      ,
             'nltk'            : 'import nltk'       ,
             'python-crfsuite' : 'import pycrfsuite' ,
             'scikit-learn'    : 'from sklearn.feature_extraction  import DictVectorizer'
           }

auxiliary = {
             'marisa-trie' : 'import marisa_trie'    ,
             'nose'        : 'import nose'
            }

nltk_data = {
            'maxent_treebank_pos_tagger' : 'import nltk ; nltk.pos_tag([])' ,
            'punkt'                      : 'import nltk ; s = nltk.stem.LancasterStemmer(); nltk.data.load("tokenizers/punkt/english.pickle")'
            }


def main():

    # Output package statuses
    print('\nREQUIRED')
    display_status(required)

    print('\nAUXILIARY')
    display_status(auxiliary)
    print()

    print('\nNLTK DATA')
    display_status(nltk_data)
    print()




def display_status(module2import):
    ''' Iterate through dictionary and display in pretty format '''
    installed = status_report(module2import)
    print('\t|\t module-name\t    |   status    |')
    print('\t|' + '-'*27 + '|' + '-' * 13 + '|')
    for module in list(installed.keys()):
        if installed[module]:
            print('\t|%-27s|  installed  |' % module)
        else:
            print('\t|%-27s|    ERROR    |'   % module)




def status_report(module2import):

    '''
    status_report()

    Purpose: Determine which modules can be successfully imported

    @param module2import. Dictionary mapping python-module-name to code-to-import
    @param <dictionary> mapping python-module-name to boolean
    '''

    installed = {}

    for module in list(module2import.keys()):

        # Attempt to import module
        try:
            # Get import statement from module name
            attempt = module2import[module]

            # Execute import
            exec(attempt)
            installed[module] = True
        except ImportError:
            installed[module] = False
        except LookupError:
            installed[module] = False

    return installed



def check_python_dependencies_installed():

    '''
    check_python_dependencies_installed()

    Purpose: Determine whether all necesarry python modules are installed

    @return a list of three booleans:
              1) The first  boolean indicates all auxiliary success
              2) The second boolean indicates all required  success
              2) The third  boolean indicates all nltk data success
    '''

    status = [True,True,True]

    # Missing auxiliary modules?
    auxiliary_modules = status_report(auxiliary)
    if not all(auxiliary_modules.values()):
        status[0] = False

    # Missing required modules?
    required_modules = status_report(required)
    if not all(required_modules.values()):
        status[1] = False

    # Missing required modules?
    nltk_data_modules = status_report(nltk_data)
    if not all(nltk_data_modules.values()):
        status[2] = False

    # Successful
    return status



if __name__ == '__main__':
    main()
