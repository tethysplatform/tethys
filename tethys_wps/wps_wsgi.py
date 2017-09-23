from django.http import HttpResponse
from werkzeug.wrappers import Request as Request_Werkzeug
from pywps.app.WPSResponse import WPSResponse
from django.views.decorators.csrf import csrf_exempt
from pywps import Service

import processes as PROCESSES
import copy
import inspect
import os

@csrf_exempt
def wps_wsgi(request):

    processes = []
    clsmembers = inspect.getmembers(PROCESSES, inspect.isclass)
    for P_class in clsmembers:
        processes.append(P_class[1]())
    # This is, how you start PyWPS instance
    pywps_cfg_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"pywps.cfg")

    #service = Service(processes, ['/usr/lib/tethys/src/tethys_wps/pywps.cfg'])
    service = Service(processes, [pywps_cfg_path])
    request_werkzeug = Request_Werkzeug(copy.copy(request.META))
    response_werkzeug = service(request_werkzeug)
    if type(response_werkzeug) is WPSResponse:
        response_werkzeug=response_werkzeug(copy.copy(request.META))

    return HttpResponse(response_werkzeug.response, content_type='text/xml')
