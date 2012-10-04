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
		response = Response(id="1", status=-1, datas=['res'])

		self.assertIsInstance(response, tuple)
		self.assertEqual(len(response), 2)
		self.assertEqual(response[0], "1")

		unpacked_response = msgpack.unpackb(response[1])
		self.assertEqual(len(unpacked_response), 2)
		self.assertIsInstance(unpacked_response, dict)
		self.assertEqual(unpacked_response['STATUS'], -1)
		self.assertEqual(unpacked_response['DATAS'], ('res', ))

	def test_response_without_values(self):
		response = Response(id="1")

		self.assertIsInstance(response, tuple)
		self.assertEqual(len(response), 2)
		self.assertEqual(response[0], "1")

		unpacked_response = msgpack.unpackb(response[1])
		self.assertIsInstance(unpacked_response, dict)
		self.assertEqual(len(unpacked_response), 2)
		self.assertEqual(unpacked_response['STATUS'], 0)
		self.assertIsNotNone(unpacked_response['DATAS'])
		self.assertIsInstance(unpacked_response['DATAS'], tuple)

	def test_response_with_non_list_or_tuple_input_datas(self):
		first_response = Response(id="1", status=1, datas={'res': 'res'})
		second_response = Response(id="2", status=1, datas='unicodetest')

		self.assertIsInstance(first_response, tuple)
		self.assertIsInstance(second_response, tuple)
		self.assertEqual(len(first_response), 2)
		self.assertEqual(len(second_response), 2)
		self.assertEqual(first_response[0], "1")
		self.assertEqual(second_response[0], "2")

		first_unpacked_response = msgpack.unpackb(first_response[1])
		second_unpacked_response = msgpack.unpackb(second_response[1])

		self.assertEqual(len(first_unpacked_response), 2)
		self.assertEqual(len(second_unpacked_response), 2)
		self.assertIsInstance(first_unpacked_response, dict)
		self.assertIsInstance(second_unpacked_response, dict)
		self.assertEqual(first_unpacked_response['STATUS'], 1)
		self.assertEqual(second_unpacked_response['STATUS'], 1)
		self.assertEqual(first_unpacked_response['DATAS'], ({'res': 'res'}, ))
		self.assertEqual(second_unpacked_response['DATAS'], ('unicodetest', ))

