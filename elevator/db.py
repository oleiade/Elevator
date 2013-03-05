# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import os
import uuid
import logging
import plyvel
import ujson as json

from shutil import rmtree
from plyvel import CorruptionError

from .constants import OS_ERROR, DATABASE_ERROR
from .utils.patterns import enum
from .helpers.internals import failure, success


activity_logger = logging.getLogger("activity_logger")
errors_logger = logging.getLogger("errors_logger")


class DatabaseOptions(dict):
    def __init__(self, *args, **kwargs):
        self['create_if_missing'] = True
        self['error_if_exists'] = False
        self['bloom_filter_bits'] = 10  # Value recommended by leveldb doc
        self['paranoid_checks'] = False
        self['lru_cache_size'] = 512 * (1 << 20)  # 512 Mo
        self['write_buffer_size'] = 4 * (1 << 20)  # 4 Mo
        self['block_size'] = 4096
        self['max_open_files'] = 1000

        for key, value in kwargs.iteritems():
            if key in self:
                self[key] = value


class Database(object):
    STATUS = enum('MOUNTED', 'UNMOUNTED')

    def __init__(self, name, path, options,
                 status=STATUS.UNMOUNTED, init_connector=False):
        self.name = name
        self.path = path
        self.status = status
        self.last_access = 0.0
        self._connector = None
        self.options = options

        if init_connector:
            self.set_connector(self.path, **self.options)

    def __del__(self):
        del self._connector

    @property
    def connector(self):
        return self._connector

    @connector.setter
    def connector(self, value):
        if isinstance(value, plyvel.DB) or value is None:
            self._connector = value
        else:
            raise TypeError("Connector whether should be"
                            "a plyvel object or None")

    @connector.deleter
    def connector(self):
        del self._connector

    def set_connector(self, path, *args, **kwargs):
        kwargs.update({'create_if_missing': True})

        try:
            self._connector = plyvel.DB(path, *args, **kwargs)
        except CorruptionError as e:
            errors_logger.exception(e.message)

    def mount(self):
        if self.status is self.STATUS.UNMOUNTED:
            self.set_connector(self.path)

            if self.connector is None:
                return failure(DATABASE_ERROR, "Database %s could not be mounted" % self.path)

            self.status = self.STATUS.MOUNTED
        else:
            return failure(DATABASE_ERROR, "Database %r already mounted" % self.path)

        return success()

    def umount(self):
        if self.status is self.STATUS.MOUNTED:
            self.status = self.STATUS.UNMOUNTED
            del self._connector
            self._connector = None
        else:
            return failure(DATABASE_ERROR, "Database %r already unmounted" % self.name)

        return success()


class DatabaseStore(dict):
    STATUSES = enum('MOUNTED', 'UNMOUNTED')

    def __init__(self, config, *args, **kwargs):
        self.index = dict().fromkeys('name_to_uid')

        self.index['name_to_uid'] = {}
        self['reverse_name_index'] = {}
        self['paths_index'] = {}
        self.store_file = config['database_store']
        self.storage_path = config['databases_storage_path']

        self._global_cache_size = None

        self.load()
        self.mount('default')  # Always mount default

    def __del__(self):
        """
        Explictly shutsdown the internal leveldb connectors
        """
        for uid in self.keys():
            del self[uid]

    @property
    def last_access(self):
        result = {}

        for uid, data in self.iteritems():
            if 'last_access' in data:
                result[uid] = data['last_access']

        return result

    def extract_store_datas(self):
        """Retrieves database store from file

        If file doesn't exist, or is invalid json,
        and empty store is returned.

        Return
        ------
        store_datas, dict
        """
        try:
            store_datas = json.load(open(self.store_file, 'r'))
        except (IOError, ValueError):
            store_datas = {}

        return store_datas

    def load(self):
        """Loads databases from store file"""
        store_datas = self.extract_store_datas()

        for db_name, db_desc in store_datas.iteritems():
            self.index['name_to_uid'].update({db_name: db_desc['uid']})
            self.update({
                db_desc['uid']: Database(db_name, db_desc['path'], db_desc['options'])
            })

        # Always bootstrap 'default'
        if 'default' not in self.index['name_to_uid']:
            self.add('default')

    def store_update(self, db_name, db_desc):
        """Updates the database store file db_name
        key, with db_desc value"""
        store_datas = self.extract_store_datas()

        store_datas.update({db_name: db_desc})
        json.dump(store_datas, open(self.store_file, 'w'))

    def store_remove(self, db_name):
        """Removes a database from store file"""
        store_datas = self.extract_store_datas()
        store_datas.pop(db_name)
        json.dump(store_datas, open(self.store_file, 'w'))

    def status(self, db_name):
        """Returns the mounted/unmounted database status"""

        db_uid = self.index['name_to_uid'][db_name] if db_name in self.index['name_to_uid'] else None
        return self[db_uid].status

    def mount(self, db_name):
        db_uid = self.index['name_to_uid'][db_name] if db_name in self.index['name_to_uid'] else None
        return self[db_uid].mount()

    def umount(self, db_name):
        db_uid = self.index['name_to_uid'][db_name] if db_name in self.index['name_to_uid'] else None
        return self[db_uid].umount()

    def add(self, db_name, db_options=None):
        """Adds a db to the DatabasesStore object, and sync it
        to the store file"""
        db_options = db_options or DatabaseOptions()
        db_name_is_path = db_name.startswith('.') or ('/' in db_name)
        is_abspath = lambda: not db_name.startswith('.') and ('/' in db_name)

        # Handle case when a db is a path
        if db_name_is_path:
            if not is_abspath():
                return failure(DATABASE_ERROR, "Canno't create database from relative path")
            try:
                new_db_path = db_name
                if not os.path.exists(new_db_path):
                    os.mkdir(new_db_path)
            except OSError as e:
                return failure(OS_ERROR, e.strerror)
        else:
            new_db_path = os.path.join(self.storage_path, db_name)

        path = new_db_path
        database = Database(db_name,
                            path,
                            db_options,
                            status=Database.STATUS.MOUNTED,
                            init_connector=True)

        # Adding db to store, and updating handler
        uid = str(uuid.uuid4())
        self.index['name_to_uid'].update({db_name: uid})
        self.store_update(db_name, {
            'path': path,
            'uid': uid,
            'options': db_options,
        })
        self.update({uid: database})

        return success()

    def drop(self, db_name):
        """Drops a db from the DatabasesHandler, and sync it
        to store file"""
        db_uid = self.index['name_to_uid'].pop(db_name)
        db_path = self[db_uid].path

        self.pop(db_uid)
        self.store_remove(db_name)

        try:
            rmtree(db_path)
        except OSError:
            return failure(DATABASE_ERROR, "Cannot drop db : %s, files not found")

        return success()

    def exists(self, db_name):
        """Checks if a database exists on disk"""
        db_uid = self.index['name_to_uid'][db_name] if db_name in self.index['name_to_uid'] else None

        if db_uid:
            if os.path.exists(self[db_uid].path):
                return True
            else:
                self.drop(db_name)

        return False

    def list(self):
        """Lists all the DatabasesHandler known databases"""
        return [db_name for db_name
                in [key for key
                    in self.index['name_to_uid'].iterkeys()]
                if self.exists(db_name)]
