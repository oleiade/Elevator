#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ujson as json

class Handler(object):
    """
    Class that handles commands server side.
    Translates, messages commands to it's methods calls.
    """
    def __init__(self, db):
        self.db = db
        # Each handlers is formatted following
        # the pattern : [ command,
        #                 default return value,
        #                 raised error ]
        self.handlers = {
            'GET': (self.Get, "", KeyError),
            'PUT': (self.Put, "True", TypeError),
            'DELETE': (self.Delete, ""),
            'RANGE': (self.Range, "",),
            }


    def Get(self, db, *args):
        """
        Handles GET message command.
        Executes a Get operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to fetch
        """
        return db.Get(*args)


    def Put(self, db, *args):
        """
        Handles Put message command.
        Executes a Put operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key, value) to update

        """
        return db.Put(*args)


    def Delete(self, db, *args):
        """
        Handles Delete message command
        Executes a Delete operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to delete from backend

        """
        return db.Delete(*args)


    def Range(self, db, *args):
        """
        Handles RANGE message command.
        Executes a RangeIter operation over the leveldb backend.

        First arg is always `from_key` which defines the starting point
        for iteration over database.

        If second arg is a string, it is considered as `to_key`
        and defines until which key to iterate over database.
        If it is an int, it defines the number of key to iterate over.
        from from_key, to to_key and returns the result as a list of
        tuples.

        For example :
        Range(db_obj, ('a', 'z')) will return [('a', value), ..., ('z', value)]
        Range(db_obj, ('a', 10) will return [(n, value), (n+1, value), ..., (n+10, value)]

        db      =>      LevelDB object
        *args   =>      (from_key, to_key/step) to delete from backend

        """
        value = []
        if not len(args) == 2:
            raise IndexError("Missing argument to_key or step to Range")
        else:
            from_key, limit = args

        # Right argument is to_key
        if isinstance(limit, str):
            for node in db.RangeIter(from_key, limit):
                value.append(node)
        # Right argument is a step value
        elif isinstance(limit, int):
            pos = 0
            it = db.RangeIter(from_key)

            while pos < limit:
                try:
                    value.append(it.next())
                except StopIteration:
                    break
                pos += 1

        return json.dumps(value) if value else None


    def command(self, message):
        command = message.command
        args = message.data

        if command in self.handlers:
            if len(self.handlers[command]) == 2:
                value = self.handlers[command][0](self.db, *args)
            else:
                # FIXME
                # global except catching is a total
                # performance killer. Should enhance
                # the handlers attributes to link possible
                # exceptions with leveldb methods.
                try:
                    value = self.handlers[command][0](self.db, *args)
                except self.handlers[command][2]:
                    return ""
        else:
            raise KeyError("command not handle")

        return value if value else self.handlers[command][1]
