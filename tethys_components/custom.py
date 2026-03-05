from tethys_portal.settings import STATIC_URL
from pathlib import Path

THIS_DIR = Path(__file__).parent
RESOURCE_DIR = THIS_DIR / "resources"


def Display(lib, **kwargs):
    """A full screen container for nesting content within."""
    style = lib.Style(height="100%")
    if "style" in kwargs:
        style |= kwargs["style"]
    return lib.bs.Container(fluid=True, style=style)(
        *kwargs.get("children", []),
    )


def LayerPanel(lib):
    return lib.ollp.LayerPanel()


def PageLoader(lib, content):
    hide_loading, set_hide_loading = lib.hooks.use_state(True)
    hide_content, set_hide_content = lib.hooks.use_state(True)
    lib.hooks.use_effect(
        # This None if ... else None is a weird pattern used to ensure that nothing is returned by this
        # lambda, since if anything besided None is returned, it is assumed to be a cleanup function
        lambda: (
            None if any([set_hide_loading(False), set_hide_content(False)]) else None
        ),
        dependencies=[],
    )

    return lib.html.div(style=lib.Style(height="100%", width="100%"))(
        (
            lib.html.div(key="loading-content")(
                lib.tethys.LoadingAnimation(),
            )
            if not hide_loading
            else None
        ),
        lib.html.div(
            key="page-content",
            style=lib.Style(
                display=None if hide_content else "unset", height="100%", width="100%"
            ),
        )(
            content,
            (
                lib.html.div(style=lib.Style(display="none"))(
                    lib.html.div(
                        id_="trigger-loaded", onClick=lambda _: set_hide_loading(True)
                    ),
                    lib.html.script(
                        """
                    window.onload = function () {
                        window.setTimeout(function () {
                            try {
                                document.getElementById('trigger-loaded').click();
                            } catch (e) {
                                'pass';
                            }
                        }, 1000)
                    }
                """
                    ),
                )
                if not hide_loading
                else None
            ),
        ),
    )


