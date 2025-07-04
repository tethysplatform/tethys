# -*- coding: utf-8 -*-
#
# Tethys Platform documentation build configuration file, created by
# sphinx-quickstart on Sat Oct 18 17:30:09 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
import sys
import subprocess
from dataclasses import asdict
from os import environ
from pathlib import Path
from unittest import mock

import django
from django.conf import settings
from setuptools_scm import get_version
from sphinxawesome_theme import ThemeOptions, LinkIcon
from sphinxawesome_theme.postprocess import Icons

# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Mock Dependencies
# NOTE: No obvious way to automatically anticipate all the sub modules without
# installing the package, which is what we are trying to avoid. For some reason
# the autodoc_mock_imports does not work.
# ---------------------------------------------------------------------------------------------------------------------
MOCK_MODULES = [
    "bcrypt",
    "bokeh",
    "bokeh.core.templates",
    "bokeh.document",
    "bokeh.embed",
    "bokeh.embed.elements",
    "bokeh.embed.util",
    "bokeh.resources",
    "bokeh.settings",
    "bokeh.server.django",
    "bokeh.server.django.consumers",
    "bokeh.util.compiler",
    "channels",
    "channels.db",
    "channels.db.database_sync_to_async",
    "channels.consumer",
    "conda",
    "conda.cli",
    "conda.cli.python_api",
    "condorpy",
    "dask",
    "dask.delayed",
    "dask.distributed",
    "distributed",
    "distributed.protocol",
    "distributed.protocol.serialize",
    "distro",
    "django_gravatar",
    "django_json_widget",
    "django_json_widget.widgets",
    "docker",
    "docker.types",
    "docker.errors",
    "guardian",
    "guardian.admin",
    "guardian.models",
    "guardian.shortcuts",
    "guardian.utils",
    "mfa",
    "mfa.models",
    "model_utils",
    "model_utils.managers",
    "plotly",
    "plotly.offline",
    "shapefile",
    "siphon",
    "siphon.catalog",
    "siphon.http_util",
    "social_core",
    "social_core.exceptions",
    "social_django",
    "social_django.utils",
    "sqlalchemy",
    "sqlalchemy.orm",
    "tethys_apps.harvester",
    "tethys_apps.models",  # Mocked to prevent issues with loading apps during docs build.
    "tethys_apps.admin",  # Mocked to prevent issues with loading models during docs build.
    "yaml",
]


# Mock dependency modules so we don't have to install them to build the documentation (takes too long)
# See: https://docs.readthedocs.io/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules
class MockModule(mock.MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return mock.MagicMock()


print(
    "NOTE: The following modules are mocked to prevent timeouts during the docs build process on RTD:"
)
print("{}".format(", ".join(MOCK_MODULES)))
sys.modules.update((mod_name, MockModule()) for mod_name in MOCK_MODULES)

# patcher = mock.patch("tethys_apps.models.register_custom_group")
# patcher.start()

# ---------------------------------------------------------------------------------------------------------------------
# Django Configuration
# ---------------------------------------------------------------------------------------------------------------------

# Fixes django settings module problem
sys.path.insert(0, str(Path("..").absolute().resolve()))

installed_apps = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tethys_config",
    "tethys_quotas",
    "tethys_apps",
    "tethys_gizmos",
    "tethys_services",
    "tethys_compute",
    "tethys_layouts",
]

try:
    settings.configure(
        INSTALLED_APPS=installed_apps,
        DEBUG=True,
        SECRET_KEY="QNT5VImbg7PktTYfyXZWGwfKqOe1G3CanQWfG0zsE5HZxwHdQs",
    )
    django.setup()
except RuntimeError as e:
    # Ignore error if settings are already configured
    # This can occur when using sphinx-autobuild
    if "settings already configured" in str(e).lower():
        pass

# ---------------------------------------------------------------------------------------------------------------------
# Sphinx Configuration
# ---------------------------------------------------------------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.extlinks",
    "sphinx.ext.todo",
    "sphinxarg.ext",
    "sphinxawesome_theme",
    "directives",
    "sphinx_tabs.tabs",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "Tethys Platform"
copyright = "2025, Tethys Platform"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
release = get_version(root="..", relative_to=__file__)
print(f'Building docs for version "{release}"')

# major/minor
version = ".".join(release.split(".")[:2])
print(f'Using simplified version "{version}"')

# Determine branch
git_directory = Path(__file__).parents[1]
ret = subprocess.run(
    ["git", "-C", git_directory, "rev-parse", "--abbrev-ref", "HEAD"],
    capture_output=True,
)
branch = ret.stdout.decode().strip() if ret.returncode == 0 else "release"

