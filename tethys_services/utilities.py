"""
********************************************************************************
* Name: utilities.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import logging
from urllib.error import HTTPError, URLError
from functools import wraps

import requests.exceptions

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.shortcuts import redirect

from tethys_apps.base.app_base import TethysAppBase
from .models import (
    DatasetService as DsModel,
    SpatialDatasetService as SdsModel,
    WebProcessingService as WpsModel,
)

from tethys_portal.optional_dependencies import optional_import

# optional imports
HydroShareDatasetEngine = optional_import(
    "HydroShareDatasetEngine", from_module="tethys_dataset_services.engines"
)
WebProcessingService = optional_import("WebProcessingService", from_module="owslib.wps")
load_strategy = optional_import("load_strategy", from_module="social_django.utils")
AuthAlreadyAssociated, AuthException = optional_import(
    ("AuthAlreadyAssociated", "AuthException"), from_module="social_core.exceptions"
)


logger = logging.getLogger(__name__)


def ensure_oauth2(provider):
    """
    Decorator to ensure a user has been authenticated with the given oauth2 provider.

    Usage:

        from tethys_sdk.services import ensure_oauth2, get_dataset_engine

        @ensure_oauth2('hydroshare-oauth2')
        def controller(request):
            engine = get_dataset_engine('default_hydroshare', request=request)
            return render(request, 'my_template.html', {})

    Note that calling get_dataset_engine for a hydroshare dataset engine will throw an error
    if it is not called in a function that is decorated with the ensure_oauth2 decorator.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            # Assemble redirect response
            redirect_url = reverse(
                "social:begin", args=[provider]
            ) + "?next={0}".format(request.path)
            redirect_response = redirect(redirect_url)

            try:
                social = user.social_auth.get(provider=provider)
            except ObjectDoesNotExist:
                # User is not associated with that provider
                return redirect_response
            except AttributeError:
                # Anonymous User needs to be logged in and associated with that provider
                return redirect_response
            except AuthAlreadyAssociated as e:
                # Another user has already used the account to associate...
                raise e
            else:
                strategy = load_strategy()
                try:
                    access_token = social.get_access_token(strategy)
                except requests.exceptions.HTTPError:
                    logger.debug(
                        "there was an error refreshing the token - redirecting user to re-authenticate"
                    )
                    return redirect_response

                request.social_access_token = access_token

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def initialize_engine_object(
    engine, endpoint, apikey=None, username=None, password=None, request=None
):
    """
    Initialize a DatasetEngine object from a string that points at the engine class.
    """
    # Constants
    HYDROSHARE_OAUTH_PROVIDER_NAME = "hydroshare"

    # Derive import parts from engine string
    engine_split = engine.split(".")
    module_string = ".".join(engine_split[:-1])
    engine_class_string = engine_split[-1]

    # Import
    module_ = __import__(module_string, fromlist=[str(engine_class_string)])
    EngineClass = getattr(module_, engine_class_string)

    # Get Token for HydroShare interactions
    if EngineClass is HydroShareDatasetEngine:
        user = request.user

        try:
            # social = user.social_auth.get(provider='google-oauth2')
            social = user.social_auth.get(provider=HYDROSHARE_OAUTH_PROVIDER_NAME)
            apikey = social.extra_data["access_token"]
        except ObjectDoesNotExist:
            # User is not associated with that provider
            # Need to prompt for association
            raise AuthException(
                "HydroShare authentication required. To automate the authentication prompt decorate "
                "your controller function with the @ensure_oauth('hydroshare') decorator."
            )
        except AttributeError:
            # Anonymous User...
            raise
        except AuthAlreadyAssociated:
            raise

    # Create Engine Object
    engine_instance = EngineClass(
        endpoint=endpoint, apikey=apikey, username=username, password=password
    )
    return engine_instance


def list_dataset_engines(request=None):
    """
    Returns a list of the available dataset engines.
    """
    dataset_service_engines = []

    site_dataset_services = DsModel.objects.all()

    if site_dataset_services:
        # Search for match
        for site_dataset_service in site_dataset_services:
            dataset_service_object = initialize_engine_object(
                engine=site_dataset_service.engine,
                endpoint=site_dataset_service.endpoint,
                apikey=site_dataset_service.apikey,
                username=site_dataset_service.username,
                password=site_dataset_service.password,
                request=request,
            )
            dataset_service_object.public_endpoint = (
                site_dataset_service.public_endpoint
            )

            dataset_service_engines.append(dataset_service_object)

    return dataset_service_engines


