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

from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata


class UltimateQuestion(Process):
    def __init__(self):
        inputs = []
        outputs = [LiteralOutput('answer', 'Answer to Ultimate Question', data_type='string')]

        super(UltimateQuestion, self).__init__(
            self._handler,
            identifier='ultimate_question',
            version='1.3.3.7',
            title='Answer to the ultimate question',
            abstract='This process gives the answer to the ultimate question'
            ' of "What is the meaning of life?"',
            profile='',
            metadata=[Metadata('Ultimate Question'), Metadata('What is the meaning of life')],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False
        )

    def _handler(self, request, response):
        response.outputs['answer'].data = '42'
        return response
