from django.shortcuts import render
from tethys_components.library import ComponentLibrary, ComponentLibraryManager
from tethys_components.utils import _get_layout_component
from tethys_portal.optional_dependencies import has_module
from uuid import uuid4


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

    return render(request, "tethys_apps/component_base.html", context)


if has_module("reactpy"):
    from reactpy import component

    @component
    def page_component_wrapper(app, user, layout, page_func, extras=None):
        """
        ReactPy component that wraps every custom user page

        The path to this component is hard-coded in tethys_apps/component_base.html
        and the component is registered on server startup in tethys_portal/asgi.py

        Args:
            app(TethysApp instance): The app rendering the page
            user(Django User object): The loggin in user acessing the page
            layout(func or None): The layout component, if any, that the page content will be nested in
            component(func): The page component to render
        """
        lib = ComponentLibraryManager.get_library(
            f"{app.package}-{page_func.__name__}", extras
        )
        page_obj = page_func(lib, **extras) if extras else page_func(lib)
        hide_loading, set_hide_loading = lib.hooks.use_state(False)

        lib.hooks.use_effect(
            lambda: None if set_hide_loading(True) else None,
            dependencies=[],
        )

        if layout is not None:
            page_obj = layout(
                lib,
                app=app,
                user=user,
                nav_links=app.navigation_links,
                content=page_obj,
            )

        # Below used instead of hasattr(lib, "m") since that would automatically create
        # the attribute and return True due to the nature of its __getattr__ method
        if "m" in dir(lib):
            page_obj = lib.m.MantineProvider(page_obj)

        page_obj = lib.html.div(
            lib.html.script(key=str(uuid4()), type="importmap")(lib.get_importmap()),
            page_obj,
            (
                lib.html.script(
                    """
                    setTimeout(() => {
                        const loadingRoot = document.getElementById("loading-root");
                        if (loadingRoot) {
                            loadingRoot.style.display = "none";
                        }
                    }, 1000);
                """
                )
                if hide_loading
                else None
            ),
        )

        return page_obj
