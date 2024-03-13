"""
********************************************************************************
* Name: models.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from urllib.error import HTTPError, URLError

from tethys_portal.optional_dependencies import optional_import, has_module

# optional imports
VALID_ENGINES, VALID_SPATIAL_ENGINES = optional_import(
    ("VALID_ENGINES", "VALID_SPATIAL_ENGINES"),
    from_module="tethys_dataset_services.valid_engines",
)
(
    CkanDatasetEngine,
    GeoServerSpatialDatasetEngine,
    HydroShareDatasetEngine,
) = optional_import(
    ("CkanDatasetEngine", "GeoServerSpatialDatasetEngine", "HydroShareDatasetEngine"),
    from_module="tethys_dataset_services.engines",
)
WPS = optional_import("WebProcessingService", from_module="owslib.wps")
TDSCatalog = optional_import("TDSCatalog", from_module="siphon.catalog")
session_manager = optional_import("session_manager", from_module="siphon.http_util")
AuthException = optional_import("AuthException", from_module="social_core.exceptions")


def validate_url(value):
    """
    Validate URLs
    """
    if "http://" not in value and "https://" not in value:
        raise ValidationError(
            'Invalid Endpoint: Must be prefixed with "http://" or "https://".'
        )


def validate_dataset_service_endpoint(value):
    """
    Validator for dataset service endpoints
    """
    validate_url(value)

    if "/api/3/action" not in value and "/hsapi" not in value:
        raise ValidationError(
            'Invalid Endpoint: CKAN endpoints follow the pattern "http://example.com/api/3/action" '
            'and HydroShare endpoints must follow the pattern "http://example.com/hsapi"'
        )


def validate_spatial_dataset_service_endpoint(value):
    """
    Validator for spatial dataset service endpoints
    """
    validate_url(value)


def validate_wps_service_endpoint(value):
    """
    Validator for spatial dataset service endpoints
    """
    validate_url(value)

    if "/wps/WebProcessingService" not in value:
        raise ValidationError(
            "Invalid Endpoint: 52 North WPS endpoints follow the pattern "
            '"http://example.com/wps/WebProcessingService".'
        )


def validate_persistent_store_port(value):
    """
    Validator for persistent store service ports
    """
    if int(value) < 1024 or int(value) > 65535:
        raise ValidationError(
            "Invalid Port: Persistent Store ports must be an integer between 1024 and 65535."
        )


class DatasetService(models.Model):
    """
    ORM for Dataset Service settings.
    """

    # Define default values for engine choices
    # TODO: These defaults allow the migration to run even if
    #  the dependency that is providing VALID_ENGINES is not installed
    CKAN = "tethys_dataset_services.engines.CkanDatasetEngine"
    HYDROSHARE = "tethys_dataset_services.engines.HydroShareDatasetEngine"
    if has_module(VALID_ENGINES):
        CKAN = VALID_ENGINES["ckan"]
        HYDROSHARE = VALID_ENGINES["hydroshare"]

    # Define default choices for engine selection
    ENGINE_CHOICES = ((CKAN, "CKAN"), (HYDROSHARE, "HydroShare"))

    name = models.CharField(max_length=30, unique=True)
    engine = models.CharField(max_length=200, choices=ENGINE_CHOICES, default=CKAN)
    endpoint = models.CharField(
        max_length=1024, validators=[validate_dataset_service_endpoint]
    )
    public_endpoint = models.CharField(
        max_length=1024, validators=[validate_dataset_service_endpoint], blank=True
    )
    apikey = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Dataset Service"
        verbose_name_plural = "Dataset Services"

    def __str__(self):
        return self.name

    def get_engine(self, request=None):
        """
        Retrieves dataset service engine
        """
        # Get Token for HydroShare interactions
        if self.engine == self.HYDROSHARE:
            # Constants
            HYDROSHARE_OAUTH_PROVIDER_NAME = "hydroshare"
            user = request.user

            try:
                # social = user.social_auth.get(provider='google-oauth2')
                social = user.social_auth.get(provider=HYDROSHARE_OAUTH_PROVIDER_NAME)
                apikey = social.extra_data["access_token"]  # noqa: F841
            except ObjectDoesNotExist:
                # User is not associated with that provider
                # Need to prompt for association
                raise AuthException(
                    "HydroShare authentication required. To automate the authentication prompt "
                    "decorate your controller function with the @ensure_oauth('hydroshare') decorator."
                )

            return HydroShareDatasetEngine(
                endpoint=self.endpoint,
                username=self.username,
                password=self.password,
                apikey=self.apikey,
            )

        return CkanDatasetEngine(
            endpoint=self.endpoint,
            username=self.username,
            password=self.password,
            apikey=self.apikey,
        )


class SpatialDatasetService(models.Model):
    """
    ORM for Spatial Dataset Service settings.
    """

    GEOSERVER = "tethys_dataset_services.engines.GeoServerSpatialDatasetEngine"
    if has_module(VALID_SPATIAL_ENGINES):
        GEOSERVER = VALID_SPATIAL_ENGINES["geoserver"]
    THREDDS = "thredds-engine"

    ENGINE_CHOICES = ((GEOSERVER, "GeoServer"), (THREDDS, "THREDDS"))

    name = models.CharField(max_length=30, unique=True)
    engine = models.CharField(max_length=200, choices=ENGINE_CHOICES, default=GEOSERVER)
    endpoint = models.CharField(
        max_length=1024, validators=[validate_spatial_dataset_service_endpoint]
    )
    public_endpoint = models.CharField(
        max_length=1024,
        validators=[validate_spatial_dataset_service_endpoint],
        blank=True,
    )
    apikey = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Spatial Dataset Service"
        verbose_name_plural = "Spatial Dataset Services"

    def __str__(self):
        return self.name

    def get_engine(self, public=False):
        """
        Retrieves spatial dataset engine.

        Args:
            public (bool): Engine bound to public_endpoint if True. Defaults to False.
        """
        engine = None

        if self.engine == self.GEOSERVER:
            engine = GeoServerSpatialDatasetEngine(
                endpoint=self.endpoint if not public else self.public_endpoint,
                username=self.username,
                password=self.password,
            )
            engine.public_endpoint = self.public_endpoint

        elif self.engine == self.THREDDS:
            if self.username and self.password:
                session_manager.set_session_options(
                    auth=(str(self.username), str(self.password))
                )

            catalog_endpoint = str(
                self.endpoint if not public else self.public_endpoint
            )
            if not catalog_endpoint.endswith(".xml"):
                catalog_endpoint = catalog_endpoint.rstrip("/") + "/catalog.xml"
            engine = TDSCatalog(str(catalog_endpoint))

        return engine


class WebProcessingService(models.Model):
    """
    ORM for Web Processing Services settings.
    """

    name = models.CharField(max_length=30, unique=True)
    endpoint = models.CharField(
        max_length=1024, validators=[validate_wps_service_endpoint]
    )
    public_endpoint = models.CharField(
        max_length=1024, validators=[validate_wps_service_endpoint], blank=True
    )
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Web Processing Service"
        verbose_name_plural = "Web Processing Services"

    def __str__(self):
        return self.name

    def activate(self, wps):
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
                    f'The WPS service could not be found at given endpoint "{self.endpoint}" for site WPS '
                    f'service named "{self.name}". Check the configuration of the WPS service in your '
                    f"portal_config.yml."
                )
                raise e
            else:
                raise e
        except URLError:
            return None

        return wps

    def get_engine(self):
        """
        Get the wps engine.

        Returns:
          (owslib.wps.WebProcessingService): A owslib.wps.WebProcessingService object.
        """
        wps = WPS(
            self.endpoint,
            username=self.username,
            password=self.password,
            verbose=False,
            skip_caps=True,
        )

        return self.activate(wps=wps)


class PersistentStoreService(models.Model):
    """
    ORM for Persistent Store Service settings.
    """

    ENGINE_CHOICES = (("postgresql", "PostgreSQL"),)
    name = models.CharField(max_length=30, unique=True)
    host = models.CharField(max_length=255, default="localhost")
    port = models.IntegerField(
        default=5435, validators=[validate_persistent_store_port]
    )
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    engine = models.CharField(
        max_length=50, default="postgresql", choices=ENGINE_CHOICES
    )
    database = None  #: temporary property for creating engines and URLs with database, but not persisted in database.

    class Meta:
        verbose_name = "Persistent Store Service"
        verbose_name_plural = "Persistent Store Services"

    def __str__(self):
        return self.name

    def get_engine(self):
        """
        Returns a Persistent Store engine
        """
        from sqlalchemy import create_engine

        url = self.get_url()
        return create_engine(url)

    def get_url(self):
        """
        Returns a Persistent Store URL
        """
        from sqlalchemy.engine.url import URL

        url = URL.create(
            drivername=self.engine,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )
        return url
