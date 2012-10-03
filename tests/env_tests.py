import unittest

from .fakers import get_test_env


class TestEnv(unittest.TestCase):
    def setUp(self):
        self.env = get_test_env()

    def tearDown(self):
        del self.env  # Singleton objects have to be explictly deleted


