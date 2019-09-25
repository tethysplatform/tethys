import unittest
from unittest import mock

import bokeh.application.application as baa
from bokeh.document import Document

from django.contrib.auth.models import User
from django.http import HttpRequest
from tethys_apps.base.bokeh_handler import add_request_to_document


@add_request_to_document
def user_dec_bokeh_handler(doc: Document):
    return doc.request


class MockSessionContext(object):
    def __init__(self, doc):
        mock_bokeh_request = dict(user=mock.MagicMock(spec=User), scheme='http')

        self._document = doc
        self.status = None
        self.counter = 0
        self.request = mock_bokeh_request


class TestBokehHandler(unittest.TestCase):
    @mock.patch('tethys_apps.base.workspace._get_user_workspace')
    @mock.patch('tethys_apps.utilities.get_active_app')
    def test_app_bokeh_handler(self, _, __):
        app = baa.Application()
        doc = app.create_document()
        session_context = MockSessionContext(doc)
        doc._session_context = session_context

        ret = user_dec_bokeh_handler(doc)
        self.assertIsInstance(ret, HttpRequest)
