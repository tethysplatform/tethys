# Generated by Django 2.2.8 on 2020-01-18 02:43

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import tethys_apps.base.mixins
import tethys_services.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tethys_services", "0001_initial_30"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProxyApp",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "endpoint",
                    models.CharField(
                        max_length=1024,
                        validators=[tethys_services.models.validate_url],
                    ),
                ),
                (
                    "logo_url",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        validators=[tethys_services.models.validate_url],
                    ),
                ),
                ("description", models.TextField(blank=True, max_length=2048)),
                ("tags", models.CharField(blank=True, default="", max_length=200)),
                ("enabled", models.BooleanField(default=True)),
                ("show_in_apps_library", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Proxy App",
                "verbose_name_plural": "Proxy Apps",
            },
        ),
        migrations.CreateModel(
            name="TethysApp",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("package", models.CharField(default="", max_length=200, unique=True)),
                ("name", models.CharField(default="", max_length=200)),
                (
                    "description",
                    models.TextField(blank=True, default="", max_length=1000),
                ),
                ("enable_feedback", models.BooleanField(default=False)),
                (
                    "feedback_emails",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            blank=True, max_length=200, null=True
                        ),
                        default=list,
                        size=None,
                    ),
                ),
                ("tags", models.CharField(blank=True, default="", max_length=200)),
                ("index", models.CharField(default="", max_length=200)),
                ("icon", models.CharField(default="", max_length=200)),
                ("root_url", models.CharField(default="", max_length=200)),
                ("color", models.CharField(default="", max_length=10)),
                ("enabled", models.BooleanField(default=True)),
                ("show_in_apps_library", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Tethys App",
                "verbose_name_plural": "Installed Apps",
                "permissions": (
                    ("view_app", "Can see app in library"),
                    ("access_app", "Can access app"),
                ),
            },
            bases=(models.Model, tethys_apps.base.mixins.TethysBaseMixin),
        ),
        migrations.CreateModel(
            name="TethysAppSetting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="", max_length=200)),
                (
                    "description",
                    models.TextField(blank=True, default="", max_length=1000),
                ),
                ("required", models.BooleanField(default=True)),
                ("initializer", models.CharField(default="", max_length=1000)),
                ("initialized", models.BooleanField(default=False)),
                (
                    "tethys_app",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="settings_set",
                        to="tethys_apps.TethysApp",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TethysExtension",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("package", models.CharField(default="", max_length=200, unique=True)),
                ("name", models.CharField(default="", max_length=200)),
                (
                    "description",
                    models.TextField(blank=True, default="", max_length=1000),
                ),
                ("root_url", models.CharField(default="", max_length=200)),
                ("enabled", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Tethys Extension",
                "verbose_name_plural": "Installed Extensions",
            },
            bases=(models.Model, tethys_apps.base.mixins.TethysBaseMixin),
        ),
        migrations.CreateModel(
            name="CustomSetting",
            fields=[
                (
                    "tethysappsetting_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="tethys_apps.TethysAppSetting",
                    ),
                ),
                ("value", models.CharField(blank=True, default="", max_length=1024)),
                ("value_json", models.JSONField(blank=True, default=dict)),

                ("default", models.CharField(blank=True, default="", max_length=1024)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("STRING", "String"),
                            ("INTEGER", "Integer"),
                            ("FLOAT", "Float"),
                            ("BOOLEAN", "Boolean"),
                            ("JSON", "Json"),

                        ],
                        default="STRING",
                        max_length=200,
                    ),
                ),
            ],
            bases=("tethys_apps.tethysappsetting",),
        ),
        migrations.CreateModel(
            name="WebProcessingServiceSetting",
            fields=[
                (
                    "tethysappsetting_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="tethys_apps.TethysAppSetting",
                    ),
                ),
                (
                    "web_processing_service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tethys_services.WebProcessingService",
                    ),
                ),
            ],
            bases=("tethys_apps.tethysappsetting",),
        ),
        migrations.CreateModel(
            name="SpatialDatasetServiceSetting",
            fields=[
                (
                    "tethysappsetting_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="tethys_apps.TethysAppSetting",
                    ),
                ),
                (
                    "engine",
                    models.CharField(
                        choices=[
                            (
                                "tethys_dataset_services.engines.GeoServerSpatialDatasetEngine",
                                "GeoServer",
                            ),
                            ("thredds-engine", "THREDDS"),
                        ],
                        default="tethys_dataset_services.engines.GeoServerSpatialDatasetEngine",
                        max_length=200,
                    ),
                ),
                (
                    "spatial_dataset_service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tethys_services.SpatialDatasetService",
                    ),
                ),
            ],
            bases=("tethys_apps.tethysappsetting",),
        ),
        migrations.CreateModel(
            name="PersistentStoreDatabaseSetting",
            fields=[
                (
                    "tethysappsetting_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="tethys_apps.TethysAppSetting",
                    ),
                ),
                ("spatial", models.BooleanField(default=False)),
                ("dynamic", models.BooleanField(default=False)),
                (
                    "persistent_store_service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tethys_services.PersistentStoreService",
                    ),
                ),
            ],
            bases=("tethys_apps.tethysappsetting",),
        ),
        migrations.CreateModel(
            name="PersistentStoreConnectionSetting",
            fields=[
                (
                    "tethysappsetting_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="tethys_apps.TethysAppSetting",
                    ),
                ),
                (
                    "persistent_store_service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tethys_services.PersistentStoreService",
                    ),
                ),
            ],
            bases=("tethys_apps.tethysappsetting",),
        ),
        migrations.CreateModel(
            name="DatasetServiceSetting",
            fields=[
                (
                    "tethysappsetting_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="tethys_apps.TethysAppSetting",
                    ),
                ),
                (
                    "engine",
                    models.CharField(
                        choices=[
                            (
                                "tethys_dataset_services.engines.CkanDatasetEngine",
                                "CKAN",
                            ),
                            (
                                "tethys_dataset_services.engines.HydroShareDatasetEngine",
                                "HydroShare",
                            ),
                        ],
                        default="tethys_dataset_services.engines.CkanDatasetEngine",
                        max_length=200,
                    ),
                ),
                (
                    "dataset_service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tethys_services.DatasetService",
                    ),
                ),
            ],
            bases=("tethys_apps.tethysappsetting",),
        ),
    ]
