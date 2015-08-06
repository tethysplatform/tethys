DEFAULT_EXPRESSION = '[0-9A-Za-z-_.]+'


class UrlMapBase(object):
    """
    Abstract base class for Tethys app controllers
    """

    root_url = ''

    def __init__(self, name, url, controller, regex=None):
        """
        Constructor

        Args:
          name (str): Name of the url map. Letters and underscores only (_).
          url (str): Url pattern to map to the controller.
          controller (str): Dot-notation _path to the controller.
          regex (str or iterable, optional): Custom regex pattern(s) for url variables. If a string is provided, it will be applied to all variables. If a list or tuple is provided, they will be applied in variable order.
        """
        # Validate
        if regex and (not isinstance(regex, basestring) and not isinstance(regex, tuple) and not isinstance(regex, list)):
            raise ValueError('Value for "regex" must be either a string, list, or tuple.')

        self.name = name
        self.url = django_url_preprocessor(url, self.root_url, regex)
        self.controller = '.'.join(['tethys_apps.tethysapp', controller])
        self.custom_match_regex = regex

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


def django_url_preprocessor(url, root_url, custom_regex=None):
    """
    Convert url from the simplified string version for app developers to Django regular expression.

    e.g.:

        '/example/resource/{variable_name}/'
        r'^/example/resource/?P<variable_name>[1-9A-Za-z\-]+/$'
    """

    # Split the url into parts
    url_parts = url.split('/')
    django_url_parts = []

    # Remove the root of the url if it is present
    if root_url in url_parts:
        index = url_parts.index(root_url)
        url_parts.pop(index)

    # Look for variables
    url_variable_count = 0
    for part in url_parts:
        # Process variables
        if '{' in part or '}' in part:
            variable_name = part.replace('{', '').replace('}', '')

            # Determine expression to use
            # String case
            if isinstance(custom_regex, basestring):
                expression = custom_regex
            # List or tuple case
            elif (isinstance(custom_regex, list) or isinstance(custom_regex, tuple)) and len(custom_regex) > 0:
                try:
                    expression = custom_regex[url_variable_count]

                except IndexError:
                    expression = custom_regex[0]

                except:
                    raise

            else:
                expression = DEFAULT_EXPRESSION

            part = '(?P<{0}>{1})'.format(variable_name, expression)
            url_variable_count += 1

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
