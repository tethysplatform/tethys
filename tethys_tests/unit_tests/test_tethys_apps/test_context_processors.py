import unittest
from unittest import mock

from django.db import models
from tethys_apps.context_processors import tethys_apps_context
from tethys_apps.models import TethysApp


class ContextProcessorsTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.context_processors.get_active_app')
    def test_tethys_apps_context(self, mock_get_active_app):
        mock_args = mock.MagicMock()
        app = TethysApp()
        app.id = 'foo.id'
        app.name = 'foo.name'
        app.icon = 'foo.icon'
        app.color = '#foobar'
        app.tags = 'tags'
        app.description = 'foo.description'
        app.enable_feedback = models.BooleanField(default=True)
        app.enable_feedback.value = False

        mock_get_active_app.return_value = app

        context = tethys_apps_context(mock_args)

        mock_get_active_app.assert_called_once()
        self.assertEqual('foo.id', context['tethys_app']['id'])
        self.assertEqual('foo.name', context['tethys_app']['name'])
        self.assertEqual('foo.icon', context['tethys_app']['icon'])
        self.assertEqual('#foobar', context['tethys_app']['color'])
        self.assertEqual('tags', context['tethys_app']['tags'])
        self.assertEqual('foo.description', context['tethys_app']['description'])
        self.assertFalse('enable_feedback' in context['tethys_app'])
        self.assertFalse('feedback_emails' in context['tethys_app'])

    @mock.patch('tethys_apps.context_processors.get_active_app')
    def test_tethys_apps_context_feedback(self, mock_get_active_app):
        mock_args = mock.MagicMock()
        app = TethysApp()
        app.id = 'foo.id'
        app.name = 'foo.name'
        app.icon = 'foo.icon'
        app.color = '#foobar'
        app.tags = 'tags'
        app.description = 'foo.description'
        app.enable_feedback = True
        app.feedback_emails.append('foo.feedback')

        mock_get_active_app.return_value = app

        context = tethys_apps_context(mock_args)

        mock_get_active_app.assert_called_once()
        self.assertEqual('foo.id', context['tethys_app']['id'])
        self.assertEqual('foo.name', context['tethys_app']['name'])
        self.assertEqual('foo.icon', context['tethys_app']['icon'])
        self.assertEqual('#foobar', context['tethys_app']['color'])
        self.assertEqual('tags', context['tethys_app']['tags'])
        self.assertEqual('foo.description', context['tethys_app']['description'])
        self.assertTrue('enable_feedback' in context['tethys_app'])
        self.assertTrue('feedback_emails' in context['tethys_app'])
        self.assertEqual(True, context['tethys_app']['enable_feedback'])
        self.assertEqual(['foo.feedback'], context['tethys_app']['feedback_emails'])
