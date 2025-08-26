from channels.db import database_sync_to_async

from .permissions import _has_permission
from .paths import (
    get_app_workspace,
    get_user_workspace,
    get_app_media,
    get_user_media,
    get_app_resources,
    get_app_public,
)


class TethysBaseMixin:
    """
    Provides methods and properties common to the TethysBase and model classes.
    """

    root_url = ""
    index = ""

    @property
    def url_namespace(self):
        """
        Get the namespace for the app or extension.
        """
        return self.root_url.replace("-", "_")

    @property
    def index_url(self):
        return f"{self.url_namespace}:{self.index}"


class TethysAsyncWebsocketConsumerMixin:
    """
    Provides methods and properties common to Tethys async websocket consumers.
    """

    permissions = []
    permissions_use_or = False
    login_required = True
    _authorized = None
    _perms = None
    _active_app = None
    _user = None

    async def _initialize_app_and_user(self):
        self._user = self.scope.get("user")
        await database_sync_to_async(self._get_active_app)()

    @property
    def perms(self):
        if self._perms is None:
            if self.permissions is None:
                self._perms = []
            elif type(self.permissions) in [list, tuple]:
                self._perms = self.permissions
            elif isinstance(self.permissions, str):
                self._perms = self.permissions.split(",")
            else:
                raise TypeError(
                    "permissions must be a list, tuple, or comma separated string"
                )
        return self._perms

    async def _authorize(self):
        if self.login_required and not self.scope["user"].is_authenticated:
            self._authorized = False
        else:
            perm_values = [
                await database_sync_to_async(_has_permission)(
                    self.active_app, self.user, perm
                )
                for perm in self.perms
            ]
            self._authorized = (
                any(perm_values) if self.permissions_use_or else all(perm_values)
            )

    @property
    async def authorized(self):
        if self._authorized is None:
            await self._authorize()
        return self._authorized

    async def authorized_connect(self):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    async def unauthorized_connect(self):
        """Custom class method to run custom code when an unauthorized user connects to the websocket"""
        pass

    async def authorized_disconnect(self, *args):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    async def unauthorized_disconnect(self, *args):
        """Custom class method to run custom code when an unauthorized user connects to the websocket"""
        pass

    async def connect(self):
        """Class method to handle when user connects to the websocket"""
        if await self.authorized:
            await self.accept()
            await self.authorized_connect()
        else:
            # User not authorized for websocket access
            await self.unauthorized_connect()

    async def disconnect(self, *args):
        """Class method to handle when user disconnects to the websocket"""
        if await self.authorized:
            await self.authorized_disconnect(*args)
        else:
            # User not authorized for websocket access
            await self.unauthorized_disconnect(*args)

    def _get_active_app(self):
        from tethys_apps.utilities import get_active_app

        request_url = self.scope["path"]

        self._active_app = get_active_app(url=request_url)

    @property
    def active_app(self):
        return self._active_app

    @property
    def user(self):
        return self.scope.get("user")

    @property
    def app_workspace(self):
        return get_app_workspace(self.active_app)

    @property
    def user_workspace(self):
        return get_user_workspace(self.active_app, self.user)

    @property
    def app_media(self):
        return get_app_media(self.active_app)

    @property
    def user_media(self):
        return get_user_media(self.active_app, self.user)

    @property
    def app_resources(self):
        return get_app_resources(self.active_app)

    @property
    def app_public(self):
        return get_app_public(self.active_app)


class TethysWebsocketConsumerMixin(TethysAsyncWebsocketConsumerMixin):
    """
    Provides methods and properties common to Tethys websocket consumers.
    """

    def _authorize_sync(self):
        """Sync version of authorization check"""
        if self.login_required and not self.scope["user"].is_authenticated:
            self._authorized = False
        else:
            # Use sync permission check directly
            perm_values = [
                _has_permission(self.active_app, self.user, perm) for perm in self.perms
            ]
            self._authorized = (
                any(perm_values) if self.permissions_use_or else all(perm_values)
            )

    @property
    def authorized(self):
        if self._authorized is None:
            self._authorize_sync()
        return self._authorized

    def authorized_connect(self):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    def unauthorized_connect(self):
        """Custom class method to run custom code when an unauthorized user connects to the websocket"""
        pass

    def authorized_disconnect(self, *args):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    def unauthorized_disconnect(self, *args):
        """Custom class method to run custom code when an unauthorized user connects to the websocket"""
        pass

    def connect(self):
        """Class method to handle when user connects to the websocket"""
        if self.authorized:
            self.accept()
            self.authorized_connect()
        else:
            # User not authorized for websocket access
            self.unauthorized_connect()

    def disconnect(self, *args):
        """Class method to handle when user disconnects to the websocket"""
        if self.authorized:
            self.authorized_disconnect(*args)
        else:
            # User not authorized for websocket access
            self.unauthorized_disconnect(*args)
