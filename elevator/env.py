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
        self.attributes = set()  # Stores manually added attributes
        if env_file:
            self.load(env_file=env_file)  # Has to be called last!

    def add(self, name, value):
        """Adds a key/value to env"""
        setattr(self, name, value)
        self.attributes.add(name)

    @lru_cache(maxsize=1024)
    def get(self, name):
        """Cached env key fetch"""
        var = getattr(self, name)

        if ',' in var:
            return var.split(',')

        return var

    def append(self, var, value):
        """
        `value` can either be a (name, value) tuple/list pair,
        or a value string. If a pair is given, the method
        will consider that the var to append to is a dict
        and will try to add the name/value to it.
        If it is a String, it will try to automatically transform
        the pointed var to a sequence and add the value to it.
        """
        env_var = getattr(self, var)
        env_var_type = type(env_var)

        if ((isinstance(value, tuple) or isinstance(value, list)) and \
             len(value) == 2):
            key, value = value
            env_var.update({key: value})
        elif isinstance(value, str):
            if env_var_type != list:
                env_var = [env_var]
                env_var.append(value)
            setattr(self, var, env_var)
        else:
            err_msg = "Env value has to wether be iterable sequence or str"
            raise TypeError(err_msg)

        self.attributes.add(var)

    def load(self, env_file):
        """Loads an ini file containing the env description : key/value"""
        config = ConfigParser()
        config.read(env_file)

        for section in config.sections():
            setattr(self, section, items_to_dict(config.items(section)))
            self.attributes.add(section)
            for k, v in getattr(self, section).iteritems():
                if self.CONFIG_SEQ_DELIMITER in v:
                    splitted = [e for e in v.split(self.SEQ_DELIMITER) if e]
                    getattr(self, section)[k] = splitted

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
