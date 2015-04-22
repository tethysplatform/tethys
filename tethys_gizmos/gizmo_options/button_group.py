from .base import TethysGizmoOptions, SecondaryGizmoOptions

__all__ = ['ButtonGroupOptions', 'ButtonOptions']


class ButtonGroupOptions(TethysGizmoOptions):
    """
    The button group gizmo can be used to generate a single button or a group of buttons. Groups of buttons can be stacked horizontally or vertically. For a single button, specify a button group with one button. This gizmo is a wrapper for Twitter Bootstrap buttons.

    Attributes:
        buttons(list, required): A list of dictionaries where each dictionary contains the options for a button.
        vertical(bool):Set to true to have button group stack vertically.

    Example

    ::

        # CONTROLLER

        from tethys_gizmos.gizmo_options import ButtonOptions, ButtonGroupOptions

        # Single Button
        button_options = ButtonOptions(display_text='Click Me',
                                       name='click_me_name',
                                       attributes='onclick=alert(this.name);',
                                       submit=True)
        single_button = ButtonGroupOptions(buttons=[button_options])

        # Horizontal Buttons
        add_button = ButtonOptions(display_text='Add',
                                   icon='glyphicon glyphicon-plus',
                                   style='success')
        delete_button = ButtonOptions(display_text='Delete',
                                      icon='glyphicon glyphicon-trash',
                                      disabled=True,
                                      style='danger')
        horizontal_buttons = ButtonGroupOptions(buttons=[add_button, delete_button])

        # Vertical Buttons
        edit_button = ButtonOptions(display_text='Edit',
                                    icon='glyphicon glyphicon-wrench',
                                    style='warning',
                                    attributes='id=edit_button')
        info_button = ButtonOptions(display_text='Info',
                                    icon='glyphicon glyphicon-question-sign',
                                    style='info',
                                    attributes='name=info')
        apps_button = ButtonOptions(display_text='Apps',
                                    icon='glyphicon glyphicon-home',
                                    href='/apps',
                                    style='primary')
        vertical_buttons = ButtonGroupOptions(buttons=[edit_button, info_button, apps_button],
                                              vertical=True)

        # TEMPLATE

        {% gizmo button_group single_button %}
        {% gizmo button_group.html horizontal_buttons %}
        {% gizmo button_group.html vertical_buttons %}

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