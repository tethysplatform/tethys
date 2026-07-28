"""
********************************************************************************
* Name: time_picker.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

from .base import TethysGizmoOptions
from tethys_portal.dependencies import vendor_static_dependencies

__all__ = ["TimePicker"]


class TimePicker(TethysGizmoOptions):
    """
    Time pickers are used to make the input of times streamlined and easy. Rather than typing the time, the user is presented with a spinner-style widget to select the time. This time picker was implemented using `Bootstrap Timepicker <https://jdewit.github.io/bootstrap-timepicker/>`_.

    Attributes:
        name (str, required): Name of the input element that will be used for form submission.
        display_text (str): Display text for the label that accompanies time picker.
        default_time (str): The time to display when the picker is first opened with no value (e.g.: '2:30 PM'). Use 'current' to default to the current time.
        minute_step (int): Specify a step for the minute field.
        second_step (int): Specify a step for the second field (only applies when ``show_seconds`` is True).
        show_seconds (bool): Set whether to show the seconds field.
        show_meridian (bool): Set whether to use a 12-hour clock with an AM/PM selector (True) or a 24-hour clock (False).
        show_inputs (bool): Set whether the widget shows editable text inputs for each field.
        disable_focus (bool): Set whether to disable the widget from opening on input focus.
        snap_to_step (bool): Set whether to snap selected values to the nearest step when scrolling.
        max_hours (int): Specify a maximum number of hours the widget will spin up to (only applies with a 24-hour clock).
        explicit_mode (bool): When True, the user may enter a time without a colon (e.g.: '0900' becomes '09:00').
        initial (str): Initial time to appear in time picker.
        disabled (bool): Disabled state of the time picker.
        error (str): Error message for form validation.
        success (str): Success message for form validation.
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Controller Example

    ::

        from tethys_sdk.gizmos import TimePicker

        # Time Picker Options
        time_picker = TimePicker(name='time1',
                                 display_text='Time',
                                 minute_step=15,
                                 show_meridian=True,
                                 default_time='2:30 PM',
                                 initial='2:30 PM')

        time_picker_error = TimePicker(name='time2',
                                       display_text='Time',
                                       initial='10:00 AM',
                                       disabled=True,
                                       error='Here is my error text.')

        context = {
                    'time_picker': time_picker,
                    'time_picker_error': time_picker_error,
                  }

    Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo time_picker %}
        {% gizmo time_picker_error %}

    """  # noqa: E501

    gizmo_name = "time_picker"
    version = vendor_static_dependencies["bootstrap-timepicker"].version

    def __init__(
        self,
        name,
        display_text="",
        default_time="",
        minute_step=15,
        second_step=30,
        show_seconds=False,
        show_meridian=True,
        show_inputs=True,
        disable_focus=False,
        snap_to_step=False,
        max_hours=24,
        explicit_mode=False,
        initial="",
        disabled=False,
        error="",
        success="",
        attributes=None,
        classes="",
    ):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.name = name
        self.display_text = display_text
        self.default_time = default_time
        self.minute_step = minute_step
        self.second_step = second_step
        self.show_seconds = show_seconds
        self.show_meridian = show_meridian
        self.show_inputs = show_inputs
        self.disable_focus = disable_focus
        self.snap_to_step = snap_to_step
        self.max_hours = max_hours
        self.explicit_mode = explicit_mode
        self.initial = initial
        self.disabled = disabled
        self.error = error
        self.success = success

    @classmethod
    def get_vendor_css(cls):
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        return (
            vendor_static_dependencies["bootstrap-timepicker"].get_custom_version_url(
                url_type="css", version=cls.version
            ),
        )

    @classmethod
    def get_vendor_js(cls):
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return (
            vendor_static_dependencies["bootstrap-timepicker"].get_custom_version_url(
                url_type="js", version=cls.version
            ),
        )

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo to be placed in the
        {% block content_dependent_styles %} block
        """
        return ("tethys_gizmos/css/time_picker.css",)
