# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

from ..constants import FAILURE_STATUS, SUCCESS_STATUS, WARNING_STATUS


def failure(err_code, err_msg):
    """Returns a formatted error status and content"""
    return (FAILURE_STATUS, [err_code, err_msg])


def success(content=None):
    """Returns a formatted success status and content"""
    return (SUCCESS_STATUS, content)


def warning(error_code, error_msg, content):
    """Returns a formatted warning status and content"""
    return (WARNING_STATUS, [error_code, error_msg, content])
