# Copyright (c) 2016 PyWPS Project Steering Committee
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'matteo'

import json
import os
import subprocess
from pywps import Process, ComplexInput, LiteralOutput, Format
from pywps.wpsserver import temp_dir


class Area(Process):
    """Process calculating area of given polygon
    """
    def __init__(self):
        inputs = [ComplexInput('layer', 'Layer', [Format('application/gml+xml')])]
        outputs = [LiteralOutput('area', 'Area', data_type='string')]

        super(Area, self).__init__(
            self._handler,
            identifier='area',
            title='Process Area',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
         # ogr2ogr requires gdal-bin
        from shapely.geometry import shape
        with temp_dir() as tmp:
            input_gml = request.inputs['layer'][0].file
            input_geojson = os.path.join(tmp, 'input.geojson')
            subprocess.check_call(['ogr2ogr', '-f', 'geojson',
                                   str(input_geojson), input_gml])
            with open(input_geojson, 'rb') as f:
                data = json.loads(f.read())
            features = []
            for feature in data['features']:
                geom = shape(feature['geometry'])
                feature['area'] = geom.area
            response.outputs['area'].data = [ feature['area'] for feature in data['features']]
            return response
