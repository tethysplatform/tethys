from pathlib import Path
from unittest import mock

from django.test import TestCase, override_settings
from tethys_cli.paths_commands import add_file_to_path, get_path


class TestPathsCommandGetPath(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from tethys_apps.models import TethysApp

        self.app = TethysApp.objects.create(
            name="An App",
            package="an_app",
        )
        self.app.save()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="test_user", email="testuser@example.com", password="testpassword"
        )
        self.user.save()

    @override_settings(USE_OLD_WORKSPACES_API=True)
    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace_old")
    def test_app_workspace_old(self, mock_gaw, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_app_workspace_path"
        mock_gaw.return_value = mock_return
        args = mock.MagicMock(type="app_workspace", app=self.app.package)
        get_path(args)
        mock_gaw.assert_called_with(self.app, bypass_quota=True)
        mock_wi.assert_called_with(f"App Workspace for app '{self.app.package}':")
        mock_wm.assert_called_with("test_app_workspace_path")

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace")
    def test_app_workspace(self, mock_gaw, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_app_workspace_path"
        mock_gaw.return_value = mock_return
        args = mock.MagicMock(type="app_workspace", app=self.app.package)
        get_path(args)
        mock_gaw.assert_called_with(self.app, bypass_quota=True)
        mock_wi.assert_called_with(f"App Workspace for app '{self.app.package}':")
        mock_wm.assert_called_with("test_app_workspace_path")

    @override_settings(USE_OLD_WORKSPACES_API=True)
    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands._get_user_workspace_old")
    def test_user_workspace_old(self, mock_guw, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_user_workspace_path"
        mock_guw.return_value = mock_return
        args = mock.MagicMock(
            type="user_workspace", app=self.app.package, user=self.user
        )
        get_path(args)
        mock_guw.assert_called_with(self.app, self.user, bypass_quota=True)
        mock_wi.assert_called_with(
            f"User Workspace for user '{self.user.username}' and app '{self.app.package}':"
        )
        mock_wm.assert_called_with("test_user_workspace_path")

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands._get_user_workspace")
    def test_user_workspace(self, mock_guw, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_user_workspace_path"
        mock_guw.return_value = mock_return
        args = mock.MagicMock(
            type="user_workspace", app=self.app.package, user=self.user
        )
        get_path(args)
        mock_guw.assert_called_with(self.app, self.user, bypass_quota=True)
        mock_wi.assert_called_with(
            f"User Workspace for user '{self.user.username}' and app '{self.app.package}':"
        )
        mock_wm.assert_called_with("test_user_workspace_path")

    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands._get_app_media")
    def test_app_media(self, mock_gam, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_app_media_path"
        mock_gam.return_value = mock_return
        args = mock.MagicMock(type="app_media", app=self.app.package)
        get_path(args)
        mock_gam.assert_called_with(self.app, bypass_quota=True)
        mock_wi.assert_called_with(f"App Media for app '{self.app.package}':")
        mock_wm.assert_called_with("test_app_media_path")

    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands._get_user_media")
    def test_user_media(self, mock_gum, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_user_media_path"
        mock_gum.return_value = mock_return
        args = mock.MagicMock(type="user_media", app=self.app.package, user=self.user)
        get_path(args)
        mock_gum.assert_called_with(self.app, self.user, bypass_quota=True)
        mock_wi.assert_called_with(
            f"User Media for user '{self.user.username}' and app '{self.app.package}':"
        )
        mock_wm.assert_called_with("test_user_media_path")

    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands.get_app_public")
    def test_app_public(self, mock_gap, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_app_public_path"
        mock_gap.return_value = mock_return
        args = mock.MagicMock(type="app_public", app=self.app.package)
        get_path(args)
        mock_gap.assert_called_with(self.app)
        mock_wi.assert_called_with(f"App Public for app '{self.app.package}':")
        mock_wm.assert_called_with("test_app_public_path")

    @mock.patch("tethys_cli.paths_commands.write_info")
    @mock.patch("tethys_cli.paths_commands.write_msg")
    @mock.patch("tethys_cli.paths_commands.get_app_resources")
    def test_app_resources(self, mock_gar, mock_wm, mock_wi):
        mock_return = mock.MagicMock()
        mock_return.path = "test_app_resources_path"
        mock_gar.return_value = mock_return
        args = mock.MagicMock(type="app_resources", app=self.app.package)
        get_path(args)
        mock_gar.assert_called_with(self.app)
        mock_wi.assert_called_with(f"App Resources for app '{self.app.package}':")
        mock_wm.assert_called_with("test_app_resources_path")

    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_no_user_provided_for_user_workspace(self, mock_we):
        args = mock.MagicMock(type="user_workspace", app=self.app.package, user=None)
        get_path(args)
        mock_we.assert_called_with(
            "The '--user' argument is required for path type 'user_workspace'."
        )

    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_no_user_provided_for_user_media(self, mock_we):
        args = mock.MagicMock(type="user_media", app=self.app.package, user=None)
        get_path(args)
        mock_we.assert_called_with(
            "The '--user' argument is required for path type 'user_media'."
        )

    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_invalid_path_type(self, mock_we):
        args = mock.MagicMock(type="invalid_path_type", app=self.app.package)
        get_path(args)
        mock_we.assert_called_with("Invalid path type: 'invalid_path_type'.")

    @mock.patch("tethys_cli.paths_commands.write_warning")
    def test_user_not_found(self, mock_ww):
        args = mock.MagicMock(
            type="user_workspace", app=self.app.package, user="nonexistent_user"
        )
        get_path(args)
        mock_ww.assert_called_with("User 'nonexistent_user' was not found.")

    @mock.patch("tethys_cli.paths_commands.write_warning")
    def test_app_not_found(self, mock_ww):
        args = mock.MagicMock(type="app_workspace", app="nonexistent_app")
        get_path(args)
        mock_ww.assert_called_with("Tethys app 'nonexistent_app' is not installed.")

    @mock.patch("tethys_cli.paths_commands.write_error")
    @mock.patch("tethys_cli.paths_commands.resolve_path")
    def test_path_not_found(self, mock_resolve_path, mock_we):
        mock_resolve_path.return_value = None
        args = mock.MagicMock(type="app_workspace", app=self.app.package)
        get_path(args)
        mock_we.assert_called_with("Could not find App Workspace.")


class TestPathsCommandAddFileToPath(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from tethys_apps.models import TethysApp

        self.app = TethysApp.objects.create(
            name="An App",
            package="an_app",
        )
        self.app.save()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="test_user", email="testuser@example.com", password="testpassword"
        )
        self.user.save()

    @override_settings(USE_OLD_WORKSPACES_API=True)
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands.shutil.copy")
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace_old")
    @mock.patch("tethys_cli.paths_commands.write_success")
    def test_add_app_workspace_old(
        self, mock_wr, mock_gaw, mock_gra, mock_caf, mock_copy, mock_path
    ):
        file_name = "test_file.txt"
        workspace = "test_app_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value.st_size = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_gra.return_value = {"resource_available": 1500}
        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_gaw.return_value = mock_return

        args = mock.MagicMock(
            type="app_workspace",
            app=self.app.package,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_gaw.assert_called_with(self.app, bypass_quota=True)
        mock_caf.assert_called()
        mock_copy.assert_called_once()
        mock_wr.assert_called_with(
            f"File '{file_name}' has been added to the App Workspace at '{workspace}/{file_name}'."
        )

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands.shutil.copy")
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace")
    @mock.patch("tethys_cli.paths_commands.write_success")
    def test_add_app_workspace(
        self, mock_wr, mock_gaw, mock_gra, mock_caf, mock_copy, mock_path
    ):
        file_name = "test_file.txt"
        workspace = "test_app_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value.st_size = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_gra.return_value = {"resource_available": 1500}
        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_gaw.return_value = mock_return

        args = mock.MagicMock(
            type="app_workspace",
            app=self.app.package,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_gaw.assert_called_with(self.app, bypass_quota=True)
        mock_caf.assert_called()
        mock_copy.assert_called_once()
        mock_wr.assert_called_with(
            f"File '{file_name}' has been added to the App Workspace at '{workspace}/{file_name}'."
        )

    @override_settings(USE_OLD_WORKSPACES_API=True)
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands.shutil.copy")
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands._get_user_workspace_old")
    @mock.patch("tethys_cli.paths_commands.write_success")
    def test_add_user_workspace_old(
        self, mock_wr, mock_guw, mock_gra, mock_caf, mock_copy, mock_path
    ):
        file_name = "test_file.txt"
        workspace = "test_user_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value.st_size = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_gra.return_value = {"resource_available": 1500}
        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_guw.return_value = mock_return

        args = mock.MagicMock(
            type="user_workspace",
            app=self.app.package,
            user=self.user,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_guw.assert_called_with(self.app, self.user, bypass_quota=True)
        mock_caf.assert_called()
        mock_copy.assert_called_once()
        mock_wr.assert_called_with(
            f"File '{file_name}' has been added to the User Workspace at '{workspace}/{file_name}'."
        )

    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands.shutil.copy")
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands._get_app_media")
    @mock.patch("tethys_cli.paths_commands.write_success")
    def test_add_app_media(
        self, mock_wr, mock_gam, mock_gra, mock_caf, mock_copy, mock_path
    ):
        file_name = "test_file.txt"
        media = "test_app_media_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{media}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_gra.return_value = {"resource_available": 1500}
        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(media)
        mock_gam.return_value = mock_return

        args = mock.MagicMock(
            type="app_media",
            app=self.app.package,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_gam.assert_called_with(self.app, bypass_quota=True)
        mock_caf.assert_called()
        mock_copy.assert_called_once()
        mock_wr.assert_called_with(
            f"File '{file_name}' has been added to the App Media at '{media}/{file_name}'."
        )

    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands.shutil.copy")
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands._get_user_media")
    @mock.patch("tethys_cli.paths_commands.write_success")
    def test_add_user_media(
        self, mock_wr, mock_gum, mock_gra, mock_caf, mock_copy, mock_path
    ):
        file_name = "test_file.txt"
        media = "test_user_media_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{media}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_gra.return_value = {"resource_available": 1500}
        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(media)
        mock_gum.return_value = mock_return

        args = mock.MagicMock(
            type="user_media",
            app=self.app.package,
            user=self.user,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_gum.assert_called_with(self.app, self.user, bypass_quota=True)
        mock_caf.assert_called()
        mock_copy.assert_called_once()
        mock_wr.assert_called_with(
            f"File '{file_name}' has been added to the User Media at '{media}/{file_name}'."
        )

    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands.shutil.copy")
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands.get_app_public")
    @mock.patch("tethys_cli.paths_commands.write_success")
    def test_add_app_public(
        self, mock_wr, mock_gap, mock_gra, mock_caf, mock_copy, mock_path
    ):
        file_name = "test_file.txt"
        public = "test_app_public_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{public}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_gra.return_value = {"resource_available": 1500}
        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(public)
        mock_gap.return_value = mock_return

        args = mock.MagicMock(
            type="app_public",
            app=self.app.package,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_gap.assert_called_with(self.app)
        mock_caf.assert_called()
        mock_copy.assert_called_once()
        mock_wr.assert_called_with(
            f"File '{file_name}' has been added to the App Public at '{public}/{file_name}'."
        )

    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands.shutil.copy")
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands.get_app_resources")
    @mock.patch("tethys_cli.paths_commands.write_success")
    def test_add_app_resources(
        self, mock_wr, mock_gar, mock_gra, mock_caf, mock_copy, mock_path
    ):
        file_name = "test_file.txt"
        resources = "test_app_resources_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{resources}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_gra.return_value = {"resource_available": 1500}
        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(resources)
        mock_gar.return_value = mock_return

        args = mock.MagicMock(
            type="app_resources",
            app=self.app.package,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_gar.assert_called_with(self.app)
        mock_caf.assert_called()
        mock_copy.assert_called_once()
        mock_wr.assert_called_with(
            f"File '{file_name}' has been added to the App Resources at '{resources}/{file_name}'."
        )

    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_no_user_provided_for_user_workspace(self, mock_we):
        args = mock.MagicMock(
            type="user_workspace", app=self.app.package, user=None, file="test_file.txt"
        )
        add_file_to_path(args)
        mock_we.assert_called_with(
            "The '--user' argument is required for path type 'user_workspace'."
        )

    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_no_user_provided_for_user_media(self, mock_we):
        args = mock.MagicMock(
            type="user_media", app=self.app.package, user=None, file="test_file.txt"
        )
        add_file_to_path(args)
        mock_we.assert_called_with(
            "The '--user' argument is required for path type 'user_media'."
        )

    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_invalid_path_type(self, mock_we):
        args = mock.MagicMock(
            type="invalid_path_type", app=self.app.package, file="test_file.txt"
        )
        add_file_to_path(args)
        mock_we.assert_called_with("Invalid path type: 'invalid_path_type'.")

    @mock.patch("tethys_cli.paths_commands.write_warning")
    def test_user_not_found(self, mock_ww):
        args = mock.MagicMock(
            type="user_workspace",
            app=self.app.package,
            user="nonexistent_user",
            file="test_file.txt",
        )
        add_file_to_path(args)
        mock_ww.assert_called_with("User 'nonexistent_user' was not found.")

    @mock.patch("tethys_cli.paths_commands.write_warning")
    def test_app_not_found(self, mock_ww):
        args = mock.MagicMock(
            type="app_workspace", app="nonexistent_app", file="test_file.txt"
        )
        add_file_to_path(args)
        mock_ww.assert_called_with("Tethys app 'nonexistent_app' is not installed.")

    @mock.patch("tethys_cli.paths_commands.write_error")
    @mock.patch("tethys_cli.paths_commands.resolve_path")
    def test_path_not_found(self, mock_resolve_path, mock_we):
        mock_resolve_path.return_value = None
        args = mock.MagicMock(
            type="app_workspace", app=self.app.package, file="test_file.txt"
        )
        add_file_to_path(args)
        mock_we.assert_called_with("Could not find App Workspace.")

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace")
    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_nonexistent_file(self, mock_we, mock_gaw, mock_path):
        file_name = "test_file.txt"
        workspace = "test_app_workspace_path"

        mock_file = mock.MagicMock()
        # Mock the file not existing
        mock_file.is_file.return_value = False

        mock_path.return_value = mock_file

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_gaw.return_value = mock_return

        args = mock.MagicMock(
            type="app_workspace",
            app=self.app.package,
            file="test_file.txt",
        )

        add_file_to_path(args)

        mock_we.assert_called_with(
            f"The specified file '{file_name}' does not exist or is not a file."
        )

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace")
    @mock.patch("tethys_cli.paths_commands.write_warning")
    def test_already_exists_destination(self, mock_ww, mock_gaw, mock_path):
        file_name = "test_file.txt"
        workspace = "test_app_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value = 1024

        # Mock the destination file already existing
        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = True
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_gaw.return_value = mock_return

        args = mock.MagicMock(
            type="app_workspace",
            app=self.app.package,
            file="test_file.txt",
        )

        add_file_to_path(args)

        mock_ww.assert_called_with(
            f"The file '{file_name}' already exists in the intended App Workspace."
        )

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands._get_user_workspace")
    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_user_quota_met(self, mock_we, mock_guw, mock_path, mock_gra, mock_caf):
        file_name = "test_file.txt"
        workspace = "test_user_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        # Mock the user quota being exceeded
        mock_gra.return_value = {"resource_available": 0}

        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_guw.return_value = mock_return

        args = mock.MagicMock(
            type="user_workspace",
            app=self.app.package,
            user=self.user,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_we.assert_called_with(
            "Cannot add file to User Workspace. Quota has already been met."
        )

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands._get_user_workspace")
    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_user_will_exceed_quota(
        self, mock_we, mock_guw, mock_path, mock_gra, mock_caf
    ):
        file_name = "test_file.txt"
        workspace = "test_user_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value.st_size = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        # Mock the resource avilable as 300 bytes so 1024 will exceed it
        mock_caf.return_value = False
        mock_gra.return_value = {"resource_available": 0.0000002794}

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_guw.return_value = mock_return

        args = mock.MagicMock(
            type="user_workspace",
            app=self.app.package,
            user=self.user,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_we.assert_called_with(
            "Cannot add file to User Workspace. File size (1 KB) exceeds available quota (300 bytes)."
        )

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace")
    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_app_quota_met(self, mock_we, mock_gaw, mock_path, mock_gra, mock_caf):
        file_name = "test_file.txt"
        workspace = "test_app_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        # Mock the user quota being exceeded
        mock_gra.return_value = {"resource_available": 0}

        mock_caf.return_value = True

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_gaw.return_value = mock_return

        args = mock.MagicMock(
            type="app_workspace",
            app=self.app.package,
            user=self.user,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_we.assert_called_with(
            "Cannot add file to App Workspace. Quota has already been met."
        )

    @override_settings(USE_OLD_WORKSPACES_API=False)
    @mock.patch("tethys_cli.paths_commands.can_add_file_to_path")
    @mock.patch("tethys_cli.paths_commands.get_resource_available")
    @mock.patch("tethys_cli.paths_commands.Path")
    @mock.patch("tethys_cli.paths_commands._get_app_workspace")
    @mock.patch("tethys_cli.paths_commands.write_error")
    def test_app_will_exceed_quota(
        self, mock_we, mock_gaw, mock_path, mock_gra, mock_caf
    ):
        file_name = "test_file.txt"
        workspace = "test_app_workspace_path"

        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_file.name = file_name
        mock_file.stat.return_value.st_size = 1024

        mock_file.exists.return_value = False
        mock_file.__str__.return_value = file_name

        mock_destination = mock.MagicMock()
        mock_destination.exists.return_value = False
        mock_destination.__str__.return_value = f"{workspace}/{file_name}"
        mock_file.__truediv__.return_value = mock_destination

        mock_path.return_value = mock_file

        # Mock the resource avilable as 300 bytes so 1024 will exceed it
        mock_caf.return_value = False
        mock_gra.return_value = {"resource_available": 0.0000002794}

        mock_return = mock.MagicMock()
        mock_return.path = Path(workspace)
        mock_gaw.return_value = mock_return

        args = mock.MagicMock(
            type="app_workspace",
            app=self.app.package,
            user=self.user,
            file="test_file.txt",
        )
        add_file_to_path(args)

        mock_we.assert_called_with(
            "Cannot add file to App Workspace. File size (1 KB) exceeds available quota (300 bytes)."
        )
