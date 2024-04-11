from tethys_sdk.base import TethysExtensionBase


class Extension(TethysExtensionBase):
    """
    Tethys extension class for Test Extension.
    """

    name = "Test Extension"
    package = "test_extension"
    root_url = "test-extension"
    description = "Place a brief description of your extension here."
