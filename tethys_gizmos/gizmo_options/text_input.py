from .base import TethysGizmoOptions

__all__ = ['TextInput']


class TextInput(TethysGizmoOptions):
    """
    Text Input

    The text input gizmo makes it easy to add text inputs to your app that are styled similarly to the other input snippets.

    Attributes:
    display_text(string): Display text for the label that accompanies select input
    name(string, required): Name of the input element that will be used for form submission
    initial(string): The initial text that will appear in the text input when it loads
    placeholder(string): Placeholder text is static text that displayed in the input when it is empty
    prepend(string): Text that is prepended to the text input
    append(string): Text that is appended to the text input
    icon_prepend(string): The name of a valid Bootstrap v2.3 icon. The icon will be prepended to the input.
    icon_append(string): The name of a valid Bootstrap v2.3 icon. The icon will be appended to the input.
    disabled(bool): Disabled state of the select input
    error(string): Error message for form validation
    """

    def __init__(self, name, display_text='', initial='', placeholder='', prepend='', append='', icon_prepend='', icon_append='', disabled=False, error=''):
        """
        Constructor
        """
        # Initialize super class
        super(TextInput, self).__init__()

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