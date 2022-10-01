"""
********************************************************************************
* Name: exceptions.py
* Author: Nathan Swain
* Created On: June 30, 2021
* Copyright: (c) Aquaveo 2021
* License: BSD 2-Clause
********************************************************************************
"""


class TethysLayoutPropertyException(Exception):
    def __init__(self, property_name, layout_class, *args, **kwargs):
        """
        Args:
            property_name (str): Name of the TethysLayout class property.
            layout_class (TethysLayout): Child class of TethysLayout.
        """
        msg = (
            f'You must define the "{property_name}" property '
            f"on your {layout_class.__name__} class to use this feature."
        )
        super().__init__(msg, *args, **kwargs)
