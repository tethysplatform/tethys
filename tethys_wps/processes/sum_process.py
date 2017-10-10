from pywps import Process, LiteralInput, LiteralOutput, Format, FORMATS
import types
import time

class SumProcess(Process):
    def __init__(self):

        inputs = [LiteralInput('input1', 'Input1 number', data_type='float'),
                  LiteralInput('input2', 'Input2 number', data_type='float')]
        outputs = [LiteralOutput('output', 'input1 add input2', data_type='float')]

        super(SumProcess, self).__init__(
            self._handler,
            identifier='sumprocess',
            version='0.1',
            title="Sum process",
            abstract='The SUM process will accept 2 input numbers and return their sum',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )


    def _handler(self, request, response):
        # import time
        # time.sleep(10)

        response.outputs['output'].data = request.inputs['input1'][0].data + request.inputs['input2'][0].data
        # self.Output.setValue(int(self.Input1.getValue())+int(abc()))
        return response