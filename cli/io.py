# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.


def prompt(*args, **kwargs):
    pattern = kwargs.pop('pattern', '@elevator> ')
    input_str = raw_input(pattern)

    return input_str


def parse_input(input_str, *args, **kwargs):
    command, args = destructurate(input_str.split(' '))


def output_result(result, *args, **kwargs):
    pass
