import unittest
from unittest import mock
from tethys_portal.views.receivers import create_auth_token


class TethysPortalReceiversTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_portal.views.receivers.Token")
    def test_create_auth_token(self, mock_token):
        expected_sender = "foo"
        expected_created = True
        mock_instance = mock.MagicMock()

        create_auth_token(
            expected_sender, instance=mock_instance, created=expected_created
        )
        mock_token.objects.create.assert_called_with(user=mock_instance)

    @mock.patch("tethys_portal.views.receivers.Token")
    def test_create_auth_token_not_created(self, mock_token):
        expected_sender = "foo"
        expected_created = False
        mock_instance = mock.MagicMock()

        create_auth_token(
            expected_sender, instance=mock_instance, created=expected_created
        )
        mock_token.objects.create.assert_not_called()
