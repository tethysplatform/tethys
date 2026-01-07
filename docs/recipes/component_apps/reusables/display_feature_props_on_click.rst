Display Feature Props On Click
==============================

.. code-block:: python

    @App.page
    def display_feature_props_on_click(lib):
        props, set_props = lib.hooks.use_state({})
        return lib.tethys.Display(
            lib.tethys.Panel(title="Properties", show=len(props) > 0, on_close=lambda e: set_props({}), extent="300px")(
                *[
                    lib.html.div(
                        lib.html.span(
                            lib.html.b(f"{k}: ")
                        ),
                        lib.html.span(v)
                    ) for k, v in props.items()
                ]
            ),
            lib.tethys.Map(
                lib.ol.layer.Vector(
                    onClick=lambda e: set_props(e.features[0] if e.features else lib.Props(Message="No features found"))
                )(
                    lib.ol.source.Vector(
                        options=lib.Props(
                            url="https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_urban_areas.geojson",
                            format_="GeoJSON"
                        )
                    )
                )
            )
        )