from django.shortcuts import render
from tethys_components.library import Library as ComponentLibrary
from tethys_apps.utilities import get_active_app
from tethys_components.utils import get_layout_component
from tethys_portal.optional_dependencies import has_module

if has_module('reactpy'):
   from reactpy import component 
else:
    component = lambda x: x # pragma: no cover

def global_page_controller(
        request, 
        layout, 
        component_func, 
        component_source_code, 
        title=None, 
        custom_css=[], 
        custom_js=[]
):
    app = get_active_app(request=request, get_class=True)
    layout_func = get_layout_component(app, layout)
    ComponentLibrary.refresh(new_identifier=component_func.__name__.replace('_', '-'))
    ComponentLibrary.load_dependencies_from_source_code(component_source_code)

    context = {
        'app': app,
        'layout_func': lambda: layout_func,
        'component_func': lambda: component_func,
        'reactjs_version': ComponentLibrary.REACTJS_VERSION,
        'title': title,
        'custom_css': custom_css,
        'custom_js': custom_js,
    }

    return render(request, 'tethys_apps/reactpy_base.html', context)

@component
def page_component_wrapper(app, user, layout, component):
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
    if layout is not None:
        return layout(
            {
                'app': app,
                'user': user,
                'nav-links': app.navigation_links
            },
            component()
        )
    else:
        return component()
