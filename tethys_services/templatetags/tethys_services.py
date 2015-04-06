from django import template

from owslib.wps import ComplexData

register = template.Library()


@register.filter
def is_complex_data(value):
    """
    Test whether value is owslib.wps.ComplexData.

    Returns:
      (bool): True if value is owslib.wps.ComplexData, false if not.
    """

    if isinstance(value, ComplexData):
        return True

    return False