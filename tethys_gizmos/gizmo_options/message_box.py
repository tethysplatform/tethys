from .base import TethysGizmoOptions

__all__ = ['MessageBox']


class MessageBox(TethysGizmoOptions):
    """
    Message box gizmos can be used to display messages to users. These are especially useful for alerts and warning messages. The message box gizmo is implemented using Twitter Bootstrap's modal.

    Attributes
        name(str, required): Unique name for the message box
        title(str, required): Title that appears at the top of the message box
        message(str): Message that will appear in the main body of the message box
        dismiss_button(str): Title for the dismiss button (a.k.a.: the "Cancel" button)
        affirmative_button(str): Title for the affirmative action button (a.k.a.: the "OK" button)
        affirmative_attributes(str): Use this to place any html attributes on the affirmative button. (e.g.: 'href="/action" onclick="doSomething();"')
        width(int): The width of the message box in pixels

    Example

    ::

        # CONTROLLER

        message_box = MessageBox(name='sampleModal',
                                 title='Message Box Title',
                                 message='Congratulations! This is a message box.',
                                 dismiss_button='Nevermind',
                                 affirmative_button='Proceed',
                                 width=400,
                                 affirmative_attributes='href=javascript:void(0);')

        # TEMPLATE

        {% gizmo message_box message_box %}

    """

    def __init__(self, name, title, message='', dismiss_button='Cancel', affirmative_button='Ok', affirmative_attributes='', width=560):
        """
        Constructor
        """
        # Initialize super class
        super(MessageBox, self).__init__()

        self.name = name
        self.title = title
        self.message = message
        self.dismiss_button = dismiss_button
        self.affirmative_button = affirmative_button
        self.affirmative_attributes = affirmative_attributes
        self.width = width