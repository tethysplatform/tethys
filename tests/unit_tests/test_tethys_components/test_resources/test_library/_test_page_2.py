def page_test(lib):
    lib.register("react-plotly@1.0.0", "p")
    chart_data = {
        "river_id": "Test 123",
        "series": [{"x": 1, "y": 100}, {"x": 2, "y": 200}],
    }
    return lib.html.div(style=lib.Style(width="100vw", height="calc(100vh - 57px)"))(
        lib.tethys.Map(
            lib.ol.layer.Image(options=lib.Props(title="GEOGLOWS Streamflow Service"))(
                lib.ol.source.ImageArcGISRest(
                    options=lib.Props(
                        url="https://livefeeds3.arcgis.com/arcgis/rest/services/GEOGLOWS/GlobalWaterModel_Medium/MapServer"
                    )
                )
            ),
            lib.ol.layer.Vector(
                lib.ol.source.Vector(
                    options=lib.Props(
                        url="https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_ocean.geojson",
                        format_="GeoJSON",
                    )
                )
            ),
        ),
        lib.tethys.Panel(
            show=True,
            anchor="right",
            extent="50vw",
            title="Forecast",
        )(
            lib.bs.Container(
                lib.bs.Row(
                    lib.bs.Col(
                        (
                            lib.html.h2(f"Streamflow @ {chart_data['river_id']}")
                            if chart_data
                            else None
                        ),
                        lib.rc.LineChart(
                            width=700, height=500, data=chart_data["series"]
                        )(
                            lib.rc.CartesianGrid(strokeDasharray="3 3"),
                            lib.rc.XAxis(label="Date"),
                            lib.rc.YAxis(
                                label=lib.Props(
                                    value="Streamflow", angle=-90, position="insideLeft"
                                )
                            ),
                            lib.rc.Tooltip(),
                            lib.rc.Line(type="monotone", data_key="y"),
                        ),
                    )
                ),
            ),
        ),
    )
