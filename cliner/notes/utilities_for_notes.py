######################################################################
#  CliNER - utilities.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Helper tools for Note objects                            #
######################################################################


import nltk.data
import pickle
import nltk.tokenize
import re
import string
import os
import sys

CLINER_PATH = os.environ["CLINER_DIR"]

class NoteException(Exception):
    pass


def classification_cmp(a,b):
    """
    concept_cmp()

    Purpose: Compare concept classification tokens
    """
    a = (int(a[1]), int(a[2]))
    b = (int(b[1]), int(b[2]))

    # Sort by line number
    if a[0] < b[0]:
        return -1
    if a[0] > b[0]:
        return  1
    else:
        # Resolve lineno ties with indices
        if a[1] < b[1]:
            return -1
        if a[1] > b[1]:
            return  1
        else:
            if a[2] < b[2]:
                return -1
            if a[2] > b[2]:
                return  1
            else:
                return 0



def concept_cmp(a,b):
    """
    concept_cmp()

    Purpose: Compare concept classification tokens
    """
    return a[1][0] < b[1][0]



# Helper function
def lineno_and_tokspan(line_inds, data, text, char_span, format):

    if format == "semeval":

        """ File character offsets => line number and index into line """
        for i,span in enumerate(line_inds):

            #print char_span
            #print span

            if char_span[1] <= span[1]:

                # start and end of span relative to sentence
                start = char_span[0] - span[0]
                end   = char_span[1] - span[0]

                #print "DATA: ", data[i]
                tok_span = [0,len(data[i])-1]
                char_count = 0

                dataWithEmptyChars =  wtokenizer.tokenize(text[span[0]:span[1] + 1], format)

                index = 0
                beginning_found = False
                for j,tok in enumerate(dataWithEmptyChars):
                    if char_count > end:
                        tok_span[1] = index -1
                        break
                    elif (beginning_found == False) and (char_count >= start):
                        tok_span[0] = index
                        beginning_found = True
                    char_count += len(tok) #+ 1

                    val = span[0]+char_count

                    if len(tok) > 0:
                       index += 1
                    #if p: print '\t',j, '\t', tok, '(', char_count, ')'

                    # Skip ahead to next non-whitespace (doesnt account for EOF)
                    #print text
                    while text[span[0]+char_count].isspace():
                        char_count += 1
                        if (span[0] + char_count) >= len(text):
                            break

                return (i, tuple(tok_span))

        return None

    else:

        """ File character offsets => line number and index into line """

        # Locate line number
        for i,candidate_span in enumerate(line_inds):
            if char_span[1] <= candidate_span[1]:
                lineno = i
                break

        phrase = text[char_span[0]:char_span[1]]

        tokenized = data[lineno]

        # TODO make test case that has a false alarm token sequence

        # Try to find token sequence that covers phrase
        buf = phrase.strip()
        #print '\tinitial buf: <%s>\n' % buf
        tokens = []
        i = 0
        while i < len(tokenized):
            token = tokenized[i]
            if buf.startswith(token):
                buf = buf[len(token):].strip()
                tokens.append(i)
                if len(buf) == 0:
                    # Verify that this is the right span
                    tokspan = (tokens[0], tokens[-1])
                    span = lno_and_tokspan__to__char_span(line_inds,data,text,lineno,tokspan, "i2b2")
                    # If this is the wrong span, then reset
                    if span != char_span:
                        buf = phrase.strip()
                        while len(tokens) > 0:
                            i -= 1
                            tokens.pop()
                        i += 1
                    else:
                        break

            else:
                # Reset buffer
                buf = phrase.strip()

                # Backtrack (Mealy model)
                while len(tokens) > 0:
                    i -= 1
                    tokens.pop()
            i += 1

        #print 'tokens: ', tokens
        start_tok = tokens[ 0]
        end_tok   = tokens[-1]

        return lineno, (start_tok,end_tok)




