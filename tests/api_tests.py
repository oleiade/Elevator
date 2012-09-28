import unittest2
import shutil
import msgpack
import os

from nose.tools import *

from elevator.api import Handler
from elevator.db import DatabasesHandler
from elevator.constants import *
from elevator.message import Request


class ApiTests(unittest2.TestCase):
    def _bootstrap_db(self, db):
        for val in xrange(9):
            db.Put(str(val), str(val))

    def setUp(self):
        self.databases = DatabasesHandler('/tmp/store.json', '/tmp')
        self.default_db_uid = self.databases['index']['default']
        self._bootstrap_db(self.databases[self.default_db_uid])
        self.handler = Handler(self.databases)

    def tearDown(self):
        shutil.rmtree('/tmp/default')
        os.remove('/tmp/store.json')

    def test_command_with_existing_command(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'GET',
            ['1'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertNotEqual(content, None)

    def test_command_with_non_existing_command(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'COTCOT',
            ['testarg'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], KEY_ERROR)

    def test_command_with_invalid_db_uid(self):
        message = Request(msgpack.packb([
            '123456',
            'PUT',
            ['1', '1'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], RUNTIME_ERROR)

    def test_get_of_existing_key(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'GET',
            ['1'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, '1')
        
    def test_get_of_non_existing_key(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'GET',
            ['abc123']
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], KEY_ERROR)

    def test_mget_of_existing_keys(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'MGET',
            [['1', '2', '3']],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, [['1', '1'], ['2', '2'], ['3', '3'],])

    def test_mget_of_not_fully_existing_keys(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'MGET',
            [['1', '2', 'touptoupidou']],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], KEY_ERROR)        

    def test_put_of_valid_key(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'PUT',
            ['a', '1']
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

    def test_put_of_existing_key(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'PUT',
            ['a', 1]
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], TYPE_ERROR)

    def test_delete(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DELETE',
            ['9']
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

    def test_range_with_to_key(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'RANGE',
            ['1', '2']
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content[0], ('1', '1'))
        self.assertEqual(content[1], ('2', '2'))
    
    def test_ramge_with_limit(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'RANGE',
            ['1', 3]
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content[0], ('1', '1'))
        self.assertEqual(content[1], ('2', '2'))
        self.assertEqual(content[2], ('3', '3'))

    def test_batch_with_valid_collection(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'BATCH',
            [[('a', 'a'), ('b', 'b'), ('c', 'c'),]],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

    def test_batch_with_invalid_collection(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'BATCH',
            [{'a': 'a', 'b': 'b', 'c': 'c'},],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], VALUE_ERROR)

    def test_connect_to_valid_database(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DBCONNECT',
            ['default'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertIsNotNone(content)

    def test_connect_to_invalid_database(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DBCONNECT',
            ['dadaislikeadad'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], KEY_ERROR)

    def test_create_valid_db(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DBCREATE',
            ['testdb'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)        

    def test_create_already_existing_db(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DBCREATE',
            ['default'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], KEY_ERROR)

    def test_drop_valid_db(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DBDROP',
            ['default'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

        # Please teardown with something to destroy
        # MOUAHAHAHAH... Hum sorry.
        os.mkdir('/tmp/default')

    def test_drop_non_existing_db(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DBDROP',
            ['testdb'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], KEY_ERROR)

    def test_list_db(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'DBLIST',
            [],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(len(content), 1)
        self.assertEqual(content, ['default',])
