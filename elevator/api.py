#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import leveldb
import ujson as json


class Handler(object):
    """
    Class that handles commands server side.
    Translates, messages commands to it's methods calls.
    """
    def __init__(self, databases, context):
        self.databases = databases
        # Each handlers is formatted following
        # the pattern : [ command,
        #                 default return value,
        #                 raised error ]
        self.handlers = {
            'GET': (self.Get, "", KeyError),
            'PUT': (self.Put, "True", TypeError),
            'DELETE': (self.Delete, ""),
            'RANGE': (self.Range, "",),
            'BPUT': (self.BPut, ""),
            'BDELETE': (self.BDelete, ""),
            'BWRITE': (self.BWrite, ""),
            'BCLEAR': (self.BClear, ""),
            'DBCREATE': (self.DBCreate, ""),
            'DBLIST': (self.DBList, ""),
            'DBDELETE': (self.DBDelete, ""),
            }

    def Get(self, db, context, *args, **kwargs):
        """
        Handles GET message command.
        Executes a Get operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to fetch
        """
        return db.Get(*args)

    def Put(self, db, context, *args, **kwargs):
        """
        Handles Put message command.
        Executes a Put operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key, value) to update

        """
        return db.Put(*args)

    def Delete(self, db, context, *args, **kwargs):
        """
        Handles Delete message command
        Executes a Delete operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to delete from backend

        """
        return db.Delete(*args)

    def Range(self, db, context, *args, **kwargs):
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

        For example:
        Range(db_obj, ('a', 'z'))
            will return [('a', value), ..., ('z', value)]
        Range(db_obj, ('a', 10)
            will return [(n, value), (n+1, value), ..., (n+10, value)]

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

    def BPut(self, db, context, *args, **kwargs):
        key, value, bid = args

        # if the sought batch to update with Put
        # operation is not yet present in the
        # context, create it
        if not bid in context:
            context[bid] = leveldb.WriteBatch()
        context[bid].Put(key, value)
        return ''

    def BDelete(self, db, context, *args, **kwargs):
        key, bid = args

        # if the sought batch to update with Put
        # operation is not yet present in the
        # context, create it
        if not bid in context:
            context[bid] = leveldb.WriteBatch()
        context[bid].Delete(key)
        return ''

    def BWrite(self, db, context, *args, **kwargs):
        bid = args[0]

        # FIXME : an error should be raised
        # whenever the batch object to write
        # doesn't exist or is empty.
        if bid in context:
            db.Write(context[bid])
        return ''

    def BClear(self, db, context, *args, **kwargs):
        bid = args[0]

        if bid in context:
            del context[bid]
        return ''

    def DBCreate(self, db, context, *args, **kwargs):
        env = kwargs.get('env', None)
        db_name = args[0]
        db_options = kwargs.pop('db_options', {})

        if env and not 'database_store' in env['global']:
            raise KeyError("Missing database_store value in environment")
        else:
            db_path = os.path.join(env['global']['database_store'], db_name)

        if not db_name in self.databases:
            self.databases.update({db_name: leveldb.LevelDB(db_path, **db_options)})
            return 'SUCCESS'
        else:
            raise KeyError("Database %s already exists" % db_name)

        return ''

    def DBList(self, db, context, *args, **kwargs):
        return json.dumps([db for db in self.databases.iterkeys()])        

    def command(self, message, context, *args, **kwargs):
        db_name = message.db_name
        command = message.command
        args = message.data

        if not db_name in self.databases:
            raise RuntimeError("Databases %s does not exist" % db_name)

        if command in self.handlers:
            if len(self.handlers[command]) == 2:
                value = self.handlers[command][0](self.databases[db_name], context, *args, **kwargs)
            else:
                # FIXME
                # global except catching is a total
                # performance killer. Should enhance
                # the handlers attributes to link possible
                # exceptions with leveldb methods.
                try:
                    value = self.handlers[command][0](self.databases[db_name], context, *args, **kwargs)
                except self.handlers[command][2]:
                    return ""
        else:
            raise KeyError("command not handle")

        return value if value else self.handlers[command][1]
