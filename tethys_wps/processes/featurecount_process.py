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

from pywps import Process, ComplexInput, Format, LiteralOutput
from pywps.app.Common import Metadata


class FeatureCount(Process):
    def __init__(self):
        inputs = [ComplexInput('layer', 'Layer', [Format('application/gml+xml')])]
        outputs = [LiteralOutput('count', 'Count', data_type='integer')]

        super(FeatureCount, self).__init__(
            self._handler,
            identifier='feature_count',
            version='None',
            title='Feature count',
            abstract='This process counts the number of features in a vector',
            profile='',
            metadata=[Metadata('Feature'), Metadata('Count')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        import lxml.etree
        from pywps.app.basic import xpath_ns
        doc = lxml.etree.parse(request.inputs['layer'][0].file)
        feature_elements = xpath_ns(doc, '//gml:featureMember')
        response.outputs['count'].data = len(feature_elements)
        return response
