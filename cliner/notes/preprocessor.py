
import re

from nltk.tokenize import word_tokenize
from nltk.data import load

class PreProcessor:

    def __init__(self):
        self.sentTokenizer = load('tokenizers/punkt/english.pickle')
        self.wordTokenizer = word_tokenize

    def tokenizeSentences(self, sentences):
        """ split block of text into sentences """
        return self.sentTokenizer.tokenize(sentences)

    def tokenizeSentence(self, sentence):
        """ Split the sentence into tokens """

        tokens = self.wordTokenizer(sentence)
       
        """
	retVal = []

	index = 0

	while index < len(tokens):
	  
	    prev = tokens[index - 1] if index != 0 else ' '
            current = tokens[index]
            next_char = tokens[index + 1] if index + 1 < len(tokens) else ' '

            token = current

            # TODO: figure out how to handle NLTK tokenization problems...
            if next_char == '.' and index + 2 < len(tokens)\
               or next_char == '.' and '.' in current\
               or next_char == '%' or next_char == '...':
                token = token + next_char
                index = index + 1

            if current == '&':
                token = token + next_char
                index = index + 1

            if current == '&' and next_char == ';':
                token = token + next_char
                index = index + 1

            retVal.append(token)

            index = index + 1
 
        return retVal
        """

        return tokens

    def tokenizeListOfStrings(self, strings):
        """ takes a list of strings and tokenizes them. returns a list of list of tokens """
        return [self.tokenizeSentence(string) for string in strings]

    def tokenizeInput(self, text):
        """ tokenize string of sentences into a list strings """

        # corects blank lines appearing when using format.py.
        text = re.sub("\n+", "\n", text)

        sentences = []

        for sentence in self.tokenizeSentences(text):
            sentences += self.tokenizeSentence(sentence)

        return sentences

if __name__ == "__main__": 
    exit("not meant to be imported")

#EOF


