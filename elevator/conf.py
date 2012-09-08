#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse


DEFAULT_CONFIG_FILE = '../config/elevator.conf'


def init_parser():
    parser = argparse.ArgumentParser(
        description="Elevator command line manager"
    )

    parser.add_argument('--daemon', action='store_true', default=False)

    parser.add_argument('--config', action='store', type=str,
                        default=DEFAULT_CONFIG_FILE)

    parser.add_argument('--bind', action='store', type=str,
                        default='127.0.0.1')

    parser.add_argument('--port', action='store', type=str, default='4141')

    parser.add_argument('--db', action='store', type=str,
                        default='/var/lib/elevator/default')

    return parser
