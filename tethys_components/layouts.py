from reactpy import component, html
from tethys_components.utils import Props
from tethys_components.custom import HeaderWithNavBar

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