#
# FIXME: Anna, look here!!
#
#
# Goal: It seems to locate the beginning character index, but it does not
#         correctly identify the character index of where the span ends
#
#
# This function is called from exactly one place:
#
#     $CLICON_DIR/clicon/notes/note_semeval.py
#
#  line 323  (part of the Note_semval::write() method)
#
#
def lno_and_tokspan__to__char_span(line_inds, data, text, lineno, tokspan, format):

    if format == "semeval":

        '''
        lno_and_tokspan__to__char_span

        Purpose: File character offsets => line number and index into line

        @param line_inds: list of tuples
               - each element is a (start,end) tuples of file character offsets
               - each tuples marks the beginning/end of the tokenized sentences
               - ex. line_inds = [(0, 353), (355, 459), (461, 567)]

        @param data: list of list of strings
               - each element of 'data' is a tokenized sentence
               - every element of the tokenized sentence is a token NOT a chunk
                   - NOTE: a chunk is a string predicted as BIIII etc from pass 1.
                           a chunks could be multiple words long
               - ex. data = [ ['Patient', 'likes', 'medicine', '.']  ,
                              ['Patient', 'looks', 'sick', '.']       ]

        @param text: string
               - the verbatim text file
               - ex. text = "Patient likes medicine.  Patient looks sick."

        @param lineno
               - index into 'line_inds' to identify which sentence we want to look at
               - ex. lineno = 0

        @param tokspan: 2-tuple of integers
               - start/end pair of the TOKENS that we want to return the char inds of
               - ex. (91, 91)

        @return 2-tuple of integers
               - start/end pair of CHARACTER offsets into the file (AKA 'text')
               - ex. (330,338)
        '''

        # Unpack start and end TOKEN indices
        startTok,endTok = tokspan


        # character offsets of line we want to look at
        start,end = line_inds[lineno]

        # region: the slice of the file that contains the line we want to look at
        region = text[start:end]

        # Tokenize original file text
        dataWithEmpty = wtokenizer.tokenize(text[start:end], "semeval")


        # DEBUG INFO
        #print '\n\n\n'
        #print '-'*60
        #print
        #print 'start: ', start
        #print 'end:   ', end
        #print 'd: ', text[start:end].replace('\n',' ').replace('\t',' ')
        #print 'dataWith: ', dataWithEmpty
        #print
        #print 'data:     ', data[lineno]
        #print


        # DEBUG INFO
        #print data[lineno][startTok]
        #print text[start:end]
        #print start
        #print


        # Identify where in the sentence's string the concept in question begins
        # After loop, 'ind' will be the index into 'region' where the concept begins
        ind = 0
        for i in range(startTok):
            # Jumps over next token and advances index over all trailing whitespace
            ind += len(dataWithEmpty[i])
            while text[start+ind].isspace(): ind += 1

            # DEBUG INFO: IDENTIFIES WHERE ind IS LOOKING AS INDEX INTO region
            #print region[ind-4:ind] + '<' + region[ind] + '>' + region[ind+1:ind+5]


        # This is where I stopped working a few weeks ago, due to time constraints
        # This loop SHOULD iterate down the tokens to find the final character offset
        # The ending character index will be stored in 'jnd'
        jnd = ind
        for i in range(startTok,endTok+1):
            #print region[jnd-4:jnd] + '<' + region[jnd] + '>' + region[jnd+1:jnd+5]
            #print jnd
            jnd += len(dataWithEmpty[i])

            """
            print "start: ", start
            print "jnd: ", jnd
            print "start+jnd", start + jnd
            print "text len: ", len(text)
            print text[start:]
            """

            while text[start+jnd].isspace():

                jnd += 1

                #print jnd
                #print len(text) - 1

                if (start + jnd) > len(text) - 1:
                    break
            #print jnd
            #print

        while (text[start+jnd-1].isspace()) or (text[start+jnd-1] in string.punctuation): jnd -= 1

        # Absolute index = (index of sentence in file) + (index of span in sentence)
        startOfTokRelToText = start + ind


        # SHOULD BE THIS (once commented out for loop works)
        endOfTokRelToText   = start + jnd
        #endOfTokRelToText   = start + ind + len(dataWithEmpty[startTok])


        # DEBUG INFO
        #print '---' + text[endOfTokRelToText-3:endOfTokRelToText+4] + '---'
        #print startOfTokRelToText, '  ', endOfTokRelToText
        #if startTok != endTok: exit()


        return startOfTokRelToText,endOfTokRelToText

    else:
        """ File character offsets => line number and index into line """
        # NOTE - makes no assumptions about what joins the tokens in the span

        # Get char offsets for that sentence
        #print '\n\n\n'
        #print 'lineno: ', lineno
        #print 'toks:   ', tokspan
        start,end = line_inds[lineno]
        phrase = text[start:end]
        #print 'start: ', start
        #print 'end:   ', end

        # Get the list of tokens for that sentence
        start_tok,end_tok = tokspan
        toks = data[lineno][start_tok:end_tok+1]

        phrase = phrase.replace('\n', '\t')
        #print '\tphrase: <%s>' % phrase
        #print '\ttarget toks: ' ,toks

        tokens = data[lineno]
        buf = phrase
        index = 0
        for i in range(1,start_tok+1):
            index += len(tokens[i-1])
            index += buf[index:].index(tokens[i])
            #print '\t\ttok: ', tokens[i]
            #print '\t\t\tindex: ', index
            #low = max(0,index-30)
            #print '\t\t\tbuf[:index]: <%s>' % buf[low:index]
        start_ind = index
        #print '\tstart_ind: ', start_ind

        #print '\n'*5
        #print 'start: <%s>' % phrase[start_ind:]
        #print '\n'*5

        for i in range(start_tok+1,end_tok+1):
            index += len(tokens[i-1])
            index += buf[index:].index(tokens[i])
            #print '\t\ttok: ', tokens[i]
            #print '\t\t\tindex: ', index
            #low = max(0,index-30)
            #print '\t\t\tbuf[:index]: <%s>' % buf[low:index]
        end_ind = index + len(tokens[end_tok])
        #print '\tend_ind:   ', end_ind

        #print '\n'*5
        #print 'finale: <%s>' % phrase[start_ind:end_ind]
        #print '\n'*5

        final_span = (start+start_ind, start+end_ind)
        return final_span



