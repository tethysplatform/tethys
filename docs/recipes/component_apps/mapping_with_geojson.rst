.. _component_app__mapping_with_geojson :



************************************
Component Apps: Mapping with GeoJSON
************************************

.. important::

    These recipes only apply to Component App development and will not work for Standard Apps.

**Last Updated:** December 2025

GeoJSON from a URL
==================

.. code-block:: python

    @App.page
    def geojson_from_url(lib):
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.Vector(
                    lib.ol.source.Vector(
                        options=lib.Props(
                            url="https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_urban_areas.geojson",
                            format_="GeoJSON"
                        )
                    )
                )
            )
        )

GeoJSON from explicit inline
============================

.. code-block:: python

    @App.page
    def geojson_from_inline(lib):
        features = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                'name': 'EPSG:3857',
                },
            },
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [0, 0],
                    },
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [
                            [4e6, -2e6],
                            [8e6, 2e6],
                        ],
                    },
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [
                            [4e6, 2e6],
                            [8e6, -2e6],
                        ],
                    },
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [-5e6, -1e6],
                                [-3e6, -1e6],
                                [-4e6, 1e6],
                                [-5e6, -1e6],
                            ],
                        ],
                    },
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'MultiLineString',
                        'coordinates': [
                            [
                                [-1e6, -7.5e5],
                                [-1e6, 7.5e5],
                            ],
                            [
                                [1e6, -7.5e5],
                                [1e6, 7.5e5],
                            ],
                            [
                                [-7.5e5, -1e6],
                                [7.5e5, -1e6],
                            ],
                            [
                                [-7.5e5, 1e6],
                                [7.5e5, 1e6],
                            ],
                        ],
                    },
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'MultiPolygon',
                        'coordinates': [
                            [
                                [
                                    [-5e6, 6e6],
                                    [-3e6, 6e6],
                                    [-3e6, 8e6],
                                    [-5e6, 8e6],
                                    [-5e6, 6e6],
                                ],
                            ],
                            [
                                [
                                    [-2e6, 6e6],
                                    [0, 6e6],
                                    [0, 8e6],
                                    [-2e6, 8e6],
                                    [-2e6, 6e6],
                                ],
                            ],
                            [
                                [
                                    [1e6, 6e6],
                                    [3e6, 6e6],
                                    [3e6, 8e6],
                                    [1e6, 8e6],
                                    [1e6, 6e6],
                                ],
                            ],
                        ],
                    },
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'GeometryCollection',
                        'geometries': [
                            {
                                'type': 'LineString',
                                'coordinates': [
                                    [-5e6, -5e6],
                                    [0, -5e6],
                                ],
                            },
                            {
                                'type': 'Point',
                                'coordinates': [4e6, -5e6],
                            },
                            {
                                'type': 'Polygon',
                                'coordinates': [
                                    [
                                        [1e6, -6e6],
                                        [3e6, -6e6],
                                        [2e6, -4e6],
                                        [1e6, -6e6],
                                    ],
                                ],
                            },
                        ],
                    },
                },
            ],
        }
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.Vector(
                    lib.ol.source.Vector(
                        options=lib.Props(
                            features=features,
                            format_="GeoJSON"
                        )
                    )
                )
            )
        )


GeoJSON from File / Pandas Dataframe
====================================

.. code-block:: python

    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point
    from tethys_sdk.components.utils import transform_coordinate

    def csv_to_geojson(csv_path):
        df = pd.read_csv(csv_path)
        geometry = [Point(transform_coordinate(xy, "EPSG:4326", "EPSG:3857")) for xy in zip(df['lat'], df['lon'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:3857")
        return gdf.to_json()

    @App.page
    def geojson_from_csv(lib):
        resources = lib.hooks.use_resources()
        geojson = csv_to_geojson(resources.path / "points.csv")
        return lib.tethys.Display(
            lib.tethys.Map(
                lib.ol.layer.Vector(
                    lib.ol.source.Vector(
                        options=lib.Props(
                            features=geojson,
                            format_="GeoJSON"
                        )
                    )
                )
            )
        )

.. include:: reusables/geojson_with_dynamic_style.rst

.. include:: reusables/geojson_unique_value_styler.rst

.. include:: reusables/display_feature_props_on_click.rst