rst_epilog = """
.. |branch| replace:: {branch}
""".format(
    branch=branch
)

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
smartquotes = False

# markup to shorten external links (see: http://www.sphinx-doc.org/en/stable/ext/extlinks.html)
install_tethys_link = "https://raw.githubusercontent.com/tethysplatform/tethys/{}/scripts/install_tethys.%s".format(
    branch
)

extlinks = {"install_tethys": (install_tethys_link, None)}

# If this is True, todo and todo list produce output, else they produce nothing. The default is False.
todo_include_todos = True

# If this is True, todo emits a warning for each TODO entries. The default is False.
todo_emit_warnings = True
# --------------------------------------------------------------------------------------------------------------------
# Link Check Configuration
# --------------------------------------------------------------------------------------------------------------------
linkcheck_ignore = [
    r"https?:(//)?(.*\.)?example\.com.*",
    r"https?://localhost.*",
    r"https?://127\.0\.0\.1.*",
    r"https?://example.onelogin.com",
    r"https?://tethys.not-real.org.*",
    r"https?://(.*\.)?my-org.com.*",
    r"https?://\<(.*)\>.*",
    r"https?:\/\/\<SERVER_DOMAIN_NAME\>.*",
    r"https?://arcgis_enterprise_host.domain.com.*",
    r"https?://developers.facebook.com.*",
    r"https?://business.facebook.com.*",
    r"https?://developers.google.com.*",
    r"https?://domain-name.*",
    r"https?://github.com/<USERNAME>/tethysapp-earth_engine",
    r"https?://linux.die.net/.*",
    r"https?://sampleserver1.arcgisonline.com.*",
    r"https?://raw.githubusercontent.com.*",
    # Tethys Dataset Services
    r"http://docs.ckan.org/en/ckan-2.2/api.html",
]

linkcheck_allowed_redirects = {
    r"https?://anaconda\.org.*": r"https?://anaconda\.org/account/login.*",
    r"https?://.*\.earthengine\.google\.com.*": r"https?://accounts\.google\.com.*",
    r"https?://console\.developers\.google\.com.*": r"https?://accounts\.google\.com.*",
    r"https?://hub\.docker\.com.*": r"https?://login\.docker\.com.*",
    r"https?://(www)?\.hydroshare\.org": r"https?://auth\.cuahsi\.org.*",
    r"https?://signup.sendgrid.com.*": r"https?://login.sendgrid.com/unified_login/start.*",
    r"https?://portal.azure.com.*": r"https?://login.microsoftonline.com/.*",
}

# --------------------------------------------------------------------------------------------------------------------
# Read the Docs Configuration
# --------------------------------------------------------------------------------------------------------------------

# on_rtd is whether we are on readthedocs.org, this line of code grabbed from docs.readthedocs.org
on_rtd = environ.get("READTHEDOCS", "") == "True"

# Define the canonical URL if you are using a custom domain on Read the Docs
html_baseurl = environ.get("READTHEDOCS_CANONICAL_URL", "")

# Tell Jinja2 templates the build is running on Read the Docs
if on_rtd:
    if "html_context" not in globals():
        html_context = {}
    html_context["READTHEDOCS"] = True

# --------------------------------------------------------------------------------------------------------------------
# Theme Configuration
# --------------------------------------------------------------------------------------------------------------------

html_title = ""
html_short_title = ""
html_favicon = "images/default_favicon.ico"
html_static_path = ["_static"]
html_css_files = [
    "css/tethys.css",
    "css/recipe_gallery.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",  # Font Awesome for arrow icons in recipe carousels
]

html_js_files = ["js/recipe_gallery.js"]

html_theme = "sphinxawesome_theme"
theme_options = ThemeOptions(
    main_nav_links={
        "Tutorials": "tutorials",
        "SDK": "tethys_sdk",
        "CLI": "tethys_cli",
        "Tethys Portal": "tethys_portal",
        "Migrate Apps": "whats_new/app_migration",
    },
    extra_header_link_icons={
        "GitHub": LinkIcon(
            icon='<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-github" viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/></svg>',
            link="https://github.com/tethysplatform/tethys",
        ),
    },
    logo_dark="images/features/tethys-on-blue.svg",
    logo_light="images/features/tethys-on-white.svg",
    show_breadcrumbs=False,
    show_prev_next=True,
    show_scrolltop=True,
)
html_theme_options = asdict(theme_options)

html_collapsible_definitions = True

# Link icon for header links instead of paragraph icons that are the default
html_permalinks_icon = Icons.permalinks_icon
