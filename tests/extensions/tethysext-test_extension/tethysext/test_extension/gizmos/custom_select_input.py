from tethys_sdk.gizmos import TethysGizmoOptions


class CustomSelectInput(TethysGizmoOptions):
    """
    Custom select input gizmo.
    """

    gizmo_name = "custom_select_input"

    def __init__(
        self,
        name,
        display_text="",
        options=(),
        initial=(),
        multiselect=False,
        disabled=False,
        error="",
        **kwargs,
    ):
        """
        constructor
        """
        # Initialize parent
        super().__init__(**kwargs)

        # Initialize Attributes
        self.name = name
        self.display_text = display_text
        self.options = options
        self.initial = initial
        self.multiselect = multiselect
        self.disabled = disabled
        self.error = error

    @staticmethod
    def get_vendor_js():
        """
        JavaScript vendor libraries.
        """
        return (
            "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/js/select2.min.js",
        )

    @staticmethod
    def get_vendor_css():
        """
        CSS vendor libraries.
        """
        return (
            "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/css/select2.min.css",
        )

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo.
        """
        return ("test_extension/gizmos/custom_select_input/custom_select_input.js",)

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo .
        """
        return ("test_extension/gizmos/custom_select_input/custom_select_input.css",)
