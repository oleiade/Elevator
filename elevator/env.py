#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser

from utils.patterns import Singleton
from utils.snippets import items_to_dict


class Environment(dict):
    """
    Unix shells like environment class. Implements add,
    get, load, flush methods. Handles lists of values too.
    Basically Acts like a basic key/value store.
    """
    __metaclass__ = Singleton

    def __init__(self, env_file='', *args, **kwargs):
        if env_file:
            self.load(env_file=env_file,
                      section=kwargs.pop('section', None))

        self.update(kwargs)
        dict.__init__(self, *args, **kwargs)

    def load(self, env_file, section=None):
        """
        Updates the environment using an ini file containing
        key/value descriptions.
        """
        config = ConfigParser()
        config.read(env_file)

        if section:
            self.update(items_to_dict(config.items(section)))
        else:
            for section in config.sections():
                self.update({section: items_to_dict(config.items(section))})

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
