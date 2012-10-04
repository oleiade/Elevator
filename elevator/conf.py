#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse


DEFAULT_CONFIG_FILE = '/etc/elevatord.conf'


def init_parser():
    parser = argparse.ArgumentParser(
        description="Elevator command line manager"
    )
    parser.add_argument('--daemon', action='store_true', default=False)
    parser.add_argument('--config', action='store', type=str,
                        default=DEFAULT_CONFIG_FILE)
    # tcp or ipc
    parser.add_argument('--protocol', action='store', type=str,
                        default='tcp')
    parser.add_argument('--bind', action='store', type=str,
                        default='127.0.0.1')
    parser.add_argument('--port', action='store', type=str, default='4141')
    parser.add_argument('--workers', action='store', type=int, default=4)
    parser.add_argument('--paranoid', action='store_true', default=False)

    return parser
