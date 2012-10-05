from __future__ import absolute_import

import unittest2
import os
import json
import shutil

from elevator.utils.snippets import from_mo_to_bytes
from elevator.constants import SUCCESS_STATUS, FAILURE_STATUS,\
                               KEY_ERROR, RUNTIME_ERROR, DATABASE_ERROR
from elevator.db import DatabasesHandler, DatabaseOptions

from .fakers import gen_test_env


class DatabaseOptionsTest(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass



class DatabasesTest(unittest2.TestCase):
    def setUp(self):
        self.store = '/tmp/store.json'
        self.dest = '/tmp/dbs'
        self.env = gen_test_env()
        os.mkdir(self.dest)
        self.handler = DatabasesHandler(self.store, self.dest)

    def tearDown(self):
        os.remove('/tmp/store.json')
        shutil.rmtree('/tmp/dbs')

    def test_init(self):
        self.assertIn('default', self.handler['index'])
        default_db_uid = self.handler['index']['default']

        self.assertIn(default_db_uid, self.handler['reverse_index'])
        self.assertEqual(self.handler['reverse_index'][default_db_uid], 'default')

        self.assertIn(default_db_uid, self.handler['paths_index'])
        self.assertEqual(self.handler['paths_index'][default_db_uid], '/tmp/dbs/default')

    def test_global_max_cache_size(self):
        self.assertEqual(self.handler.global_cache_size, 16)
        self.handler.add('test_cache', db_options={'block_cache_size': (8 * (2 << 20))})
        self.assertEqual(self.handler.global_cache_size, 32)

    def test_load(self):
        db_name = 'testdb'
        self.handler.add(db_name)

        self.assertIn(db_name, self.handler['index'])
        db_uid = self.handler['index'][db_name]
        self.assertIn(db_uid, self.handler)

        self.assertIn(db_uid, self.handler['reverse_index'])
        self.assertEqual(self.handler['reverse_index'][db_uid], db_name)

        self.assertIn(db_uid, self.handler['paths_index'])

        self.assertIn('default', self.handler['index'])

    def test_store_update(self):
        db_name = 'test_db'
        db_desc = {
            'path': '/tmp/test_path',
            'uid': 'testuid',
            'options': {},
        }
        self.handler.store_update(db_name, db_desc)

        store_datas = json.load(open(self.handler.store, 'r'))
        self.assertIn(db_name, store_datas)
        self.assertEqual(store_datas[db_name], db_desc)

    def test_store_remove(self):
        db_name = 'test_db'
        db_desc = {
            'path': '/tmp/test_path',
            'uid': 'testuid',
            'options': {},
        }
        self.handler.store_update(db_name, db_desc)
        self.handler.store_remove(db_name)
        store_datas = json.load(open(self.handler.store, 'r'))

        self.assertNotIn(db_name, store_datas)

    def test_drop_existing_db(self):
        db_name = 'default'  # Automatically created on startup
        status, content = self.handler.drop(db_name)

        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

        store_datas = json.load(open(self.handler.store, 'r'))
        self.assertNotIn(db_name, store_datas)

    def test_remove_existing_db_which_files_were_erased(self):
        db_name = 'testdb'  # Automatically created on startup
        db_path = '/tmp/dbs/testdb'
        status, content = self.handler.add(db_name)
        shutil.rmtree(db_path)
        status, content = self.handler.drop(db_name)

        self.assertEqual(status, FAILURE_STATUS)
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], DATABASE_ERROR)

        store_datas = json.load(open(self.handler.store, 'r'))
        self.assertNotIn(db_name, store_datas)

    def test_add_from_db_name_without_options_passed(self):
        db_name = 'testdb'
        default_db_options = DatabaseOptions()
        status, content = self.handler.add(db_name)

        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

        store_datas = json.load(open(self.handler.store, 'r'))
        self.assertIn(db_name, store_datas)
        self.assertEqual(store_datas[db_name]["path"],
                         os.path.join(self.dest, db_name))

        self.assertIsNotNone(store_datas[db_name]["uid"])

        stored_db_options = store_datas[db_name]["options"]
        self.assertIsNotNone(stored_db_options)
        self.assertIsInstance(stored_db_options, dict)

        for option_name, option_value in default_db_options.iteritems():
            self.assertIn(option_name, stored_db_options)
            self.assertEqual(option_value, stored_db_options[option_name])

    def test_add_from_db_name_with_options_passed(self):
        db_name = 'testdb'
        db_options = DatabaseOptions(paranoid_checks=True)
        status, content = self.handler.add(db_name, db_options)

        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

        store_datas = json.load(open(self.handler.store, 'r'))
        self.assertIn(db_name, store_datas)
        self.assertEqual(store_datas[db_name]["path"],
                         os.path.join(self.dest, db_name))

        self.assertIsNotNone(store_datas[db_name]["uid"])

        stored_db_options = store_datas[db_name]["options"]
        self.assertIsNotNone(stored_db_options)
        self.assertIsInstance(stored_db_options, dict)

        for option_name, option_value in db_options.iteritems():
            if option_name == "paranoid_check":
                self.assertEqual(option_value, False)
                continue
            self.assertIn(option_name, stored_db_options)
            self.assertEqual(option_value, stored_db_options[option_name])

    def test_add_from_db_abspath(self):
        db_path = '/tmp/dbs/testdb'  # Could be anywhere on fs
        default_db_options = DatabaseOptions()
        status, content = self.handler.add(db_path)

        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

        store_datas = json.load(open(self.handler.store, 'r'))
        self.assertIn(db_path, store_datas)
        self.assertEqual(store_datas[db_path]["path"],
                         os.path.join(self.dest, db_path))

        self.assertIsNotNone(store_datas[db_path]["uid"])

        stored_db_options = store_datas[db_path]["options"]
        self.assertIsNotNone(stored_db_options)
        self.assertIsInstance(stored_db_options, dict)

        for option_name, option_value in default_db_options.iteritems():
            self.assertIn(option_name, stored_db_options)
            self.assertEqual(option_value, stored_db_options[option_name])

    def test_add_from_db_relpath(self):
        db_path = './testdb'  # Could be anywhere on fs
        status, content = self.handler.add(db_path)

        self.assertEqual(status, FAILURE_STATUS)
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], DATABASE_ERROR)

        store_datas = json.load(open(self.handler.store, 'r'))
        self.assertNotIn(db_path, store_datas)

    def test_add_db_and_overflow_max_cache_size(self):
        orig_value = self.env["global"]["max_cache_size"]
        db_name = 'testdb'
        db_options = DatabaseOptions(block_cache_size=from_mo_to_bytes(1000))
        self.env["global"]["max_cache_size"] = 32

        # max_cache_size = default cache_size + 16
        status, content = self.handler.add(db_name, db_options)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertIsNotNone(content)
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], DATABASE_ERROR)

        self.env["global"]["max_cache_size"] = orig_value

    def test_add_db_with_enough_max_cache_size(self):
        # Default max_cache_size value is 1024, and default db already
        # occupies 16 Mo
        db_name = 'testdb'
        db_options = DatabaseOptions(block_cache_size=from_mo_to_bytes(32))

        # max_cache_size = default cache_size + 16
        status, content = self.handler.add(db_name, db_options)
        self.assertEqual(status, SUCCESS_STATUS)
