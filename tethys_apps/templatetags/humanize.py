import arrow
import isodate
from django import template

register = template.Library()


@register.filter
def human_duration(iso_duration):
    delta = isodate.parse_duration(iso_duration)
    now = arrow.utcnow()
    sum = now + delta
    return sum.humanize()
