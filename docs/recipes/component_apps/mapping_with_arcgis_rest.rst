.. _component_app__mapping_with_argis_rest :



*************************************************
Component Apps: Mapping with ArcGIS REST Services
*************************************************

.. important::

    These recipes only apply to Component App development and will not work for Standard Apps.

**Last Updated:** December 2025

Image ArcGIS MapServer
======================

.. code-block:: python

    @App.page
    def image_arcgis_mapserver(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                center=[-10997148, 4569099],
                zoom=4
            )(
                lib.ol.layer.Image(
                    lib.ol.source.ImageArcGISRest(
                        options=lib.Props(
                            ratio=1,
                            params={},
                            url="https://sampleserver6.arcgisonline.com/ArcGIS/rest/services/USA/MapServer"
                        )
                    )
                )
            )
        )


Tile ArcGIS MapServer
=====================

.. code-block:: python

    @App.page
    def tile_arcgis_mapserver(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                center=[-10997148, 4569099],
                zoom=4
            )(
                lib.ol.layer.Tile(
                    extent=[-13884991, 2870341, -7455066, 6338219]
                )(
                    lib.ol.source.TileArcGISRest(
                        url="https://sampleserver6.arcgisonline.com/ArcGIS/rest/services/USA/MapServer"
                    )
                )
            )
        )

XYZ Esri
========

.. note::

    This example sets ``default_basemap=None`` since the XYZ Esri layer is a basemap.

.. code-block:: python

    @App.page
    def xyz_esri(lib):
        return lib.tethys.Display(
            lib.tethys.Map(default_basemap=None)(
                lib.ol.layer.WebGLTile(
                    lib.ol.source.ImageTile(
                        options=lib.Props(
                            attributions=(
                                'Tiles \u00A9 <a href="https://services.arcgisonline.com/ArcGIS/' +
                                'rest/services/World_Topo_Map/MapServer">ArcGIS</a>'
                            ),
                            url=(
                                'https://server.arcgisonline.com/ArcGIS/rest/services/' +
                                'World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
                            )
                        )
                    )
                )
            )
        )