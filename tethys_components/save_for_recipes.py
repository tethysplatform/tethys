import random

from reactpy import component, html, hooks
from reactpy_django.hooks import use_location, use_query
from tethys_portal.settings import STATIC_URL
from .utils import Props
from .library import Library as lib


@component
def LeafletMap(props={}):
    height = props.get("height", "500px")
    position = [51.505, -0.09]
    return html.div(
        html.link(
            Props(
                rel="stylesheet",
                href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
                integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=",
                crossorigin="",
            )
        ),
        html.script(
            Props(
                src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
                integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=",
                crossorigin="",
            )
        ),
        lib.lm.MapContainer(
            Props(
                style=Props(height=height),
                center=position,
                zoom=13,
                scrollWheelZoom=True,
            ),
            lib.lm.TileLayer(
                Props(
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                )
            ),
            lib.lm.Marker(
                Props(position=position),
                lib.lm.Popup(
                    "A pretty CSS3 popup. ", html.br(), "Easily customizable."
                ),
            ),
        ),
    )


from tethys_sdk.components import page

lib.register("reactive-button@1.3.15", "rb", use_default=True)


@page
def test_reactive_button():
    state, set_state = lib.hooks.use_state("idle")

    def on_click_handler(event=None):
        set_state("loading")

    return lib.rb.ReactiveButton(
        Props(
            buttonState=state,
            idleText="Submit",
            loadingText="Loading",
            successText="Done",
            onClick=on_click_handler,
        )
    )


@page
def map():
    geojson, set_geojson = lib.hooks.use_state(None)
    show_chart, set_show_chart = lib.hooks.use_state(False)
    chart_data, set_chart_data = lib.hooks.use_state(None)
    feature_data, set_feature_data = lib.hooks.use_state(None)
    map_center, set_map_center = lib.hooks.use_state([39.254852, -98.593853])
    map_zoom, set_map_zoom = lib.hooks.use_state(4)
    load_layer, set_load_layer = lib.hooks.use_state(False)
    map_bounds, set_map_bounds = lib.hooks.use_state({})

    def handle_feature_click(event):
        import random

        set_show_chart(True)
        set_chart_data(
            [
                {
                    "name": f"Thing {i}",
                    "uv": random.randint(0, 10000),
                    "pv": random.randint(0, 10000),
                }
                for i in range(0, random.randint(10, 125))
            ]
        )
        set_feature_data(event["payload"]["properties"])

    def handle_bounds_changed(event):
        if not event["initial"]:
            set_map_center(event["center"])
            set_map_zoom(event["zoom"])
            set_map_bounds(event["bounds"])

        if event["zoom"] >= 9:
            set_load_layer(True)
        else:
            set_load_layer(False)
            set_geojson(None)

    def get_geojson():
        if load_layer:
            import requests

            ymax, xmax = map_bounds["ne"]
            ymin, xmin = map_bounds["sw"]
            r = requests.get(
                f"https://maps.water.noaa.gov/server/rest/services/nwm/ana_inundation_extent/FeatureServer/0/query?geometry=%7B%0D%0A++%22xmin%22+%3A+{xmin}%2C+%0D%0A++%22ymin%22+%3A+{ymin}%2C%0D%0A++%22xmax%22+%3A+{xmax}%2C%0D%0A++%22ymax%22+%3A+{ymax}%2C%0D%0A++%22spatialReference%22+%3A+%7B%22wkid%22+%3A+4326%7D%0D%0A%7D&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=true&outSR=&f=geojson"
            )
            gjson = r.json()
            if "features" in gjson and len(gjson["features"]) > 0:
                set_geojson(r.json())
        set_load_layer(False)

    lib.hooks.use_effect(get_geojson, dependencies=[load_layer])

    return lib.html.div(
        (
            lib.html.div(
                Props(
                    style=Props(
                        position="fixed", bottom="20px", left="20px", z_index="99999"
                    )
                ),
                lib.html.span("LOADING..."),
            )
            if load_layer
            else ""
        ),
        lib.pm.Map(
            Props(
                height="calc(100vh - 62px)",
                defaultCenter=map_center,
                defaultZoom=map_zoom,
                onBoundsChanged=handle_bounds_changed,
            ),
            lib.pm.ZoomControl(),
            lib.pm.GeoJson(
                Props(
                    data=geojson,
                    onClick=handle_feature_click,
                    svgAttributes=Props(
                        fill="blue",
                        strokeWidth="0",
                        stroke="black",
                    ),
                )
            ),
        ),
        lib.tethys.Panel(
            Props(
                show=show_chart,
                set_show=set_show_chart,
                position="end",
                extent="30vw",
                name="Props",
            ),
            (
                lib.html.div(
                    [
                        lib.html.div(
                            lib.html.span(key.title()), ": ", lib.html.span(val)
                        )
                        for key, val in feature_data.items()
                    ]
                )
                if feature_data
                else ""
            ),
            lib.html.br() if chart_data else "",
            lib.tethys.SimpleLineChart(chart_data) if chart_data else "",
        ),
    )


