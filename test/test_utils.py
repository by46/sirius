import unittest

from sirius.utils import group
from sirius.utils import parse_list


class UtilsTestCase(unittest.TestCase):
    def test_group(self):
        groups = list(group([1, 2, 3, 4, 5], 2))
        self.assertListEqual([(1, 2), (3, 4)], groups)

        groups = list(group([1, 2, 3, 4, 5, 6], 2))
        self.assertListEqual([(1, 2), (3, 4), (5, 6)], groups)

        groups = list(group([1, 2, 3, 4, 5, 6], 3))
        self.assertListEqual([(1, 2, 3), (4, 5, 6)], groups)

        groups = list(group([1, 2, 3, 4, 5, 6], 10))
        self.assertListEqual([], groups)

    def test_parse_list(self):
        self.assertListEqual(["1", "2", "3"], parse_list("1;2;3"))
        self.assertListEqual(["1", "2", "3"], parse_list("1,2,3", delimiter=','))
        self.assertListEqual([''], parse_list(""))
        self.assertListEqual([], parse_list(None))
        self.assertListEqual(['', ''], parse_list(';'))
