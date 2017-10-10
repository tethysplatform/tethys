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

__author__ = 'Jachym'

from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.validator.complexvalidator import validategml

from pywps.validator.mode import MODE


class GrassBuffer(Process):
    def __init__(self):
        inputs = [ComplexInput('poly_in', 'Input1',
                  supported_formats=[Format('application/gml+xml')],
                  mode=MODE.STRICT),
                  LiteralInput('buffer', 'Buffer', data_type='float',
                  allowed_values=(0, 1, 10, (10, 10, 100), (100, 100, 1000)))]
        outputs = [ComplexOutput('buff_out', 'Buffered',
            supported_formats=[Format('application/gml+xml')])]

        super(GrassBuffer, self).__init__(
            self._handler,
            identifier='grassbuffer',
            version='0.1',
            title="GRASS v.buffer",
            abstract='This process is using GRASS GIS v.buffer module ',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            #grass_location="/tmp/outputs/pyws_process_GMkyxP/pywps_location"
            grass_location="epsg:3857"
        )

    def _handler(self, request, response):

        from grass.pygrass.modules import Module
        Module('v.import',
               input=request.inputs['poly_in'][0].file,
               epsg=3857, output='poly', extent='input')
        Module('v.buffer',
               input='poly',
               distance=request.inputs['buffer'][0].data,
               output='buffer')
        Module('v.out.ogr', input='buffer', output='buffer.gml', format='GML')

        response.outputs['buff_out'].file = 'buffer.gml'

        return response
