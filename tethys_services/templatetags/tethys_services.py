from django import template

from tethys_portal.optional_dependencies import optional_import

# optional imports
ComplexData = optional_import("ComplexData", from_module="owslib.wps")

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
