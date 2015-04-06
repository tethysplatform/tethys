from .base import TethysGizmoOptions

__all__ = ['ToggleSwitch']


class ToggleSwitch(TethysGizmoOptions):
    """
    Toggle Switch Options

    Toggle switches can be used as an alternative to check boxes for boolean or binomial input. Toggle switches are implemented using the excellent `Bootstrap Switch reference <http://www.bootstrap-switch.org/>`_ project.

    Attributes
    display_text(string): Display text for the label that accompanies switch
    name(string, required): Name of the input element that will be used for form submission
    on_label(string): Text that appears in the "on" position of the switch
    off_label(string): Text that appears in the "off" position of the switch
    on_style(string): Color of the "on" position. Either: 'default', 'info', 'primary', 'success', 'warning', or 'danger'
    off_style(string): Color of the "off" position. Either: 'default', 'info', 'primary', 'success', 'warning', or 'danger'
    size(string): Size of the switch. Either: 'large', 'small', or 'mini'.
    initial(bool): The initial position of the switch (True for "on" and False for "off")
    disabled(bool): Disabled state of the switch
    error(string): Error message for form validation
    """

    def __init__(self, name, display_text='', on_label='ON', off_label='OFF', on_style='primary', off_style='default', size='regular', initial=False, disabled=False, error=''):
        """
        Constructor
        """
        # Initialize super class
        super(ToggleSwitch, self).__init__()

        self.name = name
        self.display_text = display_text
        self.on_label = on_label
        self.off_label = off_label
        self.on_style = on_style
        self.off_style = off_style
        self.size = size
        self.initial = initial
        self.disabled = disabled
        self.error = error