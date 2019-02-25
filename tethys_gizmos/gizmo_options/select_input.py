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
import json

__all__ = ['SelectInput']


class SelectInput(TethysGizmoOptions):
    """
    Select inputs are used to select values from an given set of values. Use this gizmo to create select inputs and multi select inputs. This uses the Select2 functionality.

    Attributes:
        display_text(str): Display text for the label that accompanies select input
        name(str, required): Name of the input element that will be used for form submission
        multiple(bool): If True, select input will be a multi-select
        original(bool): If True, `Select2 reference <http://ivaynberg.github.io/select2/>`_ functionality will be turned off
        select2_options (dict): Select2 options that will be passed when initializing the select2.
        options(list): List of tuples that represent the options and values of the select input
        initial(list or str): List of keys or values that represent the initial selected values or a string representing a singular initial selected value.
        disabled(bool): Disabled state of the select input
        error(str): Error message for form validation
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Controller Example

    ::

        from tethys_sdk.gizmos import SelectInput

        select_input2 = SelectInput(display_text='Select2',
                                    name='select2',
                                    multiple=False,
                                    options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                    initial=['Three'],
                                    select2_options={'placeholder': 'Select a number',
                                                     'allowClear': True})

        select_input2_multiple = SelectInput(display_text='Select2 Multiple',
                                             name='select21',
                                             multiple=True,
                                             options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                             initial=['Two', 'One'])

        select_input2_error = SelectInput(display_text='Select2 Disabled',
                                          name='select22',
                                          multiple=False,
                                          options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                          disabled=True,
                                          error='Here is my error text')

        select_input = SelectInput(display_text='Select',
                                   name='select1',
                                   multiple=False,
                                   original=True,
                                   options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                   initial=['Three'])

        select_input_multiple = SelectInput(display_text='Select Multiple',
                                            name='select11',
                                            multiple=True,
                                            original=True,
                                            options=[('One', '1'), ('Two', '2'), ('Three', '3')])


        context = {
                    'select_input2': select_input2,
                    'select_input2_multiple': select_input2_multiple,
                    'select_input2_error': select_input2_error,
                    'select_input': select_input,
                    'select_input_multiple': select_input_multiple,
                  }

    Template Example

    ::

        {% gizmo select_input2 %}
        {% gizmo select_input2_multiple %}
        {% gizmo select_input2_error %}
        {% gizmo select_input %}
        {% gizmo select_input_multiple %}

    """  # noqa: E501
    gizmo_name = "select_input"

    def __init__(self, name, display_text='', initial=[], multiple=False, original=False,
                 select2_options=None, options='', disabled=False, error='',
                 attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.display_text = display_text
        self.name = name
        self.initial_is_iterable = isinstance(initial, (list, tuple, set, dict))
        self.initial = initial
        self.multiple = multiple
        self.original = original
        self.placeholder = False if select2_options is None else 'placeholder' in select2_options
        self.select2_options = json.dumps(select2_options)
        self.options = options
        self.disabled = disabled
        self.error = error

    @staticmethod
    def get_vendor_js():
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return ('tethys_gizmos/vendor/select2_4.0.2/js/select2.full.min.js',)

    @staticmethod
    def get_vendor_css():
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        return ('tethys_gizmos/vendor/select2_4.0.2/css/select2.min.css',)

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ('tethys_gizmos/js/select_input.js',)
