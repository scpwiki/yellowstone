import unittest

from yellowstone.utils import chunks, sql_array


class TestUtils(unittest.TestCase):
    def test_chunks(self):
        self.assertEqual(
            list(chunks(range(10), 2)),
            [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)],
        )

        self.assertEqual(
            list(chunks("abcdef", 3)),
            [("a", "b", "c"), ("d", "e", "f")],
        )

        self.assertEqual(
            list(chunks("ABCDEFG", 3)),
            [("A", "B", "C"), ("D", "E", "F"), ("G",)],
        )

    def test_sql_array(self):
        self.assertEqual(sql_array((3, 7, 9, 11)), "{3, 7, 9, 11}")
