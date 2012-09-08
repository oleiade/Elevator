#!/usr/bin/env python
# -*- coding: utf-8 -*-

import leveldb
import logging

from .constants import KEY_ERROR, TYPE_ERROR,\
                       INDEX_ERROR, RUNTIME_ERROR,\
                       SUCCESS_STATUS, FAILURE_STATUS
from .env import Environment
from .db import DatabaseOptions


class Handler(object):
    """
    Class that handles commands server side.
    Translates, messages commands to it's methods calls.
    """
    def __init__(self, databases, context):
        self.databases = databases
        self.activity_logger = logging.getLogger('activity_logger')
        self.errors_logger = logging.getLogger('errors_logger')
        # Each handlers is formatted following
        # the pattern : [ command,
        #                 default return value,
        #                 raised error ]
        self.handlers = {
            'GET': self.Get,
            'PUT': self.Put,
            'DELETE': self.Delete,
            'RANGE': self.Range,
            'BPUT': self.BPut,
            'BDELETE': self.BDelete,
            'BWRITE': self.BWrite,
            'BCLEAR': self.BClear,
            'DBCONNECT': self.DBConnect,
            'DBCREATE': self.DBCreate,
            'DBLIST': self.DBList,
            'DBREPAIR': self.DBRepair,
        }

    def Get(self, db, context, *args, **kwargs):
        """
        Handles GET message command.
        Executes a Get operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to fetch
        """
        try:
            return SUCCESS_STATUS, db.Get(*args)
        except KeyError:
            self.errors_logger.exception("Key %r does not exist" % args[0])
            return (FAILURE_STATUS,
                    [KEY_ERROR, "Key does not exist"])

        return FAILURE_STATUS, None

    def Put(self, db, context, *args, **kwargs):
        """
        Handles Put message command.
        Executes a Put operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key, value) to update

        """
        try:
            return SUCCESS_STATUS, db.Put(*args)
        except TypeError:
            self.errors_logger.exception("Unsupported value type : %s" % type(args[1]))
            return (FAILURE_STATUS,
                   [TYPE_ERROR, "Unsupported value type"])

        return FAILURE_STATUS, None

    def Delete(self, db, context, *args, **kwargs):
        """
        Handles Delete message command
        Executes a Delete operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to delete from backend

        """
        return SUCCESS_STATUS, db.Delete(*args)

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
            self.errors_logger.error('Missing argument to_key or step to Range.'
                                     ' %s supplied' % str(args))
            return (FAILURE_STATUS,
                   [INDEX_ERROR, "Missing argument to_key or step to Range"])

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
        value = None if not value else value

        return SUCCESS_STATUS, value

    def BPut(self, db, context, *args, **kwargs):
        key, value, bid = args

        # if the sought batch to update with Put
        # operation is not yet present in the
        # context, create it
        if not bid in context:
            context[bid] = leveldb.WriteBatch()

        context[bid].Put(key, value)
        return SUCCESS_STATUS, None

    def BDelete(self, db, context, *args, **kwargs):
        key, bid = args

        # if the sought batch to update with Put
        # operation is not yet present in the
        # context, create it
        if not bid in context:
            context[bid] = leveldb.WriteBatch()

        context[bid].Delete(key)
        return SUCCESS_STATUS, None

    def BWrite(self, db, context, *args, **kwargs):
        bid = args[0]

        # FIXME : an error should be raised
        # whenever the batch object to write
        # doesn't exist or is empty.
        if bid in context:
            db.Write(context[bid])
        return SUCCESS_STATUS, None

    def BClear(self, db, context, *args, **kwargs):
        bid = args[0]

        if bid in context:
            del context[bid]
        return SUCCESS_STATUS, None

    def DBConnect(self, *args, **kwargs):
        db_name = kwargs.pop('db_name', None)

        if (not db_name or
            (db_name and (not db_name in self.databases['index']))):
            self.errors_logger.error("Database %s doesn't exist" % db_name)
            return (FAILURE_STATUS,
                    [KEY_ERROR, "Database %s doesn't exist" % db_name])

        return SUCCESS_STATUS, self.databases['index'][db_name]

    def DBCreate(self, db, context, *args, **kwargs):
        db_name = args[0]
        db_options = kwargs.pop('db_options', DatabaseOptions())

        if db_name in self.databases['index']:
            self.errors_logger.error("Database %s already exists" % db_name)            
            return (FAILURE_STATUS,
                    [KEY_ERROR, "Database %s already exists" % db_name])

        self.databases.add(db_name, db_options)

        return SUCCESS_STATUS, None

    def DBList(self, db, context, *args, **kwargs):
        return SUCCESS_STATUS, self.databases.list()

    def DBRepair(self, db, context, *args, **kwargs):
        db_uid = kwargs.pop('db_uid')
        db_path = self.databases['paths_index'][db_uid]

        leveldb.RepairDB(db_path)

        return SUCCESS_STATUS, None

    def command(self, message, context, *args, **kwargs):
        db_uid = message.db_uid
        command = message.command
        args = message.data
        kwargs.update({'db_uid': db_uid})  # Just in case
        status = SUCCESS_STATUS

        if command == 'DBCONNECT':
            # Here db_uid is in fact a db name, and connect
            # returns the valid seek db uid.
            return SUCCESS_STATUS, self.DBConnect(db_name=message.data['db_name'], *args, **kwargs)

        if (not db_uid or
            (db_uid and (not db_uid in self.databases))):
            self.errors_logger.error("Database %s doesn't exist" % db_uid)
            return (FAILURE_STATUS,
                    [RUNTIME_ERROR, "Database does not exist"])

        if not command in self.handlers:
            self.errors_logger.error("Command %s not handled" % command)
            return (FAILURE_STATUS,
                    [KEY_ERROR, "Command not handled"])

        status, value = self.handlers[command](self.databases[db_uid], context, *args, **kwargs)

        return status, value
