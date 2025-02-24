from os import getpid, environ
from subprocess import Popen
import platform

from django.shortcuts import render
from django.urls import reverse
from tethys_apps.base.app_base import TethysAppBase
from tethys_portal.forms import AppScaffoldForm
from tethys_apps.models import TethysApp
from tethys_apps.utilities import get_app_class
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

CONDA_ENV = environ["CONDA_DEFAULT_ENV"]
KILL_COMMAND = f'taskkill /F /PID {getpid()}' if platform.system() == "Windows" else f'kill -9 {getpid()}'

@login_required
@staff_member_required
def build_app(request):
    context = {}

    if request.POST:
        template = request.POST.get('scaffold_template')
        project_name = request.POST.get('project_name')
        app_name = request.POST.get('app_name')
        description = request.POST.get('description').replace('"', '""')
        theme_color = request.POST.get('app_theme_color')
        tags = request.POST.get('tags')
        author = request.POST.get('author')
        author_email = request.POST.get('author_email')
        license = request.POST.get('license')

        if template == 'reactpy':
            migrate_cmd = 'tethys db migrate && '
        else:
            migrate_cmd = ''
        
        command = f'conda activate {CONDA_ENV} && tethys scaffold {project_name} -t {template} --proper-name "{app_name}" --description "{description}" --color "{theme_color}" --tags "{tags}" --author "{author}" --author-email "{author_email}" --license "{license}" && cd {TethysAppBase.package_namespace}-{project_name} && tethys install -d && cd .. && {KILL_COMMAND} && {migrate_cmd}tethys start'
        Popen(command, shell=True)

        context['redirect_url'] = reverse("app_library")
    else:
        data = {'author': request.user.get_full_name(), 'author_email': request.user.email}

        context['form'] = AppScaffoldForm(initial=data)

    return render(request, "tethys_portal/scaffold_app.html", context)

@login_required
@staff_member_required
def remove_app(request, app_id):
    app = get_app_class(TethysApp.objects.get(id=app_id))
    context = {'app': app, 'deleting': False, 'redirect_url': reverse("admin:tethys_apps_tethysapp_change", args=(app_id,))}
    if request.POST:
        command = f'conda activate {CONDA_ENV} && tethys uninstall -f {app.package} && {KILL_COMMAND} && tethys start'
        Popen(command, shell=True)

        context['deleting'] = True
        context['redirect_url'] = reverse("app_library")

    return render(request, "tethys_portal/remove_app.html", context)
