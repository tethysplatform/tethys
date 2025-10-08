import sys
import subprocess
from importlib import import_module
from os import devnull
from pathlib import Path
from functools import wraps

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


TETHYS_HOME = Path(get_tethys_home_dir())


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


def supress_stdout(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        stdout = sys.stdout
        sys.stdout = open(devnull, "w")
        result = func(*args, **kwargs)
        sys.stdout = stdout
        return result

    return wrapped


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


def _parse_version_component(part: str) -> int:
    digits = "".join(ch for ch in part if ch.isdigit())
    return int(digits) if digits else 0


def select_conda_cli_module() -> str:
    """
    Return the import path for the Conda CLI module that should be used.

    Conda 25.9 moved the public API to ``conda.testing.conda_cli``. Earlier
    versions still expose ``conda.cli.python_api``. We try the preferred module
    first (based on the currently installed conda version) and fall back to the
    classic location if needed.
    """

    try:
        from conda import __version__ as conda_version
    except Exception:
        conda_version = "0.0"

    parts = conda_version.split(".")
    major = _parse_version_component(parts[0]) if parts else 0
    minor = _parse_version_component(parts[1]) if len(parts) > 1 else 0

    preferred = "conda.testing.conda_cli" if (major, minor) >= (25, 9) else "conda.cli.python_api"
    candidates = [preferred]

    for fallback in ("conda.cli.python_api", "conda.testing.conda_cli"):
        if fallback not in candidates:
            candidates.append(fallback)

    for module_name in candidates:
        try:
            import_module(module_name)
        except (ImportError, ModuleNotFoundError):
            continue
        else:
            return module_name

    return candidates[-1]
