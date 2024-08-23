from reactpy import component, html
from tethys_components.utils import Props
from tethys_components.custom import HeaderWithNavBar

def get_layout_component(app, layout):
    if callable(layout) or layout is None:
        layout_func = layout
    elif layout == 'default':
        if callable(app.default_layout):
            layout_func = app.default_layout
        else:
            layout_func = globals()[app.default_layout]
    else:
        layout_func = globals()[app.default_layout]

    return layout_func

@component
def NavHeader(props, *children):
    app = props.get('app')
    user = props.get('user')
    nav_links = props.get('nav-links')

    return html.div(
        Props(class_name="h-100"),
        HeaderWithNavBar(app, user, nav_links),
        html.div(
            Props(
                style=Props(padding_top="56px")
            ),
            *children
        ),
    )

