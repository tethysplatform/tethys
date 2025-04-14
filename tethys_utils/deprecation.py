"""
********************************************************************************
* Name: deprecation.py
* Author: Scott Christensen
* Created On: April 2024
* Copyright: (c) Tethys Geoscience Foundation 2024
* License: BSD 2-Clause
********************************************************************************
"""


def deprecation_warning(version, feature, message):
    """Prints standard deprecation warning message along with custom message passed as argument.

    Args:
        version (str): Tethys version that feature will be removed in.
        feature (str): Description of feature that is deprecated.
        message (str): Custom message describing alternatives.

    Returns: None
    """
    cli_yellow = "\033[33m"
    cli_end_styles = "\033[0m"
    warning_message = (
        f"{cli_yellow}"
        f"DEPRECATION WARNING: {feature} is deprecated and will be removed in Tethys v{version}.\n\t{message}"
        f"{cli_end_styles}"
    )
    print(warning_message)
