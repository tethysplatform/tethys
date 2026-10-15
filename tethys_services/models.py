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
from pathlib import Path
from encrypted_fields.fields import EncryptedTextField
from string import Template
import contextlib
import json

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

def _remove_quietly(path):
    """Delete a file if it exists; a concurrent refresh may already have removed it."""
    if path:
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)

def _dask_task_state(job):
    """
    The job's task state straight from the Dask scheduler: (state, error).
    (None, None) if the scheduler no longer knows the task; ("unknown", None) if it can't be reached.
    Tethys's own job status isn't usable here: it marks forget=True jobs complete as soon as they start.
    """
    from .basemap_tasks import dask_task_state

    if not job.key or job.scheduler is None:
        return "unknown", None
    try:
        client = job.scheduler.client
    except Exception:
        return "unknown", None
    try:
        return tuple(client.run_on_scheduler(dask_task_state, key=job.key))
    except Exception:
        return "unknown", None
    finally:
        client.close()

def _refresh_from_result_file(record, apply_result, what):
    """
    Shared refresh for BasemapCapture and BasemapImage while they're processing.

    Applies the task's result file if it has appeared. Otherwise asks the Dask scheduler
    about the task, and marks the record failed only if the task errored, or finished
    without writing a result.
    """
    progress_path = getattr(record, "progress_path", None)

    def apply_if_ready():
        path = record.result_path
        if not (path and os.path.exists(path)):
            return False
        with open(path) as fh:
            result = json.load(fh)
        apply_result(result)
        _remove_quietly(path)  # a concurrent refresh may already have removed it
        _remove_quietly(progress_path)
        return True

    if apply_if_ready():
        return

    job = record.job if record.job_id else None
    if job is None:
        return

    state, error = _dask_task_state(job)
    if state == "erred":
        message = f"The {what} job failed on the Dask worker." + (f"\n{error}" if error else "")
    elif state is None:
        # The scheduler let go of the task, so it finished. Its result may have landed just now.
        if apply_if_ready():
            return
        message = (
            f"The {what} job finished without writing a result file. Check that the Dask workers "
            "share the Tethys media directory, and that the Dask scheduler wasn't restarted mid-job."
        )
    else:
        return  # queued, running, or the scheduler can't be reached right now

    type(record).objects.filter(pk=record.pk).update(status="failed", error_message=message)
    _remove_quietly(progress_path)
    record.refresh_from_db()

