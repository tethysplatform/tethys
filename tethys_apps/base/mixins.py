class TethysBaseMixin:
    """
    Provides methods and properties common to the TethysBase and model classes.
    """
    root_url = ''
    index = ''

    @property
    def url_namespace(self):
        """
        Get the namespace for the app or extension.
        """
        return self.root_url.replace('-', '_')

    @property
    def index_url(self):
        return f'{self.url_namespace}:{self.index}'
