#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Handler(object):
    def __init__(self, db):
        # Each handlers is formatted following
        # the pattern : [ command,
        #                 default return value,
        #                 raised error ]
        self.handlers = {
            'GET': (db.Get, "", KeyError),
            'PUT': (db.Put, "True", TypeError),
            'DELETE': (db.Delete, ""),
            }


    def command(self, message):
        command = message.command
        args = message.data

        if command in self.handlers:
            if len(self.handlers[command]) == 2:
                value = self.handlers[command][0](*args)
            else:
                # FIXME
                # global except catching is a total
                # performance killer. Should enhance
                # the handlers attributes to link possible
                # exceptions with leveldb methods.
                try:
                    value = self.handlers[command][0](*args)
                except self.handlers[command][2]:
                    return ""
        else:
            raise KeyError("command not handle")

        return value if value else self.handlers[command][1]