class BasemapCapture(models.Model):
    """
    A basemap area saved from a map view as MBTiles, which can then be
    assigned to one or more basemap services.
    """

    class StatusChoices(models.TextChoices):
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    TILE_CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="basemap_captures",
    )
    mbtiles_file = models.FileField(upload_to=basemap_capture_upload_path, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.READY,
    )
    error_message = models.TextField(blank=True, default="")
    job = models.ForeignKey(
        "tethys_compute.DaskJob", 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
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

    @property
    def result_path(self):
        return f"{self.mbtiles_file.path}.result.json" if self.mbtiles_file else None

    @property
    def progress_path(self):
        return f"{self.mbtiles_file.path}.progress.json" if self.mbtiles_file else None

    def get_tile(self, z, x, y):
        """
        Return the bytes of the XYZ tile at z/x/y, or None if the capture doesn't have it.
        """
        import sqlite3
        from pathlib import Path

        if self.status != self.StatusChoices.READY or not self.mbtiles_file:
            return None

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

    def apply_build_result(self, result):
        if result.get("ok"):
            self.mbtiles_file.name = os.path.relpath(result["output_path"], settings.MEDIA_ROOT)
            self.tile_format = result["tile_format"]
            self.status = self.StatusChoices.READY
            self.error_message = ""
        else:
            self.status = self.StatusChoices.FAILED
            self.error_message = result.get("error", "Unknown error")
        self.save()

    def refresh_status(self):
        """Apply the build job's result once it's available, and return the status."""
        if self.status == self.StatusChoices.PROCESSING:
            _refresh_from_result_file(self, self.apply_build_result, "capture")
        return self.status

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

        image = self.images.filter(status=BasemapImage.StatusChoices.READY).order_by("-pk").first()

        if image is None:
            if self.images.exists():
                raise ValueError("No ready basemap images available for this service.")
            raise ValueError("No basemap images available for this service.")

        min_zoom = self.min_zoom
        max_zoom = self.max_zoom
        if image.capture_id:
            min_zoom = image.capture.min_zoom
            max_zoom = image.capture.max_zoom

        options = {
            "url": lazy_tile_url(image.pk),
            "control_label": self.name,
            "minZoom": min_zoom,
            "maxZoom": max_zoom,
        }
        if self.attribution:
            options["attributions"] = self.attribution

        bounds = [image.min_x, image.min_y, image.max_x, image.max_y]
        if None not in bounds:
            options["layer_extent"] = bounds

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
    job = models.ForeignKey(
        "tethys_compute.DaskJob",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
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
        if self.capture_id:
            status = self.capture.refresh_status()  # applies a finished job's result if it's waiting
            if status == BasemapCapture.StatusChoices.FAILED:
                raise ValidationError(f"That capture failed: {self.capture.error_message}")
            if status != BasemapCapture.StatusChoices.READY:
                raise ValidationError("That capture is still being built. Try again in a moment.")

    @property
    def result_path(self):
        return f"{self.generated_file.path}.result.json" if self.generated_file else None

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

    def start_generation(self, user, use_dask=False):
        """Generate the served file: inline for captures, as a background job for uploads."""
        if self.capture_id:
            self.generate_from_capture()  # just copies bounds; no job needed
            return

        from .basemap_jobs import run_basemap_task
        from .basemap_tasks import build_cog

        # Record the output path up front so refresh_status() knows where the result file goes.
        # The tile view only serves READY images, so nothing reads it early.
        self.generated_file.name = generated_basemap_upload_path(
            self, Path(self.source_file.name).stem + "_cog.tif"
        )
        self.status = self.StatusChoices.PROCESSING
        self.error_message = ""
        self.save(update_fields=["generated_file", "status", "error_message"])

        # Clear a result left over from an earlier run of this image
        with contextlib.suppress(FileNotFoundError):
            os.remove(self.result_path)

        try:
            job = run_basemap_task(
                build_cog,
                self.pk,
                self.source_file.path,
                self.generated_file.path,
                georeference_bounds=self.georeference_bounds,
                georeference_epsg=self.georeference_epsg,
                name=f"Generate basemap image {self.pk}",
                user=user,
                result_path=self.result_path,
                apply_inline=self.apply_generation_result,
                use_dask=use_dask,
            )
        except Exception as e:
            BasemapImage.objects.filter(pk=self.pk).update(
                status=self.StatusChoices.FAILED, error_message=str(e)
            )
            raise

        if job:
            # update() so we don't overwrite fields a fast job may already have set
            BasemapImage.objects.filter(pk=self.pk).update(job=job)
        self.refresh_from_db()

    def apply_generation_result(self, result):
        if not result.get("ok"):
            self.status = self.StatusChoices.FAILED
            self.error_message = result.get("error", "Unknown error")
        elif result.get("needs_georeference"):
            self.status = self.StatusChoices.NEEDS_GEOREFERENCE
            self.error_message = ""
        else:
            self.min_x, self.min_y, self.max_x, self.max_y = result["bounds"]
            self.srs = result["srs"]
            self.wkt = result["wkt"]
            if result.get("source_epsg") and not self.georeference_epsg:
                self.georeference_epsg = result["source_epsg"]
            self.generated_file.name = os.path.relpath(result["output_path"], settings.MEDIA_ROOT)
            self.status = self.StatusChoices.READY
            self.error_message = ""
        self.save()

    def refresh_status(self):
        """Apply the generation job's result once it's available, and return the status."""
        if self.status == self.StatusChoices.PROCESSING:
            _refresh_from_result_file(self, self.apply_generation_result, "generation")
        return self.status