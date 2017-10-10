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

import os
import tempfile

__author__ = 'Jachym'

from pywps import Process, BoundingBoxInput, BoundingBoxOutput


class Box(Process):
    def __init__(self):
        inputs = [BoundingBoxInput('bboxin', 'box in', ['epsg:4326', 'epsg:3035'])]
        outputs = [BoundingBoxOutput('bboxout', 'box out', ['epsg:4326'])]

        super(Box, self).__init__(
            self._handler,
            identifier='boundingbox',
            version='0.1',
            title="Bounding box in- and out",
            abstract='Give bounding box, return the same',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['bboxout'].data = request.inputs['bboxin'][0].data

        return response

