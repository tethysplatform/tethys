class TethysBaseMixin:
    """
    Provides methods and properties common to the TethysBase and model classes.
    """
    root_url = ''

    @property
    def url_namespace(self):
        """
        Get the namespace for the app or extension.
        """
        return self.root_url.replace('-', '_')
