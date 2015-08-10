"""
********************************************************************************
* Name: range_slider.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions

__all__ = ['RangeSlider']


class RangeSlider(TethysGizmoOptions):
    """
    Sliders can be used to request an input value from a range of possible values. A slider is configured with a dictionary of key-value options. The table below summarizes the options for sliders.

    Attributes:
        display_text(str): Display text for the label that accompanies slider
        name(str, required): Name of the input element that will be used on form submission
        min(int, required): Minimum value of range
        max(int, required): Maximum value of range
        initial(int, required): Initial value of slider
        step(int, required): Increment between values in range
        disabled(bool): Disabled state of the slider
        error(str): Error message for form validation
        attributes(str): A string representing additional HTML attributes to add to the primary element (e.g. "onclick=run_me();").
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Example

    ::

        # CONTROLLER
        from tethys_sdk.gizmos import RangeSlider

        slider1 = RangeSlider(display_text='Slider 1',
                              name='slider1',
                              min=0,
                              max=100,
                              initial=50,
                              step=1)

        slider2 = RangeSlider(display_text='Slider 2',
                              name='slider2',
                              min=0,
                              max=1,
                              initial=0.5,
                              step=0.1,
                              disabled=True,
                              error='Incorrect, please choose another value.')

        # TEMPLATE

        {% gizmo range_slider slider1 %}
        {% gizmo range_slider slider2 %}

    """

    def __init__(self, name, min, max, initial, step, disabled=False, display_text='', error='', attributes='', classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(RangeSlider, self).__init__(attributes=attributes, classes=classes)

        self.name = name
        self.min = min
        self.max = max
        self.initial = initial
        self.step = step
        self.disabled = disabled
        self.display_text = display_text
        self.error = error