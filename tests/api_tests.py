import unittest2
import shutil
import msgpack
import os

from nose.tools import *

from elevator.api import Handler
from elevator.db import DatabasesHandler
from elevator.constants import *
from elevator.message import Request

from .fakers import gen_test_env


class ApiTests(unittest2.TestCase):
    def _bootstrap_db(self, db):
        for val in xrange(9):
            db.Put(str(val), str(val))

    def setUp(self):
        self.env = gen_test_env()
        self.databases = DatabasesHandler('/tmp/store.json', '/tmp')
        self.default_db_uid = self.databases['index']['default']
        self._bootstrap_db(self.databases[self.default_db_uid])
        self.handler = Handler(self.databases)

    def tearDown(self):
        shutil.rmtree('/tmp/default')
        os.remove('/tmp/store.json')

    def request_message(self, command, args, db_uid=None):
        db_uid = db_uid or self.default_db_uid
        return Request(msgpack.packb({
            'DB_UID': db_uid,
            'COMMAND': command,
            'ARGS': args,
        }))


    def test_command_with_existing_command(self):
        message = self.request_message('GET', ['1'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertNotEqual(content, None)

    def test_command_with_non_existing_command(self):
        message = self.request_message('COTCOT', ['testarg'])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], KEY_ERROR)

    def test_command_with_invalid_db_uid(self):
        message = self.request_message('PUT', ['1', '1'], db_uid='failinguid')
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], RUNTIME_ERROR)


    def test_get_of_existing_key(self):
        message = self.request_message('GET', ['1'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, '1')

    def test_get_of_non_existing_key(self):
        message = self.request_message('GET', ['abc123'])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], KEY_ERROR)


    def test_mget_of_existing_keys(self):
        message = self.request_message('MGET', [['1', '2', '3']])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, [('1', '1'), ('2', '2'), ('3', '3'), ])

    def test_mget_of_not_fully_existing_keys(self):
        message = self.request_message('MGET', [['1', '2', 'touptoupidou']])
        status, content = self.handler.command(message)
        self.assertEqual(status, WARNING_STATUS)
        self.assertEqual(len(content), 3)


    def test_put_of_valid_key(self):
        message = self.request_message('PUT', ['a', '1'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

    def test_put_of_existing_key(self):
        message = self.request_message('PUT', ['a', 1])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], TYPE_ERROR)


    def test_delete(self):
        message = self.request_message('DELETE', ['9'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)


    def test_range_with_to_key(self):
        message = self.request_message('RANGE', ['1', '2'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content[0], ('1', '1'))
        self.assertEqual(content[1], ('2', '2'))

    def test_range_with_limit(self):
        message = self.request_message('RANGE', ['1', 3])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content[0], ('1', '1'))
        self.assertEqual(content[1], ('2', '2'))
        self.assertEqual(content[2], ('3', '3'))

    def test_range_of_len_one(self):
        """Should still return a tuple of tuple"""
        message = self.request_message('RANGE', ['1', '1'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(len(content), 1)
        self.assertIsInstance(content, (list, tuple))

        self.assertIsInstance(content[0], (list, tuple))
        self.assertEqual(len(content[0]), 2)


    def test_batch_with_valid_collection(self):
        message = self.request_message('BATCH', args=[
            [(SIGNAL_BATCH_PUT, 'a', 'a'),
             (SIGNAL_BATCH_PUT, 'b', 'b'),
             (SIGNAL_BATCH_PUT, 'c', 'c')],
        ])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

    def test_batch_with_invalid_signals(self):
        message = self.request_message('BATCH', [
            [(-5, 'a', 'a'),
             (-5, 'b', 'b'),
             (-5, 'c', 'c')],
        ])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], SIGNAL_ERROR)

    def test_batch_with_invalid_collection_datas_type(self):
        message = self.request_message('BATCH', [
            [(SIGNAL_BATCH_PUT, 'a', 1),
             (SIGNAL_BATCH_PUT, 'b', 2),
             (SIGNAL_BATCH_PUT, 'c', 3)],
        ])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], TYPE_ERROR)


    def test_connect_to_valid_database(self):
        message = self.request_message('DBCONNECT', ['default'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertIsNotNone(content)

    def test_connect_to_invalid_database(self):
        message = self.request_message('DBCONNECT', ['dadaislikeadad'])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], DATABASE_ERROR)


    def test_create_valid_db(self):
        message = self.request_message('DBCREATE', ['testdb'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

    def test_create_already_existing_db(self):
        message = self.request_message('DBCREATE', ['default'])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], DATABASE_ERROR)


    def test_drop_valid_db(self):
        message = self.request_message('DBDROP', ['default'])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

        # Please teardown with something to destroy
        # MOUAHAHAHAH... Hum sorry.
        os.mkdir('/tmp/default')

    def test_drop_non_existing_db(self):
        message = self.request_message('DBDROP', ['testdb'])
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], DATABASE_ERROR)


    def test_list_db(self):
        message = self.request_message('DBLIST', [])
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(len(content), 1)
        self.assertEqual(content, ['default',])
