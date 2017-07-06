# -*- coding: utf-8 -*-
#
#  tethys_models.py
#  gssha_model_builder
#
#  Created by Alan D Snow and Scott D. Christensen, 2017.
#  BSD 3-Clause
from json import dumps as json_dumps
from json import loads as json_loads
from mapkit.ColorRampGenerator import ColorRampEnum, ColorRampGenerator
import numpy as np
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.event import listens_for
from tethys_sdk.gizmos import MVLayer, MVLegendGeoServerImageClass


def get_geoserver_layer_model(app, declarative_base):
    """
    Return model for GeoServerLayer to use with app.
    """

    class GeoServerLayer(declarative_base):
        """
        Geoserver Layer SQLAlchemy DB Model

        Attributes
        ----------
        id: int
            Primary key
        name: str
            Geoserver layer name.
        workspace: str
            Geoserver workspace name for layer. Defaults to app package name.
        latlon_bbox: str
            The latitude and longitude bounding box for the layer.
        projection: str
            The projection for the layer.
        geoserver_name: str
            Name of the geoserver in the app setting.
        style_name: str
            Name of the style in GeoServer assicated with this layer.
        uploaded: bool
            If the layer was uploaded to geoserver using these tools.
        attributes: str
            A JSON string of attributes of the shapefile layer.
        tethys_app: :obj:`tethys_sdk.base.TethysAppBase`
            An instance of the tethys app class.
        type: str
            The polymorphic type to use for inheritance.

        Create Workspace Before Using::

            geo_engine = app.get_spatial_dataset_service('primary_geoserver', as_engine=True)
            # add workspace for app package
            geo_engine.create_workspace(workspace_id=app.package,
                                         uri='localhost/apps/{app_package}'
                                              .format(app_package=app.package))

        Use in your models::

            from tethys_models.geoserver import get_geoserver_layer_model
            from .app import ExampleApp as app
            from sqlalchemy.ext.declarative import declarative_base

            Base = delarative_base()

            GeoServerLayer =  get_geoserver_layer_model(app, Base)
        """
        __tablename__ = 'geoserver_layer'

        # Columns
        id = Column(Integer, primary_key=True)
        name = Column(String)
        workspace = Column(String)
        latlon_bbox = Column(String)
        projection = Column(String)
        geoserver_name = Column(String)
        style_name = Column(String)
        uploaded = Column(Boolean, default=False)
        attributes = Column(String)
        tethys_app = app

        # polymorphic
        type = Column(String(50))

        __mapper_args__ = {
            'polymorphic_identity': 'geoserver_layer',
            'polymorphic_on': type
        }

        @property
        def layer_name(self):
            """
            Gives full geoserver layer name.
            """
            return "{0}:{1}".format(self.workspace, self.name)

        @property
        def bounds(self):
            """
            Retrieves bounds to use with MVLayer
            """
            return [float(x) for x in json_loads(self.latlon_bbox)]

        @property
        def engine(self):
            """
            Retrives GeoServer engine
            """
            return self.tethys_app \
                       .get_spatial_dataset_service(self.geoserver_name,
                                                    as_engine=True)

        @property
        def base_url(self):
            """
            Retrives base url
            """
            return self.engine._get_non_rest_endpoint()

        @property
        def wfs_url(self):
            """
            Retrives WFS url
            """
            return self.engine._get_wfs_url(self.layer_name, 'GML3')

        @property
        def wms_url(self):
            """
            Retrives WMS url
            """
            return self.tethys_app \
                       .get_spatial_dataset_service(self.geoserver_name,
                                                    as_wms=True)

        def _get_mvlayer(self, source, url,
                         legend_title,
                         legend_units,
                         legend_classes=None,
                         **kwargs):
            """
            Get MVLayer object for geoserver
            """
            layer_params = {'LAYERS': self.layer_name }
            if self.style_name is not None:
                layer_params['STYLES'] = self.style_name

            if None not in (self.style_name, legend_units):
                legend_classes = [
                    MVLegendGeoServerImageClass(legend_units,
                                                geoserver_url=self.base_url,
                                                style=self.style_name,
                                                layer=self.name),
                ]
            return MVLayer(
                source=source,
                options={'url': url,
                         'params': layer_params,
                         'serverType': 'geoserver'},
                legend_title=legend_title,
                legend_extent=self.bounds,
                legend_classes=legend_classes,
                geometry_attribute='the_geom',
                **kwargs
            )

        def get_wms_mvlayer(self, legend_title,
                            legend_units=None,
                            legend_classes=None,
                            **kwargs):
            """
            Retrieve WMS MVLayer for MapView gizmo.

            Parameters
            ----------
            legend_title: str
                MVLayer.legend_title
            legend_units: str, optional
                Units of measure for legend.
                To be used with MVLegendGeoServerImageClass.
            legend_classes: list, optional
                MVLayer.legend_classes. Used in the place of
                MVLegendGeoServerImageClass.
            **kwargs: :obj:`MVLayer` inputs
                Inputs for :obj:`MVLayer`.
                
            Example::


                geoserver_elevation_layer = session.query(GeoServerLayer).first()

                elev_mvlayer = geoserver_elevation_layer.get_wms_mvlayer(
                    layer_options={'opacity': 0.8},
                    legend_title="Elevation",
                    legend_units="Meters"
                )
            """
            return self._get_mvlayer(source='ImageWMS',
                                     url=self.wms_url,
                                     legend_title=legend_title,
                                     legend_units=legend_units,
                                     legend_classes=legend_classes,
                                     **kwargs)

        def _update_layer_info(self, layer_info):
            """Update bounds and projection of layer"""
            raw_latlon_bbox = layer_info['latlon_bbox'][:4]
            self.latlon_bbox = json_dumps([raw_latlon_bbox[0],
                                           raw_latlon_bbox[2],
                                           raw_latlon_bbox[1],
                                           raw_latlon_bbox[3]])
            self.projection = layer_info['projection']

        def upload_raster_layer(self, coverage_type,
                                coverage_file=None,
                                coverage_upload=None):
            """
            Upload a geoserver layer and store needed information.

            File on Server Example::

                from .app import ExampleApp as app

                file_path = '/path/to/index_grid.tif'
                layer_name = 'index_grid'
                geoserver_layer = GeoServerLayer(name=layer_name,
                                                 workspace=app.package_name,
                                                 style_name='custom_style',
                                                 geoserver_name="master")
                geoserver_layer.upload_raster_layer(coverage_type='geotiff',
                                                    coverage_file=file_path)
            Upload Example::

                from .app import ExampleApp as app

                file_upload = request.FILES.get('index_grid')
                layer_name = 'index_grid'
                geoserver_layer = GeoServerLayer(name=layer_name,
                                                 workspace=app.package_name,
                                                 geoserver_name="master")
                geoserver_layer.upload_raster_layer(coverage_type='geotiff',
                                                    coverage_upload=file_upload)
            """
            # Upload files
            try:
                layer_info = \
                    self.engine.create_coverage_resource(
                        store_id=self.layer_name,
                        coverage_file=coverage_file,
                        coverage_upload=coverage_upload,
                        coverage_type=coverage_type,
                        coverage_name=self.name,
                        overwrite=True,
                        debug=False
                    )
            except Exception:
                self.engine.delete_store(store_id=self.layer_name, purge="all")
                raise

            if not layer_info['success']:
                self.engine.delete_store(store_id=self.layer_name, purge="all")
                raise Exception("Problems uploading {0}. \n {1}"
                                .format(self.layer_name, layer_info['error']))

            if 'result' in layer_info:
                layer_info = layer_info['result']
                if layer_info:
                    self._update_layer_info(layer_info)
                    self.uploaded = True

        def upload_shapefile(self, shapefile_upload=None, shapefile_zip=None):
            """
            Upload a shapefile to geoserver and return layer name.

            Example::

                from .app import ExampleApp as app

                file_upload = request.FILES.getlist('drainage_line_shp_file')
                layer_name = 'drainge_line'
                geoserver_layer = GeoServerLayer(name=layer_name,
                                                 workspace=app.package_name,
                                                 style_name='custom_style',
                                                 geoserver_name="master")
                geoserver_layer.upload_shapefile(file_upload)
            """
            request_info = \
                self.engine.create_shapefile_resource(self.layer_name,
                                                      shapefile_upload=shapefile_upload,
                                                      shapefile_zip=shapefile_zip)
            print(request_info)
            if not request_info['success']:
                self.engine.delete_store(store_id=self.layer_name, purge="all")
                raise Exception("Problems uploading {0}:: {1}".format(self.layer_name,
                                                                      request_info['error']))

            layer_info = request_info['result']
            print(layer_info)
            self._update_layer_info(layer_info)
            self.attributes = json_dumps(layer_info['attributes'])
            self.uploaded = True

        def update_shapefile_information(self):
            """
            Queries GeoServer to update the shapefile information.

            Generate Example::

                from .app import ExampleApp as app

                geoserver_layer = GeoServerLayer(name='drainge_line',
                                                 workspace=app.package_name,
                                                 style_name='custom_style',
                                                 geoserver_name='master')
                geoserver_layer.update_shapefile_information()

            Query Example::

                geoserver_shape_layer = session.query(GeoServerLayer).first()
                geoserver_shape_layer.update_shapefile_information()
            """
            request_info = self.engine.get_resource(resource_id=self.layer_name)

            if not request_info['success']:
                self.engine.delete_store(store_id=self.layer_name, purge="all")
                raise Exception("Problems updating {0}:: {1}".format(self.layer_name,
                                                                     request_info['error']))
            layer_info = request_info['result']
            if layer_info:
                self._update_layer_info(layer_info)
                self.attributes = json_dumps(layer_info['attributes'])
            else:
                raise Exception("Problems updating {0}: {1} ..."
                                .format(self.layer_name, layer_info['error']))

        def update_layer_group_information(self):
            """
            Update information about geoserver layer group.

            .. warning:: This is in beta stages.
            """
            layer_info = self.engine.get_layer_group(self.layer_name)

            if layer_info['success']:
                raw_latlon_bbox = layer_info['result']['bounds'][:4]
                if (abs(float(raw_latlon_bbox[0])-float(raw_latlon_bbox[2])) > 0.001 and
                        abs(float(raw_latlon_bbox[1])-float(raw_latlon_bbox[3])) > 0.001):
                    self.latlon_bbox = json_dumps([raw_latlon_bbox[0],
                                                   raw_latlon_bbox[2],
                                                   raw_latlon_bbox[1],
                                                   raw_latlon_bbox[3]])
                    self.projection = layer_info['result']['bounds'][-1]
                else:
                    raise Exception("Layer group ({0}) has invalid bounding "
                                    "box ...".format(self.layer_name))
            else:
                raise Exception("Problems updating {0}:: {1} ..."
                                .format(self.layer_name, layer_info['error']))

        def generate_style_mapkit(
            self,
            style_name=None,
            min_val=None,
            max_val=None,
            discrete_values=None,
            alpha=1.0,
            color_ramp_step=1,
            color_ramp_enum=ColorRampEnum.COLOR_RAMP_HUE
        ):
            """
            Generate style for raster layer using mapkit.


            Discrete Example::

                from .app import ExampleApp as app
                from gazar import GDALGrid
                from mapkit.ColorRampGenerator import ColorRampEnum
                import numpy as np

                file_path = '/path/to/index_grid.tif'
                layer_name = 'index_grid'

                geoserver_layer = GeoServerLayer(name=layer_name,
                                                 workspace=app.package_name,
                                                 geoserver_name="master")
                geoserver_layer.upload_raster_layer(coverage_type='geotiff',
                                                    coverage_file=file_path)

                index_grid = GDALGrid(file_path)
                discrete_values = np.unique(index_grid.np_array())
                index_map_layer.generate_style_mapkit(
                    discrete_values=discrete_values,
                    alpha=0.85
                )


            Continuous Example::

                from .app import ExampleApp as app
                from gazar import GDALGrid
                from mapkit.ColorRampGenerator import ColorRampEnum
                import numpy as np


                file_path = '/path/to/elevation.tif'
                layer_name = 'elevatin'

                geoserver_layer = GeoServerLayer(name=layer_name,
                                                 workspace=app.package_name,
                                                 geoserver_name="master")
                geoserver_layer.upload_raster_layer(coverage_type='geotiff',
                                                    coverage_file=file_path)

                elevation_grid = GDALGrid(file_path)
                ele_array = elevation_grid.np_array()

                geoserver_layer.generate_style_mapkit(
                    min_val=np.amin(ele_array),
                    max_val=np.amax(ele_array),
                    alpha=0.85,
                    color_ramp_step=3,
                    color_ramp_enum=ColorRampEnum.COLOR_RAMP_TERRAIN
                )
            """
            if style_name is None:
                self.style_name = self.name
            else:
                self.style_name = style_name

            if discrete_values is not None:
                if min_val is None:
                    min_val = np.amin(discrete_values)
                if max_val is None:
                    max_val = np.amax(discrete_values)

            # generate sld for index map
            color_ramp = \
                ColorRampGenerator.generateDefaultColorRamp(color_ramp_enum)
            mappedColorRamp = \
                ColorRampGenerator.mapColorRampToValues(
                    colorRamp=color_ramp[::color_ramp_step],
                    minValue=min_val,
                    maxValue=max_val,
                    alpha=alpha
                )
            sld_header = ('<?xml version="1.0" encoding="ISO-8859-1"?>'
                          '<StyledLayerDescriptor version="1.0.0" '
                          'xmlns="http://www.opengis.net/sld" '
                          'xmlns:ogc="http://www.opengis.net/ogc" '
                          'xmlns:xlink="http://www.w3.org/1999/xlink" '
                          'xmlns:xsi='
                          '"http://www.w3.org/2001/XMLSchema-instance" '
                          'xsi:schemaLocation="http://www.opengis.net/sld '
                          'http://schemas.opengis.net/sld/1.0.0/'
                          'StyledLayerDescriptor.xsd">'
                          '<NamedLayer><Name>{style_name}</Name>'
                          '<UserStyle><Name>{style_name}</Name>'
                          '<FeatureTypeStyle><Rule><RasterSymbolizer>'
                          ).format(style_name=self.style_name)
            sld_footer = ('</RasterSymbolizer></Rule></FeatureTypeStyle>'
                          '</UserStyle></NamedLayer></StyledLayerDescriptor>')

            if discrete_values is not None:
                sld_body = \
                    mappedColorRamp.getColorMapAsDiscreetSLD(discrete_values)
            else:
                sld_body = mappedColorRamp.getColorMapAsContinuousSLD()

            style_id = "{0}:{1}".format(app.package, self.style_name)

            try:
                sld_string = sld_header + sld_body + sld_footer
                self.engine.create_style(style_id=style_id,
                                         sld=sld_string,
                                         overwrite=True,
                                         debug=False)
            except Exception:
                self.engine.delete_style(style_id=style_id)
                raise

        def purge(self):
            """
            Purge layer from GeoServer. This should happen automatically
            unless you inherit from this class.
            """
            if self.uploaded:
                geo_engine = self.engine
                geo_engine.delete_store(self.layer_name,
                                        purge="all")
                geo_engine.delete_layer(self.layer_name,
                                        purge="all")

    @listens_for(GeoServerLayer, 'after_delete')
    def purge_geoserver_layer(mapper, connect, target):
        """method to automatically delete layers from
        geoserver that you uploaded"""
        target.purge()

    return GeoServerLayer
