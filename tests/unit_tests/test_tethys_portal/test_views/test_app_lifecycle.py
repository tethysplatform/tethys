import asyncio
from subprocess import CalledProcessError
from unittest.mock import patch, AsyncMock, MagicMock, mock_open as MockOpen
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User

import tethys_portal.views.app_lifecycle as app_lifecycle


class TestAppLifeCycle(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="top_secret"
        )
        self.user.is_staff = True
        self.user.save()

    @patch("tethys_portal.views.app_lifecycle.get_channel_layer")
    @patch("tethys_portal.views.app_lifecycle.unpatched_run")
    @patch("tethys_portal.views.app_lifecycle.run")
    @patch("tethys_portal.views.app_lifecycle.sleep")
    def test__execute_lifecycle_commands_success(
        self, mock_sleep, mock_run, mock_unpatched_run, mock_get_channel_layer
    ):
        mock_channel_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer
        mock_run.return_value.stdout = b"Successfully installed test_app"
        commands = [("echo test", "Restarting server...")]
        app_lifecycle._execute_lifecycle_commands("test_app", commands)
        self.assertTrue(mock_unpatched_run.called)
        mock_run.assert_called_once()
        mock_sleep.assert_called_once()

    @patch("tethys_portal.views.app_lifecycle.get_channel_layer")
    @patch("tethys_portal.views.app_lifecycle.unpatched_run")
    @patch("tethys_portal.views.app_lifecycle.run")
    @patch("tethys_portal.views.app_lifecycle.sleep")
    def test__execute_lifecycle_commands_called_process_error(
        self, mock_sleep, mock_run, mock_unpatched_run, mock_get_channel_layer
    ):
        mock_channel_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer
        mock_run.side_effect = CalledProcessError(returncode=999, cmd="test cmd")
        commands = [("echo test", "Whatever...")]
        app_lifecycle._execute_lifecycle_commands("test_app", commands)
        mock_run.assert_called_once()
        self.assertEqual(mock_unpatched_run.call_count, 2)
        mock_sleep.assert_not_called()

    @patch("tethys_portal.views.app_lifecycle.re")
    @patch("tethys_portal.views.app_lifecycle.get_channel_layer")
    @patch("tethys_portal.views.app_lifecycle.unpatched_run")
    @patch("tethys_portal.views.app_lifecycle.run")
    @patch("tethys_portal.views.app_lifecycle.sleep")
    def test__execute_lifecycle_commands_from_import(
        self, mock_sleep, mock_run, mock_unpatched_run, mock_get_channel_layer, mock_re
    ):
        mock_channel_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer
        mock_run.return_value.stdout = b"Successfully installed test_app"
        commands = [("echo test", "Restarting server...")]
        output = MagicMock(
            stdout="Successfully installed test_app into your active Tethys Portal."
        )
        mock_unpatched_run.return_value = output
        mock_match = MagicMock()
        mock_re.search.return_value = mock_match
        app_lifecycle._execute_lifecycle_commands(
            "test_app", commands, from_import=True
        )
        self.assertTrue(mock_unpatched_run.called)
        mock_run.assert_called_once()
        mock_sleep.assert_called_once()
        mock_re.search.assert_called_once()
        mock_match.group.assert_called_once_with(mock_match.lastindex)

    def test__execute_lifecycle_commands_cleanup_fails(self):
        cleanup = MagicMock()
        cleanup.side_effect = Exception()
        with (
            patch("tethys_portal.views.app_lifecycle.get_channel_layer"),
            patch("tethys_portal.views.app_lifecycle.unpatched_run"),
            patch("tethys_portal.views.app_lifecycle.run"),
        ):
            app_lifecycle._execute_lifecycle_commands(
                "test_app", [("echo", "msg")], cleanup=cleanup
            )
        cleanup.assert_called_once()

    def test__execute_lifecycle_commands_cleanup_not_callable(self):
        with self.assertRaises(ValueError):
            app_lifecycle._execute_lifecycle_commands(
                "test_app", [("echo", "msg")], cleanup="not_callable"
            )

    @patch("tethys_portal.views.app_lifecycle.AsyncWebsocketConsumer")
    def test_AppLifeCycleConsumer_connect_and_disconnect(self, mock_base):
        # Simulate scope and channel_layer
        consumer = app_lifecycle.AppLifeCycleConsumer()
        consumer.scope = {"url_route": {"kwargs": {"app_name": "foo"}}}
        consumer.channel_layer = AsyncMock()
        consumer.channel_name = "chan"
        # Test connect
        with patch.object(consumer, "accept", return_value=None) as mock_accept:
            self.loop_run(consumer.connect())
            consumer.channel_layer.group_add.assert_called_with("app_foo", "chan")
            mock_accept.assert_called_once()
        # Test disconnect
        self.loop_run(consumer.disconnect(1000))
        consumer.channel_layer.group_discard.assert_called_with("app_foo", "chan")

    @patch("tethys_portal.views.app_lifecycle.AsyncWebsocketConsumer")
    def test_AppLifeCycleConsumer_progress_message(self, mock_base):
        consumer = app_lifecycle.AppLifeCycleConsumer()
        consumer.send = AsyncMock()
        event = {"progress_metadata": {"foo": "bar"}}
        self.loop_run(consumer.progress_message(event))
        consumer.send.assert_called()

    def loop_run(self, coro):
        """Helper to run async coroutines in tests."""
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        return asyncio.get_event_loop().run_until_complete(coro)

    @patch("tethys_portal.views.app_lifecycle.render")
    @patch("tethys_portal.views.app_lifecycle.AppImportForm")
    @patch("tethys_portal.views.app_lifecycle.mkdtemp", return_value="/tmp/test")
    @patch("tethys_portal.views.app_lifecycle.Timer")
    def test_import_app_get(self, mock_timer, mock_mkdtemp, mock_form, mock_render):
        request = self.factory.get("/fake-url")
        request.user = self.user
        app_lifecycle.import_app(request)
        mock_render.assert_called()

    @patch("tethys_portal.views.app_lifecycle.render")
    @patch("tethys_portal.views.app_lifecycle.AppImportForm")
    @patch("tethys_portal.views.app_lifecycle.mkdtemp", return_value="/tmp/test")
    @patch("tethys_portal.views.app_lifecycle.Timer")
    @patch("tethys_portal.views.app_lifecycle.open", new_callable=MockOpen)
    @patch("tethys_portal.views.app_lifecycle.unpack_archive")
    @patch("tethys_portal.views.app_lifecycle.os")
    def test_import_app_post_valid_zip(
        self,
        mock_os,
        mock_unpack_archive,
        mock_open,
        mock_timer,
        mock_mkdtemp,
        mock_form,
        mock_render,
    ):
        mock_os.listdir.return_value = ["folder"]
        mock_zipfile = MockOpen()
        mock_zipfile.name = "test.zip"
        mock_zipfile.chunks = lambda: [r"foo", r"bar", r"baz"]
        mock_instance = MagicMock()
        mock_instance.is_valid.return_value = True
        mock_instance.cleaned_data = {"git_url": "", "zip_file": mock_zipfile}
        mock_form.return_value = mock_instance
        request = self.factory.post("/fake-url", {"zip_file": MockOpen()})
        request.user = self.user
        app_lifecycle.import_app(request)
        mock_render.assert_called_once()

    @patch("tethys_portal.views.app_lifecycle.render")
    @patch("tethys_portal.views.app_lifecycle.AppImportForm")
    @patch("tethys_portal.views.app_lifecycle.mkdtemp", return_value="/tmp/test")
    @patch("tethys_portal.views.app_lifecycle.Timer")
    def test_import_app_post_valid_git(
        self, mock_timer, mock_mkdtemp, mock_form, mock_render
    ):
        mock_instance = MagicMock()
        mock_instance.is_valid.return_value = True
        mock_instance.cleaned_data = {
            "git_url": "https://github.com/test/repo.git",
            "zip_file": None,
        }
        mock_form.return_value = mock_instance
        request = self.factory.post("/fake-url", {})
        request.user = self.user
        app_lifecycle.import_app(request)
        mock_render.assert_called()

    @patch("tethys_portal.views.app_lifecycle.render")
    @patch("tethys_portal.views.app_lifecycle.AppScaffoldForm")
    @patch("tethys_portal.views.app_lifecycle.Timer")
    def test_create_app_get(self, mock_timer, mock_form, mock_render):
        request = self.factory.get("/fake-url")
        request.user = self.user
        app_lifecycle.create_app(request)
        mock_render.assert_called()

    @patch("tethys_portal.views.app_lifecycle.render")
    @patch("tethys_portal.views.app_lifecycle.AppScaffoldForm")
    @patch("tethys_portal.views.app_lifecycle.Timer")
    def test_create_app_post_valid(self, mock_timer, mock_form, mock_render):
        mock_instance = MagicMock()
        mock_instance.is_valid.return_value = True
        mock_instance.cleaned_data = {
            "scaffold_template": "default",
            "project_name": "proj",
            "app_name": "App Name",
            "description": "desc",
            "app_theme_color": "#fff",
            "tags": "tag",
            "author": "author",
            "author_email": "author@email.com",
            "license": "MIT",
        }
        mock_form.return_value = mock_instance
        request = self.factory.post("/fake-url", {})
        request.user = self.user
        app_lifecycle.create_app(request)
        mock_render.assert_called()

    @patch("tethys_portal.views.app_lifecycle.render")
    @patch("tethys_portal.views.app_lifecycle.get_app_class")
    @patch("tethys_portal.views.app_lifecycle.TethysApp")
    @patch("tethys_portal.views.app_lifecycle.Timer")
    def test_remove_app_get(
        self, mock_timer, mock_tethysapp, mock_get_app_class, mock_render
    ):
        mock_app = MagicMock()
        mock_app.name = "App"
        mock_app.package = "app_pkg"
        mock_get_app_class.return_value = mock_app
        mock_tethysapp.objects.get.return_value = MagicMock()
        request = self.factory.get("/fake-url")
        request.user = self.user
        app_lifecycle.remove_app(request, 1)
        mock_render.assert_called()

    @patch("tethys_portal.views.app_lifecycle.render")
    @patch("tethys_portal.views.app_lifecycle.get_app_class")
    @patch("tethys_portal.views.app_lifecycle.TethysApp")
    @patch("tethys_portal.views.app_lifecycle.Timer")
    def test_remove_app_post(
        self, mock_timer, mock_tethysapp, mock_get_app_class, mock_render
    ):
        mock_app = MagicMock()
        mock_app.name = "App"
        mock_app.package = "app_pkg"
        mock_get_app_class.return_value = mock_app
        mock_tethysapp.objects.get.return_value = MagicMock()
        request = self.factory.post("/fake-url")
        request.user = self.user
        app_lifecycle.remove_app(request, 1)
        mock_render.assert_called()
        mock_timer.assert_called_once_with(
            1,
            app_lifecycle._execute_lifecycle_commands,
            args=[
                mock_app.package,
                [
                    (
                        "tethys uninstall -f app_pkg",
                        "Removing app from Tethys Portal...",
                    ),
                    (
                        app_lifecycle.TOUCH_COMMAND,
                        "Restarting server...",
                    ),
                ],
            ],
        )

    @patch("tethys_portal.views.app_lifecycle.asyncio")
    @patch("tethys_portal.views.app_lifecycle.hasattr")
    def test_unpatched_run_asyncio_has_runner(self, mock_hasattr, mock_asyncio):
        mock_hasattr.return_value = True
        mock_main = MagicMock()
        app_lifecycle.unpatched_run(mock_main)
        mock_asyncio.Runner.assert_called_once()
        mock_asyncio.Runner.return_value.__enter__.return_value.run.assert_called_once_with(
            mock_main
        )

    @patch("tethys_portal.views.app_lifecycle.asyncio")
    @patch("tethys_portal.views.app_lifecycle.hasattr")
    def test_unpatched_asyncio_missing_runner(self, mock_hasattr, mock_asyncio):
        mock_hasattr.return_value = False
        mock_main = MagicMock()
        app_lifecycle.unpatched_run(mock_main)
        mock_asyncio.run.assert_called_once_with(mock_main)
