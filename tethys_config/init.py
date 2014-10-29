from django.utils import timezone
from .models import SettingsCategory


def initial_settings(apps, schema_editor):
    """
    Load the initial settings
    """
    # Figure out what time it is right now
    now = timezone.now()

    # Create the general settings category
    general_category = SettingsCategory(name="General Settings")
    general_category.save()

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

    # Create the home page settings category
    home_category = SettingsCategory(name="Home Page")
    home_category.save()

    home_category.setting_set.create(name="Hero Text",
                                     content="Water resources modeling\nfor the 21st century.",
                                     date_modified=now)

    home_category.setting_set.create(name="Blurb Text",
                                     content="Welcome to Tethys-designed from the ground up to be fast, efficient, and"
                                             "\neasy to use. Data, modeling, and high performance computing that is "
                                             "easy to use.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 1 Heading",
                                     content="Data and Models",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 1 Body",
                                     content="Publish your data and models with Tethys to make sharing and collaborating"
                                             "a piece of cake.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 1 Image",
                                     content="/static/tethys_portal/images/data.png",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 2 Heading",
                                     content="Cloud Analysis",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 2 Body",
                                     content="Need more computing power? Use Tethys to run your analysis in the cloud.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 2 Image",
                                     content="/static/tethys_portal/images/computing.png",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 3 Heading",
                                     content="Tethys App SDK",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 3 Body",
                                     content="Build custom apps for your models and data to provide easy-to-use"
                                             "workflows for clients, demonstrations, or to use in the classroom.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 3 Image",
                                     content="/static/tethys_portal/images/sdk.png",
                                     date_modified=now)

    home_category.setting_set.create(name="Testimonial Heading",
                                     content="Simple scenario exploration.",
                                     date_modified=now)

    home_category.setting_set.create(name="Testimonial Body",
                                     content="Water resources models can provide powerful insight during critical "
                                             "decision\nmaking, but it often takes an expert to equip a model for a new"
                                             " scenario. The\nTethys team has worked hard to distill the most common"
                                             "scenario\nexploration exercises into easy-to-use workflows and apps.",
                                     date_modified=now)

    home_category.save()


def reverse_init(apps, schema_editor):
    """
    Reverse the initial settings
    """
    pass


