import pytest
import unittest
from unittest import mock

from tethys_apps.models import ProxyApp, TethysApp
from tethys_apps.views import (
    library,
    handoff_capabilities,
    handoff,
    send_beta_feedback_email,
)


class TethysAppsViewsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_apps.views.render")
    @mock.patch("tethys_apps.views.TethysApp")
    @mock.patch("tethys_apps.views.ProxyApp")
    @pytest.mark.django_db
    def test_library_staff(self, mock_ProxyApp, mock_TethysApp, mock_render):
        mock_request = mock.MagicMock()
        mock_request.user.is_staff = True

        mock_app1 = mock.MagicMock(spec=TethysApp, name="app1", order=0)
        mock_app1.configured = True
        mock_app2 = mock.MagicMock(spec=TethysApp, name="app2", order=1)
        mock_app2.configured = False
        mock_TethysApp.objects.all.return_value = [mock_app1, mock_app2]

        mock_proxy_app1 = mock.MagicMock(spec=ProxyApp, name="aa_proxy", order=0)
        mock_ProxyApp.objects.all.return_value = [mock_proxy_app1]

        # configure mock objects so they can be sorted
        for app in (mock_app1, mock_app2, mock_proxy_app1):
            app.__lt__ = lambda s, o: s.order < o.order
            app.name = app._extract_mock_name()

        mock_render.return_value = True

        ret = library(mock_request)

        self.assertEqual(ret, mock_render.return_value)
        mock_TethysApp.objects.all.assert_called_once()
        mock_ProxyApp.objects.all.assert_called_once()

        # Unconfigured apps shown to staff users
        expected_context = {
            "apps": {
                "configured": [mock_proxy_app1, mock_app1],
                "unconfigured": [mock_app2],
            }
        }
        mock_render.assert_called_with(
            mock_request, "tethys_apps/app_library.html", expected_context
        )

    @mock.patch("tethys_apps.views.get_custom_template", return_value="mock_template")
    @mock.patch("tethys_apps.views.render")
    @mock.patch("tethys_apps.views.TethysApp")
    @mock.patch("tethys_apps.views.ProxyApp")
    def test_library_not_staff(
        self, mock_ProxyApp, mock_TethysApp, mock_render, mock_get_template
    ):
        mock_request = mock.MagicMock()
        mock_request.user.is_staff = False

        mock_app1 = mock.MagicMock(spec=TethysApp, name="app1", order=2)
        mock_app1.configured = True
        mock_app2 = mock.MagicMock(spec=TethysApp, name="app2", order=1)
        mock_app2.configured = False
        mock_TethysApp.objects.all.return_value = [mock_app1, mock_app2]

        mock_proxy_app1 = mock.MagicMock(spec=ProxyApp, name="proxy", order=1)
        mock_ProxyApp.objects.all.return_value = [mock_proxy_app1]

        mock_render.return_value = True

        # configure mock objects so they can be sorted
        for app in (mock_app1, mock_app2, mock_proxy_app1):
            app.__lt__ = lambda s, o: s.order < o.order
            app.name = app._extract_mock_name()

        ret = library(mock_request)
        self.assertEqual(ret, mock_render.return_value)
        mock_TethysApp.objects.all.assert_called_once()
        mock_ProxyApp.objects.all.assert_called_once()

        # Unconfigured apps hidden to non-staff users
        expected_context = {
            "apps": {"configured": [mock_proxy_app1, mock_app1], "unconfigured": []}
        }
        mock_render.assert_called_with(mock_request, "mock_template", expected_context)
        mock_get_template.assert_called_once()

    @mock.patch("tethys_apps.views.HttpResponse")
    @mock.patch("tethys_apps.views.TethysAppBase")
    def test_handoff_capabilities(self, mock_app_base, mock_http_response):
        mock_request = mock.MagicMock()
        mock_app_name = "foo-app"
        mock_manager = mock.MagicMock()
        mock_handlers = mock.MagicMock()
        mock_app_base.get_handoff_manager.return_value = mock_manager
        mock_manager.get_capabilities.return_value = mock_handlers
        mock_http_response.return_value = True

        ret = handoff_capabilities(mock_request, mock_app_name)
        self.assertTrue(ret)
        mock_app_base.get_handoff_manager.assert_called_once()
        mock_manager.get_capabilities.assert_called_once_with(
            "foo_app", external_only=True, jsonify=True
        )
        mock_http_response.assert_called_once_with(
            mock_handlers, content_type="application/javascript"
        )

    @mock.patch("tethys_apps.views.TethysAppBase")
    def test_handoff(self, mock_app_base):
        mock_request = mock.MagicMock()
        mock_request_dict = mock.MagicMock()
        mock_request.GET.dict.return_value = mock_request_dict
        mock_app_name = "foo-app"
        mock_handler_name = "foo_handler"
        mock_manager = mock.MagicMock()
        mock_app_base.get_handoff_manager.return_value = mock_manager
        mock_manager.handoff.return_value = True

        ret = handoff(mock_request, mock_app_name, mock_handler_name)
        self.assertTrue(ret)
        mock_app_base.get_handoff_manager.assert_called_once()
        mock_manager.handoff.assert_called_once_with(
            mock_request, mock_handler_name, "foo_app"
        )
        mock_request.GET.dict.assert_called_once()

    @mock.patch("tethys_apps.views.JsonResponse")
    @mock.patch("tethys_apps.views.get_active_app")
    def test_send_beta_feedback_email_app_none(
        self, mock_get_active_app, mock_json_response
    ):
        mock_request = mock.MagicMock()
        mock_post = mock.MagicMock()
        mock_request.POST = mock_post
        mock_post.get.return_value = "http://foo/beta"
        mock_get_active_app.return_value = None
        mock_json_response.return_value = True

        ret = send_beta_feedback_email(mock_request)
        self.assertTrue(ret)
        mock_post.get.assert_called_once_with("betaFormUrl")
        mock_get_active_app.assert_called_once_with(url="http://foo/beta")
        mock_json_response.assert_called_once_with(
            {
                "success": False,
                "error": "App not found or feedback_emails not defined in app.py",
            }
        )

    @mock.patch("tethys_apps.views.send_mail")
    @mock.patch("tethys_apps.views.JsonResponse")
    @mock.patch("tethys_apps.views.get_active_app")
    def test_send_beta_feedback_email_send_mail(
        self, mock_get_active_app, mock_json_response, mock_send_mail
    ):
        mock_request = mock.MagicMock()
        mock_post = mock.MagicMock()
        mock_app = mock.MagicMock()
        mock_app.feedback_emails = "foo@feedback.foo"
        mock_app.name = "foo_name"
        mock_request.POST = mock_post
        mock_post.get.side_effect = [
            "http://foo/beta",
            "foo_betaUser",
            "foo_betaSubmitLocalTime",
            "foo_betaSubmitUTCOffset",
            "foo_betaFormUrl",
            "foo_betaFormUserAgent",
            "foo_betaFormVendor",
            "foo_betaUserComments",
        ]
        mock_get_active_app.return_value = mock_app
        mock_json_response.return_value = True
        mock_send_mail.return_value = True

        ret = send_beta_feedback_email(mock_request)
        self.assertTrue(ret)
        mock_post.get.assert_any_call("betaFormUrl")
        mock_get_active_app.assert_called_once_with(url="http://foo/beta")
        mock_post.get.assert_any_call("betaUser")
        mock_post.get.assert_any_call("betaSubmitLocalTime")
        mock_post.get.assert_any_call("betaSubmitUTCOffset")
        mock_post.get.assert_any_call("betaFormUrl")
        mock_post.get.assert_any_call("betaFormUserAgent")
        mock_post.get.assert_any_call("betaFormVendor")
        mock_post.get.assert_called_with("betaUserComments")
        expected_subject = "User Feedback for {0}".format(mock_app.name.encode("utf-8"))
        expected_message = (
            "User: {0}\n"
            "User Local Time: {1}\n"
            "UTC Offset in Hours: {2}\n"
            "App URL: {3}\n"
            "User Agent: {4}\n"
            "Vendor: {5}\n"
            "Comments:\n"
            "{6}".format(
                "foo_betaUser",
                "foo_betaSubmitLocalTime",
                "foo_betaSubmitUTCOffset",
                "foo_betaFormUrl",
                "foo_betaFormUserAgent",
                "foo_betaFormVendor",
                "foo_betaUserComments",
            )
        )
        mock_send_mail.assert_called_once_with(
            expected_subject,
            expected_message,
            from_email=None,
            recipient_list=mock_app.feedback_emails,
        )
        mock_json_response.assert_called_once_with(
            {"success": True, "result": "Emails sent to specified developers"}
        )

    @mock.patch("tethys_apps.views.send_mail")
    @mock.patch("tethys_apps.views.JsonResponse")
    @mock.patch("tethys_apps.views.get_active_app")
    def test_send_beta_feedback_email_send_mail_exception(
        self, mock_get_active_app, mock_json_response, mock_send_mail
    ):
        mock_request = mock.MagicMock()
        mock_post = mock.MagicMock()
        mock_app = mock.MagicMock()
        mock_app.feedback_emails = "foo@feedback.foo"
        mock_app.name = "foo_name"
        mock_request.POST = mock_post
        mock_post.get.side_effect = [
            "http://foo/beta",
            "foo_betaUser",
            "foo_betaSubmitLocalTime",
            "foo_betaSubmitUTCOffset",
            "foo_betaFormUrl",
            "foo_betaFormUserAgent",
            "foo_betaFormVendor",
            "foo_betaUserComments",
        ]
        mock_get_active_app.return_value = mock_app
        mock_json_response.return_value = False
        mock_send_mail.side_effect = Exception("foo_error")

        ret = send_beta_feedback_email(mock_request)
        self.assertFalse(ret)
        mock_post.get.assert_any_call("betaFormUrl")
        mock_get_active_app.assert_called_once_with(url="http://foo/beta")
        mock_post.get.assert_any_call("betaUser")
        mock_post.get.assert_any_call("betaSubmitLocalTime")
        mock_post.get.assert_any_call("betaSubmitUTCOffset")
        mock_post.get.assert_any_call("betaFormUrl")
        mock_post.get.assert_any_call("betaFormUserAgent")
        mock_post.get.assert_any_call("betaFormVendor")
        mock_post.get.assert_called_with("betaUserComments")
        expected_subject = "User Feedback for {0}".format(mock_app.name.encode("utf-8"))
        expected_message = (
            "User: {0}\n"
            "User Local Time: {1}\n"
            "UTC Offset in Hours: {2}\n"
            "App URL: {3}\n"
            "User Agent: {4}\n"
            "Vendor: {5}\n"
            "Comments:\n"
            "{6}".format(
                "foo_betaUser",
                "foo_betaSubmitLocalTime",
                "foo_betaSubmitUTCOffset",
                "foo_betaFormUrl",
                "foo_betaFormUserAgent",
                "foo_betaFormVendor",
                "foo_betaUserComments",
            )
        )
        mock_send_mail.assert_called_once_with(
            expected_subject,
            expected_message,
            from_email=None,
            recipient_list=mock_app.feedback_emails,
        )
        mock_json_response.assert_called_once_with(
            {"success": False, "error": "Failed to send email: foo_error"}
        )
