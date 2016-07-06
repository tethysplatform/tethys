"""
********************************************************************************
* Name: select_input.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions

__all__ = ['SelectInput']


class SelectInput(TethysGizmoOptions):
    """
    Select inputs are used to select values from an given set of values. Use this gizmo to create select inputs and multi select inputs. This uses the Select2 functionality.

    Attributes:
        display_text(str): Display text for the label that accompanies select input
        name(str, required): Name of the input element that will be used for form submission
        multiple(bool): If True, select input will be a multi-select
        original(bool): If True, `Select2 reference <http://ivaynberg.github.io/select2/>`_ functionality will be turned off
        options(list): List of tuples that represent the options and values of the select input
        initial(list): List of values that represent the initial selected values
        disabled(bool): Disabled state of the select input
        error(str): Error message for form validation
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Example

    ::

        # CONTROLLER
        from tethys_sdk.gizmos import SelectInput

        select_input2 = SelectInput(display_text='Select2',
                                    name='select1',
                                    multiple=False,
                                    options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                    initial=['Three'],
                                    original=['Two'])

        select_input2_multiple = SelectInput(display_text='Select2 Multiple',
                                             name='select2',
                                             multiple=True,
                                             options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                             initial=['Two', 'Three'])

        select_input_multiple = SelectInput(display_text='Select Multiple',
                                            name='select2.1',
                                            multiple=True,
                                            original=True,
                                            options=[('One', '1'), ('Two', '2'), ('Three', '3')])

        select_input2_error = SelectInput(display_text='Select2 Disabled',
                                          name='select3',
                                          multiple=False,
                                          options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                          disabled=True,
                                          error='Here is my error text')

        # TEMPLATE

        {% gizmo select_input select_input2 %}
        {% gizmo select_input select_input2_multiple %}
        {% gizmo select_input select_input_multiple %}
        {% gizmo select_input select_input2_error %}

    """

    def __init__(self, name, display_text='', initial=[], multiple=False, original=False, options='', disabled=False, error='',
                 attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(SelectInput, self).__init__(attributes=attributes, classes=classes)

        self.display_text = display_text
        self.name = name
        self.initial=initial
        self.multiple = multiple
        self.original = original
        self.options = options
        self.disabled = disabled
        self.error = error