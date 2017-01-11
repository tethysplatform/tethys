"""
********************************************************************************
* Name: text_input.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions

__all__ = ['TextInput']


class TextInput(TethysGizmoOptions):
    """
    The text input gizmo makes it easy to add text inputs to your app that are styled similarly to the other input snippets.

    Attributes:
        display_text(str): Display text for the label that accompanies select input
        name(str, required): Name of the input element that will be used for form submission
        initial(str): The initial text that will appear in the text input when it loads
        placeholder(str): Placeholder text is static text that displayed in the input when it is empty
        prepend(str): Text that is prepended to the text input
        append(str): Text that is appended to the text input
        icon_prepend(str): The name of a valid Bootstrap v2.3 icon. The icon will be prepended to the input.
        icon_append(str): The name of a valid Bootstrap v2.3 icon. The icon will be appended to the input.
        disabled(bool): Disabled state of the select input
        error(str): Error message for form validation
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Example

    ::

        # CONTROLLER
        from tethys_sdk.gizmos import TextInput

        text_input = TextInput(display_text='Text',
                               name='inputAmount',
                               placeholder='e.g.: 10.00',
                               prepend='$')

        text_error_input = TextInput(display_text='Text Error',
                                     name='inputEmail',
                                     initial='bob@example.com',
                                     disabled=True,
                                     icon_append='glyphicon glyphicon-envelope',
                                     error='Here is my error text')

        # TEMPLATE

        {% gizmo text_input text_input %}
        {% gizmo text_input text_error_input %}

    """

    def __init__(self, name, display_text='', initial='', placeholder='', prepend='', append='', icon_prepend='',
                 icon_append='', disabled=False, error='', attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(TextInput, self).__init__(attributes=attributes, classes=classes)

        self.name = name
        self.display_text = display_text
        self.initial = initial
        self.placeholder = placeholder
        self.prepend = prepend
        self.append = append
        self.icon_prepend = icon_prepend
        self.icon_append = icon_append
        self.disabled = disabled
        self.error = error