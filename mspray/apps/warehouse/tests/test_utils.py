from django.test import TestCase

from mspray.apps.warehouse.utils import flatten


class TestUtils(TestCase):

    def test_flatten(self):
        test = {'a': 1, 'c': {'a': 2, 'b': {'x': 5, 'y': 10}}, 'd': [1, 2, 3]}
        flattened = flatten(test)
        expected = {'a': 1, 'c__a': 2, 'c__b__x': 5, 'c__b__y': 10, 'd':
                    [1, 2, 3]}
        self.assertEqual(flattened, expected)
