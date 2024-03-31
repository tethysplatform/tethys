"""
********************************************************************************
* Name: button.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

from .base import TethysGizmoOptions

__all__ = ["ButtonGroup", "Button"]


class ButtonGroup(TethysGizmoOptions):
    """
    The button group gizmo can be used to generate a single button or a group of buttons. Groups of buttons can be  stacked horizontally or vertically. For a single button, specify a button group with one button. This gizmo is a wrapper for Twitter Bootstrap buttons.

    Attributes:
        buttons(list, required): A list of dictionaries where each dictionary contains the options for a button.
        vertical(bool): Set to true to have button group stack vertically.
        attributes(str): A string representing additional HTML attributes to add to the primary element (e.g. "onclick=run_me();").
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Controller Example

    ::

        from tethys_sdk.gizmos import Button, ButtonGroup

        # Horizontal Button Group
        add_button = Button(display_text='Add',
                            icon='plus-square',
                            style='success')
        delete_button = Button(display_text='Delete',
                               icon='glyphicon glyphicon-trash',
                               disabled=True,
                               style='danger')
        horizontal_buttons = ButtonGroup(buttons=[add_button, delete_button])

        # Vertical Button Group
        edit_button = Button(display_text='Edit',
                             icon='glyphicon glyphicon-wrench',
                             style='warning',
                             attributes='id=edit_button')
        info_button = Button(display_text='Info',
                             icon='glyphicon glyphicon-question-sign',
                             style='info',
                             attributes='name=info')
        apps_button = Button(display_text='Apps',
                             icon='glyphicon glyphicon-home',
                             href='/apps',
                             style='primary')
        vertical_buttons = ButtonGroup(buttons=[edit_button, info_button, apps_button], vertical=True)

        context = {
                    'horizontal_buttons': horizontal_buttons,
                    'vertical_buttons': vertical_buttons,
                  }


    Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo horizontal_buttons %}
        {% gizmo vertical_buttons %}

    """  # noqa: E501

    gizmo_name = "button_group"

    def __init__(self, buttons, vertical=False, attributes="", classes=""):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.buttons = buttons
        self.vertical = vertical


class Button(TethysGizmoOptions):
    """
    Attributes:
        display_text(str): Display text that appears on the button.
        name(str): Name of the input element that will be used for form submission.
        style(str): Name of the input element that will be used for form submission.
        icon(str): Name of a valid Bootstrap Icon (see `Bootstrap Icons <https://icons.getbootstrap.com>`_).
        href(str): Link for anchor type buttons.
        submit(bool): Set this to true to make the button a submit type button for forms.
        disabled(bool): Set the disabled state.
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element  (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Controller Example

    ::

        from tethys_sdk.gizmos import Button

        # Single Buttons
        map_button = Button(
            display_text='',
            name='map-button',
            icon='globe',
            style='info',
            attributes={
                'data-toggle':'tooltip',
                'data-placement':'top',
                'title':'Map'
            }
        )

        save_button = Button(
            display_text='',
            name='save-button',
            icon='save',
            style='success',
            attributes={
                'data-toggle':'tooltip',
                'data-placement':'top',
                'title':'Save'
            }
        )

        edit_button = Button(
            display_text='',
            name='edit-button',
            icon='pen',
            style='warning',
            attributes={
                'data-toggle':'tooltip',
                'data-placement':'top',
                'title':'Edit'
            }
        )

        remove_button = Button(
            display_text='',
            name='remove-button',
            icon='trash',
            style='danger',
            attributes={
                'data-toggle':'tooltip',
                'data-placement':'top',
                'title':'Remove'
            }
        )

        previous_button = Button(
            display_text='Previous',
            name='previous-button',
            attributes={
                'data-toggle':'tooltip',
                'data-placement':'top',
                'title':'Previous'
            }
        )

        next_button = Button(
            display_text='Next',
            name='next-button',
            attributes={
                'data-toggle':'tooltip',
                'data-placement':'top',
                'title':'Next'
            }
        )

        context = {
            'map_button': map_button,
            'save_button': save_button,
            'edit_button': edit_button,
            'remove_button': remove_button,
            'previous_button': previous_button,
            'next_button': next_button
        }

    Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo map_button %}
        {% gizmo save_button %}
        {% gizmo edit_button %}
        {% gizmo remove_button %}
        {% gizmo previous_button %}
        {% gizmo next_button %}
    """  # noqa: E501

    gizmo_name = "button"

    def __init__(
        self,
        display_text="",
        name="",
        style="",
        icon="",
        href="",
        submit=False,
        disabled=False,
        attributes=None,
        classes="",
    ):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.display_text = display_text
        self.name = name
        self.style = style
        self.icon = icon
        self.href = href
        self.submit = submit
        self.disabled = disabled
