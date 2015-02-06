

class UrlMapBase(object):
    """
    Abstract base class for Tethys app controllers
    """

    root_url = ''

    def __init__(self, name, url, controller):
        """
        Constructor
        """
        self.name = name
        self.url = django_url_preprocessor(url, self.root_url)
        self.controller = '.'.join(['tethys_apps.tethysapp', controller])

    def __repr__(self):
        """
        String representation
        """
        return '<UrlMap: name={0}, url={1}, controller={2}>'.format(self.name, self.url, self.controller)


def url_map_maker(root_url):
    """
    Returns an UrlMap class that is bound to a specific root url
    """
    properties = {'root_url': root_url}
    return type('UrlMap', (UrlMapBase,), properties)


def django_url_preprocessor(url, root_url):
    """
    Convert url from the simplified string version for app developers to Django regular expression.

    e.g.:

        '/example/resource/{variable_name}/'
        r'^/example/resource/?P<variable_name>[1-9A-Za-z\-]+/$'
    """
    # Default Django expression that will be matched
    DEFAULT_EXPRESSION = '[0-9A-Za-z-]+'

    # Split the url into parts
    url_parts = url.split('/')
    django_url_parts = []

    # Remove the root of the url if it is present
    if root_url in url_parts:
        index = url_parts.index(root_url)
        url_parts.pop(index)

    # Look for variables
    for part in url_parts:
        # Process variables
        if '{' in part or '}' in part:
            variable_name = part.replace('{', '').replace('}', '')
            part = '(?P<{0}>{1})'.format(variable_name, DEFAULT_EXPRESSION)

        # Collect processed parts
        django_url_parts.append(part)

    # Join the process parts again
    django_url_joined = '/'.join(django_url_parts)

    # Final django-formatted url
    if django_url_joined != '':
        django_url = r'^{0}/$'.format(django_url_joined)
    else:
        # Handle empty string case
        django_url = r'^$'

    return django_url
