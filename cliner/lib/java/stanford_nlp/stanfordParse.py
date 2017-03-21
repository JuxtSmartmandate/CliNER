
from py4j.java_gateway import JavaGateway
from cliner.lib.java.entry_point.gateway import GateWayServer

import os
import time
import sys

# path of stanford corenlp dir
dependency_dir = os.environ["CLINER_DIR"] + "/cliner/lib/java/stanford_nlp"
gateway_dir = os.environ["CLINER_DIR"] + "/cliner/lib/java/entry_point"

sys.path.append(gateway_dir)


class DependencyParser(object):

    def __init__(self):

        #        print "\nLoading stanford dependency parser..."

        # launches java gateway server.
#        GateWayServer.launch_gateway()

        init_time = time.time()

        while True:

            try:

                self.gateway = JavaGateway(eager_load=True)
                self.parser = self.gateway.entry_point.getStanfordParserObj()
                from IPython.core.debugger import Tracer  # NOQA
                Tracer()()

            except:

                if (time.time() - init_time) > 60:
                    exit("Could not load dependencies...")
                else:
                    time.sleep(5)
                    continue

            break

    def getNounPhraseHeads(self, string):

        heads = []

        string = string.lower()

        for head in self.parser.getNounPhraseHeads(string):
            heads.append(head)

        return heads

    def getSentenceStructure(self, string):
        return self.parser.getSentenceStructure(string)

    def _parse_string(self):
        return self.parser.getDependencyTree()

    def _get_output_field(self, line, field):
        """
        select string fields to obtain from the lines of the parser output

        example input to parser:
            "This is a test sentence."

        NOTE: base 1 indexing for tokens
              the root token has an index of 0

        example line:
            ['1', 'This', '_', 'null', 'null', '_', '5', 'nsubj', '_', '_']
        """

        ret_val = None

        fields = ['_source_index',   # the index of the token in the sentence
                  '_source_token',   # the token at the specified index in the sentence
                  '_target_index',   # the index of the token in which the current token has a relation with
                  '_rel_type']       # the type of relation between the source token and target token

        _source_index = 0  # NOQA
        _source_token = 1  # NOQA
        _target_index = 6  # NOQA
        _rel_type = 7  # NOQA

        if field in fields:
            ret_val = line[eval(field)]

        return ret_val

    def _get_source_index(self, line):
        """ get the source index specified in a line from the output parser """

        return int(self._get_output_field(line, '_source_index'))

    def _get_source_token(self, line):
        """ get the token at the source index specified in a line from the output parser. """

        return str(self._get_output_field(line, '_source_token'))

    def _get_target_index(self, line):
        """ get the target index specified in a line from the output parser """

        return int(self._get_output_field(line, '_target_index'))

    def _get_rel_type(self, line):
        """ get the relation type between two tokens in a line from the output parser """

        return str(self._get_output_field(line, '_rel_type'))

    def _process_parser_output(self, output_from_parser):

        # sentizer and tokenize output from dependency parser
        output_from_parser = [line.split(
            '\t') for line in output_from_parser.split('\n') if line != '']

        # a list of list of lists
        # [ [  [ lines of outut for a sentence, ...  ], ...  ], ...  ]
        return output_from_parser

    def get_collapsed_dependencies(self, tokenized_sentence):

        for token in tokenized_sentence:
            self.addTokenToProcess(token)

        output_from_parser = self._parse_string()

        sentence = self._process_parser_output(output_from_parser)

        dependency_group = {}

        for line in sentence:

            if self._get_rel_type(line) == 'erased':
                continue

            dependency_group[self._get_source_index(line)] = {"source_token": self._get_source_token(line),
                                                              "target_index": self._get_target_index(line),
                                                              "rel_type": self._get_rel_type(line)}

        return dependency_group

    def get_related_tokens(self, target_index, sentence, dependency_group):

        # input indices should be in base 0, but will be handled as base 1
        # throughout document...

        target_index += 1

        if target_index not in dependency_group:
            return {}

        assert dependency_group[target_index][
            "source_token"] == sentence[target_index - 1]

        dependencies = {}

        feature_name = "source_dep"

        start_index = target_index

        tmp_dependencies = {}
        curr_node = dependency_group[start_index]

        while True:

            # root
            if curr_node["target_index"] == 0:
                break

            tmp_dependencies[(feature_name,
                              dependency_group[curr_node["target_index"]]["source_token"])] = 1

            # TODO: will this be a problem?
            if curr_node["target_index"] == target_index:
                exit("circuluar dependency path, TODO: investigate...")

            curr_node = dependency_group[curr_node["target_index"]]

        dependencies.update(tmp_dependencies)

        for i in dependency_group:

            if i == target_index:
                continue

            dependencies.update(self.related_tokens_between(
                i - 1, target_index - 1, sentence, dependency_group))

        return dependencies

    def related_tokens_between(self, start_index, end_index, sentence, dependency_group):

        # TODO: amend this so it actually gets depenencies on relation path,
        # for third pass...

        # input indices should be in base 0, but will be handled as base 1
        # throughout document...

        start_index += 1
        end_index += 1

        if start_index not in dependency_group:
            return {}
        if end_index not in dependency_group:
            return {}

        assert dependency_group[start_index][
            "source_token"] == sentence[start_index - 1]
        assert dependency_group[end_index][
            "source_token"] == sentence[end_index - 1]

        dependencies = {}

        feature_name = "target_dep"

        tmp_dependencies = {}
        curr_node = dependency_group[start_index]

        tmp_dependencies[(feature_name,
                          curr_node["source_token"])] = 1

        while True:

            # root
            if curr_node["target_index"] == 0:
                tmp_dependencies = {}
                break

            if curr_node["target_index"] == end_index:
                break
            else:
                tmp_dependencies[(feature_name,
                                  dependency_group[curr_node["target_index"]]["source_token"])] = 1

            # TODO: will this be a problem?
            if curr_node["target_index"] == start_index:
                exit("circuluar dependency path, TODO: investigate...")

            curr_node = dependency_group[curr_node["target_index"]]

        dependencies.update(tmp_dependencies)

        return dependencies

    def __related_tokens_between(self, target_index, sibling_index, sentence, dependency_group):

        # TODO: amend this so it actually gets depenencies on relation path,
        # for third pass...

        # input indices should be in base 0, but will be handled as base 1
        # throughout document...

        target_index += 1
        sibling_index += 1

        assert target_index in dependency_group
        assert sibling_index in dependency_group

        assert dependency_group[target_index][
            "source_token"] == sentence[target_index - 1]
        assert dependency_group[sibling_index][
            "source_token"] == sentence[sibling_index - 1]

        dependencies = {}

        for feature_name, start_index, end_index in (("source_dep", target_index, sibling_index),
                                                     ("target_dep", sibling_index, target_index)):

            tmp_dependencies = {}
            curr_node = dependency_group[start_index]

            while True:

                # root
                if curr_node["target_index"] == 0:
                    tmp_dependencies = {}
                    break

                tmp_dependencies[(feature_name,
                                  dependency_group[curr_node["target_index"]]["source_token"])] = 1

                if curr_node["target_index"] == end_index:
                    break

                curr_node = dependency_group[curr_node["target_index"]]

            dependencies.update(tmp_dependencies)

        return dependencies

    def addTokenToProcess(self, token):
        """py4j cannot convert python lists to java objects.
           a stack approach is be used.
        """

        self.parser.addTokenToProcess(token)


if __name__ == "__main__":

    p = DependencyParser()

#    d = p.get_collapsed_dependencies("He ran really fast to his classroom. He was late to class, unfortunately.")

    d = p.get_collapsed_dependencies(["He", "ran", "to", "his classroom"])

    print(d)
    print(p.get_related_tokens(2, ["He", "ran", "to", "his classroom"], d))

    d = p.get_collapsed_dependencies(
        ["The", "man", "was", "admitted", "to", "the", "emergency room"])

    print(d)
    print(p.get_related_tokens(
        6, ["The", "man", "was", "admitted", "to", "the", "emergency room"], d))


# EOF
