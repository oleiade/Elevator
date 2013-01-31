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

from .env import Environment
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
        self['compression'] = True
        self['lru_cache_size'] = 512 * (1 << 20)  # 512 Mo
        self['write_buffer_size'] = 4 * (1 << 20)  # 4 Mo
        self['block_size'] = 4096
        self['max_open_files'] = 1000

        for key, value in kwargs.iteritems():
            if key in self:
                self[key] = value


class DatabasesHandler(dict):
    STATUSES = enum('MOUNTED', 'UNMOUNTED')

    def __init__(self, store, dest, *args, **kwargs):
        self.env = Environment()
        self.index = dict().fromkeys('name_to_uid')

        self.index['name_to_uid'] = {}
        self['reverse_name_index'] = {}
        self['paths_index'] = {}
        self.dest = dest
        self.store = store

        self._global_cache_size = None

        self.load()
        self.mount('default')  # Always mount default

    def __del__(self):
        """
        Explictly shutsdown the internal leveldb connectors
        """
        for uid in self.index['name_to_uid'].values():
            if 'connector' in self[uid] and self[uid]['connector'] is not None:
                del self[uid]['connector']

    def _get_db_connector(self, path, *args, **kwargs):
        connector = None

        try:
            connector = plyvel.DB(path, create_if_missing=True, *args, **kwargs)
        except CorruptionError as e:
            errors_logger.exception(e.message)

        return connector

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
            store_datas = json.load(open(self.store, 'r'))
        except (IOError, ValueError):
            store_datas = {}

        return store_datas

    def load(self):
        """Loads databases from store file"""
        store_datas = self.extract_store_datas()

        for db_name, db_desc in store_datas.iteritems():
            self.index['name_to_uid'].update({db_name: db_desc['uid']})
            self.update({
                db_desc['uid']: {
                    'connector': None,
                    'name': db_name,
                    'path': db_desc['path'],
                    'status': self.STATUSES.UNMOUNTED,
                    'last_access': 0.0,
                }
            })

        # Always bootstrap 'default'
        if 'default' not in self.index['name_to_uid']:
            self.add('default')

    def store_update(self, db_name, db_desc):
        """Updates the database store file db_name
        key, with db_desc value"""
        store_datas = self.extract_store_datas()

        store_datas.update({db_name: db_desc})
        json.dump(store_datas, open(self.store, 'w'))

    def store_remove(self, db_name):
        """Removes a database from store file"""
        store_datas = self.extract_store_datas()
        store_datas.pop(db_name)
        json.dump(store_datas, open(self.store, 'w'))

    def mount(self, db_name):
        db_uid = self.index['name_to_uid'][db_name] if db_name in self.index['name_to_uid'] else None

        if self[db_uid]['status'] == self.STATUSES.UNMOUNTED:
            db_path = self[db_uid]['path']
            connector = self._get_db_connector(db_path)

            if connector is None:
                return failure(DATABASE_ERROR, "Database %s could not be mounted" % db_path)

            self[db_uid]['status'] = self.STATUSES.MOUNTED
            self[db_uid]['connector'] = connector
        else:
            return failure(DATABASE_ERROR, "Database %r already mounted" % db_name)

        return success()

    def umount(self, db_name):
        db_uid = self.index['name_to_uid'][db_name] if db_name in self.index['name_to_uid'] else None

        if self[db_uid]['status'] == self.STATUSES.MOUNTED:
            self[db_uid]['status'] = self.STATUSES.UNMOUNTED
            del self[db_uid]['connector']
            self[db_uid]['connector'] = None
        else:
            return failure(DATABASE_ERROR, "Database %r already unmounted" % db_name)

        return success()

    def add(self, db_name, db_options=None):
        """Adds a db to the DatabasesHandler object, and sync it
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
            new_db_path = os.path.join(self.dest, db_name)

        path = new_db_path
        connector = self._get_db_connector(path)

        if connector is None:
            return (DATABASE_ERROR, "Database %s could not be created" % path)

        # Adding db to store, and updating handler
        uid = str(uuid.uuid4())
        options = db_options
        self.store_update(db_name, {
            'path': path,
            'uid': uid,
            'options': options,
        })

        self.index['name_to_uid'].update({db_name: uid})
        self.update({
            uid: {
                'connector': connector,
                'name': db_name,
                'path': path,
                'status': self.STATUSES.MOUNTED,
                'ref_count': 0,
            },
        })

        return success()

    def drop(self, db_name):
        """Drops a db from the DatabasesHandler, and sync it
        to store file"""
        db_uid = self.index['name_to_uid'].pop(db_name)
        db_path = self[db_uid]['path']

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
            if os.path.exists(self[db_uid]['path']):
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
