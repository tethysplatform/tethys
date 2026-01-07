def page_test(lib):
    fill_color, set_fill_color = lib.hooks.use_state("#ff0000")
    stroke_color, set_stroke_color = lib.hooks.use_state("#000000")
    return lib.tethys.Display(
        lib.html.div(style=lib.Style(position="absolute", top=10, right=20, zIndex=1))(
            lib.bs.FormLabel(htmlFor="fill-color")("Fill Color"),
            lib.bs.FormControl(
                id_="fill-color",
                type_="color",
                defaultValue=fill_color,
                onChange=lambda e: set_fill_color(e.target.value),
            ),
            lib.bs.FormLabel(htmlFor="stroke-color")("Stroke Color"),
            lib.bs.FormControl(
                id_="stroke-color",
                type_="color",
                defaultValue=stroke_color,
                onChange=lambda e: set_stroke_color(e.target.value),
            ),
        ),
        lib.tethys.Map(
            lib.ol.layer.Vector(
                style=lib.ol.style.Style(
                    stroke=lib.ol.style.Stroke(color=stroke_color, width=1),
                    fill=lib.ol.style.Fill(color=fill_color),
                )
            )(
                lib.ol.source.Vector(
                    options=lib.Props(
                        url="https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_urban_areas.geojson",
                        format_="GeoJSON",
                    )
                )
            )
        ),
    )