@page
def bootstrap_cards_example():
    return lib.bs.Card(
        Props(style=Props(width="18rem")),
        lib.bs.CardImg(
            Props(
                variant="top",
                src="https://upload.wikimedia.org/wikipedia/commons/6/63/Logo_La_Linea_100x100.png?20190604153842",
            )
        ),
        lib.bs.CardBody(
            lib.bs.CardTitle("Card Title"),
            lib.bs.CardText(
                "Some quick example text to build on the card title and make up the"
                "bulk of the card's content."
            ),
        ),
        lib.bs.ListGroup(
            Props(className="list-group-flush"),
            lib.bs.ListGroupItem("Cras justo odio"),
            lib.bs.ListGroupItem("Dapibus ac facilisis in"),
            lib.bs.ListGroupItem("Vestibulum at eros"),
        ),
        lib.bs.CardBody(
            lib.bs.CardLink(Props(href="#"), "Card Link"),
            lib.bs.CardLink(Props(href="#"), "Another Link"),
        ),
    )


@page
def recharts_treemap_example():
    data = [
        {
            "name": "axis",
            "children": [
                {"name": "Axes", "size": 1302},
                {"name": "Axis", "size": 24593},
                {"name": "AxisGridLine", "size": 652},
                {"name": "AxisLabel", "size": 636},
                {"name": "CartesianAxes", "size": 6703},
            ],
        },
        {
            "name": "controls",
            "children": [
                {"name": "AnchorControl", "size": 2138},
                {"name": "ClickControl", "size": 3824},
                {"name": "Control", "size": 1353},
                {"name": "ControlList", "size": 4665},
                {"name": "DragControl", "size": 2649},
                {"name": "ExpandControl", "size": 2832},
                {"name": "HoverControl", "size": 4896},
                {"name": "IControl", "size": 763},
                {"name": "PanZoomControl", "size": 5222},
                {"name": "SelectionControl", "size": 7862},
                {"name": "TooltipControl", "size": 8435},
            ],
        },
        {
            "name": "data",
            "children": [
                {"name": "Data", "size": 20544},
                {"name": "DataList", "size": 19788},
                {"name": "DataSprite", "size": 10349},
                {"name": "EdgeSprite", "size": 3301},
                {"name": "NodeSprite", "size": 19382},
                {
                    "name": "render",
                    "children": [
                        {"name": "ArrowType", "size": 698},
                        {"name": "EdgeRenderer", "size": 5569},
                        {"name": "IRenderer", "size": 353},
                        {"name": "ShapeRenderer", "size": 2247},
                    ],
                },
                {"name": "ScaleBinding", "size": 11275},
                {"name": "Tree", "size": 7147},
                {"name": "TreeBuilder", "size": 9930},
            ],
        },
        {
            "name": "events",
            "children": [
                {"name": "DataEvent", "size": 7313},
                {"name": "SelectionEvent", "size": 6880},
                {"name": "TooltipEvent", "size": 3701},
                {"name": "VisualizationEvent", "size": 2117},
            ],
        },
        {
            "name": "legend",
            "children": [
                {"name": "Legend", "size": 20859},
                {"name": "LegendItem", "size": 4614},
                {"name": "LegendRange", "size": 10530},
            ],
        },
        {
            "name": "operator",
            "children": [
                {
                    "name": "distortion",
                    "children": [
                        {"name": "BifocalDistortion", "size": 4461},
                        {"name": "Distortion", "size": 6314},
                        {"name": "FisheyeDistortion", "size": 3444},
                    ],
                },
                {
                    "name": "encoder",
                    "children": [
                        {"name": "ColorEncoder", "size": 3179},
                        {"name": "Encoder", "size": 4060},
                        {"name": "PropertyEncoder", "size": 4138},
                        {"name": "ShapeEncoder", "size": 1690},
                        {"name": "SizeEncoder", "size": 1830},
                    ],
                },
                {
                    "name": "filter",
                    "children": [
                        {"name": "FisheyeTreeFilter", "size": 5219},
                        {"name": "GraphDistanceFilter", "size": 3165},
                        {"name": "VisibilityFilter", "size": 3509},
                    ],
                },
                {"name": "IOperator", "size": 1286},
                {
                    "name": "label",
                    "children": [
                        {"name": "Labeler", "size": 9956},
                        {"name": "RadialLabeler", "size": 3899},
                        {"name": "StackedAreaLabeler", "size": 3202},
                    ],
                },
                {
                    "name": "layout",
                    "children": [
                        {"name": "AxisLayout", "size": 6725},
                        {"name": "BundledEdgeRouter", "size": 3727},
                        {"name": "CircleLayout", "size": 9317},
                        {"name": "CirclePackingLayout", "size": 12003},
                        {"name": "DendrogramLayout", "size": 4853},
                        {"name": "ForceDirectedLayout", "size": 8411},
                        {"name": "IcicleTreeLayout", "size": 4864},
                        {"name": "IndentedTreeLayout", "size": 3174},
                        {"name": "Layout", "size": 7881},
                        {"name": "NodeLinkTreeLayout", "size": 12870},
                        {"name": "PieLayout", "size": 2728},
                        {"name": "RadialTreeLayout", "size": 12348},
                        {"name": "RandomLayout", "size": 870},
                        {"name": "StackedAreaLayout", "size": 9121},
                        {"name": "TreeMapLayout", "size": 9191},
                    ],
                },
                {"name": "Operator", "size": 2490},
                {"name": "OperatorList", "size": 5248},
                {"name": "OperatorSequence", "size": 4190},
                {"name": "OperatorSwitch", "size": 2581},
                {"name": "SortOperator", "size": 2023},
            ],
        },
    ]
    return lib.bs.Container(
        Props(style=Props(height="90vh")),
        lib.rc.ResponsiveContainer(
            Props(width="100%", height="100%"),
            lib.rc.Treemap(
                Props(
                    width=400,
                    height=200,
                    data=data,
                    dataKey="size",
                    aspectRatio=4 / 3,
                    stroke="#fff",
                    fill="#8884d8",
                )
            ),
        ),
    )