def span_relationship(s1, s2):
    if (s1[0] <= s2[0]) and (s1[1] >= s2[1]):
        return 'subsumes'
    else:
        return None



def span_stuff(classifs):

    # Sort all concept spans
    classifs = sorted(classifs, key=lambda s:s[0])

    # Loop until convergence

    newClassifs = []

    for i in range(len(classifs)-1):

        rel = span_relationship(classifs[i], classifs[i+1])

        if rel == 'subsumes':
            #print i, '  -->  ', classifs[i], classifs[i+1]
            s1 = classifs[i]
            s2 = classifs[i+1]

            # Split s1 into leading atom (and leave s2 as second atom)
            #print s1
            #print s2
            #print
            newSpan = (s1[0], s2[0]-1)
            newClassifs.append(newSpan)

        else:
            newClassifs.append(classifs[i])

    #print newClassifs
    return newClassifs

def remove_non_ascii(string):

    ret = []

    for c in string:
        if ord(c) > 0 and ord(c) < 127:
            ret.append(c)

    ret = ''.join(ret)

    return ret


# Break file into sentences.
class SentenceTokenizer:

    def __init__(self):
        self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def tokenize(self, text_file, format):
        """ Split the document into sentences """

        if format == "semeval":
            text = open(text_file, 'r').read()

            # strip non ascii chars
            text = remove_non_ascii(text)

            # First pass: tokenizer
            first_pass = self.sent_tokenizer.tokenize(text)
           # first_pass = self.sentenizer.sentenize(text)
            return first_pass

            # Second pass, delimit on '\n'
            #retVal = []
            #for tok in first_pass:
            #    line_split = tok.split('\n')
            #    retVal.append(line_split[0])
            #    for t in line_split[1:]:
            #        #retVal.append('\n')
            #        if t != '': retVal.append(t)
            #return retVal

        else:

            #TODO: this is from master. I don't know what will happen if i use this for semeval.
            #return text.split('\n')
            #return self.sent_tokenizer.tokenize(text)
            text = re.sub('\n\n+', '\n\n', text)
            data = self.sent_tokenizer.tokenize(text)

            splitted = [ sent.split('\n\n') for sent in data  ]
            sents = sum(splitted, [])

            # Could do something (similar to here) to ensure nonprose is split well
            #splitted = [ sent.split(':')    for sent in sents ]
            #sents = sum(splitted, [])

            return [ sent.strip() for sent in sents if (sent.strip() != []) ]



# Break sentence into words
class WordTokenizer:

    def __init__(self):
        pass

    def tokenize(self, sent, format):
        """ Split the sentence into tokens """

        if format == "semeval":

            toks = nltk.tokenize.word_tokenize(sent)

            # Second pass, delimit on token-combiners such as '/' and '-'
            delims = ['/', '-', '(', ')', ',', '.', ':', '*', '[', ']', '%', '+']
            for delim in delims:
                retVal = []
                for tok in toks:
                    line_split = tok.split(delim)
                    if line_split[0] != '': retVal.append(line_split[0])
                    for t in line_split[1:]:
                        retVal.append(delim)
                        if t != '': retVal.append(t)
                toks = retVal

            return retVal

        else:

            """ Split the sentence into tokens """
            #return sent.strip().split()
            #return sent.strip().split(' ')
            #return filter(lambda word: word!= '', nltk.tokenize.wordpunct_tokenize(sent))
            toks = filter(lambda w: len(w)>0, nltk.tokenize.wordpunct_tokenize(sent))
            #splitted = [ w.replace('/',' / ').split() for w in toks ]
            #toks = sum(splitted, [])
            return toks

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)



# Instantiate tokenizers
wtokenizer = WordTokenizer()
stokenizer = SentenceTokenizer()


