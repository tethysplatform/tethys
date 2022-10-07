# flake8: noqa

import re
import inspect
from django.utils import timezone
from tethys_cli.site_commands import add_site_parser


args = re.findall(
    "add_argument\(.*?dest='(.*?)'.*?help='(.*?)'\)",
    inspect.getsource(add_site_parser),
    re.DOTALL,
)

args_dict = {arg[0]: arg[1] for arg in args}
args_dict.pop("restore_defaults")

custom_templates_settings = {
    k: v for k, v in args_dict.items() if k.endswith("template")
}
custom_styles_settings = {k: v for k, v in args_dict.items() if k.endswith("css")}
home_page_settings = {
    k: v
    for k, v in args_dict.items()
    if k.split("_")[0].upper() in ["HERO", "BLURB", "FEATURE", "CALL"]
}
general_settings = {
    k: v
    for k, v in args_dict.items()
    if k
    not in set(custom_styles_settings)
    .union(custom_styles_settings)
    .union(home_page_settings)
}

col1_len = 30
col2_len = 80


def get_table_sep(num_key_cols):
    key_col = "=" * col1_len
    key_cols = " ".join([key_col] * num_key_cols)
    return f'{key_cols} {"=" * col2_len}'


def get_table_header(key_cols):
    table_sep = get_table_sep(len(key_cols))
    key_cols = " ".join([f"{key_col:<{col1_len}}" for key_col in key_cols])
    return f'{table_sep}\n{key_cols} {"Description":<{col2_len}}\n{table_sep}\n'


def get_portal_config_key(key):
    return key.upper()


def get_admin_setting(key):
    return key.replace("_", " ").title()


def get_site_command_option(key):
    return f"--{key.replace('_', '-')}"


pre_post_statements = {
    "GENERAL_SETTINGS": (
        "The following settings can be used to modify global features of the site. Access the settings using the "
        "Site Settings > General Settings links on the admin pages or under the ``GENERAL_SETTINGS`` category "
        "in the ``site_settings`` section of the :file:`portal_config.yml` file.",
        "",
    ),
    "HOME_PAGE": (
        "The following settings can be used to modify the content on the home page. Access the settings using the "
        "Site Settings > Home Page links on the admin pages or under the ``HOME_PAGE`` category "
        "in the ``site_settings`` section of the :file:`portal_config.yml` file.",
        "For more advanced customization, you may use the Custom Styles and Custom Template options to completely "
        "replace the Home Page or Apps Library page CSS and HTML.",
    ),
    "CUSTOM_STYLES": (
        "The following settings can be used to add additional CSS to the Home page, Apps Library page, and "
        "portal-wide. Access the settings using the Site Settings > Custom Styles links on the admin pages or under "
        "the ``CUSTOM_STYLES`` category in the ``site_settings`` section of the :file:`portal_config.yml` file.",
        "",
    ),
    "CUSTOM_TEMPLATES": (
        "The following settings can be used to override the templates for the Home page and Apps Library page. "
        "Access the settings using the Site Settings > Custom Templates links on the admin pages or under "
        "the ``CUSTOM_TEMPLATES`` category in the ``site_settings`` section of the :file:`portal_config.yml` file..",
        "",
    ),
}


def get_table():
    output = ""
    for category, settings in {
        "GENERAL_SETTINGS": general_settings,
        "HOME_PAGE": home_page_settings,
        "CUSTOM_STYLES": custom_styles_settings,
        "CUSTOM_TEMPLATES": custom_templates_settings,
    }.items():
        prefix, postfix = pre_post_statements[category]
        category = get_admin_setting(category)
        key_cols = [
            "Admin Setting",
            "Portal Config Yaml Key",
            "Site Setting Command Option",
        ]
        table_header = get_table_header(key_cols)
        table_sep = get_table_sep(len(key_cols))
        output += f'\n{category}\n{"+" * len(category)}\n\n{prefix}\n\n{table_header}'
        for k, v in settings.items():
            admin_key = get_admin_setting(k)
            portal_config_key = get_portal_config_key(k)
            site_command_option = get_site_command_option(k)
            key_columns = f"{admin_key:<{col1_len}} {portal_config_key:<{col1_len}} {site_command_option:<{col1_len}}"

            v = re.sub("[\s']+", " ", v)
            output += f"{key_columns} {v:<{col2_len}}\n"
        postfix = f"\n{postfix}\n" if postfix else postfix
        output += f"{table_sep}\n{postfix}"

    output = output.replace(
        'f Default is "Copyright © {timezone.now():%Y}',
        f'Default is "Copyright © {timezone.now():%Y}',
    )

    print(output)


if __name__ == "__main__":
    get_table()
