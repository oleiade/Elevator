#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import argparse

from utils.snippets import items_to_dict

DEFAULT_CONFIG_FILE = '../config/elevator.conf'

def parse_config(config_path=None):
    """Outputs the content of the config file as a dictionnary"""
    # if config_file_path is not given as param,
    # load the default one.
    config_file = config_path if config_path else DEFAULT_CONFIG_FILE

    conf_dict = {}
    config = ConfigParser.ConfigParser()
    config.read(config_file)

    for section in config.sections():
        conf_dict.update(items_to_dict(config.items(section)))

    return conf_dict


def init_parser():
    parser = argparse.ArgumentParser(description="Elevator command line manager")

    parser.add_argument('--daemon', action='store_true', default=False)
    parser.add_argument('--config', action='store', type=str, default=DEFAULT_CONFIG_FILE)
    parser.add_argument('--bind', action='store', type=str, default='127.0.0.1')
    parser.add_argument('--port', action='store', type=str, default='4141')
    parser.add_argument('--db', action='store', type=str, default='/var/lib/elevator/default')

    return parser
