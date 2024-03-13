"""
********************************************************************************
* Name: message_box.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

from .base import TethysGizmoOptions

__all__ = ["MessageBox"]


class MessageBox(TethysGizmoOptions):
    """
    Message box gizmos can be used to display messages to users. These are especially useful for alerts and warning messages. The message box gizmo is implemented using Twitter Bootstrap's modal.

    Attributes:
        name(str, required): Unique name for the message box
        title(str, required): Title that appears at the top of the message box
        message(str): Message that will appear in the main body of the message box
        dismiss_button(str): Title for the dismiss button (a.k.a.: the "Cancel" button)
        affirmative_button(str): Title for the affirmative action button (a.k.a.: the "OK" button)
        affirmative_attributes(str): Use this to place any html attributes on the affirmative button. (e.g.: 'href="/action" onclick="doSomething();"')
        width(int): The width of the message box in pixels
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Controller Example

    ::

        from tethys_sdk.gizmos import MessageBox

        message_box = MessageBox(name='sampleModal',
                                 title='Message Box Title',
                                 message='Congratulations! This is a message box.',
                                 dismiss_button='Nevermind',
                                 affirmative_button='Proceed',
                                 width=400,
                                 affirmative_attributes='href=javascript:void(0);')

        context = {
                    'message_box': message_box,
                  }

    Template Example

    ::

        {% load tethys_gizmos %}

        <a href="#sampleModal" role="button" class="btn btn-success" data-toggle="modal">Show Message Box</a>

        {% block after_app_content %}
            {% gizmo message_box %}
        {% endblock %}
    """  # noqa: E501

    gizmo_name = "message_box"

    def __init__(
        self,
        name,
        title,
        message="",
        dismiss_button="Cancel",
        affirmative_button="Ok",
        affirmative_attributes="",
        width=560,
        attributes=None,
        classes="",
    ):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.name = name
        self.title = title
        self.message = message
        self.dismiss_button = dismiss_button
        self.affirmative_button = affirmative_button
        self.affirmative_attributes = affirmative_attributes
        self.width = width
