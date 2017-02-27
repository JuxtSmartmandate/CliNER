


######################################################################
#  CliNER - note_i2b2.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Derived note object for reading i2b2 formatted data.     #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Nov. 6, 2014'


from functools import cmp_to_key
import string
import re
import nltk
import os

from .abstract_note import AbstractNote
from .utilities_for_notes import classification_cmp, lineno_and_tokspan
from .utilities_for_notes import NoteException



class Note_i2b2(AbstractNote):

    def __init__(self):
        # Internal representation natural for i2b2 format
        self.data            = []  # list of list of tokens
        self.classifications = []  # list of concept tuples
        self.line_inds       = []  # list of (start,end) indices for every line


    def getExtension(self):
        return 'con'


    def getText(self):
        return self.text


    def getTokenizedSentences(self):
        return [(' '.join(s)).split() for s in self.data]


    def getClassificationTuples(self):
        # return value
        retVal = []

        # Build list of standardized classification tuples
        for classification in self.classifications:
            concept,lineno,tok_start,tok_end = classification

            # character offset of beginning of line
            begin = self.line_inds[lineno-1][0]

            # Sweep through line to get character offsets from line start
            start = 0
            for word in self.data[lineno-1][:tok_start]:
                start += len(word) + 1
                while self.text[begin+start].isspace():
                    start += 1

            # Length of concept span
            end = start
            for word in self.data[lineno-1][tok_start:tok_end+1]:
                end += len(word)
                while self.text[begin+end].isspace():
                    end += 1
            #if q:
            #    print '\tword: <%s[%s]%s> end=%d' % \
            #        ( self.text[begin+end-5:begin+end],
            #          self.text[begin+end]            ,
            #          self.text[begin+end+1:begin+end+5],
            #          end )
            end -= 1
            while self.text[begin+end].isspace():
                end -= 1
            end += 1

            #if q:
            #    print begin
            #    print begin+start, begin+end
            #    print '~~' + self.text[begin+start:begin+end] + '~~'

            retVal.append( (concept,[(begin+start,begin+end)]) )

        #exit()

