"""
********************************************************************************
* Name: toggle_switch.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions

__all__ = ['ToggleSwitch']


class ToggleSwitch(TethysGizmoOptions):
    """
    Toggle switches can be used as an alternative to check boxes for boolean or binomial input. Toggle switches are implemented using the excellent `Bootstrap Switch reference <http://www.bootstrap-switch.org/>`_ project.

    Attributes:
        display_text(str): Display text for the label that accompanies switch
        name(str, required): Name of the input element that will be used for form submission
        on_label(str): Text that appears in the "on" position of the switch
        off_label(str): Text that appears in the "off" position of the switch
        on_style(str): Color of the "on" position. Either: 'default', 'info', 'primary', 'success', 'warning', or 'danger'
        off_style(str): Color of the "off" position. Either: 'default', 'info', 'primary', 'success', 'warning', or 'danger'
        size(str): Size of the switch. Either: 'large', 'small', or 'mini'.
        initial(bool): The initial position of the switch (True for "on" and False for "off")
        disabled(bool): Disabled state of the switch
        error(str): Error message for form validation
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Controller Example

    ::

        from tethys_sdk.gizmos import ToggleSwitch

        toggle_switch = ToggleSwitch(display_text='Defualt Toggle',
                                     name='toggle1')

        toggle_switch_styled = ToggleSwitch(display_text='Styled Toggle',
                                            name='toggle2',
                                            on_label='Yes',
                                            off_label='No',
                                            on_style='success',
                                            off_style='danger',
                                            initial=True,
                                            size='large')

        toggle_switch_disabled = ToggleSwitch(display_text='Disabled Toggle',
                                              name='toggle3',
                                              on_label='On',
                                              off_label='Off',
                                              on_style='success',
                                              off_style='warning',
                                              size='mini',
                                              initial=False,
                                              disabled=True,
                                              error='Here is my error text')

        context = {
                    'toggle_switch': toggle_switch,
                    'toggle_switch_styled': toggle_switch_styled,
                    'toggle_switch_disabled': toggle_switch_disabled,
                  }

    Template Example

    ::

        {% gizmo toggle_switch %}
        {% gizmo toggle_switch_styled %}
        {% gizmo toggle_switch_disabled %}

    """  # noqa: E501
    gizmo_name = "toggle_switch"

    def __init__(self, name, display_text='', on_label='ON', off_label='OFF', on_style='primary', off_style='default',
                 size='regular', initial=False, disabled=False, error='', attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

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

    @staticmethod
    def get_vendor_js():
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return ('tethys_gizmos/vendor/bootstrap_switch/dist/js/bootstrap-switch.min.js',)

    @staticmethod
    def get_vendor_css():
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        return ('tethys_gizmos/vendor/bootstrap_switch/dist/css/bootstrap3/bootstrap-switch.min.css',)

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ('tethys_gizmos/js/toggle_switch.js',)
