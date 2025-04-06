from tethys_portal.settings import STATIC_URL
from pathlib import Path

THIS_DIR = Path(__file__).parent
RESOURCE_DIR = THIS_DIR / "resources"


def LayerPanel(lib, **kwargs):
    return lib.ollp.LayerPanel(**kwargs)


def PageLoader(lib, **kwargs):
    hide_loading, set_hide_loading = lib.hooks.use_state(True)
    hide_content, set_hide_content = lib.hooks.use_state(True)

    lib.hooks.use_effect(
        # Delay the content load so it doesn't flash at all
        lambda: (
            None
            if all(
                [
                    set_hide_loading(False),
                    lib.utils.background_execute(set_hide_content, [False], 0.5),
                    lib.utils.background_execute(set_hide_loading, [True], 2),
                ]
            )
            else None
        ),
        dependencies=[],
    )

    return lib.html.div(
        (
            lib.html.div(key="loading-content")(
                lib.tethys.LoadingAnimation(),
            )
            if not hide_loading
            else None
        ),
        lib.html.div(
            key="page-content",
            style=lib.Props(display=None if hide_content else "unset"),
        )(kwargs.get("content", [])),
    )


def LoadingAnimation(lib, **kwargs):
    return lib.html._(
        lib.html.div(
            style=lib.Props(
                zIndex=1029,
                background="white",
                top=0,
                right=0,
                bottom=0,
                left=0,
                position="absolute",
            )
        )(
            lib.html.div(className="center"),
            lib.html.div(className="inner-spin")(
                lib.html.div(className="inner-arc inner-arc_start-a"),
                lib.html.div(className="inner-arc inner-arc_end-a"),
                lib.html.div(className="inner-arc inner-arc_start-b"),
                lib.html.div(className="inner-arc inner-arc_end-b"),
                lib.html.div(className="inner-moon-a"),
                lib.html.div(className="inner-moon-b"),
            ),
            lib.html.div(className="outer-spin")(
                lib.html.div(className="outer-arc outer-arc_start-a"),
                lib.html.div(className="outer-arc outer-arc_end-a"),
                lib.html.div(className="outer-arc outer-arc_start-b"),
                lib.html.div(className="outer-arc outer-arc_end-b"),
                lib.html.div(className="outer-moon-a"),
                lib.html.div(className="outer-moon-b"),
            ),
            lib.html.div(className="loading-text")("Loading..."),
        )
    )


def BaseMapSuite(lib, **kwargs):
    default = kwargs.get("default", "OpenStreetMap")
    ESRI_BASEMAP_NAMES = [
        "NatGeo_World_Map",
        "USA_Topo_Maps",
        "World_Imagery",
        "World_Physical_Map",
        "World_Shaded_Relief",
        "World_Street_Map",
        "World_Terrain_Base",
        "World_Topo_Map",
    ]
    CARTO_DB_BASEMAP_STYLES = ["light", "dark"]
    CARTO_DB_BASEMAP_LABELS = ["all", "nolabels"]
    SUPPORTED_BASEMAPS = {
        "None": lib.ol.source.XYZ(),
        "OpenStreetMap": lib.ol.source.OSM(),
        # "Bing": lib.ol.source.BingMaps(),
        "XYZ": lib.ol.source.XYZ(
            url="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png"
        ),
        **{
            " ".join(esri_basemap.split("_")): lib.ol.source.XYZ(
                url=f"https://server.arcgisonline.com/ArcGIS/rest/services/{esri_basemap}/MapServer/tile/{{z}}/{{y}}/{{x}}"
            )
            for esri_basemap in ESRI_BASEMAP_NAMES
        },
        **{
            f"CartoDB ({style}_{label})": lib.ol.source.XYZ(
                url=f"http://{{1-4}}.basemaps.cartocdn.com/{style}_{label}/{{z}}/{{x}}/{{y}}.png"
            )
            for style, label in [
                (style, label)
                for style in CARTO_DB_BASEMAP_STYLES
                for label in CARTO_DB_BASEMAP_LABELS
            ]
        },
    }
    return lib.ol.layer.Group(title="Basemap", fold="close")(
        *[
            lib.ol.layer.Tile(visible=default == title, type="base", title=title)(
                source
            )
            for title, source in SUPPORTED_BASEMAPS.items()
        ]
    )


def Map(lib, **kwargs):
    on_click = kwargs.get("onClick")
    return lib.ol.Map(**({"onClick": on_click} if on_click else {}))(
        lib.ol.View(
            center=kwargs.get("center", [-100, 40]), zoom=kwargs.get("zoom", 3.5)
        ),
        lib.tethys.BaseMapSuite(),
        lib.ol.layer.Group(title="Overlays", fold="open")(*kwargs.get("children", [])),
        lib.ol.control.ScaleLine(),
        lib.tethys.LayerPanel(),
    )


