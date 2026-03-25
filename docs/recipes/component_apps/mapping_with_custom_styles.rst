.. _component_app__mapping_with_custom_styles :



******************************************
Component Apps: Mapping with Custom Styles
******************************************

.. important::

    These recipes only apply to Component App development and will not work for Standard Apps.

**Last Updated:** January 2026

Style Vector Points with Icons from pytablericons
=================================================

.. note::

    ``pytablericons`` does not come pre-installed with Tethys Platform and can be installed with ``pip install pytablericons``.

    View all available icons `here <https://tabler.io/icons>`__ and the note on their usage within ``pytablericons`` `here <https://github.com/niklashenning/pytablericons?tab=readme-ov-file#usage>`__.

.. code-block:: python

    import base64
    import math
    import numpy as np
    from io import BytesIO
    from pytablericons import TablerIcons, FilledIcon, OutlineIcon

    def get_icon_data_url(icon, size=32, color="black"):
        icon_img = TablerIcons.load(icon, size=size, color=color)
        buffered = BytesIO()
        icon_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_url = f"data:image/png;base64,{img_str}"
        return data_url

    @App.page
    def points_with_pytablericons(lib):
        icon_size = 16
        icons = list(FilledIcon)
        num_icons = len(icons)
        num_rows = num_cols = int(math.sqrt(num_icons))
        x_min, x_max, x_spacing = -180, 180, 360/num_rows
        y_min, y_max, y_spacing = -90, 90, 180/num_rows

        x_coords = np.arange(x_min, x_max + x_spacing, x_spacing)
        y_coords = np.arange(y_min, y_max + y_spacing, y_spacing)

        X, Y = np.meshgrid(x_coords, y_coords)

        X_flat = X.ravel()
        Y_flat = Y.ravel()

        combinations_xy = np.vstack((X_flat, Y_flat)).T

        features = [
            lib.Props(
                geometry=lib.ol.geom.Point([int(x), int(y)]),
                style=lib.ol.Style(
                    image=lib.ol.style.Icon(
                        anchor=[0, 0],
                        anchorXUnits="fraction",
                        anchorYUnits="pixels",
                        width=icon_size,
                        height=icon_size,
                        src=get_icon_data_url(icons[i], size=icon_size)
                    )
                )
            ) for i, (x, y) in enumerate(combinations_xy) if i < num_icons
        ]

        return lib.tethys.Display(
            lib.tethys.Map(projection="EPSG:4326")(
                lib.ol.layer.Vector(
                    lib.ol.source.Vector(
                        features=features,
                        format="olFeature"
                    )
                )
            )
        )

Style Vector Points with Icons from simplepycons
================================================

.. note::

    ``simplepycons`` does not come pre-installed with Tethys Platform and can be installed with ``pip install simplepycons``.

    View all available icons `here <https://simpleicons.org/>`__ and the note on their usage within ``simplepycons`` `here <https://github.com/carstencodes/simplepycons?tab=readme-ov-file#usage>`__

.. code-block:: python

    import math
    import numpy as np
    from simplepycons import all_icons

    @App.page
    def points_with_simplepycons(lib):
        icon_size = 16
        icon_names = [
            x.split('_')[1] 
            for x in dir(all_icons) 
            if x.startswith("get_")
        ][:100]  # Limit to 100 unique icons
        num_icons = len(icon_names)
        num_rows = num_cols = int(math.sqrt(num_icons))
        x_min, x_max, x_spacing = -180, 180, 360/num_rows
        y_min, y_max, y_spacing = -90, 90, 180/num_rows

        x_coords = np.arange(x_min, x_max + x_spacing, x_spacing)
        y_coords = np.arange(y_min, y_max + y_spacing, y_spacing)

        X, Y = np.meshgrid(x_coords, y_coords)

        X_flat = X.ravel()
        Y_flat = Y.ravel()

        combinations_xy = np.vstack((X_flat, Y_flat)).T

        features = [
            lib.Props(
                geometry=lib.ol.geom.Point([int(x), int(y)]),
                style=lib.ol.Style(
                    image=lib.ol.style.Icon(
                        anchor=[0, 0],
                        anchorXUnits="fraction",
                        anchorYUnits="pixels",
                        width=icon_size,
                        height=icon_size,
                        src=all_icons[icon_names[i]].customize_svg_as_data_url(
                            fill="blue", 
                            width=str(icon_size), 
                            height=str(icon_size)
                        )
                    )
                )
            ) for i, (x, y) in enumerate(combinations_xy) if i < num_icons
        ]

        return lib.tethys.Display(
            lib.tethys.Map(projection="EPSG:4326")(
                lib.ol.layer.Vector(
                    lib.ol.source.Vector(
                        features=features,
                        format="olFeature"
                    )
                )
            )
        )


