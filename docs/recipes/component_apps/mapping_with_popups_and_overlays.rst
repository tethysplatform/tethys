.. _component_app__mapping_with_popups_and_overlays :



************************************************
Component Apps: Mapping with Popups and Overlays
************************************************

.. important::

    These recipes only apply to Component App development and will not work for Standard Apps.

**Last Updated:** December 2025

Text Link Overlay
=================

.. code-block:: python

    @App.page
    def map_overlays(lib):
        static_position = lib.utils.transform_coordinate([48.208889, 16.3725], "EPSG:4326", "EPSG:3857")

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
                )
            )("Vienna"),
            lib.tethys.Map(
                lib.ol.Overlay(
                    options=lib.Props(
                        stopEvent=False
                    ),
                    position=static_position,
                    element="vienna"  # The id_ of the above component to be used for this Overlay
                ),
            )
        )

Marker Overlay
==============

.. code-block:: python

    @App.page
    def map_overlays(lib):
        static_position = lib.utils.transform_coordinate([48.208889, 16.3725], "EPSG:4326", "EPSG:3857")

        return lib.tethys.Display(
            lib.html.div(
                id_="marker",  # id_ is essential, as it's referenced in the associated "element" attribute below
                style=lib.Style(
                    width="20px",
                    height="20px",
                    border="1px solid #088",
                    border_radius="10px",
                    background_color="#0FF",
                    opacity="0.5",
                )
            ),
            lib.tethys.Map(
                lib.ol.Overlay(
                    options=lib.Props(
                        stopEvent=False
                    ),
                    position=static_position,
                    positioning="center-center",
                    element="marker" # The id_ of the above component to be used for this Overlay
                ),
            )
        )

Popup
=====

.. code-block:: python

    @App.page
    def map_overlays(lib):
        position, set_position = lib.hooks.use_state(None)

        return lib.tethys.Display(
            lib.html.div(
                id_="dynamic",  # id_ is essential, as it's referenced in the associated "element" attribute below
                style=lib.Style(
                    position="relative",
                ),
                hidden=position is None
            )(
                lib.html.div(
                    style=lib.Style(
                        position="absolute",
                        left="-6px",
                        width=0,
                        height=0,
                        border_left="6px solid transparent",   # Controls the width of the triangle
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
                        border="1px black solid"
                    )
                )(
                    lib.icons.XCircle(
                        style=lib.Style(
                            position="absolute",
                            right="10px",
                            top="5px",
                            font_weight="bold"
                        ),
                        onClick=lambda _: set_position(None)
                    ),
                    lib.html.div(
                        f"You clicked at: {", ".join(map(str, position))}"
                    ) if position else None
                )
            ),
            lib.tethys.Map(
                onClick=lambda e: set_position(e.coordinate)
            )(
                lib.ol.Overlay(
                    position=position or [0,0],
                    element="dynamic" # The id_ of the above component to be used for this Overlay
                )
            )
        )

Combining All Previous Examples
===============================

.. code-block:: python

    @App.page
    def map_overlays(lib):
        position, set_position = lib.hooks.use_state(None)
        static_position = lib.utils.transform_coordinate([48.208889, 16.3725], "EPSG:4326", "EPSG:3857")

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
                )
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
                )
            ),
            lib.html.div(
                id_="dynamic",  # id_ is essential, as it's referenced in the associated "element" attribute below
                style=lib.Style(
                    position="relative",
                ),
                hidden=position is None
            )(
                lib.html.div(
                    style=lib.Style(
                        position="absolute",
                        left="-6px",
                        width=0,
                        height=0,
                        border_left="6px solid transparent",   # Controls the width of the triangle
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
                        border="1px black solid"
                    )
                )(
                    lib.icons.XCircle(
                        style=lib.Style(
                            position="absolute",
                            right="10px",
                            top="5px",
                            font_weight="bold"
                        ),
                        onClick=lambda _: set_position(None)
                    ),
                    lib.html.div(
                        f"You clicked at: {", ".join(map(str, position))}"
                    ) if position else None
                )
            ),
            lib.tethys.Map(
                onClick=lambda e: set_position(e.coordinate)
            )(
                lib.ol.Overlay(
                    options=lib.Props(
                        stopEvent=False
                    ),
                    position=static_position,
                    element="vienna"  # The id_ of the above component to be used for this Overlay
                ),
                lib.ol.Overlay(
                    options=lib.Props(
                        stopEvent=False
                    ),
                    position=static_position,
                    positioning="center-center",
                    element="marker" # The id_ of the above component to be used for this Overlay
                ),
                lib.ol.Overlay(
                    position=position or [0,0],
                    element="dynamic" # The id_ of the above component to be used for this Overlay
                )
            )
        )

.. include:: reusables/display_feature_props_on_click.rst