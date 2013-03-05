# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from ConfigParser import ConfigParser

from utils.snippets import items_to_dict


class Config(dict):
    """
    Unix shells like environment class. Implements add,
    get, load, flush methods. Handles lists of values too.
    Basically Acts like a basic key/value store.
    """
    def __init__(self, f, *args, **kwargs):
        if f:
            self.update_with_file(f)  # Has to be called last!

        self.update(kwargs)
        dict.__init__(self, *args, **kwargs)

    def update_with_file(self, f):
        """
        Updates the environment using an ini file containing
        key/value descriptions.
        """
        config = ConfigParser()

        with open(f, 'r') as f:
            config.readfp(f)

            for section in config.sections():
                self.update(items_to_dict(config.items(section)))

    def reload_from_file(self, f=''):
        self.flush(f)
        self.load(f)

    def update_with_args(self, args):
        """Loads argparse kwargs into environment, as `section`"""
        for (arg, value) in args:
            if value is not None:
                self[arg] = value

    def flush(self):
        """
        Flushes the environment from it's manually
        set attributes.
        """
        for attr in self.attributes:
            delattr(self, attr)
