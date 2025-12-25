def page_test(lib):
    position, set_position = lib.hooks.use_state(None)
    static_position = [48.208889, 16.3725]

    return lib.tethys.Display(
        lib.html.a(
            id_="vienna",  # id_ is essential, as it's referenced in the associated "element" attribute below
            className="overlay",
            target="_blank",
            href="https://en.wikipedia.org/wiki/Vienna",
            style=lib.Style(
                text_decoration=None,
                color="white",
                font_size="11pt",
                font_weight="bold",
                text_shadow="black 0.1em 0.1em 0.2em",
            ),
        )("Vienna"),
        lib.html.div(
            id_="marker",  # id_ is essential, as it's referenced in the associated "element" attribute below
            style=lib.Style(
                width="20px",
                height="20px",
                border="1px solid #088",
                border_radius="10px",
                background_color="#0FF",
                opacity="0.5",
            ),
        ),
        (
            lib.html.div(
                id_="dynamic",  # id_ is essential, as it's referenced in the associated "element" attribute below
                style=lib.Style(
                    position="relative",
                ),
            )(
                lib.html.div(
                    style=lib.Style(
                        position="absolute",
                        left="-6px",
                        width=0,
                        height=0,
                        border_left="6px solid transparent",  # Controls the width of the triangle
                        border_right="6px solid transparent",  # Controls the width of the triangle
                        border_bottom="6px solid #ff0000",
                    )
                ),
                lib.html.div(
                    style=lib.Style(
                        position="absolute",
                        left="-6px",
                        top="6px",
                        width="200px",
                        background_color="lightblue",
                        padding="1em",
                        border="1px black solid",
                    )
                )(f"You clicked at: {', '.join(map(str, position))}"),
            )
            if position
            else lib.html.div()
        ),
        lib.tethys.Map(
            key="map",
            projection=lib.Props(
                code="EPSG:21781",
                extent=[485869.5728, 76443.1884, 837076.5648, 299941.7864],
            ),
            center=[660000, 190000],
            onClick=lambda e: set_position(e.coordinate),
        )(
            lib.ol.Overlay(
                options=lib.Props(stopEvent=False),
                position=static_position,
                element="vienna",  # The id_ of the above component to be used for this Overlay
            ),
            lib.ol.Overlay(
                options=lib.Props(stopEvent=False),
                position=static_position,
                positioning="center-center",
                element="marker",  # The id_ of the above component to be used for this Overlay
            ),
            (
                lib.ol.Overlay(
                    position=position,
                    element="dynamic",  # The id_ of the above component to be used for this Overlay
                )
                if position
                else None
            ),
            None,
        ),
    )
