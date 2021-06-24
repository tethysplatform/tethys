"""
********************************************************************************
* Name: tethys_layout.py
* Author: nswain
* Created On: June 24, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""
import logging

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, reverse

from tethys_apps.utilities import get_active_app
from tethys_sdk.base import TethysController
from tethys_sdk.permissions import has_permission

from tethysext.atcore.exceptions import ATCoreException
from tethysext.atcore.models.app_users import AppUser, Organization, Resource
from tethysext.atcore.services.app_users.decorators import active_user_required, resource_controller
from tethysext.atcore.services.app_users.permissions_manager import AppPermissionsManager
from tethysext.atcore.services.model_database import ModelDatabase

log = logging.getLogger(f'tethys.{__name__}')


# TODO: Merge into TethysLayout
class AppUsersViewMixin(TethysController):
    """
    Mixin for class-based views that adds convenience methods for working with the app user models.
    """
    _AppUser = AppUser
    _Organization = Organization
    _Resource = Resource
    _PermissionsManager = AppPermissionsManager
    _app = None
    _persistent_store_name = ''

    def get_app(self):
        return self._app

    def get_app_user_model(self):
        return self._AppUser

    def get_organization_model(self):
        return self._Organization

    def get_resource_model(self):
        return self._Resource

    def get_permissions_manager(self):
        return self._PermissionsManager(self._app.namespace)

    def get_sessionmaker(self):
        if not self._app:
            raise NotImplementedError('get_sessionmaker method not implemented.')

        return self._app.get_persistent_store_database(self._persistent_store_name, as_sessionmaker=True)

    def get_base_context(self, request):
        base_context = {
            'is_app_admin': has_permission(request, 'has_app_admin_role')
        }
        return base_context


# TODO: Merge into TethysLayout
class ResourceViewMixin(AppUsersViewMixin):
    """
    Mixin for class-based views that adds convenience methods for working with resources.
    """

    back_url = ''

    def dispatch(self, request, *args, **kwargs):
        """
        Intercept kwargs before calling handler method.
        """
        # Handle back_url
        self.back_url = kwargs.get('back_url', '')

        # Default to the resource details page
        if not self.back_url:
            self.back_url = self.default_back_url(
                request=request,
                *args, **kwargs
            )
        return super(ResourceViewMixin, self).dispatch(request, *args, **kwargs)

    def default_back_url(self, request, *args, **kwargs):
        """
        Hook for custom back url. Defaults to the resource details page.

        Returns:
            str: back url.
        """
        resource_id = kwargs.get('resource_id', '') or args[0]
        active_app = get_active_app(request)
        app_namespace = active_app.namespace
        back_controller = f'{app_namespace}:{self._Resource.SLUG}_resource_details'
        return reverse(back_controller, args=(str(resource_id),))

    def get_resource(self, request, resource_id, session=None):
        """
        Get the resource and check permissions.

        Args:
            request: Django HttpRequest.
            resource_id: ID of the resource.
            session: SQLAlchemy session. Optional.

        Returns:
            Resource: the resource.
        """
        # Setup
        _AppUser = self.get_app_user_model()
        _Resource = self.get_resource_model()
        manage_session = False

        if not session:
            manage_session = True
            make_session = self.get_sessionmaker()
            session = make_session()

        request_app_user = _AppUser.get_app_user_from_request(request, session)
        try:
            resource = session.query(_Resource). \
                filter(_Resource.id == resource_id). \
                one()

            # TODO: Let the apps check permissions so anonymous user only has access to app specific resources?
            if not getattr(settings, 'ENABLE_OPEN_PORTAL', False):
                if not request_app_user.can_view(session, request, resource):
                    raise ATCoreException('You are not allowed to access this {}'.format(
                        _Resource.DISPLAY_TYPE_SINGULAR.lower()
                    ))
        finally:
            if manage_session:
                session.close()

        return resource

# TODO: Merge applicable methods from ResourceViewMixin and AppUsersViewMixin
class TethysLayout(ResourceViewMixin):
    """
    Base controller for all Resource-based views.
    """
    _ModelDatabase = ModelDatabase

    view_title = ''
    view_subtitle = ''
    template_name = ''
    base_template = 'atcore/base.html'

    @active_user_required()
    @resource_controller()
    def get(self, request, session, resource, back_url, *args, **kwargs):
        """
        Handle GET requests.
        """
        from django.conf import settings

        # Call on get hook
        ret_on_get = self.on_get(request, session, resource, *args, **kwargs)
        if ret_on_get and isinstance(ret_on_get, HttpResponse):
            return ret_on_get

        # Check for GET request alternative methods
        the_method = self.request_to_method(request)

        if the_method is not None:
            return the_method(
                request=request,
                session=session,
                resource=resource,
                back_url=back_url,
                *args, **kwargs
            )

        # Get Managers Hook
        model_db = self.get_model_db(
            request=request,
            resource=resource,
            *args, **kwargs
        )

        # Initialize context
        context = {}

        # Add named url variables to context
        context.update(self.kwargs)

        # Add base view variables to context
        open_portal_mode = getattr(settings, 'ENABLE_OPEN_PORTAL', False)
        context.update({
            'resource': resource,
            'is_in_debug': settings.DEBUG,
            'nav_subtitle': self.view_subtitle,
            'back_url': self.back_url,
            'open_portal_mode': open_portal_mode,
            'base_template': self.base_template
        })

        if resource:
            context.update({'nav_title': self.view_title or resource.name})
        else:
            context.update({'nav_title': self.view_title})

        # Context hook
        context = self.get_context(
            request=request,
            session=session,
            context=context,
            resource=resource,
            model_db=model_db,
            *args, **kwargs
        )

        # Default Permissions
        permissions = {}

        # Permissions hook
        permissions = self.get_permissions(
            request=request,
            permissions=permissions,
            model_db=model_db,
            *args, **kwargs
        )

        context.update(permissions)

        return render(request, self.template_name, context)

    @active_user_required()
    @resource_controller()
    def post(self, request, session, resource, back_url, *args, **kwargs):
        """
        Route POST requests.
        """
        the_method = self.request_to_method(request)

        if the_method is None:
            return HttpResponseNotFound()

        return the_method(
            request=request,
            session=session,
            resource=resource,
            back_url=back_url,
            *args, **kwargs
        )

    def request_to_method(self, request):
        """
        Derive python method on this class from "method" GET or POST parameter.
        Args:
            request (HttpRequest): The request.

        Returns:
            callable: the method or None if not found.
        """
        if request.method == 'POST':
            method = request.POST.get('method', '')
        elif request.method == 'GET':
            method = request.GET.get('method', '')
        else:
            return None
        python_method = method.replace('-', '_')
        the_method = getattr(self, python_method, None)
        return the_method

    def on_get(self, request, session, resource, *args, **kwargs):
        """
        Hook that is called at the beginning of the get request, before any other controller logic occurs.
            request (HttpRequest): The request.
            session (sqlalchemy.Session): the session.
            resource (Resource): the resource for this request.
        Returns:
            None or HttpResponse: If an HttpResponse is returned, render that instead.
        """  # noqa: E501
        return None

    def get_model_db(self, request, resource, *args, **kwargs):
        """
        Hook to get managers. Avoid removing or modifying items in context already to prevent unexpected behavior.

        Args:
            request (HttpRequest): The request.
            resource (Resource): Resource instance or None.

        Returns:
            model_db (ModelDatabase): ModelDatabase instance.
            map_manager (MapManager): Map Manager instance
        """  # noqa: E501
        database_id = None

        if resource:
            database_id = resource.get_attribute('database_id')

        if not database_id:
            log.warning('No model database provided')
            model_db = None
        else:
            model_db = self._ModelDatabase(app=self._app, database_id=database_id)

        return model_db

    def get_context(self, request, session, resource, context, model_db, *args, **kwargs):
        """
        Hook to add additional content to context. Avoid removing or modifying items in context already to prevent unexpected behavior.

        Args:
            request (HttpRequest): The request.
            session (sqlalchemy.Session): the session.
            resource (Resource): the resource for this request.
            context (dict): The context dictionary.
            model_db (ModelDatabase): ModelDatabase instance associated with this request.

        Returns:
            dict: modified context dictionary.
        """  # noqa: E501
        return context

    def get_permissions(self, request, permissions, model_db, *args, **kwargs):
        """
        Hook to modify permissions.

        Args:
            request (HttpRequest): The request.
            permissions (dict): The permissions dictionary with boolean values.
            model_db (ModelDatabase): ModelDatabase instance associated with this request.

        Returns:
            dict: modified permisssions dictionary.
        """
        return permissions
