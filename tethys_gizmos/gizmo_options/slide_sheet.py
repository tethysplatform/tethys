# ********************************************************************************
# * Name: slide_sheet
# * Author: nswain
# * Created On: June 24, 2021
# * Copyright: (c) Aquaveo 2021
# ********************************************************************************
from tethys_gizmos.gizmo_options.base import TethysGizmoOptions


class SlideSheet(TethysGizmoOptions):
    """
    Adds a slide sheet that slides up from the bottom of the page. Add content to the slidesheet by creating an HTML template with the desired content and then providing the path to the template to the template using the `template` argument.

    Args:
        id: ID of the slide sheet.
        content_template: Path to template containing content for the slide sheet.
        title: Title of the slide sheet.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import SlideSheet

        slide_sheet = SlideSheet(
            id='slide-sheet',
            title='Slide Sheet',
            content_template='my_first_app/slide_sheet_content.html'
        )

        context = {
            'slide_sheet': slide_sheet,
        }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% block app_content %}
            <button class="btn btn-success" onclick="SLIDE_SHEET.open('{{ slide_sheet.id }}');">Show Slide Sheet</button>
            {% gizmo slide_sheet %}
        {% endblock %}

    """  # noqa: E501

    gizmo_name = "slide_sheet"

    def __init__(
        self,
        id: str = "slide-sheet",
        content_template: str = "",
        title: str = "",
        attributes: dict = dict,
        classes: str = "",
        **kwargs,
    ):
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
        return ("tethys_gizmos/js/slide_sheet.js",)

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo .
        """
        return ("tethys_gizmos/css/slide_sheet.css",)
