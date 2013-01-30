# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import msgpack


class ServiceMessage(object):
    @staticmethod
    def dumps(data):
        if not isinstance(data, (tuple, list)):
            data = (data, )

        return msgpack.packb(data)

    @staticmethod
    def loads(msg):
        return msgpack.unpackb(msg)
