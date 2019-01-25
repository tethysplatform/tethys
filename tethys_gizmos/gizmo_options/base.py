"""
********************************************************************************
* Name: base.py
* Authors: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import re


class TethysGizmoOptions(dict):
    """
    Base class for Tethys Gizmo Options objects.
    """

    gizmo_name = "tethys_gizmo_options"

    def __init__(self, attributes={}, classes=''):
        """
        Constructor for Tethys Gizmo Options base.
        """
        # Initialize super class
        super().__init__()

        # Dictionary magic
        self.__dict__ = self

        if isinstance(attributes, str):
            # 'key="value" key2="value with spaces"'
            pattern = r'(\w+)='
            pairs = re.split(pattern, attributes)
            if pairs:
                pairs = [x.strip().strip('\'').strip('\"') for x in pairs]
                attributes = dict()
                for i in range(1, len(pairs), 2):
                    attributes[pairs[i]] = pairs[i + 1]

        self.attributes = attributes
        self.classes = classes

    @staticmethod
    def get_tethys_gizmos_js():
        """
        Tethys gizmo JavaScript files applicable to all gizmos
        """
        return ('tethys_gizmos/js/tethys_gizmos.js',)

    @staticmethod
    def get_tethys_gizmos_css():
        """
        Tethys gizmo CSS files applicable to all gizmos
        """
        return ('tethys_gizmos/css/tethys_gizmos.css',)

    @staticmethod
    def get_vendor_js():
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return ()

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ()

    @staticmethod
    def get_vendor_css():
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        return ()

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo to be placed in the
        {% block content_dependent_styles %} block
        """
        return ()


class SecondaryGizmoOptions(dict):
    """
    Base class for Secondary Tethys Gizmo Options objects.
    """

    def __init__(self):
        """
        Constructor for Tethys Gizmo Options base.
        """
        # Initialize super class
        super().__init__()

        # Dictionary magic
        self.__dict__ = self
