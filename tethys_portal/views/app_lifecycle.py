import json
import os
import platform
import re

from pathlib import Path
from shutil import unpack_archive, rmtree
from subprocess import run, CalledProcessError
from tempfile import mkdtemp
from threading import Timer
from time import sleep

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from tethys_apps.base.app_base import TethysAppBase
from tethys_apps.models import TethysApp
from tethys_apps.utilities import get_app_class
from tethys_cli.scaffold_commands import APP_PREFIX
from tethys_portal.forms import AppScaffoldForm, AppImportForm


CONDA_ENV = os.environ["CONDA_DEFAULT_ENV"]
KILL_COMMAND = (
    f"taskkill /F /PID {os.getpid()}"
    if platform.system() == "Windows"
    else f"kill -9 {os.getpid()}"
)


def _execute_lifecycle_commands(app_package, command_message_tuples, cleanup=None):
    if cleanup and not callable(cleanup):
        raise ValueError('The "cleanup" argument must be a function or callable.')

    revised_app_package = None

    channel_layer = get_channel_layer()
    try:
        for index, (command, message) in enumerate(command_message_tuples):
            async_to_sync(channel_layer.group_send)(
                f"app_{app_package}",
                {
                    "type": "progress.message",
                    "progress_metadata": {
                        "app_package": revised_app_package or app_package,
                        "error_code": 0,
                        "percentage": int(100 * index / len(command_message_tuples)),
                        "message": message,
                    },
                },
            )
            if message == "Restarting server...":
                sleep(
                    0.5
                )  # So the websocket has time to send the message prior to killing the server
            result = run(command, shell=True, check=True, capture_output=True)
            output = str(result.stdout)
            if "Successfully installed " in output:
                revised_app_package = re.search(
                    r"Successfully installed ([\w_]+)", output
                ).group(1)

    except CalledProcessError as e:
        async_to_sync(channel_layer.group_send)(
            f"app_{app_package}",
            {
                "type": "progress.message",
                "progress_metadata": {
                    "error_code": 1,
                    "message": str(e),
                },
            },
        )
    if cleanup:
        try:
            cleanup()
        except Exception:
            pass


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
def import_app(request):
    context = {"form": AppImportForm()}  # form key removed below if valid POST request

    if request.method == "POST":
        form = AppImportForm(request.POST, request.FILES)
        context["form"] = form
        if form.is_valid():
            git_url = form.cleaned_data["git_url"]
            zip_file = form.cleaned_data["zip_file"]
            tmpdir = mkdtemp()
            import_name = git_url or zip_file.name
            app_folder_name = Path(import_name).stem
            app_package = app_folder_name.replace(f"{APP_PREFIX}-", "")
            abs_app_project_fpath = Path(tmpdir)

            command_message_tuples = [
                (f"conda activate {CONDA_ENV}", "Activating environment..."),
            ]

            if zip_file:
                dest_fpath = f"{tmpdir}/{zip_file.name}"
                with open(dest_fpath, "wb+") as dest:
                    for chunk in zip_file.chunks():
                        dest.write(chunk)
                unpack_archive(dest_fpath, tmpdir)
                os.remove(dest_fpath)
                unzipped_contents = os.listdir(tmpdir)
                if len(unzipped_contents) == 1:
                    abs_app_project_fpath /= unzipped_contents[0]

            else:  # git_url
                command_message_tuples.append(
                    (
                        f"cd {tmpdir} && git clone {git_url}",
                        f"Cloning source code from {git_url}",
                    ),
                )
                abs_app_project_fpath /= app_folder_name

            command_message_tuples += [
                (
                    f"cd {abs_app_project_fpath} && tethys install -q",
                    "Installing into Tethys Portal...",
                ),
                (f"{KILL_COMMAND} && tethys start", "Restarting server..."),
            ]
            app_package = app_package.replace("-", "_")

            Timer(
                1,
                _execute_lifecycle_commands,
                args=[app_package, command_message_tuples, lambda: rmtree(tmpdir)],
            ).start()

            context["app_name"] = import_name
            context["app_package"] = app_package
            del context["form"]

    return render(request, "tethys_portal/import_app.html", context)


@login_required
@staff_member_required
def create_app(request):
    initial = {
        "author": request.user.get_full_name(),
        "author_email": request.user.email,
    }
    context = {"form": AppScaffoldForm(initial=initial)}

    if request.method == "POST":
        form = AppScaffoldForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            # Form is valid
            template = form.cleaned_data["scaffold_template"]
            project_name = form.cleaned_data["project_name"]
            app_name = form.cleaned_data["app_name"]
            description = form.cleaned_data["description"].replace('"', '""')
            theme_color = form.cleaned_data["app_theme_color"]
            tags = form.cleaned_data["tags"]
            author = form.cleaned_data["author"]
            author_email = form.cleaned_data["author_email"]
            license = form.cleaned_data["license"]
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
            del context["form"]

    return render(request, "tethys_portal/create_app.html", context)


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
    if request.method == "POST":
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
