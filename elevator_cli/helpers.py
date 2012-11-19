# -*- coding:utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from elevator.constants import SUCCESS_STATUS, FAILURE_STATUS


def fail(type, msg):
    return FAILURE_STATUS, "Error : " + ', '.join([type.upper(), msg])


def success(datas):
    return SUCCESS_STATUS, datas
