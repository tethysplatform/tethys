from .base import TethysGizmoOptions

__all__ = ['MessageBox']


class MessageBox(TethysGizmoOptions):
    """
    Message Box

    Message box gizmos can be used to display messages to users. These are especially useful for alerts and warning messages. The message box gizmo is implemented using Twitter Bootstrap's modal.

    Attributes
    name(string, required): Unique name for the message box
    title(string, required): Title that appears at the top of the message box
    message(string): Message that will appear in the main body of the message box
    dismiss_button(string): Title for the dismiss button (a.k.a.: the "Cancel" button)
    affirmative_button(string): Title for the affirmative action button (a.k.a.: the "OK" button)
    affirmative_attributes(string): Use this to place any html attributes on the affirmative button. (e.g.: 'href="/action" onclick="doSomething();"')
    width(numeric): The width of the message box in pixels
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