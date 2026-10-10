"""
********************************************************************************
* Name: models.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from urllib.error import HTTPError, URLError
import os
from encrypted_fields.fields import EncryptedTextField
from string import Template

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


PERSISTENT_STORE_SERVICE_ENGINE_CHOICES = (
    ("postgresql", "PostgreSQL"),
    ("sqlite", "SQLite"),
)


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


class PersistentStoreServiceBase(models.Model):
    """
    ORM for Persistent Store Service settings.
    """

    name = models.CharField(max_length=30, unique=True)
    engine = models.CharField(
        max_length=50,
        default="postgresql",
        choices=PERSISTENT_STORE_SERVICE_ENGINE_CHOICES,
    )
    database = None  #: temporary property for creating engines and URLs with database, but not persisted in database.

    class Meta:
        verbose_name = "Persistent Store Service"
        verbose_name_plural = "Persistent Store Services"
        abstract = True

    def __str__(self):
        return self.name

    def get_engine(self, **kwargs):
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
        return None


class PostgresPersistentStoreService(PersistentStoreServiceBase):
    engine = models.CharField(
        max_length=50, default="postgresql", choices=(("postgresql", "PostgreSQL"),)
    )
    host = models.CharField(max_length=255, default="localhost")
    port = models.IntegerField(
        default=5435, validators=[validate_persistent_store_port]
    )
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "PostgreSQL Persistent Store Service"
        verbose_name_plural = "PostgreSQL Persistent Store Services"
        db_table = "tethys_services_persistentstoreservice_postgres"

    def get_url(self):
        """
        Returns a Persistent Store URL
        """
        from sqlalchemy.engine.url import URL

        return URL.create(
            drivername=self.engine,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )


class SQLitePersistentStoreService(PersistentStoreServiceBase):
    dir_path = models.CharField(max_length=255)
    engine = models.CharField(
        max_length=50, default="sqlite", choices=(("sqlite", "SQLite"),)
    )

    class Meta:
        verbose_name = "SQLite Persistent Store Service"
        verbose_name_plural = "SQLite Persistent Store Services"
        db_table = "tethys_services_persistentstoreservice_sqlite"

    def get_engine(self, spatial=False):
        """
        Returns a Persistent Store engine
        """
        from sqlalchemy import create_engine
        from geoalchemy2 import load_spatialite
        from sqlalchemy.event import listen

        url = self.get_url()
        engine = create_engine(url)
        if spatial:
            if not os.environ.get("SPATIALITE_LIBRARY_PATH"):
                raise EnvironmentError(
                    "SPATIALITE_LIBRARY_PATH environment variable must be set to enable spatial features on SQLite persistent stores. To enable SpatiaLite support, Install and set the SPATIALITE_LIBRARY_PATH environment variable to the path of the SpatiaLite library on your system. Check https://www.gaia-gis.it/fossil/libspatialite/home for installation instructions."
                )
            listen(engine, "connect", load_spatialite)

        return engine

    def get_url(self):
        db_file = os.path.join(self.dir_path, f"{self.database}.sqlite")
        return f"sqlite:///{db_file}"


class SecureMapService(models.Model):
    """
    ORM for Secure Map Service settings.
    """

    name = models.CharField(max_length=30, unique=True)
    legend_title = models.CharField(max_length=100, blank=True)
    endpoint = models.CharField(max_length=1024, validators=[validate_url])
    authentication_method = models.CharField(
        max_length=100, blank=True, choices=[("api_key", "API Key"), ("oauth", "OAuth")]
    )
    api_key = EncryptedTextField(blank=True, null=True)
    oauth_provider = models.CharField(max_length=100, blank=True)
    service_type = models.CharField(
        max_length=50,
        choices=[
            ("ImageWMS", "WMS"),
            ("GML", "GML"),
            ("GeoJSON", "GeoJSON"),
            ("REST", "REST/JSON API"),
        ],
        default="ImageWMS",
    )
    params = models.JSONField(blank=True, null=True, default=dict)
    use_proxy = models.BooleanField(default=False)  # Hide API key in requests

    class Meta:
        verbose_name = "Secure Map Service"
        verbose_name_plural = "Secure Map Services"

    def __str__(self):
        return self.name

    @classmethod
    def get_authentication_method_options(cls):
        """
        Get the available authentication method options for the SecureMapService model.
        This method is used for populating the choices in the admin form.
        """
        return [
            value for value, _ in cls._meta.get_field("authentication_method").choices
        ]

    def get_oauth_token(self, user):
        """
        Retrieve the OAuth token for the given user.
        Args:
            user (User): The user for whom to retrieve the OAuth token.

        Returns:
            str: The OAuth token for the user.
        """
        if self.authentication_method != "oauth":
            raise ValueError(
                "Authentication method must be 'oauth' to retrieve an OAuth token."
            )
        if not self.oauth_provider:
            raise ValueError(
                "OAuth provider must be specified to retrieve an OAuth token."
            )

        try:
            auth = user.social_auth.get(provider=self.oauth_provider)
        except ObjectDoesNotExist:
            raise ValueError(f"User not linked to {self.oauth_provider}.")

        access_token = auth.extra_data.get("access_token")
        if not access_token:
            raise ValueError("No access token found for user.")

        return access_token

    def get_resolved_params(self):
        """
        Resolve template variables in the service parameters using the model's attributes.

        Returns:
            dict: A dictionary of resolved parameters.
        """
        if not self.params:
            return {}

        safe_attribute_names = {
            f.name: str(getattr(self, f.name, "") or "") for f in self._meta.fields
        }

        resolved_params = {}
        for key, value in self.params.items():
            if isinstance(value, str):
                value = Template(value).safe_substitute(safe_attribute_names)
            resolved_params[key] = value
        return resolved_params

    def update_params(self, new_params):
        """
        Merge the given parameters into the parameters of the service and save.

        Note that a SecureMapService may be shared by multiple settings and apps,
        so updating its parameters affects every app that uses it.

        Args:
            new_params (dict): The parameters to merge into the service parameters.
        """
        params = self.params or {}
        params.update(new_params)
        self.params = params
        self.save()

def original_basemap_upload_path(instance, filename):
    return f"basemaps/original/{instance.basemap_service.name}/{filename}"

def generated_basemap_upload_path(instance, filename):
    return f"basemaps/generated/{instance.basemap_service.name}/{filename}"

def basemap_capture_upload_path(instance, filename):
    return f"basemaps/captures/{filename}"


class BasemapCapture(models.Model):
    """
    A basemap area saved from a map view as MBTiles, which can then be
    assigned to one or more basemap services.
    """

    TILE_CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="basemap_captures",
    )
    mbtiles_file = models.FileField(upload_to=basemap_capture_upload_path)
    tile_format = models.CharField(max_length=10, default="png")
    min_zoom = models.PositiveSmallIntegerField()
    max_zoom = models.PositiveSmallIntegerField()
    # Bounds in EPSG:3857
    min_x = models.FloatField()
    min_y = models.FloatField()
    max_x = models.FloatField()
    max_y = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} (z{self.min_zoom}-{self.max_zoom})"

    @property
    def tile_content_type(self):
        return self.TILE_CONTENT_TYPES.get(self.tile_format, "application/octet-stream")

    def get_tile(self, z, x, y):
        """
        Return the bytes of the XYZ tile at z/x/y, or None if the capture doesn't have it.
        """
        import sqlite3
        from pathlib import Path

        uri = Path(self.mbtiles_file.path).as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            # MBTiles rows use the TMS scheme: row 0 is the southernmost row
            row = conn.execute(
                "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
                (z, x, (2**z - 1) - y),
            ).fetchone()
        finally:
            conn.close()
        return row[0] if row else None

class BasemapService(models.Model):

    name = models.CharField(max_length=30, unique=True)
    attribution = models.CharField(max_length=255, blank=True)
    min_zoom = models.IntegerField(default=0)
    max_zoom = models.PositiveSmallIntegerField(default=22)

    def __str__(self):
        return self.name

    def as_basemap(self):
        from django.urls import reverse
        from django.utils.functional import lazy

        def _tile_url(image_pk):
            url = reverse(
                "basemap_tile",
                kwargs={
                    "image_id": image_pk,
                    "z": 0,
                    "x": 0,
                    "y": 0,
                }
            )

            if "/0/0/0.png" not in url:
                raise ValueError(f"Unexpected tile URL shape: {url}")
            return url.replace("/0/0/0.png", "/{z}/{x}/{y}.png")

        lazy_tile_url = lazy(_tile_url, str)

        # TODO fix this
        if not self.images.exists():
            raise ValueError("No basemap images available for this service.")
        image = self.images.first()

        options = {
            "url": lazy_tile_url(image.pk),
            "control_label": self.name,
            "attribution": self.attribution,
            "min_zoom": self.min_zoom,
            "max_zoom": self.max_zoom,
        }

        bounds = [image.min_x, image.min_y, image.max_x, image.max_y]
        if None not in bounds:
            options["layer_extent"] = bounds

        if image.capture_id:
            options["minZoom"] = image.capture.min_zoom
            options["maxZoom"] = image.capture.max_zoom

        
        if image.capture_id:
            # Past the capture's deepest zoom, have OpenLayers scale up those tiles
            # instead of requesting tiles that don't exist
            options["maxZoom"] = image.capture.max_zoom
        return {"XYZ": options}

class BasemapImage(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        FAILED = 'failed', 'Failed'
        READY = 'ready', 'Ready'
        NEEDS_GEOREFERENCE = 'needs_georeference', 'Needs Georeference'

    basemap_service = models.ForeignKey(BasemapService, on_delete=models.CASCADE, related_name="images")
    source_file = models.FileField(upload_to=original_basemap_upload_path, blank=True)
    # Set instead of source_file when the image is a capture saved from a map view
    capture = models.ForeignKey(
        BasemapCapture, on_delete=models.PROTECT, blank=True, null=True, related_name="images"
    )
    generated_file = models.FileField(upload_to=generated_basemap_upload_path, blank=True, null=True)
    status = models.CharField(max_length=30, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    error_message = models.TextField(blank=True, null=True)
    srs = models.CharField(max_length=64, blank=True, null=True)
    wkt = models.TextField(blank=True, null=True)
    min_x = models.FloatField(blank=True, null=True)
    min_y = models.FloatField(blank=True, null=True)
    max_x = models.FloatField(blank=True, null=True)
    max_y = models.FloatField(blank=True, null=True)
    georeference_bounds = models.JSONField(blank=True, null=True)
    georeference_epsg = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        if self.capture_id:
            return f"{self.capture.name} ({self.basemap_service.name})"
        return f"{self.source_file.name.split('/')[-1].split('.')[0]} ({self.basemap_service.name})"

    def clean(self):
        if bool(self.source_file) == bool(self.capture_id):
            raise ValidationError("Upload a source file or choose a capture, but not both.")

    def generate_from_capture(self):
        """
        Captures are already web mercator tiles, so they are served as-is: just copy the bounds.
        """
        capture = self.capture
        self.min_x, self.min_y, self.max_x, self.max_y = (
            capture.min_x, capture.min_y, capture.max_x, capture.max_y
        )
        self.srs = "3857"
        self.wkt = ""
        self.status = self.StatusChoices.READY
        self.error_message = ""
        self.save()

    def generate(self):
        import tempfile
        from pathlib import Path
        from django.core.files import File
        try:
            import rasterio
            from rasterio.warp import calculate_default_transform, reproject, Resampling
            from rasterio.shutil import copy as rio_copy
            from rasterio.transform import from_bounds
        except ImportError:
            raise ImportError("rasterio is required to generate basemap images.")
        
        if self.capture_id:
            self.generate_from_capture()
            return

        self.status = self.StatusChoices.PROCESSING
        self.save(update_fields=["status"])

        try:
            with rasterio.open(self.source_file.path) as src:
                src_crs = src.crs
                src_transform = src.transform

                if src_crs is None:
                    if not self.georeference_bounds:
                        self.status = self.StatusChoices.NEEDS_GEOREFERENCE
                        self.error_message = ""
                        self.save(update_fields=["status", "error_message"])
                        return

                    min_x, min_y, max_x, max_y = self.georeference_bounds
                    src_crs = rasterio.crs.CRS.from_epsg(self.georeference_epsg)
                    src_transform = from_bounds(min_x, min_y, max_x, max_y, src.width, src.height)
                    self.srs = str(src_crs.to_epsg() or "")
                    self.wkt = src_crs.to_wkt()

                else:
                    self.srs = str(src_crs.to_epsg() or "")
                    self.wkt = src_crs.to_wkt()
                    self.georeference_epsg = src_crs.to_epsg()

                dst_crs = "EPSG:3857"
                src_bounds = (
                    tuple(self.georeference_bounds) if src.crs is None else src.bounds
                )
                transform, width, height = calculate_default_transform(
                    src_crs, dst_crs, src.width, src.height, *src_bounds
                )

                profile = src.profile.copy()

                profile = {
                    "driver": "GTiff",
                    "dtype": src.dtypes[0],
                    "count": src.count,
                    "crs": dst_crs,
                    "transform": transform,
                    "width": width,
                    "height": height,
                    "tiled": True,
                    "blockxsize": 512,
                    "blockysize": 512,
                    "compress": "DEFLATE",
                }

                with tempfile.TemporaryDirectory() as tmpdir:
                    warped = Path(tmpdir) / "warped.tif"

                    with rasterio.open(warped, "w", **profile) as dst:
                        for i in range(1, src.count + 1):
                            reproject(
                                source = src.read(i) if src.crs is None else rasterio.band(src, i),
                                destination=rasterio.band(dst, i),
                                src_transform=src_transform,
                                src_crs=src_crs,
                                dst_transform=transform,
                                dst_crs=dst_crs,
                                resampling=Resampling.bilinear,
                                src_nodata=None,
                                dst_nodata=0
                            )

                    cog = Path(tmpdir) / "cog.tif"
                    rio_copy(warped, cog, driver="COG", compress="DEFLATE", overview_resampling="nearest")

                    with rasterio.open(cog) as final:
                        self.min_x, self.min_y, self.max_x, self.max_y = final.bounds
                        self.srs = str(final.crs.to_epsg() or "")
                        self.wkt = final.crs.to_wkt()

                    if self.generated_file:
                        self.generated_file.delete(save=False)

                    generated_name = Path(self.source_file.name).stem + "_cog.tif"
                    with open(cog, "rb") as fh:
                        self.generated_file.save(generated_name, File(fh), save=False)

            self.status = self.StatusChoices.READY
            self.error_message = ""
            self.save()

        except Exception as e:
            print(f"Error occurred: {e}")
            self.status = self.StatusChoices.FAILED
            self.error_message = str(e)
            self.save(update_fields=["status", "error_message"])
            raise