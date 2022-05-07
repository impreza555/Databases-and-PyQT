import os
import sys
import unittest

from common.utilites import arg_parser

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.settings import RESPONSE, ERROR, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import Client


class TestClass(unittest.TestCase):
    def setUp(self):
        attr = arg_parser('client')
        connect_address = attr.address
        connect_port = attr.port
        self.client = Client(connect_address, connect_port, 'Guest')

    def test_def_presense(self):
        test = self.client.presence()
        test[TIME] = 5.2
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 5.2, ACCOUNT_NAME: 'Guest'})

    def test_200_ans(self):
        self.assertEqual(self.client.response({RESPONSE: 200}), 'Соединение установлено')

    def test_400_ans(self):
        self.assertEqual(self.client.response({RESPONSE: 400, ERROR: 'Bad Request'}),
                         'Ошибка соединения с сервером: Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, self.client.response, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
