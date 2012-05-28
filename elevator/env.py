#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser

from utils.patterns import Singleton
from utils.decorators import lru_cache
from utils.snippets import items_to_dict


class Environment(object):
    """
    Unix shells like environment class. Implements add,
    get, load, flush methods. Handles lists of values too.
    Basically Acts like a basic key/value store.
    """
    __metaclass__ = Singleton

    SEQ_DELIMITER = ','

    def __init__(self, env_file=''):
        self._store = {}
        self.attributes = set()  # Stores manually added attributes
        if env_file:
            self.load(env_file=env_file)  # Has to be called last!

    @property
    def store(self):
        return self._store

    def add(self, name, value):
        """Adds a key/value to env"""
        self._store.update({name: value})

    def get(self, name):
        """Cached env key fetch"""
        return self._store[name]

    def load(self, env_file):
        """
        Updates the environment using an ini file containing
        key/value descriptions.
        """
        config = ConfigParser()
        config.read(env_file)

        for section in config.sections():
            section_content = items_to_dict(config.items(section))

            for k, v in section_content.iteritems():
                self._store.update({':'.join([section, k]): v})

    def reload(self, env_file=''):
        self.flush(env_file)
        self.load(env_file)

    def flush(self):
        """
        Flushes the environment from it's manually
        set attributes.
        """
        for attr in self.attributes:
            delattr(self, attr)
