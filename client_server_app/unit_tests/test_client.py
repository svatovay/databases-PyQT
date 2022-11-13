import unittest
from client import create_presence, process_ans


class TestCreatePresenceFunction(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_dict_keys(self):
        self.assertEqual(tuple(create_presence('Ivan').keys()), ('action', 'time', 'user'))

    def test_action(self):
        self.assertEqual(create_presence('Ivan')['action'], 'presence')

    def test_account_name(self):
        self.assertEqual(create_presence('Ivan')['user']['account_name'], 'Ivan')


class TestProcessAnsFunction(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_raise_value_error(self):
        with self.assertRaises(ValueError):
            process_ans('test_message')
