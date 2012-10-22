# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

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
            self.load_from_file(env_file=env_file)  # Has to be called last!

        self.update(kwargs)
        dict.__init__(self, *args, **kwargs)

    def load_from_file(self, env_file):
        """
        Updates the environment using an ini file containing
        key/value descriptions.
        """
        config = ConfigParser()

        with open(env_file, 'r') as f:
            config.readfp(f)

            for section in config.sections():
                self.update({section: items_to_dict(config.items(section))})

    def reload_from_file(self, env_file=''):
        self.flush(env_file)
        self.load(env_file)

    def load_from_args(self, section, args):
        """Loads argparse kwargs into environment, as `section`"""
        if not section in self:
            self[section] = {}

        for (arg, value) in args:
            self[section][arg] = value

    def flush(self):
        """
        Flushes the environment from it's manually
        set attributes.
        """
        for attr in self.attributes:
            delattr(self, attr)
