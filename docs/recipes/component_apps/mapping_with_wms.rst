.. _component_app__mapping_with_wms :



********************************
Component Apps: Mapping with WMS
********************************

.. important::

    These recipes only apply to Component App development and will not work for Standard Apps.

**Last Updated:** December 2025

Single Image WMS
================

.. code-block:: python

    @App.page
    def single_image_wms(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.Image(
                    lib.ol.source.ImageWMS(
                        options=lib.Props(
                            url="https://ahocevar.com/geoserver/wms",
                            params=lib.Props(LAYERS='topp:states'),
                            ratio=1,
                            serverType="geoserver"
                        )
                    )
                )
            )
        )

Tiled WMS
=========

.. code-block:: python

    @App.page
    def tiled_wms(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.WebGLTile(
                    lib.ol.source.TileWMS(
                        options=lib.Props(
                            url="https://ahocevar.com/geoserver/wms",
                            params=lib.Props(LAYERS='topp:states', TILED=True),
                            serverType="geoserver",
                            # Countries have transparency, so do not fade tiles:
                            transition=0
                        )
                    )
                )
            )
        )

MapServer WMS
=============

.. code-block:: python

    @App.page
    def tiled_wms(lib):
        return lib.tethys.Display(
            lib.tethys.Map(projection="EPSG:4326")(
                lib.ol.layer.Image(
                    lib.ol.source.Image(
                        options=lib.Props(
                            loader=lib.Props(
                                url="https://demo.mapserver.org/cgi-bin/wms?",
                                params=lib.Props(
                                    LAYERS=['bluemarble,country_bounds,cities'],
                                    VERSION="1.3.0",
                                    FORMAT="image/png"
                                ),
                                projection="EPSG:4326",
                                # note: serverType only needs to be set when hidpi is True
                                hidpi=True,
                                serverType="mapserver"
                            )
                        )
                    )
                )
            )
        )

WMS Custom-Sized Tiles
======================

.. code-block:: python

    from pyproj import CRS, Transformer
    import math

    def get_resolutions():
        resolutions = []
        crs_3857 = CRS("EPSG:3857")
        geographic_bounds = crs_3857.area_of_use.bounds
        transformer = Transformer.from_crs(crs_3857.geodetic_crs, crs_3857, always_xy=True)
        proj_extent = transformer.transform_bounds(*geographic_bounds)
        start_resolution = (proj_extent[2] - proj_extent[0]) / 256
        for i in range(22):
            resolutions.append(start_resolution / math.pow(2, i))
        return resolutions

    @App.page
    def wms_custom_sized_tiles(lib):
        get_resolutions()
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.Tile(
                    lib.ol.source.TileWMS(
                        options=lib.Props(
                            url="https://ahocevar.com/geoserver/wms",
                            params=lib.Props(
                                LAYERS=['topp:states'],
                                TILED=True
                            ),
                            serverType="mapserver",
                            tileGrid=lib.Props(
                                extent=[-13884991, 2870341, -7455066, 6338219],
                                resolutions=get_resolutions(),
                                tileSize=[512, 256]
                            )
                        )
                    )
                )
            )
        )

WMS Legend
==========

.. important::

    This example uses ``lib.ol.Map`` rather than ``lib.tethys.Map``. 
    This is because ``lib.tethys.Map`` does not provide the granular control over the underlying ``lib.ol.View`` that is required by this example.

.. code-block:: python

    @App.page
    def wms_legend(lib):
        legend_url, set_legend_url = lib.hooks.use_state("")

        wms_source = lib.ol.source.ImageWMS(
            options=lib.Props(
                url="https://ahocevar.com/geoserver/wms",
                params=lib.Props(LAYERS='topp:states'),
                ratio=1,
                serverType="geoserver"
            )
        )

        lib.hooks.use_effect(lambda: set_legend_url(wms_source.get_legend_url()), dependencies=[])

        return lib.tethys.Display(style=lib.Style(position="relative"))(
            lib.html.div(style=lib.Style(position="absolute", top="5px", right="20px", zIndex=1))(
                lib.html.img(src=legend_url) if legend_url else None
            ),
            lib.ol.Map(
                lib.ol.View(
                    onChange=lambda e: set_legend_url(wms_source.get_legend_url(e.target.values_.resolution)),
                    center=[-10997148, 4569099],
                    zoom=4
                ),
                lib.ol.layer.Tile(lib.ol.source.OSM()),
                lib.ol.layer.Image(
                    wms_source
                )
            )
        )

WMS Loader with SVG Format
==========================

