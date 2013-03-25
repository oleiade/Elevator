# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import argparse


DEFAULT_CONFIG_FILE = '/etc/elevator/elevator.conf'


def init_parser():
    parser = argparse.ArgumentParser(
        description="Elevator command line manager"
    )
    parser.add_argument('-d', '--daemon', action='store_true', default=False)
    parser.add_argument('-c', '--config', action='store', type=str,
                        default=DEFAULT_CONFIG_FILE)
    # tcp or ipc
    parser.add_argument('-t', '--transport', action='store', type=str)
    parser.add_argument('-b', '--bind', action='store', type=str)
    parser.add_argument('-p', '--port', action='store', type=str)
    parser.add_argument('-w', '--workers', action='store', type=int, default=4)
    parser.add_argument('-v', '--log-level', action='store', type=str, default='INFO')

    return parser
