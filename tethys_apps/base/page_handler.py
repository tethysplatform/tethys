from django.shortcuts import render
from tethys_components.library import ComponentLibrary, ComponentLibraryManager
from tethys_components.utils import _get_layout_component
from tethys_portal.optional_dependencies import has_module


def global_page_controller(
    request,
    app,
    layout,
    component_func,
    title=None,
    custom_css=None,
    custom_js=None,
    **kwargs,
):
    layout_func = _get_layout_component(app, layout)

    context = {
        "app": app,
        "layout_func": lambda: layout_func,
        "component_func": lambda: component_func,
        "reactjs_version": ComponentLibrary.REACTJS_VERSION,
        "reactjs_version_int": ComponentLibrary.REACTJS_VERSION_INT,
        "title": title,
        "custom_css": custom_css or [],
        "custom_js": custom_js or [],
        "extras": kwargs,
    }

    return render(request, "tethys_apps/reactpy_base.html", context)


if has_module("reactpy"):
    from reactpy import component

    @component
    def page_component_wrapper(app, user, layout, component, extras=None):
        """
        ReactPy Component that wraps every custom user page

        The path to this component is hard-coded in tethys_apps/reactpy_base.html
        and the component is registered on server startup in tethys_portal/asgi.py

        Args:
            app(TethysApp instance): The app rendering the page
            user(Django User object): The loggin in user acessing the page
            layout(func or None): The layout component, if any, that the page content will be nested in
            component(func): The page component to render
        """
        lib = ComponentLibraryManager.get_library(f"{app.package}-{component.__name__}")
        component_obj = component(lib, **extras) if extras else component(lib)

        if layout is not None:
            page_obj = layout(
                {"app": app, "user": user, "nav-links": app.navigation_links},
                component_obj,
            )
        else:
            page_obj = component_obj

        return page_obj
