import unittest
from unittest.mock import patch

import requests

from yellowstone.request import site_members
from yellowstone.request.site_members import SiteMemberData

from .helpers import FakeResponse, make_wikidot


class TestSiteMembers(unittest.TestCase):
    def setUp(self):
        self.wikidot = make_wikidot()

    def test_site_members_regular(self):
        http_response = FakeResponse.ajax_from_file("site_members_regular")
        with patch.object(requests, "post", return_value=http_response) as mock_1:
            models = site_members.get(
                "scp-wiki",
                1,
                wikidot=self.wikidot,
                use_admin=False,
            )
            mock_1.assert_called_once()

        self.assertIsInstance(models, list)
        self.assertEquals(len(models), 6)
        self.assertIsInstance(models[0], SiteMemberData)
        self.assertEqual(models[0].name, "The Administrator")
        self.assertEqual(models[1].name, "Dr Gears")
        self.assertEqual(models[2].name, "Lee Byron")
        self.assertEqual(models[3].name, "Kain Pathos Crow")
        self.assertEqual(models[4].name, "Kraito")
        self.assertEqual(models[5].name, "Lt Masipag")

    def test_site_members_admin(self):
        # TODO add this when ADMIN_MEMBER_MODULE is working
        pass