# @component  NOTE: Breaks if @component decorator applied
def ButtonWithTooltip(button_props, tooltip_props, *children):
    from time import sleep

    event, set_event = hooks.use_state({})

    def show_tooltip(event):
        sleep(0.4)
        set_event(event)
        if "on_mouse_enter" in button_props:
            button_props["on_mouse_enter"]()

    def hide_tooltip(event):
        sleep(0.25)
        set_event({})
        if "on_mouse_leave" in button_props:
            button_props["on_mouse_leave"]()

    return lib.html.div(
        lib.bs.Button(
            Props(
                variant="success",
                on_mouse_enter=show_tooltip,
                on_mouse_leave=hide_tooltip,
            ),
            *children,
            (
                lib.html.div(
                    Props(
                        style=Props(
                            background="rgba(250,250,250,0)",
                            position="absolute",
                            top=event["y"],
                            left=event["x"],
                            display="flex",
                            flex_flow="column nowrap",
                            align_items="center",
                        )
                    ),
                    lib.html.div(
                        Props(
                            style=Props(
                                width=0,
                                height=0,
                                border_left="5px solid transparent",
                                border_right="5px solid transparent",
                                border_bottom="5px solid black",
                            )
                        )
                    ),
                    lib.html.div(
                        Props(
                            style=Props(
                                background="black",
                                color="white",
                                padding="5pt",
                                font_size="12pt",
                            )
                        ),
                        (
                            tooltip_props["text"]
                            if "text" in tooltip_props
                            else 'Could not find prop "text" on tooltip_props'
                        ),
                    ),
                )
                if event
                else ""
            ),
        )
    )


@component  # NOTE: Breaks if @component decorator applied
def OlMap(props, *children):
    load_js, set_load_js = hooks.use_state(False)

    def delay_load_script(event):
        set_load_js(True)

    def handle_map_click(event):
        pass

    return lib.html.div(
        lib.html.div(
            Props(
                id="map",
                class_name="map",
                style=Props(width="100%", position="absolute", top=0, bottom=0),
                on_click=handle_map_click,
            )
        ),
        lib.html.div(
            Props(on_load=delay_load_script),
            html.script(Props(src="https://cdn.jsdelivr.net/npm/ol@v9.2.4/dist/ol.js")),
            html.link(
                Props(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/ol@v9.2.4/ol.css",
                )
            ),
            (
                html.script(
                    """
                const MAP = new ol.Map({
                    target: 'map',
                    layers: [
                        new ol.layer.Tile({
                            source: new ol.source.OSM(),
                        }),
                    ],
                    view: new ol.View({
                        center: [0, 0],
                        zoom: 2,
                    }),
                });
                MAP.on('click', function (e) {
                    console.log(e);
                });
                """
                )
                if load_js and set_load_js(False) == None
                else ""
            ),
        ),
    )
