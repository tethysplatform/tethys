import json
import platform

from pathlib import Path
from os import getpid, environ
from subprocess import run
from threading import Timer
from time import sleep

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from tethys_apps.base.app_base import TethysAppBase
from tethys_apps.models import TethysApp
from tethys_apps.utilities import get_app_class
from tethys_cli.scaffold_commands import APP_PREFIX
from tethys_portal.forms import AppScaffoldForm


CONDA_ENV = environ["CONDA_DEFAULT_ENV"]
KILL_COMMAND = (
    f"taskkill /F /PID {getpid()}"
    if platform.system() == "Windows"
    else f"kill -9 {getpid()}"
)


def _execute_lifecycle_commands(app_package, command_message_tuples):
    channel_layer = get_channel_layer()
    for index, (command, message) in enumerate(command_message_tuples):
        async_to_sync(channel_layer.group_send)(
            f"app_{app_package}",
            {
                "type": "progress.message",
                "progress_metadata": {
                    "percentage": int(100 * index / len(command_message_tuples)),
                    "message": message,
                },
            },
        )
        if message == "Restarting server...":
            sleep(
                0.5
            )  # So the websocket has time to send the message prior to killing the server
        run(command, shell=True, check=True)


class AppLifeCycleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.app_package = self.scope["url_route"]["kwargs"]["app_name"]
        self.app_package_group_name = f"app_{self.app_package}"

        # Join app lifecycle group
        await self.channel_layer.group_add(
            self.app_package_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave app lifecycle group
        await self.channel_layer.group_discard(
            self.app_package_group_name, self.channel_name
        )

    # Receive message from room group
    async def progress_message(self, event):
        progress_metadata = event["progress_metadata"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(progress_metadata))


@login_required
@staff_member_required
def build_app(request):
    context = {}

    if request.POST:
        template = request.POST.get("scaffold_template")
        project_name = request.POST.get("project_name")
        app_name = request.POST.get("app_name")
        description = request.POST.get("description").replace('"', '""')
        theme_color = request.POST.get("app_theme_color")
        tags = request.POST.get("tags")
        author = request.POST.get("author")
        author_email = request.POST.get("author_email")
        license = request.POST.get("license")

        data = {k: v[0] for k, v in dict(request.POST).items()}

        project_path = Path.cwd() / f"{APP_PREFIX}-{project_name}"
        if project_path.exists():
            messages.add_message(
                request, messages.ERROR, f"A project already exists at {project_path}"
            )
            context["form"] = AppScaffoldForm(initial=data)
        else:
            migrate_cmd = "&& tethys db migrate" if template == "reactpy" else ""

            command_message_tuples = [
                (f"conda activate {CONDA_ENV}", "Activating environment..."),
                (
                    f'tethys scaffold {project_name} -t {template} --proper-name "{app_name}" --description "{description}" --color "{theme_color}" --tags "{tags}" --author "{author}" --author-email "{author_email}" --license "{license}"',
                    "Generating files...",
                ),
                (
                    f"cd {TethysAppBase.package_namespace}-{project_name} && tethys install -q -d {migrate_cmd}",
                    "Installing into Tethys Portal...",
                ),
                (f"{KILL_COMMAND} && tethys start", "Restarting server..."),
            ]

            Timer(
                1,
                _execute_lifecycle_commands,
                args=[project_name, command_message_tuples],
            ).start()

            context["app_name"] = app_name
            context["app_package"] = project_name
    else:
        data = {
            "author": request.user.get_full_name(),
            "author_email": request.user.email,
        }

        context["form"] = AppScaffoldForm(initial=data)

    return render(request, "tethys_portal/scaffold_app.html", context)


@login_required
@staff_member_required
def remove_app(request, app_id):
    app = get_app_class(TethysApp.objects.get(id=app_id))
    app_name = app.name
    app_package = app.package
    context = {
        "app_name": app_name,
        "app_package": app_package,
        "deleting": False,
        "redirect_url": reverse("admin:tethys_apps_tethysapp_change", args=(app_id,)),
    }
    if request.POST:
        command_message_tuples = [
            (f"conda activate {CONDA_ENV}", "Activating environment..."),
            (
                f"tethys uninstall -f {app_package}",
                "Removing app from Tethys Portal...",
            ),
            (f"{KILL_COMMAND} && tethys start", "Restarting server..."),
        ]

        Timer(
            1, _execute_lifecycle_commands, args=[app_package, command_message_tuples]
        ).start()

        context["deleting"] = True

    return render(request, "tethys_portal/remove_app.html", context)
