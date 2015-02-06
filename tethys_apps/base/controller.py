from .url_map import UrlMapBase


def app_controller_maker(root_url):
    """
    Returns an AppController class that is bound to a specific root url. This method is deprecated. Use url_map_maker.
    """
    properties = {'root_url': root_url}
    return type('UrlMap', (UrlMapBase,), properties)


