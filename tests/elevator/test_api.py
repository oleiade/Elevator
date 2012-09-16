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
    def setUp(self):
        self.databases = DatabasesHandler('/tmp/store.json', '/tmp')
        self.default_db_uid = self.databases['index']['default']
        self.handler = Handler(self.databases)

    def tearDown(self):
        shutil.rmtree('/tmp/default')
        os.remove('/tmp/store.json')

    def test_command_with_existing_command(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'PUT',
            ['1', 'a'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, SUCCESS_STATUS)
        self.assertEqual(content, None)

    def test_command_with_non_existing_command(self):
        message = Request(msgpack.packb([
            self.default_db_uid,
            'COTCOT',
            ['testarg'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], KEY_ERROR)

    def test_command_with_invalid_db_uid(self):
        message = Request(msgpack.packb([
            '123456',
            'PUT',
            ['1', 'a'],
        ]))
        status, content = self.handler.command(message)
        self.assertEqual(status, FAILURE_STATUS)
        self.assertEqual(content[0], RUNTIME_ERROR)

    def test_get_of_existing_key(self):
        pass

    def test_get_of_non_existing_key(self):
        pass
