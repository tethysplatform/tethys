from .base import TethysGizmoOptions, SecondaryGizmoOptions

__all__ = ['ButtonGroupOptions', 'ButtonOptions']


class ButtonGroupOptions(TethysGizmoOptions):
    """
    Button Group Gizmo Options

    The button group gizmo can be used to generate a single button or a group of buttons. Groups of buttons can be stacked horizontally or vertically. For a single button, specify a button group with one button. This gizmo is a wrapper for Twitter Bootstrap buttons.

    Attributes:
        buttons(list, required): A list of dictionaries where each dictionary contains the options for a button.
        vertical(bool):Set to true to have button group stack vertically.

    Example

    ::

        # CONTROLLER

        from tethys_gizmos.gizmo_options import ButtonOptions, ButtonGroupOptions

        button_options = ButtonOptions(display_text='Click Me',
                                    name='click_me_name',
                                    attributes='onclick=alert(this.name);',
                                    submit=True)
        single_button_group = ButtonGroupOptions(buttons=[button_options])

        # TEMPLATE

        {% gizmo button_group single_button_group %}

    """

    def __init__(self, buttons, vertical=False):
        """
        Constructor
        """
        # Initialize super class
        super(ButtonGroupOptions, self).__init__()

        self.buttons = buttons
        self.vertical = vertical


class ButtonOptions(SecondaryGizmoOptions):
    """
    Button Gizmo Options

    Attributes:
      display_text(str): Display text that appears on the button.
      name(str): Name of the input element that will be used for form submission
      style(str): Name of the input element that will be used for form submission
      icon(str): Name of a valid Twitter Bootstrap icon class (see the Bootstrap `glyphicon reference <http://getbootstrap.com/components/#glyphicons-glyphs>`_)
      href(str): Link for anchor type buttons
      attributes(str): Use this to add any additional attributes to the html element
      submit(bool): Set this to true to make the button a submit type button for forms
      disabled(bool): Set the disabled state
    """

    def __init__(self, display_text='', name='', style='', icon='', href='', attributes='',
                 submit=False, disabled=False):
        """
        Constructor
        """
        # Initialize super class
        super(ButtonOptions, self).__init__()

        self.display_text = display_text
        self.name = name
        self.style = style
        self.icon = icon
        self.href = href
        self.attributes = attributes
        self.submit = submit
        self.disabled = disabled