import unittest
from unittest import mock

import bokeh.application.application as baa
from bokeh.document import Document

from django.contrib.auth.models import User
from django.http import HttpRequest
from tethys_apps.base.bokeh_handler import with_request, with_workspaces


@with_request
def with_request_decorated(doc: Document):
    return doc


@with_workspaces
def with_workspaces_decorated(doc: Document):
    return doc


class TestBokehHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.app = baa.Application()
        self.doc = self.app.create_document()
        self.doc._session_context = self.make_session_context(self.doc)

    def make_session_context(self, doc):
        mock_session_context = mock.MagicMock(
            return_value=mock.MagicMock(
                _document=doc,
                status=None,
                counter=0,
                request=dict(
                    user=mock.MagicMock(spec=User),
                    scheme='http'
                )
            )
        )
        return mock_session_context

    def test_with_request_decorator(self):
        ret_doc = with_request_decorated(self.doc)

        self.assertIsNotNone(getattr(ret_doc, 'request', None))
        self.assertIsNotNone(getattr(ret_doc.request, 'user', None))
        self.assertIsInstance(ret_doc.request, HttpRequest)

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_apps.base.workspace.log')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_user_workspace')
    @mock.patch('tethys_apps.base.workspace._get_app_workspace')
    def test_with_workspaces_decorator(self, mock_gaw, mock_guw, _, __, ___):
        mock_guw.return_value = 'user-workspace'
        mock_gaw.return_value = 'app-workspace'

        ret_doc = with_workspaces_decorated(self.doc)
        self.assertIsNotNone(getattr(ret_doc, 'user_workspace', None))
        self.assertIsNotNone(getattr(ret_doc, 'app_workspace', None))
        self.assertEqual('user-workspace', ret_doc.user_workspace)
        self.assertEqual('app-workspace', ret_doc.app_workspace)
