# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import argparse

DEFAULT_CONFIG_FILE = '/etc/elevatord.conf'


def init_parser():
    parser = argparse.ArgumentParser(description="Elevator command line client")
    parser.add_argument('-c', '--config', action='store', type=str,
                        default=DEFAULT_CONFIG_FILE)
    # tcp or ipc
    parser.add_argument('-t', '--protocol', action='store', type=str,
                        default='tcp')
    parser.add_argument('-b', '--endpoint', action='store', type=str,
                        default='127.0.0.1:4141')

    return parser
