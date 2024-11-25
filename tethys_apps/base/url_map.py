"""
********************************************************************************
* Name: url_map.py
* Author: Nathan Swain
* Created On: September 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

DEFAULT_EXPRESSION = r"[0-9A-Za-z-_.]+"


class UrlMapBase:
    """
    Abstract URL base class for Tethys app controllers and consumers
    """

    root_url = ""

    def __init__(
        self,
        name,
        url,
        controller,
        protocol="http",
        regex=None,
        handler=None,
        handler_type=None,
        title=None,
        index=None,
    ):
        """
        Constructor

        Args:
          name (str): Name of the url map. Letters and underscores only (_). Must be unique within the app.
          url (str): Url pattern to map the endpoint for the controller or consumer.
          controller (str): Dot-notation path to the controller function or consumer class.
          protocol (str): 'http' for controllers or 'websocket' for consumers. Default is http.
          regex (str or iterable, optional): Custom regex pattern(s) for url variables. If a string is provided, it will be applied to all variables. If a list or tuple is provided, they will be applied in variable order.
          handler (str): Dot-notation path a handler function. A handler is associated to a specific controller and contains the main logic for creating and establishing a communication between the client and the server.
          handler_type (str): Tethys supported handler type. 'bokeh' is the only handler type currently supported.
          title (str): The title to be used both in navigation and in the browser tab.
          index (int): Used to determine the render order of nav items in navigation. Defaults to the unpredictable processing order of decorated functions. Set to -1 to remove from navigation.
        """  # noqa: E501
        # Validate
        if regex and (
            not isinstance(regex, str)
            and not isinstance(regex, tuple)
            and not isinstance(regex, list)
        ):
            raise ValueError(
                'Value for "regex" must be either a string, list, or tuple.'
            )

        self.name = name
        self.url = django_url_preprocessor(url, self.root_url, protocol, regex)
        self.controller = controller
        self.protocol = protocol
        self.custom_match_regex = regex
        self.handler = handler
        self.handler_type = handler_type
        self.title = title
        self.index = index

    def __repr__(self):
        """
        String representation
        """
        return (
            f"<UrlMap: name={self.name}, url={self.url}, controller={self.controller}, protocol={self.protocol}, "
            f"handler={self.handler}, handler_type={self.handler_type}, title={self.title}, index={self.index}>"
        )

    @staticmethod
    def _get_function_dot_path(func):
        return func if isinstance(func, str) else f"{func.__module__}.{func.__name__}"

    def display(self, prefix=""):
        value = (
            f"{prefix}UrlMap:\n"
            f"{prefix}  name: {self.name}\n"
            f"{prefix}  url: {self.url}\n"
            f"{prefix}  protocol: {self.protocol}\n"
            f"{prefix}  controller: {self._get_function_dot_path(self.controller)}\n"
        )
        if self.handler:
            value += (
                f"{prefix}  handler: {self._get_function_dot_path(self.handler)}\n"
                f"{prefix}  handler_type: {self.handler_type}\n"
            )
        return value


def url_map_maker(root_url):
    """
    Returns an UrlMap class that is bound to a specific root url
    """
    properties = {"root_url": root_url}
    return type("UrlMap", (UrlMapBase,), properties)


def django_url_preprocessor(url, root_url, protocol, custom_regex=None):
    """
    Convert url from the simplified string version for app developers to Django regular expression.

    e.g.:

        '/example/resource/{variable_name}/'
        r'^/example/resource/(?P<variable_name>[0-9A-Za-z-]+)//$'
    """
    # Remove last slash if present
    if url.endswith("/"):
        url = url[:-1]

    # Remove starting slash if present
    if url.startswith("/"):
        url = url[1:]

    # Split the url into parts
    url_parts = url.split("/")
    django_url_parts = []

    # Remove the root of the url if it is present
    if root_url in url_parts:
        index = url_parts.index(root_url)
        url_parts.pop(index)

    # Look for variables
    url_variable_count = 0
    for part in url_parts:
        # Process variables
        if "{" in part or "}" in part:
            variable_name = part.replace("{", "").replace("}", "")

            # Determine expression to use
            # String case
            if isinstance(custom_regex, str):
                expression = custom_regex
            # List or tuple case
            elif (
                isinstance(custom_regex, list) or isinstance(custom_regex, tuple)
            ) and len(custom_regex) > 0:
                try:
                    expression = custom_regex[url_variable_count]
                except IndexError:
                    expression = custom_regex[0]

            else:
                expression = DEFAULT_EXPRESSION

            part = f"(?P<{variable_name}>{expression})"
            url_variable_count += 1

        # Collect processed parts
        django_url_parts.append(part)

    # Join the process parts again
    django_url_joined = "/".join(django_url_parts)

    # Final django-formatted url
    if protocol == "http":
        if django_url_joined != "":
            django_url = f"^{django_url_joined}/$"
        else:
            # Handle empty string case
            django_url = r"^$"
    elif protocol == "websocket":
        # Append the "ws" suffix
        if django_url_joined != "":
            django_url = f"^{django_url_joined}/ws/$"
        else:
            # Handle empty string case
            django_url = r"^ws/$"

    return django_url