def LoadingAnimation(lib):
    return lib.html._(
        lib.html.div(
            style=lib.Style(
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


def BaseMapSuite(lib, default="OpenStreetMap"):
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
            options=lib.Props(url="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png")
        ),
        **{
            " ".join(esri_basemap.split("_")): lib.ol.source.XYZ(
                options=lib.Props(
                    url=f"https://server.arcgisonline.com/ArcGIS/rest/services/{esri_basemap}/MapServer/tile/{{z}}/{{y}}/{{x}}"
                )
            )
            for esri_basemap in ESRI_BASEMAP_NAMES
        },
        **{
            f"CartoDB ({style}_{label})": lib.ol.source.XYZ(
                options=lib.Props(
                    url=f"http://{{1-4}}.basemaps.cartocdn.com/{style}_{label}/{{z}}/{{x}}/{{y}}.png"
                )
            )
            for style, label in [
                (style, label)
                for style in CARTO_DB_BASEMAP_STYLES
                for label in CARTO_DB_BASEMAP_LABELS
            ]
        },
    }
    return lib.ol.layer.Group(options=lib.Props(title="Basemap", fold="close"))(
        *[
            lib.ol.layer.Tile(
                options=lib.Props(
                    visible=str(default) == str(title), type="base", title=str(title)
                )
            )(source)
            for title, source in SUPPORTED_BASEMAPS.items()
        ]
    )


def Map(
    lib,
    default_basemap="OpenStreetMap",
    projection="EPSG:3857",
    center=None,
    zoom=1,
    children=None,
    **kwargs,
):
    """A Map for displaying geospatial data. Fixed to the EPSG:3857 projection.

    Args:
        center ([int|float,int|float]): The center point of the rendered map, in [lon, lat] or [x, y] format. Defaults to [-100, 40].
        zoom (int|float): The initial zoom level of the map, where 1 is at the global scale and 20 is at the neighborhood scale. Defaults to 3.5.
        on_click (callable): A function that should be called when the map is clicked. Defaults to None.
        children (list[]): A list of layers to be rendered. These can also be passed in as nested components (i.e. Map()(layer1, layer2, layer3)). Defaults to [].
    """
    if isinstance(projection, dict):
        if not center and not projection.get("definition"):
            raise ValueError(
                "Either provide a center point or a projection definition from which a center point can be calculated."
            )
    center = center or (
        [-100, 40]
        if projection == "EPSG:3857"
        else lib.utils.transform_coordinate([-100, 40], "EPSG:3857", projection)
    )
    view_opts = lib.Props(projection=projection)
    actual_children = []
    overlays = []
    if children:
        for child in children:
            if not child:
                continue
            if dict(child)["tagName"] == "Overlay":
                overlays.append(child)
            else:
                actual_children.append(child)
    if isinstance(projection, dict) and projection.get("extent"):
        view_opts |= lib.Props(extent=projection["extent"])
    return lib.ol.Map(**lib.Props(**kwargs))(
        lib.ol.View(options=view_opts, center=center, zoom=zoom),
        lib.tethys.BaseMapSuite(default=default_basemap),
        *overlays if overlays else [],
        lib.ol.layer.Group(options=lib.Props(title="Overlays", fold="open"))(
            *actual_children or []
        ),
        lib.ol.control.ScaleLine(),
        lib.tethys.LayerPanel(),
    )


def Chart(
    lib,
    data=None,
    width=400,
    height=300,
    color="red",
    title="",
    x_label="",
    y_label="",
    x_attr="x",
    y_attr="y",
):
    """A chart for displaying x-y coordinate pairs

    Args:
        data (DataFrame|): Any dataset that can be initialized as a Panadas DataFrame, including a Pandas Dataframe itself.
        width (int): The rendered width of the chart in pixels. Defaults to 500.
        height (int): The rendered height of the chart in pixels. Defaults to 400.
        x_label (str): The rendered label of the x-axis. Defauls to "".
        color (str): The color of the chart. Defaults to "red".
        title (str): The title of the chart. Defaults to "".
        x_label (str): The rendered label of the x-axis. Defauls to "".
        y_label (str): The rendered label of the y-axis. Defauls to "".
        x_attr (str): The name of the attribute in the data to use for the x-axis. Defaults to "x".
        y_attr (str): The name of the attribute in the data to use for the y-axis. Defaults to "y".
    """
    from pandas import DataFrame

    if data is None:
        data = DataFrame(columns=[x_attr, y_attr])
    elif not isinstance(data, DataFrame):
        data = DataFrame(data)

    return lib.pl.Plot(
        data=[
            lib.Props(
                x=list(getattr(data, x_attr)),
                y=list(getattr(data, y_attr)),
                type="scatter",
                mode="lines+markers",
                marker=lib.Props(color=color),
            )
        ],
        layout=lib.Props(
            width=width,
            height=height,
            title=lib.Props(text=title),
            xaxis=lib.Props(title=lib.Props(text=x_label)),
            yaxis=lib.Props(title=lib.Props(text=y_label)),
        ),
    )


def Panel(
    lib,
    show=True,
    on_close=lambda _: None,
    anchor="right",
    extent="500px",
    title="Panel",
    style=None,
    children=None,
):
    """A pop out panel with custom content anchored to the left, right, top or bottom

    Args:
        show (bool): Whether to show initially. Defaults to False.
        set_show (callable): The function that will be used to update the show state. It accepts
        anchor (str): Where to anchor the panel. Must be one of: right, left, top, or bottom. Defaults to "right".
        extent (str): The height/width of the panel. Defaults to "500px".
        title (str): The title to display at the top of the panel. Defaults to "Panel".
        style (dict[str: str]|Style): Any CSS styles as key:value pairs to be applied to the panel. Defaults to {}.
        children: The actual nested content that is to be rendered. Can also be supplied as call args to Panel (i.e. Panel()(panel_content)).
    """
    style = style or {}
    if anchor in ["top", "bottom"]:
        style["height"] = extent
    else:
        if anchor not in ["right", "left"]:
            raise ValueError("Position must be one of: right, left, top, or bottom")
        anchor = {"right": "end", "left": "start"}[anchor]
        style["width"] = extent

    return lib.html.div(
        role="dialog",
        **{"aria-modal": "true"},
        class_name=f"offcanvas offcanvas-{anchor}{' show' if show else ''}",
        tabIndex="-1",
        style=lib.Style(visibility="visible") | style,
    )(
        lib.html.div(class_name="offcanvas-header")(
            lib.html.div(class_name="offcanvas-title h5")(title),
            lib.html.button(
                type="button",
                class_name="btn-close",
                **{"aria-label": "true"},
                onClick=on_close,
            ),
        ),
        lib.html.div(class_name="offcanvas-body")(*children or []),
    )


def HeaderButton(lib, **kwargs):
    defaults = lib.Props(
        variant="light",
        size="sm",
        class_name=f"{kwargs.get('class_name', '')} styled-header-button",
        style=lib.Style(
            background_color="rgba(255, 255, 255, 0.1)",
            border="none",
            color="white",
            border_radius="50%" if kwargs.get("shape") == "circle" else "unset",
        )
        | kwargs.get("style", {}),
    )
    return lib.bs.Button(**dict(defaults, **kwargs))(
        *kwargs.get("children", []),
    )


def NavIcon(lib, src="", style=None):
    style = style or {}
    return lib.html.img(
        src=src,
        class_name="d-inline-block align-top",
        style=lib.Style(
            padding=0,
            height="30px",
            **{"border-radius": "50%"},
        )
        | style,
    )


def HeaderWithNavBar(lib, app, user, nav_links=None):
    nav_links = nav_links or []
    app_db_query = lib.hooks.use_query(lib.utils._get_db_object, {"app": app})
    app_id = app_db_query.data.id if app_db_query.data else 999
    location = lib.hooks.use_location()
    margin_top, set_margin_top = lib.hooks.use_state(-56)
    redirect, set_redirect = lib.hooks.use_state(False)

    lib.hooks.use_effect(
        lambda: (
            None if lib.utils.background_execute(set_margin_top, [0], 0.5) else None
        ),
        [],
    )

    def handle_exit(*_, **__):  # pragma: no cover
        set_margin_top(-56)
        set_redirect(True)

    return lib.html.div(
        (
            lib.html.div(
                style=lib.Style(
                    position="fixed",
                    top=0,
                    bottom=0,
                    right=0,
                    left=0,
                    background="white",
                    zIndex=100,
                )
            )(
                lib.html.script(
                    f"""window.setTimeout(function () {{window.location = "{app.exit_url}";}}, 200);"""
                )
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
            style=lib.Style(
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
                (
                    lib.bs.NavbarToggle(
                        aria_controls="offcanvasNavbar",
                        class_name="styled-header-button",
                    )
                    if len(nav_links) > 1
                    else lib.html.span()
                ),
                lib.bs.NavbarBrand(
                    href=f"/apps/{app.root_url}/",
                    class_name="mx-0 d-none d-sm-block",
                    style=lib.Style(color="white"),
                )(
                    lib.tethys.NavIcon(
                        src=f"{STATIC_URL}{app.icon}",
                        style=lib.Style(background_color=app.color),
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
                                    active=location.pathname == link["href"]
                                    or location.pathname[:-1] == link["href"],
                                    style=lib.Style(padding_left="10pt"),
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
