######################################################################
#  CliCon - clicon_genia_interface.py                                #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Provide a way for Python to utilize the output of the    #
#               GENIA Tagger                                         #
#                                                                    #
#  Genia Tagger: http://www.nactem.ac.uk/tsujii/GENIA/tagger/        #
######################################################################

import os
import os.path as op
import tempfile
from subprocess import check_output
from cliner.features_dir.genia_dir.genia_cache import GeniaCache

__author__ = 'Willie Boag'
__date__ = 'Jan. 27, 2014'


def genia(geniatagger, data):
    '''
    genia()

    Purpose: Call the genia tagger and return its output in python format

    @param geniatagger.  A path to the executable geniatagger
    @param data.         A list of list of strings (lines of words from a file)
    @return              A list of dcitionaries of the genia tagger's output.
    '''

    # Lookup cache
    cache = GeniaCache()

    # Get uncached lines
    uncached = []
    for line in data:
        sent = ' '.join(line)
        if sent not in cache.cache:
            uncached.append(sent)

    if uncached:
        # write list to file and then feed it to GENIA
        genia_dir = op.dirname(geniatagger)
        genia_exec = geniatagger

        os_handle, uncached_fname = tempfile.mkstemp(suffix="genia_temp")

        with open(uncached_fname, 'w') as f:
            for line in uncached:
                f.write(line + '\n')

        # Run genia tagger
        print('\t\tRunning  GENIA tagger')
        genia_command = [genia_exec, "-nt", uncached_fname]

        stream = check_output(genia_command, cwd=genia_dir).decode('utf-8')

        # print 'stream: ', stream

        # print '\t\tFinished GENIA tagger'

        # Organize tagger output
        linetags = []
        tagged = []

        # if the sentence is too long genia outputs an error.
        stream_lines = stream.split('\n')

        # get the line the warning might be on.
        #  potential_warning = "" if len(
        #      stream_lines[4:5]) == 0 else stream_lines[4:5][0]

        # genia_stream = None

        #  if "warning: the sentence seems" in potential_warning:
        #      # skip over warning
        #      genia_stream = stream_lines[5:]
        #  else:
        #      genia_stream = stream_lines[4:]

        for tag in stream_lines:
            if tag.split():               # Part of line
                linetags.append(tag)
            else:                         # End  of line
                tagged.append(linetags)
                linetags = []

        # Add tagger output to cache
        for line, tags in zip(uncached, tagged):
            cache.add_map(line, tags)

        # Remove temp file
        os.close(os_handle)

        # print 'GENIA OUTPUT: ', open(out,"rb").read()

        os.remove(uncached_fname)

    # Extract features
    linefeats = []
    retlist = []
    for line in data:

        # print 'line: ', line

        line = ' '.join(line)

        # Get tagged output from cache
        tags = cache.get_map(line)

        # print 'tags: ', tags

        for tag in tags:
            tag = tag.split()
            output = {'GENIA-word': tag[0],
                      'GENIA-stem': tag[1],
                      'GENIA-POS': tag[2],
                      'GENIA-chunktag': tag[3],
                      'GENIA-NEtag': tag[4]}

            linefeats.append(output)

        retlist.append(linefeats)
        linefeats = []

    # print 'retlist: ', retlist

    return retlist
