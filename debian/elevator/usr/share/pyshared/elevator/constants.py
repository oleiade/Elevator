# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

## Internals
WORKER_HALT = "-1"

## Protocol

# Status codes
SUCCESS_STATUS = 1
FAILURE_STATUS = -1
WARNING_STATUS = -2

# Error codes
TYPE_ERROR = 0
KEY_ERROR = 1
VALUE_ERROR = 2
INDEX_ERROR = 3
RUNTIME_ERROR = 4
OS_ERROR = 5
DATABASE_ERROR = 6
SIGNAL_ERROR = 7
REQUEST_ERROR = 8

# Signals
SIGNAL_BATCH_PUT = 1
SIGNAL_BATCH_DELETE = 0