.. code-block:: python

    @App.page
    def wms_loader_with_svg_format(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.Image(
                    lib.ol.source.Image(
                        options=lib.Props(
                            loader=lib.Props(
                                url="https://ahocevar.com/geoserver/wms",
                                params=lib.Props(
                                    LAYERS=['topp:states'],
                                    FORMAT="image/svg+xml"
                                ),
                                ratio=1,
                                load=True
                            )
                        )
                    )
                )
            )
        )
    
WMS Time
========

.. code-block:: python

    import datetime as dt

    def three_hours_ago():
        now = dt.datetime.now()
        return (now - dt.timedelta(hours=3)).replace(
            minute=int(now.minute/15)*15, 
            second=0, 
            microsecond=0
        )

    @App.page
    def wms_time(lib):
        frame_rate = 0.5  # frames per second
        wms_time, set_wms_time = lib.hooks.use_state(lambda: three_hours_ago())
        timer, set_timer = lib.hooks.use_state(None)

        return lib.tethys.Display(style=lib.Style(position="relative"))(
            lib.html.div(
                style=lib.Style(
                    zIndex=1, 
                    position="absolute", 
                    top="5px", 
                    right="20px"
                )
            )(
                lib.html.div(style=lib.Style(display="flex", justify_content="center"))(
                    lib.html.button(
                        on_click=lambda _: set_timer(
                            lib.utils.background_execute(
                                lambda: set_wms_time(lambda old: three_hours_ago() if old + dt.timedelta(minutes=15) > dt.datetime.now() else old + dt.timedelta(minutes=15)),
                                repeat_seconds=1/frame_rate
                            )
                        ),
                        disabled=timer is not None
                    )(
                        "Play"
                    ),
                    lib.html.button(
                        on_click=lambda _: (
                            timer.cancel() if timer else None,
                            set_timer(None)
                        ),
                        disabled=timer is None
                    )(
                        "Stop"
                    )
                ),
                lib.html.div(
                    f"Time: {wms_time.isoformat()}"
                )
            ),
            lib.tethys.Map(
                lib.ol.layer.Tile(
                    lib.ol.source.TileWMS(
                        options=lib.Props(
                            url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r-t.cgi"
                        ),
                        params=lib.Props(
                            LAYERS=['nexrad-n0r-wmst'], 
                            TIME=wms_time.isoformat()
                        )
                    )
                )
            )
        )

WMS without Projection
======================

As long as no coordinate transformations are required, the underlying OpenLayers mapping engine works fine with projections that are only configured with a code and units.

.. important::

    This example uses ``lib.ol.Map`` rather than ``lib.tethys.Map``. 
    This is because ``lib.tethys.Map`` provides a default suite of basemaps which are not compatible with projections lacking a full definition, like the one used in this example.

.. code-block:: python

    @App.page
    def wms_without_projection(lib):
        return lib.tethys.Display(
            lib.ol.Map(
                lib.ol.View(
                    options=lib.Props(
                        projection=lib.Props(code="EPSG:21781", units="m"),
                    ),
                    center=[660000, 190000],
                    zoom=9
                ),
                lib.ol.layer.Group(options=lib.Props(title="Overlays", fold="open"))(
                    lib.ol.layer.Tile(options=lib.Props(title="Custom Projection Basemap"))(
                        lib.ol.source.TileWMS(
                            options=lib.Props(
                                attributions=(
                                    '\u00A9 <a href="https://shop.swisstopo.admin.ch/en/products/maps/national/lk1000"' +
                                    'target="_blank">Pixelmap 1:1000000 / geo.admin.ch</a>'
                                ),
                                crossOrigin="anonymous",
                                params=lib.Props(
                                    LAYERS="ch.swisstopo.pixelkarte-farbe-pk1000.noscale",
                                    FORMAT="image/jpeg"
                                ),
                                url="https://wms.geo.admin.ch/",
                            ),
                        )
                    ),
                    lib.ol.layer.Image(options=lib.Props(title="Flood Alert"))(
                        lib.ol.source.ImageWMS(
                            options=lib.Props(
                                attributions=(
                                    '\u00A9 <a href="https://www.hydrodaten.admin.ch/en/notes-on-the-flood-alert-maps.html"' +
                                    'target="_blank">Flood Alert / geo.admin.ch</a>'
                                ),
                                crossOrigin="anonymous",
                                params=lib.Props(LAYERS="ch.bafu.hydroweb-warnkarte_national"),
                                serverType="mapserver",
                                url="https://wms.geo.admin.ch/"
                            )
                        )
                    ),
                ),
                lib.ol.control.ScaleLine(),
                lib.tethys.LayerPanel(),
            )
        )

Single Image WMS with Custom Projection
========================================

