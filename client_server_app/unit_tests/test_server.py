import unittest
from server import process_client_message


class TestProcessClientMessageFunction(unittest.TestCase):
    def setUp(self) -> None:
        self.test_request_ok = {
            'action': 'presence',
            'time': '1665905571.378162',
            'user': {
                'account_name': 'Guest'
            }
        }

        self.test_bad_request = {
            'test_message': 'test_message'
        }

    def tearDown(self) -> None:
        pass

    def test_response_ok(self):
        self.assertEqual(process_client_message(self.test_request_ok), {'response': 200})

    def test_response_bad_request(self):
        self.assertEqual(process_client_message(self.test_bad_request), {'response': 400, 'error': 'Bad Request'})
