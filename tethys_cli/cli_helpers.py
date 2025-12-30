import sys
import subprocess
from os import devnull
from pathlib import Path
from functools import wraps
import os
import shutil
from importlib import import_module
import bcrypt
import django
import yaml

from tethys_apps.base.testing.environment import set_testing_environment
from tethys_apps.utilities import (
    get_tethys_src_dir,
    get_tethys_home_dir,
    secrets_signed_unsigned_value,
)
from tethys_cli.cli_colors import (
    pretty_output,
    FG_RED,
    write_success,
    write_warning,
)
from tethys_portal.optional_dependencies import optional_import, FailedImport


TETHYS_HOME = Path(get_tethys_home_dir())


class _LocalCondaCommands:
    COMPARE = "compare"
    CONFIG = "config"
    CLEAN = "clean"
    CREATE = "create"
    INFO = "info"
    INSTALL = "install"
    LIST = "list"
    REMOVE = "remove"
    SEARCH = "search"
    UPDATE = "update"
    RUN = "run"


def add_geoserver_rest_to_endpoint(endpoint):
    parts = endpoint.split("//")
    protocol = parts[0]
    parts2 = parts[1].split(":")
    host = parts2[0]
    port_and_path = parts2[1]
    port = port_and_path.split("/")[0]

    return "{0}//{1}:{2}/geoserver/rest/".format(protocol, host, port)


def get_manage_path(args):
    """
    Validate user defined manage path, use default, or throw error
    """
    # Determine path to manage.py file
    manage_path = Path(get_tethys_src_dir()) / "tethys_portal" / "manage.py"

    # Check for path option
    if hasattr(args, "manage"):
        manage_path = args.manage or manage_path

    # Throw error if path is not valid
    if not Path(manage_path).is_file():
        with pretty_output(FG_RED) as p:
            p.write('ERROR: Can\'t open file "{0}", no such file.'.format(manage_path))
        exit(1)

    return str(manage_path)


def run_process(process):
    # Call the process with a little trick to ignore the keyboard interrupt error when it happens
    try:
        if "test" in process:
            set_testing_environment(True)
        return subprocess.call(process)
    except KeyboardInterrupt:
        pass
    finally:
        set_testing_environment(False)


def conda_available() -> bool:
    return bool(
        shutil.which("conda")
        or os.environ.get("CONDA_EXE")
        or shutil.which("mamba")
        or shutil.which("micromamba")
        or os.environ.get("MAMBA_EXE")
    )


def load_conda_commands():
    """
    Try new location first, then old, then a local stub.
    """
    for mod in (
        "conda.cli.python_api",  # old
        "conda.testing.integration",  # new verison has commands here
    ):
        try:
            return import_module(mod).Commands
        except (ImportError, AttributeError):
            pass
    return _LocalCondaCommands


def conda_run_command():
    """
    Prefer Conda's Python API when available; otherwise use our shell fallback.
    """
    run_api = optional_import("run_command", from_module="conda.cli.python_api")
    if not isinstance(run_api, FailedImport):
        return run_api
    # Fall back to shell implementation
    return _shell_run_command


def _shell_run_command(
    command, *args, use_exception_handler=False, stdout=None, stderr=None, **kwargs
):
    exe = (
        shutil.which("conda")
        or os.environ.get("CONDA_EXE")
        or shutil.which("mamba")
        or shutil.which("micromamba")
        or os.environ.get("MAMBA_EXE")
    )
    if not exe:
        return ("", "conda executable not found on PATH", 1)

    cmd = [exe, str(command), *args]
    auto_yes_commands = {_LocalCondaCommands.INSTALL}
    if str(command) in auto_yes_commands and not any(
        a in ("--yes", "-y") for a in args
    ):
        cmd.append("--yes")

    proc = subprocess.Popen(
        cmd,
        stdin=None,
        stdout=stdout or subprocess.PIPE,
        stderr=stderr or subprocess.PIPE,
        text=True,
    )
    try:
        out, err = proc.communicate()
    except KeyboardInterrupt:
        proc.terminate()
        out, err = proc.communicate()
    return out, err, proc.returncode


def supress_stdout(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        stdout = sys.stdout
        sys.stdout = open(devnull, "w")
        result = func(*args, **kwargs)
        sys.stdout = stdout
        return result

    return wrapped


def prompt_yes_or_no(question):
    """Handles a yes/no question cli prompt

    Returns:
        True if "yes"
        False if "no"
        None if cancelled (IMPORTANT: None is falsey, so don't confuse cancelled with "no")
    """
    negative_choices = ["n", "no", ""]
    valid_choices = ["y", "n", "yes", "no"]

    response = ""
    valid = False
    while not valid:
        try:
            response = input(f"{question} [y/n]: ")
        except (KeyboardInterrupt, SystemExit):
            return None

        if response.lower() in valid_choices:
            valid = True

    return response.lower() not in negative_choices


def setup_django(supress_output=False):
    func = django.setup
    if supress_output:
        func = supress_stdout(func)
    func()


def generate_salt_string():
    salt = bcrypt.gensalt()
    return salt


def gen_salt_string_for_setting(app_name, setting):
    secret_yaml_file = TETHYS_HOME / "secrets.yml"
    secret_settings = {}
    secret_unsigned = secrets_signed_unsigned_value(
        setting.name, setting.value, setting.tethys_app.package, is_signing=False
    )
    with secret_yaml_file.open("r") as secret_yaml:
        secret_settings = yaml.safe_load(secret_yaml) or {}
        if app_name not in secret_settings["secrets"]:
            write_warning(
                f"No definition for the app {app_name} in the secrets.yml. Generating one..."
            )
            secret_settings["secrets"][app_name] = {}
        if "custom_settings_salt_strings" not in secret_settings["secrets"][app_name]:
            write_warning(
                f"No custom_settings_salt_strings in the app {app_name} in the secrets.yml. Generating one..."
            )
            secret_settings["secrets"][app_name]["custom_settings_salt_strings"] = {}

        salt_string = generate_salt_string().decode()
        secret_settings["secrets"][app_name]["custom_settings_salt_strings"][
            setting.name
        ] = salt_string
        with secret_yaml_file.open("w") as secret_yaml:
            yaml.dump(secret_settings, secret_yaml)
            write_success(
                f"Salt string generated for setting: {setting.name} in app {app_name}"
            )
        setting.value = secret_unsigned
        setting.clean()
        setting.save()
