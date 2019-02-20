class TethysBaseMixin:
    """
    Provides methods and properties common to the TethysBase and model classes.
    """
    root_url = ''

    @property
    def namespace(self):
        """
        Get the namespace for the app or extension.
        """
        if not hasattr(self, '_namespace'):
            self._namespace = None

        if self._namespace is None:
            self._namespace = self.root_url.replace('-', '_')

        return self._namespace
