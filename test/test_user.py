import unittest
from unittest.mock import patch

import requests

from yellowstone.request import user
from yellowstone.request.user import UserData

from .helpers import FakeResponse, make_wikidot


class TestUser(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_user(self):
        user_id = 4598089
        http_response = FakeResponse.ajax_from_file("user_info_win")
        with patch.object(requests, "post", return_value=http_response) as mock:
            model = user.get(user_id, wikidot=self.wikidot)
            mock.assert_called_once()

        self.assertIsInstance(model, UserData)
        self.assertEqual(model.id, user_id)
        self.assertEqual(model.slug, "aismallard")
        self.assertEqual(model.name, "aismallard")
        self.assertEqual(model.gender, "female")
        self.assertIsNone(model.birthday)
        self.assertIsNone(model.location)
        self.assertIsNone(model.bio)
        self.assertEqual(model.karma, 5)
