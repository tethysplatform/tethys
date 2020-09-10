import arrow
import isodate
from django import template

register = template.Library()


@register.filter
def human_duration(iso_duration_str):
    """
    Converts an ISO 8601 formatted duration to a humanized time from now (UTC).

    Args:
        iso_duration_str: An ISO 8601 formatted string (e.g. "P1DT3H6M")

    Returns:
        str: humanized string representing the amount of time from now (e.g.: "in 30 minutes").
    """
    time_change = isodate.parse_duration(iso_duration_str)
    now = arrow.utcnow()
    time_from_now = now + time_change
    return time_from_now.humanize()
