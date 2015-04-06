from .base import TethysGizmoOptions

__all__ = ['RangeSlider']


class RangeSlider(TethysGizmoOptions):
    """
    Range Slider

    Sliders can be used to request an input value from a range of possible values. A slider is configured with a dictionary of key-value options. The table below summarizes the options for sliders.

    Attributes:
        display_text(string): Display text for the label that accompanies slider
        name(string, required): Name of the input element that will be used on form submission
        min(numeric, required): Minimum value of range
        max(numeric, required): Maximum value of range
        initial(numeric, required): Initial value of slider
        step(numeric, required): Increment between values in range
        disabled(bool): Disabled state of the slider
        error(string): Error message for form validation
    """

    def __init__(self, name, min, max, initial, step, disabled=False, display_text='', error=''):
        """
        Constructor
        """
        # Initialize super class
        super(RangeSlider, self).__init__()

        self.name = name
        self.min = min
        self.max = max
        self.initial = initial
        self.step = step
        self.disabled = disabled
        self.display_text = display_text
        self.error = error