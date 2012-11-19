# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import shlex

from clint.textui import puts, colored

from elevator.utils.patterns import destructurate

from .helpers import FAILURE_STATUS


def prompt(*args, **kwargs):
    current_db = kwargs.pop('current_db', 'default')

    if current_db:
        pattern = '@ Elevator.{db} => '.format(db=current_db)
    else:
        pattern = '! Offline => '
    input_str = raw_input(pattern)

    return input_str


def parse_input(input_str, *args, **kwargs):
    input_str = shlex.split(input_str.strip())
    command, args = destructurate(input_str)
    return command.upper(), args


def output_result(status, result, *args, **kwargs):
    if result:
        if status == FAILURE_STATUS:
            puts(colored.red(str(result)))
        else:
            puts(str(result))
