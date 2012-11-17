# -*- coding:utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

SUCCESS_STATUS = 0
FAILURE_STATUS = 1


def fail(type, msg):
    return FAILURE_STATUS, "Error : " + ', '.join([type.upper(), msg])


def success(datas):
    return SUCCESS_STATUS, datas
