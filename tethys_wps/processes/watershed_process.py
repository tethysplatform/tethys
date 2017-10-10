import os
import sys
import subprocess
import tempfile
import logging
import binascii
from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS

class WatershedProcess(Process):
    def __init__(self):
        # init process
        inputs = [LiteralInput('outlet_x', 'Outlet Longitude', data_type='float', allowed_values=[[-8010000, 7570000]]),
                  LiteralInput('outlet_y', 'Outlet Latitude', data_type='float', allowed_values=[[-1923000, 2270000]])]
        outputs = [ComplexOutput('watershed', 'Delineated Watershed', supported_formats=[Format('application/gml+xml')])]

        super(WatershedProcess, self).__init__(
            self._handler,
            identifier='watershedprocess', # must be same, as filename
            version='0.1',
            title="Watershed delineation process",
            abstract='This process provides watershed delineation function using GRASS',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )



    def _handler(self, request, response):

        #get input values
        xlon = request.inputs['outlet_x'][0].data
        ylat = request.inputs['outlet_y'][0].data
        prj = "native"
        string_length = 4
        jobid = binascii.hexlify(os.urandom(string_length))

        # Run SC()
        basin_GEOJSON, msg = SC(jobid, xlon, ylat, prj)

        print basin_GEOJSON


        response.outputs['watershed'].output_format = FORMATS.GML
        response.outputs['watershed'].file = basin_GEOJSON

        print response.outputs['watershed'].file

        return response



def SC(jobid, xlon, ylat, prj):

        # Apache should have ownership and full permission over this path
        DEM_FULL_PATH = "/home/sherry/dem/dr_srtm_30_3857.tif"
        DEM_NAME = 'dr_srtm_30_3857' # DEM layer name, no extension (no .tif)
        DRAINAGE_FULL_PATH = "/home/sherry/dem/dr_srtm_30_3857_drain.tif"
        DRAINAGE_NAME = 'dr_srtm_30_3857_drain'
        GISBASE = "/usr/lib/grass72" # full path to GRASS installation
        GRASS7BIN = "grass" # command to start GRASS from shell
        # GISDB = os.path.join(tempfile.gettempdir(), 'grassdata')
        OUTPUT_DATA_PATH = os.path.join(tempfile.gettempdir(), 'grassdata', "output_data")

        dem_full_path = DEM_FULL_PATH
        dem = DEM_NAME
        drainage_full_path = DRAINAGE_FULL_PATH
        drainage = DRAINAGE_NAME
        gisbase = GISBASE
        grass7bin = GRASS7BIN

        # Define grass data folder, location, mapset
        gisdb = os.path.join(tempfile.gettempdir(), 'grassdata')
        if not os.path.exists(gisdb):
            os.mkdir(gisdb)
        location = "location_{0}".format(dem)
        mapset = "PERMANENT"
        msg = ""

        output_data_path = OUTPUT_DATA_PATH
        if not os.path.exists(output_data_path):
            os.mkdir(output_data_path)

        try:
            # Create location
            location_path = os.path.join(gisdb, location)
            if not os.path.exists(location_path):
                startcmd = grass7bin + ' -c ' + dem_full_path + ' -e ' + location_path

                p = subprocess.Popen(startcmd, shell=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if p.returncode != 0:
                    print >>sys.stderr, 'ERROR: %s' % err
                    print >>sys.stderr, 'ERROR: Cannot generate location (%s)' % startcmd
                    sys.exit(-1)

            xlon = float(xlon)
            ylat = float(ylat)
            outlet = (xlon, ylat)

            # Set GISBASE environment variable
            os.environ['GISBASE'] = gisbase
            # the following not needed with trunk
            os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
            # Set GISDBASE environment variable
            os.environ['GISDBASE'] = gisdb

            # define GRASS-Python environment
            gpydir = os.path.join(gisbase, "etc", "python")
            sys.path.append(gpydir)

            # import GRASS Python bindings (see also pygrass)
            import grass.script as gscript
            import grass.script.setup as gsetup
            gscript.core.set_raise_on_error(True)

            # launch session
            gsetup.init(gisbase, gisdb, location, mapset)

            # Check the dem file, import if not exist
            dem_mapset_path = os.path.join(gisdb, location, mapset, "cell", dem)

            if not os.path.exists(dem_mapset_path):
                stats = gscript.read_command('r.in.gdal', flags='o', input=dem_full_path, output=dem)

            #import drainage
            drainage_mapset_path = os.path.join(gisdb, location, mapset, "cell", drainage)
            if not os.path.exists(drainage_mapset_path):
                stats = gscript.read_command('r.in.gdal', flags='o', input=drainage_full_path, output=drainage)

            # Project xlon, ylat wgs84 into current
            if prj.lower() != "native" or prj.lower() == "wgs84":
                logging.info("\n ---------- Reproject xlon and ylat into native dem projection ------------- \n")
                stats = gscript.read_command('m.proj', coordinates=(xlon, ylat), flags='i')
                coor_list = stats.split("|")
                xlon = float(coor_list[0])
                ylat = float(coor_list[1])
                outlet = (xlon, ylat)

            # Define region
            stats = gscript.parse_command('g.region', raster=dem, flags='p')

            # Flow accumulation analysis
            if not os.path.exists(drainage_mapset_path):
                stats = gscript.read_command('r.watershed', elevation=dem, threshold='10000', drainage=drainage, flags='s', overwrite=True)

            # Delineate watershed
            basin = "{0}_basin_{1}".format(dem, jobid)
            stats = gscript.read_command('r.water.outlet', input=drainage, output=basin, coordinates=outlet, overwrite=True)

            # output lake
            basin_all_0 = "{0}_all_0".format(basin)
            mapcalc_cmd = '{0} = if({1}, 0)'.format(basin_all_0, basin)
            gscript.mapcalc(mapcalc_cmd, overwrite=True, quiet=True)

            # covert raster lake_rast_all_0 into vector
            basin_all_0_vect = "{0}_all_0_vect".format(basin)
            stats = gscript.parse_command('r.to.vect', input=basin_all_0, output=basin_all_0_vect, type="area", overwrite=True)

            # output GeoJSON
            geojson_f_name = "{0}.GEOJSON".format(basin)
            basin_GEOJSON = os.path.join(output_data_path, geojson_f_name)
            stats = gscript.parse_command('v.out.ogr', input=basin_all_0_vect, output=basin_GEOJSON, \
                                          format="GeoJSON", type="area", overwrite=True, flags="c")

            return basin_GEOJSON, msg

        except Exception as e:

            msg = e.message
            return None, msg
