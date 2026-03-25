Style GeoJSON with Unique Values Styler
=======================================

.. code-block:: python

    @App.page
    def geojson_unique_styler(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.Vector(
                    style=lib.ol.style.Styler(
                        method="unique_values",
                        fields=["scalerank"],
                        values=[
                            (
                                1, 
                                lib.ol.style.Style(
                                    stroke=lib.ol.style.Stroke(
                                        color="purple",
                                        width=1
                                    ),
                                    fill=lib.ol.style.Fill(
                                        color="white"
                                    ),
                                    text=lib.ol.style.Text(
                                        text="%{$feature.scalerank}",
                                        fill=lib.ol.style.Fill(color="orange"),
                                        stroke=lib.ol.style.Stroke(color="#f1234567", width=2),
                                    ),
                                )
                            ),
                            (
                                2,
                                lib.ol.style.Style(
                                    stroke=lib.ol.style.Stroke(
                                        color="#459302",
                                        width=1
                                    ),
                                    fill=lib.ol.style.Fill(
                                        color="#18181818"
                                    ),
                                    text=lib.ol.style.Text(
                                        text="%{$feature.scalerank}",
                                        fill=lib.ol.style.Fill(color="orange"),
                                        stroke=lib.ol.style.Stroke(color="#f1234567", width=2),
                                    ),
                                )
                            ),
                            (
                                3,
                                lib.ol.style.Style(
                                    stroke=lib.ol.style.Stroke(
                                        color="#93102849",
                                        width=1
                                    ),
                                    fill=lib.ol.style.Fill(
                                        color="#f930efd3"
                                    ),
                                    text=lib.ol.style.Text(
                                        text="%{$feature.scalerank}",
                                        fill=lib.ol.style.Fill(color="orange"),
                                        stroke=lib.ol.style.Stroke(color="#f1234567", width=2),
                                    ),
                                )
                            )
                        ],
                        default=lib.ol.style.Style(
                            stroke=lib.ol.style.Stroke(
                                color="#000000",
                                width=1
                            ),
                            fill=lib.ol.style.Fill(
                                color="#ff0000"
                            ),
                            text=lib.ol.style.Text(
                                text="%{$feature.scalerank}",
                                fill=lib.ol.style.Fill(color="blue"),
                                stroke=lib.ol.style.Stroke(color="white", width=2),
                            ),
                        )
                    )
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