from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()

# npm CDNs whose URL layout maps 1:1 to node_modules (<cdn>/<pkg>@<version>/<path>)
NPM_CDNS = (
    "https://cdn.jsdelivr.net/npm/",
    "https://unpkg.com/",
)


def _local_path(cdn_url, app_package):
    """Convert a jsDelivr or unpkg npm URL to a local path in the app's node_modules directory.

    Requires a "<cdn>/<pkg>@<version>/<path>" URL (version and path required).
    The local path will be <app>/node_modules/<pkg>/<path>.

    Args:
        cdn_url (str): The jsDelivr or unpkg npm URL.
        app_package (str): The package name of the active Tethys app.

    Returns:
        str: The local path to the file in the app's node_modules directory.
    """
    # Strip whichever npm-CDN prefix matched, leaving "<pkg>@<version>/<path>"
    for prefix in NPM_CDNS:
        if cdn_url.startswith(prefix):
            rest = cdn_url[len(prefix):]
            break

    # Scoped packages (@scope/pkg) carry their own "@", so peel the scope off first
    if rest.startswith("@"):
        # Separate the scope from the rest
        scope, rest = rest[1:].split("/", 1)
        # Separate the package name from the version/path
        name, tail = rest.split("@", 1)
        # Rebuild the full scoped package name
        pkg = f"@{scope}/{name}"
    else:
        # Unscoped: separate the package name from the version/path
        name, tail = rest.split("@", 1)
        pkg = name

    # Keep the path; the version is unused (node_modules has whatever was installed)
    _version, path = tail.split("/", 1)

    # Build the local path within the app's node_modules directory
    return f"{app_package}/node_modules/{pkg}/{path}"


def _resolve(context, cdn_url, local_path=None):
    """Resolve the appropriate URL for a dependency based on the STATICFILES_USE_NPM setting.

    Args:
        context (dict): The template context.
        cdn_url (str): The CDN URL to the dependency.
        local_path (str, optional): Explicit local static path, used offline when
            the CDN URL can't be auto-derived (i.e. not a jsDelivr/unpkg npm URL).

    Returns:
        str: The resolved URL, either local or CDN.
    """
    # Online mode: use the CDN URL as-is
    if not settings.STATICFILES_USE_NPM:
        return cdn_url

    # Offline mode: try to auto-derive the local path from a jsDelivr/unpkg npm URL
    app = (context.get("tethys_app") or {}).get("package")
    if app and cdn_url.startswith(NPM_CDNS):
        try:
            return static(_local_path(cdn_url, app))
        except ValueError:
            pass  # malformed npm URL: fall through to the explicit local_path/CDN

    # Fall back to an explicit local path (for other CDNs, or when derivation failed)
    if local_path:
        return static(local_path)

    # Nothing to localize with: use the CDN (won't work offline)
    return cdn_url


@register.simple_tag(takes_context=True)
def dependency_script(context, cdn_url, local_path=None):
    """
    Returns a script tag for the given local or CDN path depending on the STATICFILES_USE_NPM setting.

    For jsDelivr/unpkg URLs the local path is derived automatically; for other
    CDNs, pass local_path explicitly.
    
    Example Usage:
        {% load tethys %}
        {% dependency_script "https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.js" %}
        {% dependency_script "https://unpkg.com/axios@0.21.1/dist/axios.min.js" %}
        {% dependency_script "https://example.com/some-library.js" local_path="my_app/js/some-library.js" %}

    Args:
        context (dict): The template context.
        cdn_url (str): The CDN URL to the script.
        local_path (str, optional): Explicit local static path for non-jsDelivr/unpkg CDNs.

    Returns:
        str: A script tag with the appropriate src attribute.
    """
    return format_html('<script src="{}"></script>', _resolve(context, cdn_url, local_path))


@register.simple_tag(takes_context=True)
def dependency_link(context, cdn_url, local_path=None):
    """
    Returns a link tag for the given local or CDN path depending on the STATICFILES_USE_NPM setting.

    For jsDelivr/unpkg URLs the local path is derived automatically; for other
    CDNs, pass local_path explicitly.
    
    Example Usage:
        {% load tethys %}
        {% dependency_link "https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.css" %}
        {% dependency_link "https://unpkg.com/axios@0.21.1/dist/axios.min.css" %}
        {% dependency_link "https://example.com/some-library.css" local_path="my_app/css/some-library.css" %}

    Args:
        context (dict): The template context.
        cdn_url (str): The CDN URL to the stylesheet.
        local_path (str, optional): Explicit local static path for non-jsDelivr/unpkg CDNs.

    Returns:
        str: A link tag with the appropriate href attribute.
    """
    return format_html('<link rel="stylesheet" href="{}">', _resolve(context, cdn_url, local_path))
