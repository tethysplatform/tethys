from reactpy import component
from tethys_portal.settings import STATIC_URL
from .utils import Props
from .library import ComponentLibraryManager

lib = ComponentLibraryManager.get_library("tethys_components_custom")

@component
def Panel(props, *children):
    show = props.pop("show", False)
    set_show = props.pop("set-show", lambda x: x)
    position = props.pop("position", "bottom")
    extent = props.pop("extent", "300px")
    name = props.pop("name", "Panel")
    style = {}
    if position in ["top", "bottom"]:
        style["height"] = extent
    else:
        style["width"] = extent

    def handle_close(event):
        set_show(False)

    return lib.html.div(
        Props(
            role="dialog",
            aria_modal="true",
            class_name=f"offcanvas offcanvas-{position}{' show' if show else ''}",
            tabindex="-1",
            style=Props(visibility="visible") | style,
        ),
        lib.html.div(
            Props(class_name="offcanvas-header"),
            lib.html.div(Props(class_name="offcanvas-title h5"), name),
            lib.html.button(
                Props(
                    type="button",
                    class_name="btn-close",
                    aria_label="Close",
                    on_click=handle_close,
                )
            ),
        ),
        lib.html.div(Props(class_name="offcanvas-body"), *children),
    )


# @component  NOTE: Breaks if @component decorator applied
def HeaderButton(props, *children):
    href = props.get("href")
    shape = props.get("shape")
    style = props.pop("style", {})
    class_name = props.pop("class_name", "")

    return lib.bs.Button(
        Props(
            href=href,
            variant="light",
            size="sm",
            class_name=f"{class_name} styled-header-button",
            style=Props(
                background_color="rgba(255, 255, 255, 0.1)",
                border="none",
                color="white",
            )
            | style
            | (Props(border_radius="50%") if shape == "circle" else {}),
        )
        | props,
        *children,
    )


# @component  NOTE: Breaks if @component decorator applied
def NavIcon(src, background_color):
    return lib.html.img(
        Props(
            src=src,
            class_name="d-inline-block align-top",
            style={
                "padding": "0",
                "height": "30px",
                "border-radius": "50%",
                "background": background_color,
            },
        )
    )


@component
def NavMenu(props, *children):
    nav_title = props.pop("nav-title", "Navigation")

    return lib.html.div(
        lib.bs.Offcanvas(
            Props(id="offcanvasNavbar", show=False) | props,
            lib.bs.OffcanvasHeader(
                Props(closeButton=True), lib.bs.OffcanvasTitle(nav_title)
            ),
            lib.bs.OffcanvasBody(*children),
        )
    )


def get_db_object(app):
    return app.db_object


@component
def HeaderWithNavBar(app, user, nav_links):
    app_db_query = lib.hooks.use_query(get_db_object, {"app": app})
    app_id = app_db_query.data.id if app_db_query.data else 999
    location = lib.hooks.use_location()

    return lib.bs.Navbar(
        Props(
            fixed="top",
            class_name="shadow",
            expand=False,
            variant="dark",
            style=Props(background=app.color, min_height="56px"),
        ),
        lib.bs.Container(
            Props(as_="header", fluid=True, class_name="px-4"),
            lib.bs.NavbarToggle(
                Props(
                    aria_controls="offcanvasNavbar", class_name="styled-header-button"
                )
            ),
            lib.bs.NavbarBrand(
                Props(
                    href=f"/apps/{app.root_url}/",
                    class_name="mx-0 d-none d-sm-block",
                    style=Props(color="white"),
                ),
                NavIcon(src=f"{STATIC_URL}{app.icon}", background_color=app.color),
                f" {app.name}",
            ),
            lib.bs.Form(
                Props(inline="true"),
                (
                    HeaderButton(
                        Props(
                            id="btn-app-settings",
                            href=f"/admin/tethys_apps/tethysapp/{app_id}/change/",
                            tooltipPlacement="bottom",
                            tooltipText="Settings",
                            class_name="me-2",
                        ),
                        lib.icons.Gear(Props(size="1.5rem")),
                    )
                    if user.is_staff
                    else ""
                ),
                HeaderButton(
                    Props(
                        id="btn-exit-app",
                        href=app.exit_url,
                        tooltipPlacement="bottom",
                        tooltipText="Exit",
                    ),
                    lib.icons.X(Props(size="1.5rem")),
                ),
            ),
            lib.bs.NavbarOffcanvas(
                Props(id="offcanvasNavbar", aria_labelledby="offcanvasNavbarLabel"),
                lib.bs.OffcanvasHeader(
                    Props(closeButton=True),
                    lib.bs.OffcanvasTitle(
                        Props(id="offcanvasNavbarLabel"), "Navigation"
                    ),
                ),
                lib.bs.OffcanvasBody(
                    lib.bs.Nav(
                        {
                            "variant": "pills",
                            "defaultActiveKey": f"/apps/{app.root_url}",
                            "class_name": "flex-column",
                        },
                        [
                            lib.bs.NavLink(
                                Props(
                                    href=link["href"],
                                    key=f"link-{index}",
                                    active=location.pathname == link["href"],
                                    style=Props(padding_left="10pt"),
                                ),
                                link["title"],
                            )
                            for index, link in enumerate(nav_links)
                        ],
                    )
                ),
            ),
        ),
    )
