from django.utils import timezone
from .models import SettingsCategory


def initial_settings(apps, schema_editor):
    """
    Load the initial settings
    """

    # Create the general settings category
    general_category = SettingsCategory(name="General Settings")

    general_category.save()

    # Create default settings for the general category
    now = timezone.now()
    general_category.setting_set.create(name="Site Title",
                                        content="Tethys",
                                        date_modified=now)

    general_category.setting_set.create(name="Favicon",
                                        content="/static/tethys_portal/images/default_favicon.png",
                                        date_modified=now)

    general_category.setting_set.create(name="Brand Text",
                                        content="Tethys",
                                        date_modified=now)

    general_category.setting_set.create(name="Brand Image",
                                        content="/static/tethys_portal/images/tethys-logo-75.png",
                                        date_modified=now)

    general_category.save()

