import yaml
from pathlib import Path
import copy

from django.core.exceptions import ObjectDoesNotExist

TEMPLATE = {
    "necessary": {
        "name": "Necessary",
        "description": "These cookies are essential for {name} to function properly.",
        "is_required": True,
        "is_deletable": False,
        "ordering": 1,
        "cookies": {},
    },
    "preferences": {
        "name": "Preferences",
        "description": "These cookies allow {name} to remember choices you make.",
        "is_required": False,
        "is_deletable": True,
        "ordering": 2,
        "cookies": {},
    },
    "analytics": {
        "name": "Analytics",
        "description": "These cookies help us understand how you interact with {name}.",
        "is_required": False,
        "is_deletable": True,
        "ordering": 3,
        "cookies": {},
    },
    "marketing": {
        "name": "Marketing",
        "description": "These cookies allow {name} to deliver advertisements relevant to you.",
        "is_required": False,
        "is_deletable": True,
        "ordering": 4,
        "cookies": {},
    },
}


def _get_cookie_config(cookie_yaml_path, formal_namespace):
    """
    Load and validate cookie configuration from a YAML file.

    Args:
        cookie_yaml_path (str or Path): Path to the YAML file containing cookie definitions.
        formal_namespace (str): Human-readable app name used when formatting group descriptions.
    Returns:
        dict: Merged and validated cookie configuration.
    """
    _purge_groups = []
    # Support YAML cookie configuration files
    with open(cookie_yaml_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f) or {}

    merged_config = copy.deepcopy(TEMPLATE)

    for group_key in raw_config:
        if group_key not in TEMPLATE.keys():
            raise ValueError(f"Invalid cookie group: {group_key}")
        merged_config[group_key]["cookies"] = raw_config[group_key]

    for group_key, group_data in merged_config.items():
        if not group_data["cookies"]:
            _purge_groups.append(group_key)
        else:
            group_data["description"] = group_data["description"].format(
                name=formal_namespace
            )

    for group_key in _purge_groups:
        merged_config.pop(group_key)

    return merged_config


def sync_cookies_from_yaml(yaml_path, namespace, name):
    """Load cookie definitions from a YAML file and synchronize them.

    This is a thin wrapper that loads the YAML cookie configuration using
    :func:`_get_cookie_config` and then applies the configuration to the
    database by calling :func:`_sync_cookies_from_dict`.

    Args:
        yaml_path (str or Path): Path to the YAML file containing cookie definitions.
        namespace (str): A short namespace to prefix cookie group varnames in the DB
            (typically the app package or "tethys_portal").
        name (str): Human-readable app name used when building group display names.
    """
    cookie_config_dict = _get_cookie_config(yaml_path, name)
    _sync_cookies_from_dict(cookie_config_dict, namespace, name)


def sync_portal_cookies():
    """
    Sync the portal cookies with the template and application-defined cookies.

    This function reads the cookie definitions from the YAML file, merges them
    with the template, and updates the database accordingly.
    """
    # Use YAML cookie resource by default
    _cookies_fpath = Path(__file__).parent / "resources" / "cookies.yaml"
    sync_cookies_from_yaml(_cookies_fpath, "tethys_portal", "Tethys Portal")


def _sync_cookies_from_dict(cookie_config_dict, namespace, name):
    """Synchronize cookie groups and cookies with the database.

    Given a cookie configuration dictionary (as returned by
    :func:`_get_cookie_config`), ensure the database reflects the
    configuration for the provided namespace. The function will:

    - Delete cookie groups (and their cookies) that exist in the DB but are
      not present in the configuration for the namespace.
    - Delete individual cookies from groups when a cookie exists in the DB
      but not in the configuration.
    - Create new cookie groups and cookies when they are present in the
      configuration but missing from the DB.
    - Update existing cookie groups and cookies when properties differ.

    Args:
        cookie_config_dict (dict): Merged cookie configuration dictionary.
        namespace (str): Namespace used as a prefix for DB cookie group varnames.
        name (str): Human-readable app name used when building group display names.
    """
    from cookie_consent.models import CookieGroup, Cookie

    db_cookie_groups = CookieGroup.objects.filter(
        varname__contains=namespace + "__"
    ).all()

    # Delete cookie groups and cookies that are no longer defined in the app
    for db_cookie_group in db_cookie_groups:
        app_stripped_db_groupname = db_cookie_group.varname.replace(
            f"{namespace}__", ""
        )
        if app_stripped_db_groupname not in cookie_config_dict:
            # Delete cookie group and its cookies if not defined in the app
            db_cookie_group.delete()
        else:
            for db_cookie in db_cookie_group.cookie_set.all():
                if (
                    db_cookie.name
                    not in cookie_config_dict[app_stripped_db_groupname]["cookies"]
                ):
                    # Delete cookie if not defined in the app
                    db_cookie.delete()

    # Add or update cookie groups and cookies defined in the app
    for config_cookie_group_varname, config_cookie_group in cookie_config_dict.items():
        try:
            db_cookie_group = CookieGroup.objects.get(
                varname=f"{namespace}__{config_cookie_group_varname}"
            )
        except ObjectDoesNotExist:
            db_cookie_group = None
        if db_cookie_group is None:
            # Create new cookie group
            db_cookie_group = CookieGroup.objects.create(
                varname=f"{namespace}__{config_cookie_group_varname}",
                name=f"{name}: {config_cookie_group['name']}",
                description=config_cookie_group["description"],
                is_required=config_cookie_group["is_required"],
                is_deletable=config_cookie_group["is_deletable"],
                ordering=config_cookie_group["ordering"],
            )
            for config_cookie_name, config_cookie_props in config_cookie_group[
                "cookies"
            ].items():
                Cookie.objects.create(
                    cookiegroup=db_cookie_group,
                    name=config_cookie_name,
                    description=config_cookie_props["description"],
                    path=config_cookie_props["path"],
                    domain=config_cookie_props["domain"],
                )
        else:
            # Update existing cookie group
            db_cookie_group.name = f"{name}: {config_cookie_group['name']}"
            db_cookie_group.description = config_cookie_group["description"]
            db_cookie_group.is_required = config_cookie_group["is_required"]
            db_cookie_group.is_deletable = config_cookie_group["is_deletable"]
            db_cookie_group.ordering = config_cookie_group["ordering"]
            db_cookie_group.save()
            for config_cookie_name, config_cookie_props in config_cookie_group[
                "cookies"
            ].items():
                try:
                    db_cookie = db_cookie_group.cookie_set.get(name=config_cookie_name)
                except ObjectDoesNotExist:
                    db_cookie = None

                if db_cookie is None:
                    # Create new cookie
                    Cookie.objects.create(
                        cookiegroup=db_cookie_group,
                        name=config_cookie_name,
                        description=config_cookie_props["description"],
                        path=config_cookie_props["path"],
                        domain=config_cookie_props["domain"],
                    )
                else:
                    # Update existing cookie
                    db_cookie.description = config_cookie_props["description"]
                    db_cookie.path = config_cookie_props["path"]
                    db_cookie.domain = config_cookie_props["domain"]
                    db_cookie.save()