.. code-block:: python

    CUSTOM_PRJ = (
        '+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 ' +
        '+x_0=600000 +y_0=200000 +ellps=bessel ' +
        '+towgs84=660.077,13.551,369.344,2.484,1.783,2.939,5.66 +units=m +no_defs'
    )

    @App.page
    def wms_image_with_custom_projection(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                projection=lib.Props(
                    code="EPSG:21781", 
                    extent=[485869.5728, 76443.1884, 837076.5648, 299941.7864],
                    definition=CUSTOM_PRJ
                ),
                zoom=2,
                center=lib.utils.transform_coordinate([8.23, 46.86], "EPSG:4326", CUSTOM_PRJ)
            )(
                lib.ol.layer.Tile(options=lib.Props(title="Custom Projection Basemap"))(
                    lib.ol.source.TileWMS(
                        options=lib.Props(
                            attributions=(
                                '\u00A9 <a href="https://shop.swisstopo.admin.ch/en/products/maps/national/lk1000"' +
                                'target="_blank">Pixelmap 1:1000000 / geo.admin.ch</a>'
                            ),
                            crossOrigin="anonymous",
                            params=lib.Props(
                                LAYERS="ch.swisstopo.pixelkarte-farbe-pk1000.noscale",
                                FORMAT="image/jpeg"
                            ),
                            url="https://wms.geo.admin.ch/",
                        ),
                    )
                ),
                lib.ol.layer.Image(options=lib.Props(title="Flood Alert"))(
                    lib.ol.source.ImageWMS(
                        options=lib.Props(
                            attributions=(
                                '\u00A9 <a href="https://www.hydrodaten.admin.ch/en/notes-on-the-flood-alert-maps.html"' +
                                'target="_blank">Flood Alert / geo.admin.ch</a>'
                            ),
                            crossOrigin="anonymous",
                            params=lib.Props(LAYERS="ch.bafu.hydroweb-warnkarte_national"),
                            serverType="mapserver",
                            url="https://wms.geo.admin.ch/"
                        )
                    )
                )
            )
        )

WMS GetFeatureInfo (Image Layer)
================================

.. code-block:: python

    @App.page
    def wms_get_feature_info(lib):
        props, set_props = lib.hooks.use_state(None)

        wms_source = lib.ol.source.ImageWMS(
            options=lib.Props(
                url="https://ahocevar.com/geoserver/wms",
                params=lib.Props(LAYERS="ne:ne"),
                serverType="geoserver",
                crossOrigin="anonymous"
            )
        )

        return lib.tethys.Display(
            lib.html.div(
                style=lib.Style(height="85vh")
            )(
                lib.tethys.Map(
                    default_basemap=None,
                    on_click=lambda e: (
                        set_props(
                            lib.utils.fetch(
                                wms_source.get_feature_info_url(
                                    e.coordinate,
                                    e.target.frameState_.viewState.resolution,
                                    e.target.values_.view.projection_.code_,
                                    "EPSG:3857",
                                    {"INFO_FORMAT": "text/html"}
                                )
                            )
                        )
                    )
                )(
                    lib.ol.layer.Image(wms_source)
                )
            ),
            lib.html.div(
                style=lib.Style(height="15vh", width="95vw")
            )(
                lib.html.iframe(width="100%", srcdoc=props) if props else lib.html.h1("Click Map For Feature Info")
            )
        )

WMS GetFeatureInfo (Tile Layer)
================================

.. code-block:: python

    @App.page
    def wms_get_feature_info(lib):
        props, set_props = lib.hooks.use_state(None)

        wms_source = lib.ol.source.TileWMS(
            options=lib.Props(
                url="https://ahocevar.com/geoserver/wms",
                params=lib.Props(LAYERS="ne:ne", TILED=True),
                serverType="geoserver",
                crossOrigin="anonymous"
            ),
        )

        return lib.tethys.Display(
            lib.html.div(
                style=lib.Style(height="85vh")
            )(
                lib.tethys.Map(
                    default_basemap=None,
                    on_click=lambda e: (
                        set_props(
                            lib.utils.fetch(
                                wms_source.get_feature_info_url(
                                    e.coordinate,
                                    e.target.frameState_.viewState.resolution,
                                    e.target.values_.view.projection_.code_,
                                    "EPSG:3857",
                                    {"INFO_FORMAT": "text/html"}
                                )
                            )
                        )
                    )
                )(
                    lib.ol.layer.Tile(
                        wms_source    
                    )
                )
            ),
            lib.html.div(
                style=lib.Style(height="15vh", width="95vw")
            )(
                lib.html.iframe(width="100%", srcdoc=props) if props else lib.html.h1("Click Map For Feature Info")
            )
        )
