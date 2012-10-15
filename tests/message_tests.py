from __future__ import absolute_import

import unittest2
import msgpack

from nose.tools import raises

from elevator.message import Request, Response, MessageFormatError
from elevator.constants import *


class RequestTest(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @raises(MessageFormatError)
    def test_request_with_missing_mandatory_arguments(self):
        request = msgpack.packb({
            'uid': '123-456-789',
            'cmd': 'GET',
        })

        request = Request(request)

    def test_valid_request_without_meta(self):
        request = msgpack.packb({
            'uid': '123-456-789',
            'cmd': 'PUT',
            'args': ['key', 'value']
        })

        request = Request(request)
        self.assertIsNotNone(request)

        self.assertTrue(hasattr(request, 'meta'))
        self.assertTrue(hasattr(request, 'db_uid'))
        self.assertTrue(hasattr(request, 'command'))
        self.assertTrue(hasattr(request, 'data'))

        self.assertEqual(request.db_uid, '123-456-789')
        self.assertEqual(request.command, 'PUT')
        self.assertEqual(request.data, ('key', 'value'))

    def test_valid_request_with_meta(self):
        request = msgpack.packb({
            'meta': {
                'test': 'test',
            },
            'uid': '123-456-789',
            'cmd': 'PUT',
            'args': ['key', 'value']
        })

        request = Request(request)
        self.assertIsNotNone(request)

        self.assertTrue(hasattr(request, 'meta'))
        self.assertTrue(hasattr(request, 'db_uid'))
        self.assertTrue(hasattr(request, 'command'))
        self.assertTrue(hasattr(request, 'data'))

        self.assertEqual(request.meta, {'test': 'test'})
        self.assertEqual(request.db_uid, '123-456-789')
        self.assertEqual(request.command, 'PUT')
        self.assertEqual(request.data, ('key', 'value'))


class ResponseTest(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_success_response_with_values(self):
        response = Response(id="1", status=SUCCESS_STATUS, datas=['thisistheres'])

        self.assertIsInstance(response, tuple)
        self.assertEqual(len(response), 2)

        unpacked_response = msgpack.unpackb(response[1])
        self.assertIsInstance(unpacked_response, dict)
        self.assertIn('meta', unpacked_response)
        self.assertIn('status', unpacked_response['meta'])
        self.assertIn('datas', unpacked_response)

        self.assertEqual(unpacked_response['meta']['status'], SUCCESS_STATUS)
        self.assertEqual(unpacked_response['datas'], ('thisistheres',))

    def test_failure_response_with_values(self):
        response = Response(id="1", status=FAILURE_STATUS, datas=[OS_ERROR, "this is the os error"])

        self.assertIsInstance(response, tuple)
        self.assertEqual(len(response), 2)

        unpacked_response = msgpack.unpackb(response[1])
        self.assertIsInstance(unpacked_response, dict)
        self.assertIn('meta', unpacked_response)
        self.assertIn('status', unpacked_response['meta'])
        self.assertIn('err_code', unpacked_response['meta'])
        self.assertIn('err_msg', unpacked_response['meta'])
        self.assertIn('datas', unpacked_response)

        self.assertEqual(unpacked_response['meta']['status'], FAILURE_STATUS)
        self.assertEqual(unpacked_response['meta']['err_code'], OS_ERROR)
        self.assertEqual(unpacked_response['datas'], ())

    @raises
    def test_success_response_without_values(self):
        response = Response(id="1")
