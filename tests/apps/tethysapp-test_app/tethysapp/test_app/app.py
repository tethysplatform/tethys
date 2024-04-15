from tethys_sdk.base import TethysAppBase
from tethys_sdk.app_settings import (
    CustomSetting,
    JSONCustomSetting,
    SecretCustomSetting,
    PersistentStoreDatabaseSetting,
    PersistentStoreConnectionSetting,
    DatasetServiceSetting,
    SpatialDatasetServiceSetting,
    WebProcessingServiceSetting,
    SchedulerSetting,
)

from tethys_sdk.handoff import HandoffHandler


class App(TethysAppBase):
    """
    Tethys app class for Test App.
    """

    name = "Test App"
    description = "Place a brief description of your app here."
    index = "home"
    package = "test_app"
    icon = f"{package}/images/icon.gif"
    root_url = "test-app"
    color = "#2c3e50"
    tags = ""
    enable_feedback = False
    feedback_emails = []

    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting(
                name="default_name",
                type=CustomSetting.TYPE_STRING,
                description="Default model name.",
                include_in_api=True,
                required=True,
            ),
            CustomSetting(
                name="max_count",
                type=CustomSetting.TYPE_INTEGER,
                description="Maximum allowed count in a method.",
                include_in_api=False,
                required=False,
            ),
            CustomSetting(
                name="change_factor",
                type=CustomSetting.TYPE_FLOAT,
                description="Change factor that is applied to some process.",
                required=False,
            ),
            CustomSetting(
                name="enable_feature",
                type=CustomSetting.TYPE_BOOLEAN,
                description="Enable this feature when True.",
                include_in_api=True,
                required=False,
            ),
            JSONCustomSetting(
                name="JSON_setting_not_default_value_required",
                description="This is JSON setting without a default value",
                required=True,
            ),
            JSONCustomSetting(
                name="JSON_setting_not_default_value",
                description="This is JSON setting without a default value",
                required=False,
            ),
            JSONCustomSetting(
                name="JSON_setting_default_value_required",
                description="This is JSON setting with a default value",
                include_in_api=True,
                required=True,
                default={"Test": "JSON test String"},
            ),
            JSONCustomSetting(
                name="JSON_setting_default_value",
                description="This is JSON setting with a default value",
                include_in_api=False,
                required=False,
                default={"Test": "JSON test String"},
            ),
            SecretCustomSetting(
                name="Secret_Test_required",
                description="This is SECRET setting with required True",
                include_in_api=True,
                required=True,
            ),
            SecretCustomSetting(
                name="Secret_Test2_without_required",
                description="This is SECRET setting with required False",
                required=False,
            ),
        )

        return custom_settings

    def persistent_store_settings(self):
        """
        Example persistent_store_settings method.
        """
        ps_settings = (
            # Connection only, no database
            PersistentStoreConnectionSetting(
                name="primary",
                description="Connection with superuser role needed.",
                required=True,
            ),
            # Connection only, no database
            PersistentStoreConnectionSetting(
                name="creator", description="Create database role only.", required=False
            ),
            # Spatial database
            PersistentStoreDatabaseSetting(
                name="spatial_db",
                description="for storing important spatial stuff",
                required=True,
                initializer="appsettings.model.init_spatial_db",
                spatial=True,
            ),
            # Non-spatial database
            PersistentStoreDatabaseSetting(
                name="temp_db",
                description="for storing temporary stuff",
                required=False,
                initializer="appsettings.model.init_temp_db",
                spatial=False,
            ),
        )

        return ps_settings

    def dataset_service_settings(self):
        """
        Example dataset_service_settings method.
        """
        ds_settings = (
            DatasetServiceSetting(
                name="primary_ckan",
                description="Primary CKAN service for app to use.",
                engine=DatasetServiceSetting.CKAN,
                required=True,
            ),
            DatasetServiceSetting(
                name="hydroshare",
                description="HydroShare service for app to use.",
                engine=DatasetServiceSetting.HYDROSHARE,
                required=False,
            ),
        )

        return ds_settings

    def spatial_dataset_service_settings(self):
        """
        Example spatial_dataset_service_settings method.
        """
        sds_settings = (
            SpatialDatasetServiceSetting(
                name="primary_geoserver",
                description="spatial dataset service for app to use",
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True,
            ),
            SpatialDatasetServiceSetting(
                name="primary_thredds",
                description="spatial dataset service for app to use",
                engine=SpatialDatasetServiceSetting.THREDDS,
                required=False,
            ),
        )

        return sds_settings

    def scheduler_settings(self):
        """
        Example scheduler_settings method.
        """
        scheduler_settings = (
            SchedulerSetting(
                name="primary_condor",
                description="HTCondor scheduler",
                engine=SchedulerSetting.HTCONDOR,
                required=True,
            ),
            SchedulerSetting(
                name="primary_dask",
                description="Dask scheduler",
                engine=SchedulerSetting.DASK,
                required=False,
            ),
        )

        return scheduler_settings

    def web_processing_service_settings(self):
        """
        Example wps_services method.
        """
        wps_services = (
            WebProcessingServiceSetting(
                name="primary_52n",
                description="WPS service for app to use",
                required=True,
            ),
        )

        return wps_services

    def handoff_handlers(self):
        """
        Register some handoff handlers
        """
        handoff_handlers = (
            HandoffHandler(name="test_name", handler="test_app.handoff.csv"),
        )
        return handoff_handlers
