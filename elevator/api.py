#!/usr/bin/env python
# -*- coding: utf-8 -*-

import leveldb
import logging

from .constants import KEY_ERROR, TYPE_ERROR,\
                       INDEX_ERROR, RUNTIME_ERROR,\
                       VALUE_ERROR, SUCCESS_STATUS, FAILURE_STATUS
from .db import DatabaseOptions


class Handler(object):
    """
    Class that handles commands server side.
    Translates, messages commands to it's methods calls.
    """
    def __init__(self, databases):
        self.databases = databases
        self.activity_logger = logging.getLogger('activity_logger')
        self.errors_logger = logging.getLogger('errors_logger')
        self.handlers = {
            'GET': self.Get,
            'PUT': self.Put,
            'DELETE': self.Delete,
            'RANGE': self.Range,
            'BATCH': self.Batch,
            'MGET': self.MGet,
            'DBCONNECT': self.DBConnect,
            'DBCREATE': self.DBCreate,
            'DBDROP': self.DBDrop,
            'DBLIST': self.DBList,
            'DBREPAIR': self.DBRepair,
        }

    def Get(self, db, key, *args, **kwargs):
        """
        Handles GET message command.
        Executes a Get operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to fetch
        """
        try:
            return SUCCESS_STATUS, db.Get(key)
        except KeyError:
            error_msg = "Key %r does not exist" % key
            self.errors_logger.exception(error_msg)
            return (FAILURE_STATUS,
                    [KEY_ERROR, error_msg])

    def MGet(self, db, keys, *args, **kwargs):
        value = []

        for key in keys:
            try:
                value.append([key, db.Get(key)])
            except KeyError:
                error_msg = "Key %r does not exist" % key
                self.errors_logger.exception(error_msg)
                return (FAILURE_STATUS,
                        [KEY_ERROR, error_msg])
        return SUCCESS_STATUS, value

    def Put(self, db, key, value, *args, **kwargs):
        """
        Handles Put message command.
        Executes a Put operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key, value) to update

        """
        try:
            return SUCCESS_STATUS, db.Put(key, value)
        except TypeError:
            error_msg = "Unsupported value type : %s" % type(value)
            self.errors_logger.exception(error_msg)
            return (FAILURE_STATUS,
                   [TYPE_ERROR, error_msg])

    def Delete(self, db, key, *args, **kwargs):
        """
        Handles Delete message command
        Executes a Delete operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to delete from backend

        """
        return SUCCESS_STATUS, db.Delete(key)

    def Range(self, db, from_key, limit, *args, **kwargs):
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

        # Operate over a snapshot in order to return
        # a consistent state of the db
        db_snapshot = db.CreateSnapshot()

        # Right argument is to_key
        if isinstance(limit, str):
            for node in db_snapshot.RangeIter(from_key, limit):
                value.append(node)
        # Right argument is a step value
        elif isinstance(limit, int):
            pos = 0
            it = db_snapshot.RangeIter(from_key)

            while pos < limit:
                try:
                    value.append(it.next())
                except StopIteration:
                    break
                pos += 1

        return SUCCESS_STATUS, value

    def Batch(self, db, collection, *args, **kwargs):
        batch = leveldb.WriteBatch()

        try:
            for (key, value) in collection:
                batch.Put(key, value)
        except ValueError:
            return (FAILURE_STATUS,
                    [VALUE_ERROR, "Batch only accepts sequences (list, tuples,...)"])
        db.Write(batch)

        return SUCCESS_STATUS, None

    def DBConnect(self, db_name=None, *args, **kwargs):
        if (not db_name or
            not self.databases.exists(db_name)):
            error_msg = "Database %s doesn't exist" % db_name
            self.errors_logger.error(error_msg)
            return (FAILURE_STATUS,
                    [KEY_ERROR, error_msg])

        return SUCCESS_STATUS, self.databases['index'][db_name]

    def DBCreate(self, db, db_name, db_options=None, *args, **kwargs):
        db_options = DatabaseOptions() if db_options is None else db_options

        if db_name in self.databases['index']:
            error_msg = "Database %s already exists" % db_name
            self.errors_logger.error(error_msg)
            return (FAILURE_STATUS,
                    [KEY_ERROR, error_msg])

        status, content = self.databases.add(db_name, db_options)
        return status, content

    def DBDrop(self, db, db_name, *args, **kwargs):
        if not self.databases.exists(db_name):
            error_msg = "Database %s does not exist" % db_name
            self.errors_logger.error(error_msg)
            return (FAILURE_STATUS,
                    [KEY_ERROR, error_msg])

        status, content = self.databases.drop(db_name)
        return status, content

    def DBList(self, db, *args, **kwargs):
        return SUCCESS_STATUS, self.databases.list()

    def DBRepair(self, db, db_uid, *args, **kwargs):
        db_path = self.databases['paths_index'][db_uid]

        leveldb.RepairDB(db_path)

        return SUCCESS_STATUS, None

    def command(self, message, *args, **kwargs):
        db_uid = message.db_uid
        command = message.command
        args = message.data
        kwargs.update({'db_uid': db_uid})  # Just in case
        status = SUCCESS_STATUS

        if command == 'DBCONNECT':
            # Here db_uid is in fact a db name, and connect
            # returns the valid seek db uid.
            status, value = self.DBConnect(db_name=message.data[0])
            return status, value

        if (not db_uid or
            (db_uid and (not db_uid in self.databases))):
            error_msg = "Database %s doesn't exist" % db_uid
            self.errors_logger.error(error_msg)
            return (FAILURE_STATUS,
                    [RUNTIME_ERROR, error_msg])

        if not command in self.handlers:
            error_msg = "Command %s not handled" % command
            self.errors_logger.error(error_msg)
            return (FAILURE_STATUS,
                    [KEY_ERROR, error_msg])

        status, value = self.handlers[command](self.databases[db_uid], *args, **kwargs)

        return status, value
