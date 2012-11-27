# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import os
import re


def rm_from_pattern(dir, pattern):
    """Removes directory files matching with a provided
    pattern"""
    for f in os.listdir(dir):
        if re.search(pattern, f):
                os.remove(os.path.join(dir, f))
