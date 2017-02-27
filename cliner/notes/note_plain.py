

######################################################################
#  CliNER - note_plain.py                                            #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Derived note object for reading planintext files         #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Aug 2, 2015'


import string
import sys
import re
import nltk

from .abstract_note import AbstractNote
from .utilities_for_notes import concept_cmp, classification_cmp
from .utilities_for_notes import lineno_and_tokspan, lno_and_tokspan__to__char_span
from .utilities_for_notes import WordTokenizer, SentenceTokenizer


word_tokenizer =     WordTokenizer()
sent_tokenizer = SentenceTokenizer()



class Note_plain(AbstractNote):

    def __init__(self):
        # Internal representation natural for i2b2 format
        self.data            = []  # list of list of tokens
        self.classifications = []  # list of concept tuples
        self.line_inds       = []  # list of (start,end) indices for every line


    def getExtension(self):
        return 'plain'


    def getText(self):
        return self.text


    def getTokenizedSentences(self):
        return self.data


    def getClassificationTuples(self):
        retVal = []
        for classification in  self.classifications:
            concept,span = classification
            retVal.append( (concept,[span]) )
        return retVal



    def getLineIndices(self):
        return self.line_inds



    def read_standard(self, txt, con=None):

        print('ERROR: MAKE SURE TOKENIZATION IN READ_STANDARD()')
        exit()

        start = 0
        end = 0

        with open(txt) as f:

            # Get entire file
            text = f.read().strip('\n')
            self.text = text

            # Split into lines
            self.data = [s.split() for s in text.split('\n')]

            # Tokenize each sentence into words (and save line number indices)
            toks = []
            gold = []          # Actual lines

            for sent in self.data:

                gold.append(sent)

                # Keep track of which indices each line has
                for word in sent:
                    end += len(word) + 1

                self.line_inds.append( (start,end-1) )
                start = end

                # Skip ahead to next non-whitespace
                while (start < len(text)) and text[start].isspace(): start += 1


        # If an accompanying concept file was specified, read it
        if con:
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # Parse concept file line
                    fields = line.strip().split('||')
                    #print fields
                    concept = fields[0]
                    span_inds = []
                    for i in range(1,len(fields),2):
                        span = int(fields[i]), int(fields[i+1])
                        span_inds.append( span )

                    # FIXME - For now, treat non-contiguous spans as separate
                    for span in span_inds:
                        # Add the classification to the Note object
                        l,(start,end) = lineno_and_tokspan(self.line_inds,
                                                           self.data,
                                                           self.text,
                                                           span)
                        #print 'span:   ', span
                        #print 'lineno: ', l
                        #print 'start:  ', start
                        #print 'end:    ', end
                        #print '\n'
                        classifications.append((concept,l+1,start,end))

            # Safe guard against concept file having duplicate entries
            classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications,cmp=classification_cmp)



    def read(self, txt, con=None):
        """
        Note_plain::read()

        @param txt. A file path for the tokenized medical record
        @param con. A file path for the plain annotated concepts for txt
        """

        # Character indices of each line
        start = 0
        end = 0

        sent_tokenize = sent_tokenizer.tokenize
        word_tokenize = word_tokenizer.tokenize

        # Read in the medical text
        with open(txt) as f:
            # Original text file
            text = f.read().strip('\n')
            self.text = [x for x in text if x in string.printable]

            i = 0
            sentences = sent_tokenize(self.text)
            for sentence in sentences:

                # NOTE - Fails on repeat line
                #  need to reference previous length to advance by that much guaranteed
                # Get verbatim slice into sentence
                start += self.text[start:].index(sentence)
                end = start + len(sentence)

                #i += 1
                #print 'line: ' , i
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

                # Advance index to avoid rare issue of duplicate lines
                start = end

                # FIXME - Should we be removing unprintable?
                sentence = [x for x in sentence if x in string.printable]
                self.data.append(word_tokenize(sentence))

                #i += 1
                #if i < 4: continue
                #exit()

        '''
        # TEST - is line_inds correct?
        i = 0
        for line,span in zip(self.data,self.line_inds):
            start,end = span
            print 'line: ', i+1
            print 'inds: ', span
            toks = word_tokenize(self.text[start:end].replace('\n','\t\t'))
            print '<t>' + ' '.join(toks)                       + '</t>'
            print '<l>' + ' '.join(line).replace('\n','\t\t')  + '</l>'
            print '\n'
            i += 1
            #if i == 4: exit()
        exit()
        '''

        # If an accompanying concept file was specified, read it
        if con:
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # Extract info
                    regex = '^c="(.*)" (\d+) (\d+)\|\|t="(.*)"$'
                    match = re.search(regex, line)
                    text,start,end,concept = match.groups()
                    span = (int(start),int(end))

                    # Add the classification to the Note object
                    classifications.append( (concept,span) )

                    #print "txt:   ", txt
                    #print "start: ", start
                    #print "end:   ", end
                    #print "\n" + "-" * 80

            # Safe guard against concept file having duplicate entries
            classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications, key=lambda t:t[1][0])



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
            line_inds = self.line_inds
            data      = self.data
            text      = self.text
            classifications = []
            for concept,char_span in self.classifications:
                lineno,tokspan = lineno_and_tokspan(line_inds, data, text, char_span)
                classifications.append( ( concept,lineno+1,tokspan[0],tokspan[1] ) )
            classifications = sorted(classifications, cmp=classification_cmp)
        else:
            raise Exception('Cannot write concept file: must specify labels')

        '''
        #print classifications
        for classification in classifications:
            concept = classification[0]
            lineno  = classification[1]
            start   = classification[2]
            end     = classification[3]

            span = lno_and_tokspan__to__char_span(self.line_inds, self.data, self.text, lineno-1, (start,end))

            print "classification: ", classification
            print "lineno:         ", lineno
            print "start:          ", start
            print "end             ", end

            print "tokens:          <%s>" % ' '.join(self.data[lineno-1][start:end+1]).replace('\n','\t')
            print "concept:        ", concept
            print 'span:           ', span
            print '\n\n\n'
        '''

        #exit()
        #print '\n'*40

        # For each classification
        for classification in classifications:

            #if classification != ('test', 6, 309, 311): continue

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
            #print "tokens:         ", text[start:end+1]
            #print "concept:        ", concept

            # Find the text string that the concept refers to
            span = lno_and_tokspan__to__char_span(self.line_inds, self.data, self.text, lineno-1, (start,end))
            span_start, span_end = span

            #print 'span:           ', span

            datum = self.text[span_start:span_end].replace('\n','\t')
            #print 'span_text:       <%s>' % datum

            # Classification
            label = concept

            # Print format (very similar to i2b2)
            retStr +=  "c=\"%s\" %d %d||t=\"%s\"\n" % (datum,span_start,span_end,label)

        # return formatted data
        return retStr.strip()