def get_dataset_engine(name, app_class=None, request=None):
    """
    Get a dataset engine with the given name.

    Args:
      name (string): Name of the dataset engine to retrieve.
      app_class (class): The app class to include in the search for dataset engines.

    Returns:
      (DatasetEngine): A dataset engine object.
    """
    # If the app_class is given, check it first for a dataset engine
    app_dataset_services = None

    if app_class and issubclass(app_class, TethysAppBase):
        # Instantiate app class and retrieve dataset services list
        app = app_class()
        app_dataset_services = app.dataset_services()

    if app_dataset_services:
        # Search for match
        for app_dataset_service in app_dataset_services:
            # If match is found, initiate engine object
            if app_dataset_service.name == name:
                return initialize_engine_object(
                    engine=app_dataset_service.engine,
                    endpoint=app_dataset_service.endpoint,
                    apikey=app_dataset_service.apikey,
                    username=app_dataset_service.username,
                    password=app_dataset_service.password,
                    request=request,
                )

    # If the dataset engine cannot be found in the app_class, check database for site-wide dataset engines
    site_dataset_services = DsModel.objects.all()

    if site_dataset_services:
        # Search for match
        for site_dataset_service in site_dataset_services:
            # If match is found initiate engine object
            if site_dataset_service.name == name:
                dataset_service_object = initialize_engine_object(
                    engine=site_dataset_service.engine,
                    endpoint=site_dataset_service.endpoint,
                    apikey=site_dataset_service.apikey,
                    username=site_dataset_service.username,
                    password=site_dataset_service.password,
                    request=request,
                )

                dataset_service_object.public_endpoint = (
                    site_dataset_service.public_endpoint
                )
                return dataset_service_object

    raise NameError(
        f'Could not find dataset service with name "{name}". Please check that dataset service with that '
        f"name exists in your app.py."
    )


def list_spatial_dataset_engines():
    """
    Returns a list of available spatial dataset engines
    """
    spatial_dataset_service_engines = []
    # If the dataset engine cannot be found in the app_class, check database for site-wide dataset engines
    site_spatial_dataset_services = SdsModel.objects.all()

    if site_spatial_dataset_services:
        # Search for match
        for site_spatial_dataset_service in site_spatial_dataset_services:
            spatial_dataset_object = initialize_engine_object(
                engine=site_spatial_dataset_service.engine,
                endpoint=site_spatial_dataset_service.endpoint,
                apikey=site_spatial_dataset_service.apikey,
                username=site_spatial_dataset_service.username,
                password=site_spatial_dataset_service.password,
            )
            spatial_dataset_object.public_endpoint = (
                site_spatial_dataset_service.public_endpoint
            )
            spatial_dataset_service_engines.append(spatial_dataset_object)

    return spatial_dataset_service_engines


def get_spatial_dataset_engine(name, app_class=None):
    """
    Get a spatial dataset engine with the given name.

    Args:
      name (string): Name of the dataset engine to retrieve.
      app_class (class): The app class to include in the search for dataset engines.

    Returns:
      (SpatialDatasetEngine): A spatial dataset engine object.
    """
    # If the app_class is given, check it first for a dataset engine
    app_spatial_dataset_services = None

    if app_class and issubclass(app_class, TethysAppBase):
        # Instantiate app class and retrieve dataset services list
        app = app_class()
        app_spatial_dataset_services = app.spatial_dataset_services()

    if app_spatial_dataset_services:
        # Search for match
        for app_spatial_dataset_service in app_spatial_dataset_services:
            # If match is found, initiate engine object
            if app_spatial_dataset_service.name == name:
                return initialize_engine_object(
                    engine=app_spatial_dataset_service.engine,
                    endpoint=app_spatial_dataset_service.endpoint,
                    apikey=app_spatial_dataset_service.apikey,
                    username=app_spatial_dataset_service.username,
                    password=app_spatial_dataset_service.password,
                )

    # If the dataset engine cannot be found in the app_class, check database for site-wide dataset engines
    site_spatial_dataset_services = SdsModel.objects.all()

    if site_spatial_dataset_services:
        # Search for match
        for site_spatial_dataset_service in site_spatial_dataset_services:
            # If match is found initiate engine object
            if site_spatial_dataset_service.name == name:
                spatial_dataset_object = initialize_engine_object(
                    engine=site_spatial_dataset_service.engine,
                    endpoint=site_spatial_dataset_service.endpoint,
                    apikey=site_spatial_dataset_service.apikey,
                    username=site_spatial_dataset_service.username,
                    password=site_spatial_dataset_service.password,
                )

                spatial_dataset_object.public_endpoint = (
                    site_spatial_dataset_service.public_endpoint
                )
                return spatial_dataset_object

    raise NameError(
        'Could not find spatial dataset service with name "{0}". Please check that dataset service with '
        "that name exists in either the Admin Settings or in your app.py.".format(name)
    )


