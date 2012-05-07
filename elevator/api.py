#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Handler(object):
    def __init__(self, db):
        # Each handlers is formatted following
        # the pattern : [ command,
        #                 default return value,
        #                 raised error ]
        self.handles = {
            'GET': (db.Get, "", KeyError),
            'PUT': (db.Put, "True", TypeError),
            'DELETE': (db.Delete, ""),
            }


    def command(self, message):
        op_code = message.op_code
        args = message.data

        if op_code in self.handles:
            if len(self.handles[op_code]) == 2:
                value = self.handles[op_code][0](*args)
            else:
                # FIXME
                # global except catching is a total
                # performance killer. Should enhance
                # the handles attributes to link possible
                # exceptions with leveldb methods.
                try:
                    value = self.handles[op_code][0](*args)
                except self.handles[op_code][2]:
                    return ""
        else:
            raise KeyError("op_code not handle")

        return value if value else self.handles[op_code][1]
