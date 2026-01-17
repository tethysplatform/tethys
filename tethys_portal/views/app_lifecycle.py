import json
import os
import platform
import re

import asyncio
from pathlib import Path
from shutil import unpack_archive, rmtree
from subprocess import run, CalledProcessError
from tempfile import mkdtemp
from threading import Timer
from time import sleep

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
from tethys_portal import settings


TOUCH_COMMAND = (
    f"copy /b {settings.__file__}+,, {settings.__file__}"
    if platform.system() == "Windows"
    else f"touch {settings.__file__}"
)


def unpatched_run(main):
    """An "unpatched" version of asyncio.run (see below)

    The reactpy-django package depends upon nest-asyncio, which patches
    the call to asyncio.run to redirect those calls to itself. The
    nest-asyncio package hasn't been updated in a couple of years, and in
    the meantime, asyncio.get_event_loop was updated to no longer
    automatically create the loop if missing. The code here in app_lifecycle.py
    was originally written to use asgiref.async_to_sync, which under the covers
    would call asyncio.get_event_loop and automatically create a loop for use
    in the new thread. Due to asyncio's update, it became necessary to
    self-manage the event loop in the thread. The best practice for this is to
    use asyncio.run, which will create and manage an event loop for the duration
    of the process, closing it at the end. Circling back to where this started
    above, asyncio.run is patched by nest-asyncio, and their version of "run"
    doesn't manage the event loop, but relies on one already being there or
    being auto-created by the old behavior of "asyncio.get_event_loop".
    """
    # If using Python >= 3.11, the asyncio.Runner() must be called directly
    # rather than use asyncio.run, since nest-asyncio's patched version still
    # expect asyncio.get_event_loop to create its own event loop if it does
    # not exist.
    if hasattr(asyncio, "Runner"):
        with asyncio.Runner() as runner:
            return runner.run(main)
    else:
        # If using Python 3.10, the nest-asycnio patched version's call to
        # asyncio.get_event_loop under the hood will automatically create
        # the loop if missing.
        asyncio.run(main)


def _execute_lifecycle_commands(
    app_package, command_message_tuples, from_import=False, cleanup=None
):
    if cleanup and not callable(cleanup):
        raise ValueError('The "cleanup" argument must be a function or callable.')

    revised_app_package = None

    channel_layer = get_channel_layer()
    try:
        for index, (command, message) in enumerate(command_message_tuples):
            unpatched_run(
                channel_layer.group_send(
                    f"app_{app_package}",
                    {
                        "type": "progress.message",
                        "progress_metadata": {
                            "app_package": revised_app_package or app_package,
                            "error_code": 0,
                            "percentage": int(
                                100 * index / len(command_message_tuples)
                            ),
                            "message": message,
                        },
                    },
                )
            )
            if message == "Restarting server...":
                sleep(
                    0.5
                )  # So the websocket has time to send the message prior to killing the server
            result = run(command, shell=True, check=True, capture_output=True)
            output = str(result.stdout)
            if from_import:
                match = re.search(
                    r"Successfully installed ([\w_]+) into your active Tethys Portal.",
                    output,
                )
                if match:
                    revised_app_package = match.group(match.lastindex)

    except CalledProcessError as e:
        unpatched_run(
            channel_layer.group_send(
                f"app_{app_package}",
                {
                    "type": "progress.message",
                    "progress_metadata": {
                        "error_code": 1,
                        "message": str(e),
                    },
                },
            )
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
    command_message_tuples = []
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
                (TOUCH_COMMAND, "Restarting server..."),
            ]
            app_package = app_package.replace("-", "_")

            Timer(
                1,
                _execute_lifecycle_commands,
                args=[
                    app_package,
                    command_message_tuples,
                    True,
                    lambda: rmtree(tmpdir),
                ],
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
    command_message_tuples = []

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
            migrate_cmd = (
                "&& tethys manage migrate reactpy_django"
                if template == "component"
                else ""
            )

            command_message_tuples += [
                (
                    f'tethys scaffold {project_name} -t {template} --proper-name "{app_name}" --description "{description}" --color "{theme_color}" --tags "{tags}" --author "{author}" --author-email "{author_email}" --license "{license}"',
                    "Generating files...",
                ),
                (
                    f"cd {TethysAppBase.package_namespace}-{project_name} && tethys install -q -d {migrate_cmd}",
                    "Installing into Tethys Portal...",
                ),
                (TOUCH_COMMAND, "Restarting server..."),
            ]

            Timer(
                1,
                _execute_lifecycle_commands,
                args=[project_name, command_message_tuples],
            ).start()

            context["app_name"] = app_name
            context["app_package"] = project_name
            del context["form"]

    context["project_location"] = Path.cwd() / f"{APP_PREFIX}-<Project Name>"

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
    command_message_tuples = []

    if request.method == "POST":
        command_message_tuples += [
            (
                f"tethys uninstall -f {app_package}",
                "Removing app from Tethys Portal...",
            ),
            (TOUCH_COMMAND, "Restarting server..."),
        ]

        Timer(
            1, _execute_lifecycle_commands, args=[app_package, command_message_tuples]
        ).start()

        context["deleting"] = True

    return render(request, "tethys_portal/remove_app.html", context)
