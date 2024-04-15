from django import template

from tethys_portal.optional_dependencies import optional_import

# optional imports
arrow = optional_import("arrow")
isodate = optional_import("isodate")


register = template.Library()


@register.filter
def human_duration(iso_duration_str):
    """
    Converts an ISO 8601 formatted duration to a humanized time from now (UTC).

    .. important::

       This feature requires the `arrow` and `isodate` libraries to be installed. Starting with Tethys 5.0 or if you are
       using `micro-tethys-platform`, you will need to install these libraries using conda or pip as follows:

       .. code-block:: bash

          # conda: conda-forge channel strongly recommended
          conda install -c conda-forge arrow isodate

          # pip
          pip install arrow isodate

    Args:
        iso_duration_str: An ISO 8601 formatted string (e.g. "P1DT3H6M")

    Returns:
        str: humanized string representing the amount of time from now (e.g.: "in 30 minutes").

    Usage:
        Be sure to include the ``tethys`` argument to the ``load`` template tag.

        .. code-block:: html+django

            {% load tethys %}

            {{ P1DT3H6M|human_duration }}
    """
    time_change = isodate.parse_duration(iso_duration_str)
    now = arrow.utcnow()
    time_from_now = now + time_change
    return time_from_now.humanize()
