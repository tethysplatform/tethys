from tethys_apps.base.app_base import TethysAppBase
from tethys_apps.base.controller import page as page_controller


class AppSingleton(type):
    """
    Metaclass used by TethysAppBase to ensure all Tethys app instances are singletons
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ComponentBase(TethysAppBase, metaclass=AppSingleton):
    """
    Base class used for Component Apps.

    Inherited Attributes:
      name (string): Name of the app.
      description (string): Description of the app.
      package (string): Name of the app package. (Note: should not be changed)
      index (string): Lookup term for the index URL of the app.
      icon (string): Location of the image to use for the app icon.
      root_url (string): Root URL of the app.
      color (string): App theme color as RGB hexadecimal.
      tags (string): A string for filtering apps.
      enable_feedback (boolean): Shows feedback button on all app pages.
      feedback_emails (list): A list of emails corresponding to where submitted feedback forms are sent.

    Unique Attributes:
      default_layout (string): The default layout for the app. Can be ``"NavHeader"`` or ``None``.
      nav_links (list or "auto"): A list of dictionaries containing navigation links for the app.
        Each dictionary should have a "title" and "href" key. If set to "auto", the navigation links will be
        automatically generated based on the functions decorated with ``@App.page``.

    """

    @property
    def navigation_links(self):
        nav_links = self.nav_links
        if nav_links == "auto":
            nav_links = []
            for url_map in sorted(
                self.registered_url_maps,
                key=lambda x: x.index if x.index is not None else 999,
            ):
                href = f"/apps/{self.root_url}/"
                if url_map.name != self.index:
                    href += url_map.name.replace("_", "-") + "/"
                if url_map.index == -1:
                    continue  # Do not render
                nav_links.append(
                    {
                        "title": url_map.title,
                        "href": href,
                    }
                )
            self.nav_links = nav_links  # Caches results of "auto"
        return nav_links

    @classmethod
    def page(cls, *args, **kwargs):

        kwargs["app"] = cls
        return page_controller(*args, **kwargs)