def abstract_is_link(process):
    """
    Determine if the process abstract is a link.

    Args:
      process (owslib.wps.Process): WPS Process object.

    Returns:
      (bool): True if abstract is a link, False otherwise.
    """
    try:
        abstract = process.abstract
    except AttributeError:
        return False

    if abstract[:4] == "http":
        return True

    else:
        return False


def activate_wps(wps, endpoint, name):
    """
    Activate a WebProcessingService object by calling getcapabilities() on it and handle errors appropriately.

    Args:
      wps (owslib.wps.WebProcessingService): A owslib.wps.WebProcessingService object.

    Returns:
      (owslib.wps.WebProcessingService): Returns an activated WebProcessingService object or None if it is invalid.
    """
    # Initialize the object with get capabilities call
    try:
        wps.getcapabilities()
    except HTTPError as e:
        if e.code == 404:
            e.msg = (
                f'The WPS service could not be found at given endpoint "{endpoint}" for site WPS service '
                f'named "{name}". Check the configuration of the WPS service'
            )
            raise e
        else:
            raise e
    except URLError:
        return None

    return wps


def list_wps_service_engines(app_class=None):
    """
    Get all wps engines offered.

    Args:
      app_class (class, optional): The app class to include in the search for wps engines.

    Returns:
      (tuple): A tuple of WPS engine dictionaries.
    """
    # Init vars
    wps_services_list = []

    # If the app_class is given, check it first for a wps engine
    app_wps_services = None

    if app_class and issubclass(app_class, TethysAppBase):
        # Instantiate app class and retrieve wps services list
        app = app_class()
        app_wps_services = app.wps_services()

    if app_wps_services:
        # Search for match
        for app_wps_service in app_wps_services:
            wps = WebProcessingService(
                app_wps_service.endpoint,
                username=app_wps_service.username,
                password=app_wps_service.password,
                verbose=False,
                skip_caps=True,
            )

            activated_wps = activate_wps(
                wps=wps, endpoint=app_wps_service.endpoint, name=app_wps_service.name
            )

            if activated_wps:
                wps_services_list.append(activated_wps)

    # If the wps engine cannot be found in the app_class, check settings for site-wide wps engines
    site_wps_services = WpsModel.objects.all()

    for site_wps_service in site_wps_services:
        # Create OWSLib WebProcessingService engine object
        wps = WebProcessingService(
            site_wps_service.endpoint,
            username=site_wps_service.username,
            password=site_wps_service.password,
            verbose=False,
            skip_caps=True,
        )

        # Initialize the object with get capabilities call
        activated_wps = activate_wps(
            wps=wps, endpoint=site_wps_service.endpoint, name=site_wps_service.name
        )

        if activated_wps:
            wps_services_list.append(activated_wps)

    return wps_services_list


def get_wps_service_engine(name, app_class=None):
    """
    Get a wps engine with the given name.

    Args:
      name (string): Name of the wps engine to retrieve.
      app_class (class, optional): The app class to include in the search for wps engines.

    Returns:
      (owslib.wps.WebProcessingService): A owslib.wps.WebProcessingService object.
    """
    # If the app_class is given, check it first for a wps engine
    app_wps_services = None

    if app_class and issubclass(app_class, TethysAppBase):
        # Instantiate app class and retrieve wps services list
        app = app_class()
        app_wps_services = app.wps_services()

    if app_wps_services:
        # Search for match
        for app_wps_service in app_wps_services:
            # If match is found, initiate engine object
            if app_wps_service.name == name:
                wps = WebProcessingService(
                    app_wps_service.endpoint,
                    username=app_wps_service.username,
                    password=app_wps_service.password,
                    verbose=False,
                    skip_caps=True,
                )

                return activate_wps(
                    wps=wps,
                    endpoint=app_wps_service.endpoint,
                    name=app_wps_service.name,
                )

    # If the wps engine cannot be found in the app_class, check database for site-wide wps engines
    site_wps_services = WpsModel.objects.all()

    if site_wps_services:
        # Search for match
        for site_wps_service in site_wps_services:
            # If match is found initiate engine object
            if site_wps_service.name == name:
                # Create OWSLib WebProcessingService engine object
                wps = WebProcessingService(
                    site_wps_service.endpoint,
                    username=site_wps_service.username,
                    password=site_wps_service.password,
                    verbose=False,
                    skip_caps=True,
                )

                # Initialize the object with get capabilities call
                return activate_wps(
                    wps=wps,
                    endpoint=site_wps_service.endpoint,
                    name=site_wps_service.name,
                )

    raise NameError(
        'Could not find wps service with name "{0}". Please check that a wps service with that name '
        "exists in the admin console or in your app.py.".format(name)
    )
