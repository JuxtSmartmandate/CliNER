######################################################################
#  CliCon - test.py                                                  #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Test some functions from the features module.            #
######################################################################


import os

from cliner.features_dir import features



def test_prose_sentence():

    # Test sentences
    sents = [ 'Home with Service',
              'Discharge Diagnosis :',
              'Coronary artery disease s/p Coronary Artery Bypass Graft x3',
              'PMH : Carpal tunnel syndrome , Hypertension , Hyperlipidemia , Arthritis',
              'Discharge Condition :'
            ]


    sents = [  s.split()  for  s  in  sents  ]


    # Partition into prose and nonprose
    prose    = []
    nonprose = []
    for s in sents:
        if features.prose_sentence(s):
            print('prose')
            print('\t', ' '.join(s))
            print() 
        else:
            print('nonprose')
            print('\t', ' '.join(s))
            print() 





def main():
    test_prose_sentence()



if __name__ == '__main__':
    main()
