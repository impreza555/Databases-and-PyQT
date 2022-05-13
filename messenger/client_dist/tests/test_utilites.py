import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.settings import USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from common.utilites import Encoder, Message

test_dict_send = {
    ACTION: PRESENCE,
    TIME: 111111.111111,
    USER: {
        ACCOUNT_NAME: 'test_test'
    }
}
test_dict_encoded = b'{"action": "presence", "time": 111111.111111, "user": {"account_name": "test_test"}}'


class TestSocket:
    def __init__(self, test_dict, dict_encoded):
        self.test_dict = test_dict
        self.dict_encoded = dict_encoded
        self.received_message = None

    def send(self, message_to_send):
        self.received_message = message_to_send
        return self.received_message

    def recv(self, max_len):
        self.max_len = max_len
        return self.dict_encoded


class TestUtilites(unittest.TestCase):
    def setUp(self):
        self.encoder = Encoder()
        self.message = Message()
        self.test_socket = TestSocket(test_dict_send, test_dict_encoded)

    def test_encode_message(self):
        self.assertEqual(self.encoder.encoding(test_dict_send), test_dict_encoded)

    def test_encode_error_value(self):
        self.assertRaises(ValueError, self.encoder.encoding, 'non_dict_data')

    def test_decode_message(self):
        self.assertEqual(self.encoder.decoding(test_dict_encoded), test_dict_send)

    def test_decode_error_json_loads(self):
        self.assertRaises(ValueError, self.encoder.encoding, 'non_byte_data')

    def test_get_message(self):
        self.assertEqual(self.message.get(self.test_socket), test_dict_send)

    def test_send_message(self):
        self.message.send(self.test_socket, test_dict_send)
        self.assertEqual(self.test_socket.received_message, test_dict_encoded)


if __name__ == '__main__':
    unittest.main()
