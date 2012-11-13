# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from elevator.utils.patterns import destructurate


def prompt(*args, **kwargs):
    pattern = kwargs.pop('pattern', '@elevator> ')
    input_str = raw_input(pattern)

    return input_str


def parse_input(input_str, *args, **kwargs):
    input_str = input_str.strip().split()
    command, args = destructurate(input_str)
    return command, args


def output_result(result, *args, **kwargs):
    if result:
        print result
