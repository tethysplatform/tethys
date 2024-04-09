import re
from django import template

register = template.Library()
hex_regex_str = r"#([A-Fa-f0-9]{6})$"
hex_regex_pattern = re.compile(hex_regex_str)


@register.filter
def lighten(hex_color, percentage):
    """
    Lighten a hex color by a certain percentage and return the lightened color.

    Args:
        hex_color: A hex color value in the format "#2d3436".
        percentage: A number (0-100) representing a percentage to lighten the color by.

    Returns: A hex color value in the format "#2d3436"

    Usage:
        Be sure to include the ``tethys`` argument to the ``load`` template tag.

        .. code-block:: html+django

            {% loads tethys %}

            {{ tethys_app.color|lighten:20 }}

    """
    if not re.search(hex_regex_pattern, hex_color):
        raise ValueError(
            f'Given "{hex_color}", but needs to be in hex color format (e.g.: "#2d3436").'
        )

    # Extract the hex strings for the RGB components
    rgb_hex = [hex_color[x : x + 2] for x in [1, 3, 5]]

    # Convert RGB hex strings to integer numbers
    rgb_int = [int(x, 16) for x in rgb_hex]

    # Compute modified RGB values
    new_rgb_int = [x + (255 * (percentage / 100)) for x in rgb_int]

    # Make sure new values are between 0 and 255
    valid_new_rgb_int = [int(min([255, max(0, i)])) for i in new_rgb_int]

    new_hex = [hex(i) for i in valid_new_rgb_int]

    # Convert result to hex string
    new_hex_str = "#" + "".join([i[2:].zfill(2) for i in new_hex])
    return new_hex_str
