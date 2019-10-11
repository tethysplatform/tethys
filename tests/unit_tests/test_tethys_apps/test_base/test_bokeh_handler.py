import unittest
from unittest import mock

import bokeh.application.application as baa
from bokeh.document import Document

from django.contrib.auth.models import User
from django.http import HttpRequest
from tethys_apps.base.bokeh_handler import with_request, with_workspaces


@with_request
def bokeh_to_http_request_handler(doc: Document):
    return doc.request


@with_workspaces
def add_workspaces_to_document_handler(doc: Document):
    return doc.user_workspace, doc.app_workspace


class MockSessionContext(object):
    def __init__(self, doc):
        mock_bokeh_request = dict(user=mock.MagicMock(spec=User), scheme='http')

        self._document = doc
        self.status = None
        self.counter = 0
        self.request = mock_bokeh_request


class TestBokehHandler(unittest.TestCase):
    def test_bokeh_to_http_request(self):
        app = baa.Application()
        doc = app.create_document()
        session_context = MockSessionContext(doc)
        doc._session_context = session_context

        ret = bokeh_to_http_request_handler(doc)
        self.assertIsInstance(ret, HttpRequest)

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_apps.base.workspace.log')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_user_workspace')
    def test_add_workspaces_to_document(self, _, __, ___, ____):
        app = baa.Application()
        doc = app.create_document()
        session_context = MockSessionContext(doc)
        doc._session_context = session_context

        ret = add_workspaces_to_document_handler(doc)
        self.assertIn('_get_user_workspace', ret[0].__repr__())
        self.assertIn('app_workspace', ret[1].__repr__())
