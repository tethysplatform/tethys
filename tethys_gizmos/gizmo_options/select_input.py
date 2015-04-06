from .base import TethysGizmoOptions

__all__ = ['SelectInput']


class SelectInput(TethysGizmoOptions):
    """
    Select Input

    Select inputs are used to select values from an given set of values. Use this gizmo to create select inputs and multi select inputs. This uses the Select2 functionality.

    Attributes:
    display_text(string): Display text for the label that accompanies select input
    name(string, required): Name of the input element that will be used for form submission
    multiple(bool): If True, select input will be a multi-select
    original(bool): If True, `Select2 reference <http://ivaynberg.github.io/select2/>`_ functionality will be turned off
    options(list): List of tuples that represent the options and values of the select input
    disabled(bool): Disabled state of the select input
    error(string): Error message for form validation
    """

    def __init__(self, name, display_text='', multiple=False, original=False, options='', disabled=False, error=''):
        """
        Constructor
        """
        # Initialize super class
        super(SelectInput, self).__init__()

        self.display_text = display_text
        self.name = name
        self.multiple = multiple
        self.original = original
        self.options = options
        self.disabled = disabled
        self.error = error