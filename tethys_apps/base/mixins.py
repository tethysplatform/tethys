from .permissions import scoped_user_has_permission


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

    @property
    async def authorized(self):
        if self._authorized is None:
            if self.login_required and not self.scope["user"].is_authenticated:
                self._authorized = False
                return self._authorized

            if self.permissions_use_or:
                self._authorized = False
                for perm in self.perms:
                    if await scoped_user_has_permission(self.scope, perm):
                        self._authorized = True
            else:
                self._authorized = True
                for perm in self.perms:
                    if not await scoped_user_has_permission(self.scope, perm):
                        self._authorized = False
        return self._authorized

    async def authorized_connect(self):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    async def unauthorized_connect(self):
        """Custom class method to run custom code when an unauthorized user connects to the websocket"""
        pass

    async def authorized_disconnect(self, close_code):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    async def unauthorized_disconnect(self, close_code):
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

    async def disconnect(self, close_code):
        """Class method to handle when user disconnects to the websocket"""
        if await self.authorized:
            await self.authorized_disconnect(close_code)
        else:
            # User not authorized for websocket access
            await self.unauthorized_disconnect(close_code)


class TethysWebsocketConsumerMixin:
    """
    Provides methods and properties common to Tethys websocket consumers.
    """

    permissions = []
    permissions_use_or = False
    login_required = True
    _authorized = None
    _perms = None

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

    @property
    def authorized(self):
        if self._authorized is None:
            if self.login_required and not self.scope["user"].is_authenticated:
                self._authorized = False
                return self._authorized

            if self.permissions_use_or:
                self._authorized = False
                for perm in self.perms:
                    if scoped_user_has_permission(self.scope, perm):
                        self._authorized = True
            else:
                self._authorized = True
                for perm in self.perms:
                    if not scoped_user_has_permission(self.scope, perm):
                        self._authorized = False
        return self._authorized

    def authorized_connect(self):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    def unauthorized_connect(self):
        """Custom class method to run custom code when an unauthorized user connects to the websocket"""
        pass

    def authorized_disconnect(self, close_code):
        """Custom class method to run custom code when an authorized user connects to the websocket"""
        pass

    def unauthorized_disconnect(self, close_code):
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

    def disconnect(self, close_code):
        """Class method to handle when user disconnects to the websocket"""
        if self.authorized:
            self.authorized_disconnect(close_code)
        else:
            # User not authorized for websocket access
            self.unauthorized_disconnect(close_code)
