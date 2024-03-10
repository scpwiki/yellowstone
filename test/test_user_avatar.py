import unittest
from unittest.mock import patch

import requests

from yellowstone.request import user_avatar

from .helpers import FakeResponse


class TestUserAvatar(unittest.TestCase):
    def test_user_avatar(self):
        http_response = FakeResponse(b"foo")
        with patch.object(requests, "get", return_value=http_response) as mock:
            data = user_avatar.get(4598089)
            self.assertEqual(data, b"foo")
            mock.assert_called_once()
