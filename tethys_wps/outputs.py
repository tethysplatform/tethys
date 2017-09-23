from django.http import HttpResponse
from django.http import Http404
import os

def outputs(request,fn):

    outputs_dir_path = os.path.dirname(os.path.realpath(__file__)) + "/outputs"

    targetfile = os.path.join(outputs_dir_path, fn)
    if os.path.isfile(targetfile):
        file_ext = os.path.splitext(targetfile)[1]
        with open(targetfile, mode='rb') as f:
            file_bytes = f.read()

        mime_type = None
        if 'xml' in file_ext:
            mime_type = 'text/xml'

        return HttpResponse(file_bytes, content_type=mime_type)

    else:
        return Http404("{0} NOT FOUND".format(fn))
