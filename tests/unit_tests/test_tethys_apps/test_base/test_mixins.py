import unittest
from unittest import mock
import tethys_apps.base.mixins as tethys_mixins
from ... import UserFactory


class TestTethysBaseMixin(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysBaseMixin(self):
        result = tethys_mixins.TethysBaseMixin()
        result.root_url = "test-url"
        self.assertEqual("test_url", result.url_namespace)


class TestTethysAsyncWebsocketConsumer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.consumer = tethys_mixins.TethysAsyncWebsocketConsumerMixin()
        self.consumer.accept = mock.AsyncMock()
        self.consumer.permissions = ["test_permission"]
        self.consumer.scope = {"user": UserFactory(), "path": "path/to/app"}

    def tearDown(self):
        pass

    def test_perms_list(self):
        self.assertTrue(self.consumer.perms == ["test_permission"])

    def test_perms_none(self):
        self.consumer.permissions = None
        self.assertTrue(self.consumer.perms == [])

    def test_perms_str(self):
        self.consumer.permissions = "test_permission,test_permission1"
        self.assertTrue(self.consumer.perms == ["test_permission", "test_permission1"])

    def test_perms_exception(self):
        self.consumer.permissions = {"test": "test_permsision"}
        with self.assertRaises(TypeError) as context:
            self.consumer.perms

        self.assertTrue(
            context.exception.args[0]
            == "permissions must be a list, tuple, or comma separated string"
        )

    async def test_authorized_login_required_success(self):
        self.consumer.permissions = []
        self.consumer.login_required = True
        self.assertTrue(await self.consumer.authorized)

    async def test_authorized_login_required_failure(self):
        self.consumer.permissions = []
        self.consumer.login_required = True
        self.consumer.scope = {
            "user": mock.MagicMock(is_authenticated=False),
            "path": "path/to/app",
        }
        self.assertFalse(await self.consumer.authorized)

    @mock.patch("tethys_apps.base.mixins.scoped_user_has_permission")
    async def test_authorized_permissions_and(self, mock_suhp):
        self.consumer.permissions = ["test_permission", "test_permission1"]
        mock_suhp.side_effect = [True, True]
        self.assertTrue(await self.consumer.authorized)

    @mock.patch("tethys_apps.base.mixins.scoped_user_has_permission")
    async def test_authorized_inadequate_permissions_and(self, mock_suhp):
        self.consumer.permissions = ["test_permission", "test_permission1"]
        mock_suhp.side_effect = [True, False]
        self.assertFalse(await self.consumer.authorized)

    @mock.patch("tethys_apps.base.mixins.scoped_user_has_permission")
    async def test_authorized_permissions_or(self, mock_suhp):
        self.consumer.permissions = ["test_permission", "test_permission1"]
        self.consumer.permissions_use_or = True
        mock_suhp.side_effect = [True, False]
        self.assertTrue(await self.consumer.authorized)

    @mock.patch("tethys_apps.base.mixins.scoped_user_has_permission")
    async def test_authorized_inadequate_permissions_or(self, mock_suhp):
        self.consumer.permissions = ["test_permission", "test_permission1"]
        self.consumer.permissions_use_or = True
        mock_suhp.side_effect = [False, False]
        self.assertFalse(await self.consumer.authorized)

    async def test_authorized_connect(self):
        await self.consumer.authorized_connect()

    async def test_unauthorized_connect(self):
        await self.consumer.unauthorized_connect()

    async def test_authorized_disconnect(self):
        event = {}
        await self.consumer.authorized_disconnect(event)

    async def test_unauthorized_disconnect(self):
        event = {}
        await self.consumer.unauthorized_disconnect(event)

    @mock.patch(
        "tethys_apps.base.mixins.TethysAsyncWebsocketConsumerMixin.authorized_connect"
    )
    async def test_connect(self, mock_authorized_connect):
        self.consumer._authorized = True
        await self.consumer.connect()
        self.consumer.accept.assert_called_once()
        mock_authorized_connect.assert_called_once()

    @mock.patch(
        "tethys_apps.base.mixins.TethysAsyncWebsocketConsumerMixin.unauthorized_connect"
    )
    async def test_connect_not_authorized(self, mock_unauthorized_connect):
        self.consumer._authorized = False
        await self.consumer.connect()
        self.consumer.accept.assert_not_called()
        mock_unauthorized_connect.assert_called_once()

    @mock.patch(
        "tethys_apps.base.mixins.TethysAsyncWebsocketConsumerMixin.authorized_disconnect"
    )
    async def test_disconnect(self, mock_authorized_disconnect):
        self.consumer._authorized = True
        event = "event"
        await self.consumer.disconnect(event)
        mock_authorized_disconnect.assert_called_with(event)

    @mock.patch(
        "tethys_apps.base.mixins.TethysAsyncWebsocketConsumerMixin.unauthorized_disconnect"
    )
    async def test_disconnect_not_authorized(self, mock_unauthorized_disconnect):
        self.consumer._authorized = False
        event = "event"
        await self.consumer.disconnect(event)
        mock_unauthorized_disconnect.assert_called_once()


class TestTethysWebsocketConsumer(unittest.TestCase):
    def setUp(self):
        self.consumer = tethys_mixins.TethysWebsocketConsumerMixin()
        self.consumer.accept = mock.MagicMock()
        self.consumer.permissions = ["test_permission"]
        self.consumer.scope = {"user": UserFactory(), "path": "path/to/app"}

    def tearDown(self):
        pass

    def test_perms_list(self):
        self.assertTrue(self.consumer.perms == ["test_permission"])

    def test_perms_none(self):
        self.consumer.permissions = None
        self.assertTrue(self.consumer.perms == [])

    def test_perms_str(self):
        self.consumer.permissions = "test_permission,test_permission1"
        self.assertTrue(self.consumer.perms == ["test_permission", "test_permission1"])

    def test_perms_exception(self):
        self.consumer.permissions = {"test": "test_permsision"}
        with self.assertRaises(TypeError) as context:
            self.consumer.perms

        self.assertTrue(
            context.exception.args[0]
            == "permissions must be a list, tuple, or comma separated string"
        )

    def test_authorized_login_required_success(self):
        self.consumer.permissions = []
        self.consumer.login_required = True
        self.assertTrue(self.consumer.authorized)

    def test_authorized_login_required_failure(self):
        self.consumer.permissions = []
        self.consumer.login_required = True
        self.consumer.scope = {
            "user": mock.MagicMock(is_authenticated=False),
            "path": "path/to/app",
        }
        self.assertFalse(self.consumer.authorized)

    def test_authorized_permissions_and(self):
        self.consumer.permissions = ["test_permission"]
        with mock.patch(
            "tethys_apps.base.mixins.scoped_user_has_permission", user_has_perms
        ):
            self.assertTrue(self.consumer.authorized)

    def test_authorized_inadequate_permissions_and(self):
        self.consumer.permissions = ["test_permission", "test_permission1"]
        with mock.patch(
            "tethys_apps.base.mixins.scoped_user_has_permission", user_has_perms
        ):
            self.assertFalse(self.consumer.authorized)

    def test_authorized_permissions_or(self):
        self.consumer.permissions = ["test_permission", "test_permission1"]
        self.consumer.permissions_use_or = True
        with mock.patch(
            "tethys_apps.base.mixins.scoped_user_has_permission", user_has_perms
        ):
            self.assertTrue(self.consumer.authorized)

    def test_authorized_inadequate_permissions_or(self):
        self.consumer.permissions = ["test_permission1"]
        self.consumer.permissions_use_or = True
        with mock.patch(
            "tethys_apps.base.mixins.scoped_user_has_permission", user_has_perms
        ):
            self.assertFalse(self.consumer.authorized)

    def test_authorized_connect(self):
        self.consumer.authorized_connect()

    def test_unauthorized_connect(self):
        self.consumer.unauthorized_connect()

    def test_authorized_disconnect(self):
        event = {}
        self.consumer.authorized_disconnect(event)

    def test_unauthorized_disconnect(self):
        event = {}
        self.consumer.unauthorized_disconnect(event)

    @mock.patch(
        "tethys_apps.base.mixins.TethysWebsocketConsumerMixin.authorized_connect"
    )
    def test_connect(self, mock_authorized_connect):
        self.consumer._authorized = True
        self.consumer.connect()
        self.consumer.accept.assert_called_once()
        mock_authorized_connect.assert_called_once()

    @mock.patch(
        "tethys_apps.base.mixins.TethysWebsocketConsumerMixin.unauthorized_connect"
    )
    def test_connect_not_authorized(self, mock_unauthorized_connect):
        self.consumer._authorized = False
        self.consumer.connect()
        self.consumer.accept.assert_not_called()
        mock_unauthorized_connect.assert_called_once()

    @mock.patch(
        "tethys_apps.base.mixins.TethysWebsocketConsumerMixin.authorized_disconnect"
    )
    def test_disconnect(self, mock_authorized_disconnect):
        self.consumer._authorized = True
        event = "event"
        self.consumer.disconnect(event)
        mock_authorized_disconnect.assert_called_with(event)

    @mock.patch(
        "tethys_apps.base.mixins.TethysWebsocketConsumerMixin.unauthorized_disconnect"
    )
    def test_disconnect_not_authorized(self, mock_unauthorized_disconnect):
        self.consumer._authorized = False
        event = "event"
        self.consumer.disconnect(event)
        mock_unauthorized_disconnect.assert_called_once()


def user_has_perms(_, perm):
    if perm == "test_permission":
        return True
    return False
