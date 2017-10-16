import requests
import json
from httmock import urlmatch, HTTMock, response
from unittest.mock import MagicMock

from django.test import TestCase

from mspray.apps.warehouse.utils import flatten, requests_retry_session
from mspray.apps.warehouse.utils import send_request


@urlmatch(netloc=r'(.*\.)?mosh\.com$')
def good_connection(url, request):
    headers = {'content-type': 'application/json'}
    content = {'success': True}
    return response(200, content, headers, None, 5, request)


def connection_error(*args, **kwargs):
    raise requests.exceptions.ConnectionError


def invalid_url(*args, **kwargs):
    raise requests.exceptions.InvalidURL


class TestUtils(TestCase):

    def connection_error():
        raise requests.exceptions.ConnectionError

    def test_flatten(self):
        test = {'a': 1, 'c': {'a': 2, 'b': {'x': 5, 'y': 10}}, 'd': [1, 2, 3]}
        flattened = flatten(test)
        expected = {'a': 1, 'c__a': 2, 'c__b__x': 5, 'c__b__y': 10, 'd':
                    [1, 2, 3]}
        self.assertEqual(flattened, expected)

    def test_good_connection(self):
        # try something that works
        with HTTMock(good_connection):
            r = requests_retry_session().get('https://www.mosh.com')
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json().get('success'))

    def test_connection_error(self):
        # test connection error
        requests.get = MagicMock(side_effect=connection_error)
        with self.assertRaises(requests.exceptions.ConnectionError):
            resp = requests_retry_session().get('http://localhost:99999999')
            self.assertEqual(resp, {'request_error': 'ConnectionTimeout'})

    def test_invalid_url(self):
        # test connection error
        requests.get = MagicMock(side_effect=invalid_url)
        with self.assertRaises(requests.exceptions.InvalidURL):
            resp = requests_retry_session().get('http://localhost:wth')
            self.assertEqual(resp, {'request_error': 'InvalidURL'})

    def test_send_request(self):
        with HTTMock(good_connection):
            result = send_request(json.dumps([]), 'https://www.mosh.com')
            self.assertTrue(result['success'])

    def test_bad_send_request(self):
        send_request = MagicMock(side_effect=connection_error)
        with self.assertRaises(requests.exceptions.ConnectionError):
            resp = send_request(json.dumps([]), 'http://localhost:99999999')
            self.assertEqual(resp, {'request_error': 'ConnectionTimeout'})

    def test_invalid_send_request(self):
        send_request = MagicMock(side_effect=invalid_url)
        with self.assertRaises(requests.exceptions.InvalidURL):
            resp = send_request(json.dumps([]), 'http://localhost:wth')
            self.assertEqual(resp, {'request_error': 'ConnectionTimeout'})
