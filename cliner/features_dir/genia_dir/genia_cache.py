import pickle
import os
import sys
from cliner.features_dir.utilities import load_pickled_obj
sys.path.append((os.environ["CLINER_DIR"] + "/cliner/features_dir"))


class GeniaCache(object):

    def __init__(self):
        try:
            prefix = os.path.dirname(__file__)
            self.filename = os.path.join(prefix, 'genia_cache')
            self.cache = load_pickled_obj(self.filename)
        except IOError:
            self.cache = {}

    def has_key(self, key):
        return str(key) in self.cache

    def add_map(self, key, value):
        self.cache[str(key)] = value

    def get_map(self, key):
        return self.cache[str(key)]

    def __del__(self):
        with open(self.filename, "wb") as f_out:
            pickle.dump(self.cache, f_out)