Style Vector Point with Dynamic Icon from pytablericons
=======================================================

.. note::

    ``pytablericons`` does not come pre-installed with Tethys Platform and can be installed with ``pip install pytablericons``.

    View all available icons `here <https://tabler.io/icons>`__ and the note on their usage within ``pytablericons`` `here <https://github.com/niklashenning/pytablericons?tab=readme-ov-file#usage>`__.

.. code-block:: python

    import base64
    from io import BytesIO
    from pytablericons import TablerIcons, FilledIcon

    def get_icon_data_url(icon, size=32, color="black"):
        icon_img = TablerIcons.load(icon, size=size, color=color)
        buffered = BytesIO()
        icon_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_url = f"data:image/png;base64,{img_str}"
        return data_url

    @App.page
    def dynamic_icon_with_pytablericons(lib):
        icon_index, set_icon_index = lib.hooks.use_state(0)
        icon_size = 16
        icons = list(FilledIcon)
        num_icons = len(icons)

        features = [
            lib.ol.Feature(
                geometry=lib.ol.geom.Point([0, 0]),
                style=lib.ol.Style(
                    image=lib.ol.style.Icon(
                        anchor=[0, 0],
                        anchorXUnits="fraction",
                        anchorYUnits="pixels",
                        width=icon_size,
                        height=icon_size,
                        src=get_icon_data_url(icons[icon_index], size=icon_size)
                    )
                )
            )
        ]

        return lib.tethys.Display(
            lib.bs.Button(
                style=lib.Style(
                    position="absolute",
                    top=0,
                    right="20px",
                    zIndex=1
                ),
                onClick=lambda _: set_icon_index(icon_index + 1 if icon_index + 1 < num_icons else 0)
            )("Swap Icon"),
            lib.tethys.Map(
                lib.ol.layer.Vector(
                    lib.ol.source.Vector(
                        features=features,
                        format="olFeature"
                    )
                )
            )
        )


Style Vector Point with Dynamic Icon from simplepycons
======================================================

.. note::

    ``simplepycons`` does not come pre-installed with Tethys Platform and can be installed with ``pip install simplepycons``.

    View all available icons `here <https://simpleicons.org/>`__ and the note on their usage within ``simplepycons`` `here <https://github.com/carstencodes/simplepycons?tab=readme-ov-file#usage>`__

.. code-block:: python

    from simplepycons import all_icons

    @App.page
    def dynamic_icon_with_simplepycons(lib):
        icon_index, set_icon_index = lib.hooks.use_state(0)
        icon_size = 16
        icon_names = [x.split('_')[1] for x in dir(all_icons) if x.startswith("get_")]
        num_icons = len(icon_names)

        features = [
            lib.ol.Feature(
                geometry=lib.ol.geom.Point([0, 0]),
                style=lib.ol.Style(
                    image=lib.ol.style.Icon(
                        anchor=[0, 0],
                        anchorXUnits="fraction",
                        anchorYUnits="pixels",
                        width=icon_size,
                        height=icon_size,
                        src=all_icons[icon_names[icon_index]].customize_svg_as_data_url(
                            fill="black", 
                            width=str(icon_size), 
                            height=str(icon_size)
                        )
                    )
                )
            )
        ]

        return lib.tethys.Display(
            lib.bs.Button(
                style=lib.Style(
                    position="absolute",
                    top=0,
                    right="20px",
                    zIndex=1
                ),
                onClick=lambda _: set_icon_index(icon_index + 1 if icon_index + 1 < num_icons else 0)
            )("Swap Icon"),
            lib.tethys.Map(
                lib.ol.layer.Vector(
                    lib.ol.source.Vector(
                        features=features,
                        format="olFeature"
                    )
                )
            )
        )

.. include:: reusables/geojson_with_dynamic_style.rst

.. include:: reusables/geojson_unique_value_styler.rst