import unittest2
import os
import json
import shutil

from elevator.db import DatabasesHandler


class DatabasesTest(unittest2.TestCase):
	def setUp(self):
		self.store = '/tmp/store.json'
		self.dest = '/tmp'
		self.handler = DatabasesHandler(self.store, self.dest)

	def tearDown(self):
		os.remove('/tmp/store.json')
		shutil.rmtree('/tmp/default')

	def test_init(self):
		self.assertIn('default', self.handler['index'])
		default_db_uid = self.handler['index']['default']

		self.assertIn(default_db_uid, self.handler['reverse_index'])
		self.assertEqual(self.handler['reverse_index'][default_db_uid], 'default')

		self.assertIn(default_db_uid, self.handler['paths_index'])
		self.assertEqual(self.handler['paths_index'][default_db_uid], '/tmp/default')

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

