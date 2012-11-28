from __future__ import absolute_import

import unittest2
import msgpack

from nose.tools import raises

from elevator.message import Request, ResponseContent,\
                             ResponseHeader, MessageFormatError
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


class ResponseContentTest(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_success_response_with_values(self):
        response = ResponseContent(datas=['thisistheres'])
        unpacked_response = msgpack.unpackb(response)
        self.assertIsInstance(unpacked_response, dict)
        self.assertIn('datas', unpacked_response)
        self.assertEqual(unpacked_response['datas'], ('thisistheres',))

    @raises
    def test_success_response_without_values(self):
        ResponseContent()


class ResponseHeaderTest(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_success_header(self):
        header = ResponseHeader(status=SUCCESS_STATUS)
        unpacked_header = msgpack.unpackb(header)

        self.assertIsInstance(unpacked_header, dict)
        self.assertIn('status', unpacked_header)
        self.assertIn('err_code', unpacked_header)
        self.assertIn('err_msg', unpacked_header)
        self.assertEqual(unpacked_header['status'], SUCCESS_STATUS)
        self.assertIsNone(unpacked_header['err_code'], None)
        self.assertIsNone(unpacked_header['err_msg'], None)
