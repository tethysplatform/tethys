# Generated by Django 4.2.14 on 2024-08-20 21:42

from django.db import migrations
from django.utils import timezone
from tethys_config.init import (
    initial_settings,
    reverse_init,
    custom_settings,
    reverse_custom,
)


def update_brand_image(apps, schema_editor):
    """
    Update the brand image setting
    """
    Setting = apps.get_model("tethys_config", "Setting")

    # Get the brand image setting
    brand_image_setting = Setting.objects.get(name="Brand Image")

    # Update the brand image setting if it's the default
    if brand_image_setting.content == "/tethys_portal/images/tethys-logo-25.png":
        brand_image_setting.content = (
            "/tethys_portal/images/tethys-on-blue-icon-only.svg"
        )
        brand_image_setting.date_modified = timezone.now()
        brand_image_setting.save()


def reverse_update_brand_image(apps, schema_editor):
    """
    Reverse the brand image setting update
    """
    Setting = apps.get_model("tethys_config", "Setting")

    # Get the brand image setting
    brand_image_setting = Setting.objects.get(name="Brand Image")

    # Update the brand image setting if it's the default
    if (
        brand_image_setting.content
        == "/tethys_portal/images/tethys-on-blue-icon-only.svg"
    ):
        brand_image_setting.content = "/tethys_portal/images/tethys-logo-25.png"
        brand_image_setting.date_modified = timezone.now()
        brand_image_setting.save()


class Migration(migrations.Migration):

    dependencies = [
        ("tethys_config", "0001_initial_40"),
    ]

    operations = [
        migrations.RunPython(
            update_brand_image, reverse_code=reverse_update_brand_image
        ),
    ]
