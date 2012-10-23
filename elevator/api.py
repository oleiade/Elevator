# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import leveldb
import logging

from .db import DatabaseOptions
from .message import ResponseContent, ResponseHeader
from .constants import KEY_ERROR, TYPE_ERROR, DATABASE_ERROR,\
                       VALUE_ERROR, RUNTIME_ERROR, SIGNAL_ERROR,\
                       SUCCESS_STATUS, FAILURE_STATUS, WARNING_STATUS,\
                       SIGNAL_BATCH_PUT, SIGNAL_BATCH_DELETE
from .utils.patterns import destructurate
from .helpers.internals import failure, success


errors_logger = logging.getLogger('errors_logger')


class Handler(object):
    """
    Class that handles commands server side.
    Translates, messages commands to it's methods calls.
    """
    def __init__(self, databases):
        self.databases = databases
        self.handlers = {
            'GET': self.Get,
            'PUT': self.Put,
            'DELETE': self.Delete,
            'RANGE': self.Range,
            'SLICE': self.Slice,
            'BATCH': self.Batch,
            'MGET': self.MGet,
            'DBCONNECT': self.DBConnect,
            'DBMOUNT': self.DBMount,
            'DBUMOUNT': self.DBUmount,
            'DBCREATE': self.DBCreate,
            'DBDROP': self.DBDrop,
            'DBLIST': self.DBList,
            'DBREPAIR': self.DBRepair,
        }
        self.context = {}

    def Get(self, db, key, *args, **kwargs):
        """
        Handles GET message command.
        Executes a Get operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to fetch
        """
        try:
            return success(db.Get(key))
        except KeyError:
            error_msg = "Key %r does not exist" % key
            errors_logger.exception(error_msg)
            return failure(KEY_ERROR, error_msg)

    def MGet(self, db, keys, *args, **kwargs):
        def get_or_none(key, context):
            try:
                res = db.Get(key)
            except KeyError:
                warning_msg = "Key {0} does not exist".format(key)
                context['status'] = WARNING_STATUS
                errors_logger.warning(warning_msg)
                res = None
            return res

        context = {'status': SUCCESS_STATUS}
        value = [get_or_none(key, context) for key in keys]
        status = context['status']

        return status, value

    def Put(self, db, key, value, *args, **kwargs):
        """
        Handles Put message command.
        Executes a Put operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key, value) to update

        """
        try:
            return success(db.Put(key, value))
        except TypeError:
            error_msg = "Unsupported value type : %s" % type(value)
            errors_logger.exception(error_msg)
            return failure(TYPE_ERROR, error_msg)

    def Delete(self, db, key, *args, **kwargs):
        """
        Handles Delete message command
        Executes a Delete operation over the leveldb backend.

        db      =>      LevelDB object
        *args   =>      (key) to delete from backend

        """
        return success(db.Delete(key))

    def Range(self, db, key_from, key_to, *args, **kwargs):
        """Returns the Range of key/value between
        `key_from and `key_to`"""
        # Operate over a snapshot in order to return
        # a consistent state of the db
        db_snapshot = db.CreateSnapshot()
        value = list(db_snapshot.RangeIter(key_from, key_to))

        return success(value)

    def Slice(self, db, key_from, offset, *args, **kwargs):
        """Returns a slice of the db. `offset` keys,
        starting a `key_from`"""
        # Operates over a snapshot in order to return
        # a consistent state of the db
        db_snapshot = db.CreateSnapshot()
        it = db_snapshot.RangeIter(key_from)
        value = []
        pos = 0

        while pos < offset:
            try:
                value.append(it.next())
            except StopIteration:
                break
            pos += 1

        return success(value)

    def Batch(self, db, collection, *args, **kwargs):
        batch = leveldb.WriteBatch()
        batch_actions = {
            SIGNAL_BATCH_PUT: batch.Put,
            SIGNAL_BATCH_DELETE: batch.Delete,
        }

        try:
            for command in collection:
                signal, args = destructurate(command)
                batch_actions[signal](*args)
        except KeyError:  # Unrecognized signal
            return (FAILURE_STATUS,
                    [SIGNAL_ERROR, "Unrecognized signal received : %r" % signal])
        except ValueError:
            return (FAILURE_STATUS,
                    [VALUE_ERROR, "Batch only accepts sequences (list, tuples,...)"])
        except TypeError:
            return (FAILURE_STATUS,
                    [TYPE_ERROR, "Invalid type supplied"])
        db.Write(batch)

        return success()

    def DBConnect(self, *args, **kwargs):
        db_name = args[0]

        if (not db_name or
            not self.databases.exists(db_name)):
            error_msg = "Database %s doesn't exist" % db_name
            errors_logger.error(error_msg)
            return failure(DATABASE_ERROR, error_msg)

        db_uid = self.databases.index['name_to_uid'][db_name]
        if self.databases[db_uid]['status'] == self.databases.STATUSES.UNMOUNTED:
            self.databases.mount(db_name)

        return success(db_uid)

    def DBMount(self, db_name, *args, **kwargs):
        return self.databases.mount(db_name)

    def DBUmount(self, db_name, *args, **kwargs):
        return self.databases.umount(db_name)

    def DBCreate(self, db, db_name, db_options=None, *args, **kwargs):
        db_options = DatabaseOptions(**db_options) if db_options else DatabaseOptions()

        if db_name in self.databases.index['name_to_uid']:
            error_msg = "Database %s already exists" % db_name
            errors_logger.error(error_msg)
            return failure(DATABASE_ERROR, error_msg)

        return self.databases.add(db_name, db_options)

    def DBDrop(self, db, db_name, *args, **kwargs):
        if not self.databases.exists(db_name):
            error_msg = "Database %s does not exist" % db_name
            errors_logger.error(error_msg)
            return failure(DATABASE_ERROR, error_msg)

        status, content = self.databases.drop(db_name)
        return status, content

    def DBList(self, db, *args, **kwargs):
        return success(self.databases.list())

    def DBRepair(self, db, db_uid, *args, **kwargs):
        db_path = self.databases['paths_index'][db_uid]

        leveldb.RepairDB(db_path)

        return success()

    def _gen_response(self, request, cmd_status, cmd_value):
        if cmd_status == FAILURE_STATUS:
            header = ResponseHeader(status=cmd_status, err_code=cmd_value[0], err_msg=cmd_value[1])
            content = ResponseContent(datas=None)
        else:
            if 'compression' in request.meta:
                compression = request.meta['compression']
            else:
                compression = False

            header = ResponseHeader(status=cmd_status, compression=compression)
            content = ResponseContent(datas=cmd_value, compression=compression)

        return header, content

    def command(self, message, *args, **kwargs):
        status = SUCCESS_STATUS
        err_code, err_msg = None, None

        # DB does not exist
        if message.db_uid and (not message.db_uid in self.databases):
            error_msg = "Database %s doesn't exist" % message.db_uid
            errors_logger.error(error_msg)
            status, value = failure(RUNTIME_ERROR, error_msg)
        # Command not recognized
        elif not message.command in self.handlers:
            error_msg = "Command %s not handled" % message.command
            errors_logger.error(error_msg)
            status, value = failure(KEY_ERROR, error_msg)
        # Valid request
        else:
            if not message.db_uid:
                status, value = self.handlers[message.command](*message.data, **kwargs)
            else:
                database = self.databases[message.db_uid]['connector']
                status, value = self.handlers[message.command](database, *message.data, **kwargs)

        # Will output a valid ResponseHeader and ResponseContent objects
        return self._gen_response(message, status, value)
