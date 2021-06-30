"""
********************************************************************************
* Name: slide_sheet
* Author: nswain
* Created On: June 24, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""
from tethys_gizmos.gizmo_options.base import TethysGizmoOptions


class SlideSheet(TethysGizmoOptions):
    """
    Spatial reference select input gizmo.
    """
    gizmo_name = 'slide_sheet'

    def __init__(self, id='slide-sheet', content_template='', title='', attributes={}, classes='', **kwargs):
        """
        constructor

        Args:
            id(str): id of slide sheet. Use this to differentiate multiple slide sheets on the same page.
            content_template(str): path to template to use for slide sheet content.
            title(str): title for slide sheet.
        """
        # Initialize parent
        super(SlideSheet, self).__init__(attributes=attributes, classes=classes)

        self.id = id
        self.content_template = content_template
        self.title = title

        # Add remaining kwargs as attributes so they are accessible to the base template
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo.
        """
        return ('tethys_gizmos/js/slide_sheet.js',)

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo .
        """
        return ('tethys_gizmos/css/slide_sheet.css',)
