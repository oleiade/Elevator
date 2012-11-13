# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from clint.textui import puts, indent
from clint.textui import colored

from elevator.utils.patterns import destructurate

from .helpers import FAILURE_STATUS


def prompt(*args, **kwargs):
    current_db = kwargs.pop('current_db', 'default')
    pattern = 'elevator@{db} =# '.format(db=current_db)
    input_str = raw_input(pattern)

    return input_str


def parse_input(input_str, *args, **kwargs):
    input_str = input_str.strip().split()
    command, args = destructurate(input_str)
    return command, args


def output_result(status, result, *args, **kwargs):
    if result:
        if status == FAILURE_STATUS:
            puts(colored.red(result))
        else:
            puts(result)