def Panel(lib, **kwargs):
    show = kwargs.get("show", False)
    set_show = kwargs.get("set_show", lambda x: x)
    position = kwargs.get("position", "end")
    extent = kwargs.get("extent", "40vw")
    name = kwargs.get("name", "Panel")
    style = kwargs.get("style", {})
    if position in ["top", "bottom"]:  # pragma: no cover
        style["height"] = extent
    else:
        style["width"] = extent

    def handle_close(event):  # pragma: no cover
        set_show(False)

    return lib.html.div(
        role="dialog",
        **{"aria-modal": "true"},
        class_name=f"offcanvas offcanvas-{position}{' show' if show else ''}",
        tabIndex="-1",
        style=lib.Props(visibility="visible") | style,
    )(
        lib.html.div(class_name="offcanvas-header")(
            lib.html.div(class_name="offcanvas-title h5")(name),
            lib.html.button(
                type="button",
                class_name="btn-close",
                **{"aria-label": "true"},
                onClick=handle_close,
            ),
        ),
        lib.html.div(class_name="offcanvas-body")(*kwargs.get("children", [])),
    )


def HeaderButton(lib, **kwargs):
    defaults = lib.Props(
        variant="light",
        size="sm",
        class_name=f"{kwargs.get('class_name', '')} styled-header-button",
        style=lib.Props(
            background_color="rgba(255, 255, 255, 0.1)",
            border="none",
            color="white",
            border_radius="50%" if kwargs.get("shape") == "circle" else "unset",
        ),
    )
    return lib.bs.Button(**dict(defaults, **kwargs))(
        *kwargs.get("children", []),
    )


def NavIcon(lib, **kwargs):
    return lib.html.img(
        src=kwargs.get("src"),
        class_name="d-inline-block align-top",
        style=lib.Props(
            padding=0,
            height="30px",
            **{"border-radius": "50%"},
            background=kwargs.get("backgroundColor") or kwargs.get("background-color"),
        ),
    )


def _get_db_object(app):
    return app.db_object


def HeaderWithNavBar(lib, **kwargs):
    app = kwargs["app"]
    user = kwargs["user"]
    nav_links = kwargs.get("nav_links", [])
    app_db_query = lib.hooks.use_query(_get_db_object, {"app": app})
    app_id = app_db_query.data.id if app_db_query.data else 999
    location = lib.hooks.use_location()
    margin_top, set_margin_top = lib.hooks.use_state(-56)
    redirect, set_redirect = lib.hooks.use_state(False)

    lib.hooks.use_effect(
        lambda: lib.utils.background_execute(set_margin_top, [0], 0.5), []
    )

    def handle_exit(*_, **__):  # pragma: no cover
        set_margin_top(-56)
        set_redirect(True)

    return lib.html.div(
        (
            lib.html.script(
                f"""window.setTimeout(function () {{window.location = "{app.exit_url}";}}, 200);"""
            )
            if redirect
            else None
        ),
        lib.bs.Navbar(
            key="navbar",
            fixed="top",
            class_name="shadow",
            expand=False,
            variant="dark",
            style=lib.Props(
                background=app.color,
                height="56px",
                margin_top=margin_top,
                **{
                    "transition": "margin 0.4s ease",
                    "-webkit-transition": "margin 0.4s ease",
                    "-moz-transition": "margin 0.4s ease",
                    "-o-transition": "margin 0.4s ease",
                },
            ),
        )(
            lib.bs.Container(as_="header", fluid=True, class_name="px-4")(
                lib.bs.NavbarToggle(
                    aria_controls="offcanvasNavbar",
                    class_name="styled-header-button",
                ),
                lib.bs.NavbarBrand(
                    href=f"/apps/{app.root_url}/",
                    class_name="mx-0 d-none d-sm-block",
                    style=lib.Props(color="white"),
                )(
                    lib.tethys.NavIcon(
                        src=f"{STATIC_URL}{app.icon}", background_color=app.color
                    ),
                    f" {app.name}",
                ),
                lib.bs.Form(inline="true")(
                    (
                        lib.tethys.HeaderButton(
                            id="btn-app-settings",
                            href=f"/admin/tethys_apps/tethysapp/{app_id}/change/",
                            class_name="me-2",
                        )(
                            lib.icons.Gear(size="1.5rem"),
                        )
                        if user.is_staff
                        else None
                    ),
                    lib.tethys.HeaderButton(
                        id="btn-exit-app",
                        href="#",
                        onClick=handle_exit,
                    )(
                        lib.icons.X(size="1.5rem"),
                    ),
                ),
                lib.bs.NavbarOffcanvas(
                    id="offcanvasNavbar", aria_labelledby="offcanvasNavbarLabel"
                )(
                    lib.bs.OffcanvasHeader(closeButton=True)(
                        lib.bs.OffcanvasTitle(id="offcanvasNavbarLabel")("Navigation")
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
                                    href=link["href"],
                                    key=f"link-{index}",
                                    active=location.pathname == link["href"],
                                    style=lib.Props(padding_left="10pt"),
                                )(
                                    link["title"],
                                )
                                for index, link in enumerate(nav_links)
                            ],
                        )
                    ),
                ),
            ),
        ),
    )
