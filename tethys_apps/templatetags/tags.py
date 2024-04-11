from django import template
import re

register = template.Library()


def parse_tags(app_tags):
    """
    Parse given tags value, standardize, and remove duplicates.
    """
    app_tags = [_f for _f in re.split("[,]+ *", app_tags) if _f]
    tags = []

    for tag in app_tags:
        tag = tag.replace('"', "")
        tag = tag.replace("'", "")
        tag = re.sub(r"\s+", "-", tag)
        tag = tag.lower()
        tags.append(tag)

    tags = list(set(tags))
    return tags


@register.filter
def get_tags_from_apps(apps):
    tags_list = set([])

    if len(apps.get("configured", [])) > 5:
        for app in apps.get("configured"):
            if isinstance(app, dict):
                if not app.get("enabled", True) or not app.get(
                    "show_in_apps_library", True
                ):
                    continue
                app_tags = app["tags"]
            else:
                if not app.enabled or not app.show_in_apps_library:
                    continue
                app_tags = app.tags

            # Standardize tags and remove duplicates
            tags = parse_tags(app_tags)

            tag_tuples = []
            for tag in tags:
                # Create human readable version of tag for search field
                human_tag = tag.replace("-", " ")
                human_tag = human_tag.title()
                # Create tuple pairs with tag and human readable version
                tag_tuples.append((tag, human_tag))

            tags_list.update(tag_tuples)

    return list(tags_list)


@register.filter
def get_tag_class(app):
    if isinstance(app, dict):
        app_tags = app["tags"]
    else:
        app_tags = app.tags

    # Standardize tags and remove duplicates
    tags = parse_tags(app_tags)

    # Join tags into a single space delimited string
    tags_list = " ".join(tags)
    return tags_list


@register.filter
def url(app, controller_name):
    """
    A shortcut to add the active Tethys app namespace to a controller name.

    Args:
        app: the active Tethys app loaded in the context
        controller_name: the name of the controller from the active Tethys app to get the URL for

    Returns:
        str: A controller name with the namespace from the active Tethys app prepended

    Usage:
        Be sure to include the ``tethys`` argument to the ``load`` template tag.

        .. code-block:: html+django

            {% load tethys %}

            {% url tethys_app|url:'home' %}

    Note:
        This filter allows you to avoid having the app package hardcoded in your templates. If the active app package is ``my_first_app``, then the following would be equivalent:

        Recommended Usage:

        .. code-block:: html+django

            {% load tethys %}

            {% url tethys_app|url:'home' %}

        Equivalent (but not recommended):

        .. code-block:: html+django

            {% url 'my_first_app:home' %}

    """
    app_package = app["package"] if isinstance(app, dict) else app.package
    return f"{app_package}:{controller_name}"


@register.filter
def public(app, static_path):
    """
    Add the active Tethys app namespace to a public filepath.

    Args:
        app: the active Tethys app loaded in the context
        static_path: the relative path to a static file in the active Tethys app's ``public`` directory

    Returns:
        str: The path to the static file with the active Tethys app's namespace prepended

    Usage:
        Be sure to include the ``tethys`` argument to the ``load`` template tag.

        .. code-block:: html+django

            {% load static tethys %}

            {% static tethys_app|public:'css/main.css' %}

    Note:
        This filter allows you to avoid having the app package hardcoded in your templates. If the active app package is ``my_first_app``, then the following would be equivalent:

        Recommended Usage:

        .. code-block:: html+django

            {% load static tethys %}

            {% static tethys_app|public:'css/main.css' %}

        Equivalent (but not recommended):

        .. code-block:: html+django

            {% load static %}

            {% static 'my_first_app/css/main.css' %}

    """
    app_package = app["package"] if isinstance(app, dict) else app.package
    return f"{app_package}/{static_path}"