#        print retVal

        return retVal


    def getLineIndices(self):
        return self.line_inds


    def read_standard(self, txt, con=None):

        print('ERROR: MAKE SURE TOKENIZATION IN READ_STANDARD()')
        exit()



    def read(self, txt, con=None):
        """
        Note_i2b2::read()

        @param txt. A file path for the tokenized medical record
        @param con. A file path for the i2b2 annotated concepts for txt
        """

        # Character indices of each line
        start = 0
        end = 0

        sent_tokenize = lambda text: text.split('\n')

        word_tokenize = lambda text: text.split()

        # Read in the medical text
        with open(txt) as f:
            # Original text file
            self.text = f.read().strip('\n')

            # each line is seperate by newline
            sentences = sent_tokenize(self.text)
            for sentence in sentences:

                # NOTE - technically, assumes every sentence is unique
                # Get verbatim slice into sentence
                start += self.text[start:].index(sentence)
                end = start + len(sentence)

                #print '<%s>' % sentence
                #print '\n\n||||||||||\n\n'
                #print start, end
                #print '<%s>' % self.text[start:end]
                #print

                #print '<<<%s>>>' % self.text[start:start+20]
                #print
                #print '[[%s]]' % self.text[start]
                #print '[[%s]]' % self.text[start+1]
                #print '[[%s]]' % self.text[start+2]
                #print '[[%s]]' % self.text[start+3]
                #print '\n'*10

                self.line_inds.append( (start,end) )

                # 'start' picks up where 'end' leaves off
                start = end

                # FIXME - Should we be removing unprintable?
                sent = ''.join([x if (x in string.printable) else '@' for x in sentence])
                self.data.append(word_tokenize(sent))

                #i += 1
                #if i < 4: continue
                #exit()


        # TEST - is line_inds correct?
        #i = 0
        #for line,span in zip(self.data,self.line_inds):
        #    start,end = span
        #    print 'line: ', i+1
        #    print 'inds: ', span
        #    toks = word_tokenize(self.text[start:end].replace('\n','\t\t'))
        #    print '<t>' + ' '.join(toks)                       + '</t>'
        #    print '<l>' + ' '.join(line).replace('\n','\t\t')  + '</l>'
        #    print '\n'
        #    i += 1
        #    #if i == 4: exit()
        #exit()

        # If an accompanying concept file was specified, read it
        if con:
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # concept
                    prefix, suffix = line.split('||')
                    text = prefix.split()
                    conc = suffix[3:-2]

                    start = text[-2].split(':')
                    end   = text[-1].split(':')

                    assert "concept spans one line", start[0] == end[0]

                    # lineno
                    l = int(start[0])

                    # starttok
                    # endtok
                    start = int(start[1])
                    end   = int(  end[1])

                    # Add the classification to the Note object
                    classifications.append( (conc,l,start,end) )

                    #print "txt:   ", txt
                    #print "l:     ", l
                    #print "start: ", start
                    #print "end:   ", end
                    #print "line:  ", self.data[l-1]

                    #print "\n" + "-" * 80

            # Safe guard against concept file having duplicate entries
            classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications,
                                          key=cmp_to_key(classification_cmp))

            # TODO - eliminate minor spans which are subsumed
            # Detect subsumed concept spans

        #    print self.classifications
            for i in range(len(self.classifications)-1):

                c1 = self.classifications[i]
                c2 = self.classifications[i+1]
                if c1[1] == c2[1]:


                    """
                    if c1[1] == 30:
                        print "LINE: ", c1[1]
                        print "c1: ", c1
                        print "c2: ", c2
                    """

                    if c1[2] <= c2[2] and c2[2] <= c1[3]:
                        error_msg = '%s file has overlapping entities one line %d. This file will not be processed until you remove one of the offending entities' % (os.path.basename(con),c1[1])
                        raise NoteException(error_msg)

                #print c1
                #print c2
                #print


    def write(self, labels=None):

        """
        Note_i2b2::write()

        Purpose: Return the given concept label predictions in i2b2 format

        @param  labels. A list of classifications
        @return         A string of i2b2-concept-file-formatted data
        """

        # Return value
        retStr = ''

        # List of list of words (line-by-line)
        tlist = self.data


        # If given labels to write, use them. Default to self.classifications
        if labels != None:
            classifications = labels
        elif self.classifications != None:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')


        # For each classification
        for classification in classifications:

            # Ensure 'none' classifications are skipped
            if classification[0] == 'none':
                raise('Classification label "none" should never happen')

            concept = classification[0]
            lineno  = classification[1]
            start   = classification[2]
            end     = classification[3]

            # A list of words (corresponding line from the text file)
            text = tlist[lineno-1]

            #print "\n" + "-" * 80
            #print "classification: ", classification
            #print "lineno:         ", lineno
            #print "start:          ", start
            #print "end             ", end
            #print "text:           ", text
            #print 'len(text):      ', len(text)
            #print "text[start]:    ", text[start]
            #print "concept:        ", concept

            # The text string of words that has been classified
            datum = text[start]
            for j in range(start, end):
                datum += " " + text[j+1]

            #print 'datum:          ', datum

            # Line:TokenNumber of where the concept starts and ends
            idx1 = "%d:%d" % (lineno, start)
            idx2 = "%d:%d" % (lineno, end  )

            # Classification
            label = concept

            # Fixing issue involving i2b2 format (remove capitalization)
            lowercased = [w.lower() for w in datum.split()]
            datum = ' '.join(lowercased)

            # Print format
            retStr +=  "c=\"%s\" %s %s||t=\"%s\"\n" % (datum, idx1, idx2, label)

        # return formatted data
        return retStr.strip()

