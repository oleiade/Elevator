import unittest
import msgpack

from nose.tools import raises

from elevator.message import Request, Response, MessageFormatError

class RequestTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	@raises(MessageFormatError)
	def test_request_with_missing_arguments(self):
		request = msgpack.packb({
			'DB_UID': '123-456-789',
			'COMMAND': 'GET',
		})
		
		request = Request(request)

	def test_valid_request(self):
		request = msgpack.packb({
			'DB_UID': '123-456-789',
			'COMMAND': 'PUT',
			'ARGS': (
				'key',
				'value',
			)
		})

		request = Request(request)
		self.assertIsNotNone(request)

		self.assertTrue(hasattr(request, 'db_uid'))
		self.assertTrue(hasattr(request, 'command'))
		self.assertTrue(hasattr(request, 'data'))

		self.assertEqual(request.db_uid, '123-456-789')
		self.assertEqual(request.command, 'PUT')
		self.assertEqual(request.data, ('key', 'value'))


class ResponseTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_response_with_values(self):
		response = Response(id="1", status=-1, datas={'res': 'res'})

		self.assertIsInstance(response, tuple)
		self.assertEqual(len(response), 2)
		self.assertEqual(response[0], "1")

		unpacked_response = msgpack.unpackb(response[1])
		self.assertEqual(len(unpacked_response), 2)
		self.assertIsInstance(unpacked_response, dict)
		self.assertEqual(unpacked_response['STATUS'], -1)
		self.assertEqual(unpacked_response['DATAS'], {'res': 'res'})

	def test_response_without_values(self):
		response = Response(id="1")

		self.assertIsInstance(response, tuple)
		self.assertEqual(len(response), 2)
		self.assertEqual(response[0], "1")

		unpacked_response = msgpack.unpackb(response[1])
		self.assertIsInstance(unpacked_response, dict)
		self.assertEqual(len(unpacked_response), 2)
		self.assertEqual(unpacked_response['STATUS'], 0)
		self.assertIsNone(unpacked_response['DATAS'])
		