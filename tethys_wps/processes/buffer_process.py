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

__author__ = 'Brauni'

from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.validator.complexvalidator import validategml

from pywps.validator.mode import MODE


class Buffer(Process):
    def __init__(self):
        inputs = [ComplexInput('poly_in', 'Input vector file',
                  supported_formats=[Format('application/gml+xml')],
                  mode=MODE.STRICT),
                  LiteralInput('buffer', 'Buffer size', data_type='float',
                  allowed_values=(0, 1, 10, (10, 10, 100), (100, 100, 1000)))]
        outputs = [ComplexOutput('buff_out', 'Buffered file',
            supported_formats=[Format('application/gml+xml')])]

        super(Buffer, self).__init__(
            self._handler,
            identifier='buffer',
            version='0.1',
            title="GDAL Buffer process",
            abstract='This process provides standard buffer function using GDAL library',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        from osgeo import ogr

        inSource = ogr.Open(request.inputs['poly_in'][0].file)

        inLayer = inSource.GetLayer()
        out = inLayer.GetName() + '_buffer'

        # create output file
        driver = ogr.GetDriverByName('GML')
        outSource = driver.CreateDataSource(out, ["XSISCHEMAURI=http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayer = outSource.CreateLayer(out, None, ogr.wkbUnknown)

        # for each feature
        featureCount = inLayer.GetFeatureCount()
        index = 0

        while index < featureCount:
            # get the geometry
            inFeature = inLayer.GetNextFeature()
            inGeometry = inFeature.GetGeometryRef()

            # make the buffer
            buff = inGeometry.Buffer(float(request.inputs['buffer'][0].data))

            # create output feature to the file
            outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
            outFeature.SetGeometryDirectly(buff)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()  # makes it crash when using debug
            index += 1

            response.update_status('Buffering', 100*(index/featureCount))

        outSource.Destroy()

        response.outputs['buff_out'].output_format = FORMATS.GML
        response.outputs['buff_out'].file = out

        return response

