"""
********************************************************************************
* Name: gen_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import json
import string
import sys
import random
from os import environ
from datetime import datetime
from pathlib import Path
from subprocess import call, run

from jinja2 import Template
import yaml

from django.conf import settings

import tethys_portal
from tethys_apps.utilities import (
    get_tethys_home_dir,
    get_tethys_src_dir,
    get_installed_tethys_items,
    get_secret_custom_settings,
)
from tethys_portal.dependencies import vendor_static_dependencies
from tethys_cli.cli_colors import write_error, write_info, write_warning
from tethys_cli.cli_helpers import (
    setup_django,
    load_conda_commands,
    conda_run_command,
)

from .site_commands import SITE_SETTING_CATEGORIES

from tethys_portal.optional_dependencies import (
    has_module,
    optional_import,
    FailedImport,
)

# optional imports
_conda_python_run_command = optional_import(
    "run_command", from_module="conda.cli.python_api"
)
run_command = (
    _conda_python_run_command
    if not isinstance(_conda_python_run_command, FailedImport)
    else conda_run_command()
)
Commands = load_conda_commands()

environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")

GEN_APACHE_OPTION = "apache"
GEN_APACHE_SERVICE_OPTION = "apache_service"
GEN_ASGI_SERVICE_OPTION = "asgi_service"
GEN_NGINX_OPTION = "nginx"
GEN_NGINX_SERVICE_OPTION = "nginx_service"
GEN_PORTAL_OPTION = "portal_config"
GEN_SECRETS_OPTION = "secrets"
GEN_SERVICES_OPTION = "services"
GEN_INSTALL_OPTION = "install"
GEN_META_YAML_OPTION = "metayaml"
GEN_PACKAGE_JSON_OPTION = "package_json"
GEN_PYPROJECT_OPTION = "pyproject"
GEN_REQUIREMENTS_OPTION = "requirements"

FILE_NAMES = {
    GEN_APACHE_OPTION: "tethys_apache.conf",
    GEN_APACHE_SERVICE_OPTION: "apache_supervisord.conf",
    GEN_ASGI_SERVICE_OPTION: "asgi_supervisord.conf",
    GEN_NGINX_OPTION: "tethys_nginx.conf",
    GEN_NGINX_SERVICE_OPTION: "nginx_supervisord.conf",
    GEN_PORTAL_OPTION: "portal_config.yml",
    GEN_SECRETS_OPTION: "secrets.yml",
    GEN_SERVICES_OPTION: "services.yml",
    GEN_INSTALL_OPTION: "install.yml",
    GEN_META_YAML_OPTION: "meta.yaml",
    GEN_PACKAGE_JSON_OPTION: "package.json",
    GEN_PYPROJECT_OPTION: "pyproject.toml",
    GEN_REQUIREMENTS_OPTION: "requirements.txt",
}

VALID_GEN_OBJECTS = (
    GEN_APACHE_OPTION,
    GEN_APACHE_SERVICE_OPTION,
    GEN_ASGI_SERVICE_OPTION,
    GEN_NGINX_OPTION,
    GEN_NGINX_SERVICE_OPTION,
    GEN_PORTAL_OPTION,
    GEN_SECRETS_OPTION,
    GEN_SERVICES_OPTION,
    GEN_INSTALL_OPTION,
    GEN_META_YAML_OPTION,
    GEN_PACKAGE_JSON_OPTION,
    GEN_PYPROJECT_OPTION,
    GEN_REQUIREMENTS_OPTION,
)

TETHYS_SRC = get_tethys_src_dir()
TETHYS_HOME = get_tethys_home_dir()


def add_gen_parser(subparsers):
    # Setup generate command
    gen_parser = subparsers.add_parser(
        "gen",
        help="Aids the installation of Tethys by automating the "
        "creation of supporting files.",
    )
    gen_parser.add_argument(
        "type", help="The type of object to generate.", choices=VALID_GEN_OBJECTS
    )
    gen_parser.add_argument(
        "-d", "--directory", help="Destination directory for the generated object."
    )
    gen_parser.add_argument(
        "-p",
        "--pin-level",
        choices=["major", "minor", "patch", "none"],
        help='Level to pin dependencies when generating the meta.yaml. One of "major", "minor", '
        '"patch", or "none". Defaults to "none".',
    )
    gen_parser.add_argument(
        "--micro",
        action="store_true",
        help="Use micro-tethys dependencies when generating the meta.yaml.",
    )
    gen_parser.add_argument(
        "--client-max-body-size",
        dest="client_max_body_size",
        help='Populate the client_max_body_size parameter for nginx config. Defaults to "75M".',
    )
    gen_parser.add_argument(
        "--asgi-processes",
        dest="asgi_processes",
        help="The maximum number of asgi worker processes. Defaults to 1.",
    )
    gen_parser.add_argument(
        "--conda-prefix",
        dest="conda_prefix",
        help="The path to the Tethys conda environment. Required if $CONDA_PREFIX is not defined.",
    )
    gen_parser.add_argument(
        "--tethys-port",
        dest="tethys_port",
        help="Port for the Tethys Server to run on in production. This is used when generating the "
        "Daphne, Nginx, and Apache configuration files. Defaults to 8000.",
    )
    gen_parser.add_argument(
        "--web-server-port",
        dest="server_port",
        help="Port for the proxy web server (i.e. Apache or Nginx) to listen on in production. "
        "This is used when generating the Apache configuration files. "
        "Defaults to 80 (or 443 if the --ssl option is used).",
    )
    gen_parser.add_argument(
        "--micromamba",
        dest="micromamba",
        action="store_true",
        help="Generate files to work in a Micromamba environment. Used when generating the "
        "configuration files for a Docker build (the Docker image uses the micromamba image "
        "as the base image).",
    )
    gen_parser.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing file without prompting.",
    )
    gen_parser.add_argument(
        "--ssl",
        dest="ssl",
        action="store_true",
        help="Add configuration settings for serving with SSL/HTTPS. "
        "Used for the Apache configuration file.",
    )
    gen_parser.add_argument(
        "--ssl-cert-path",
        dest="ssl_cert",
        help="Path to the certificate to use for SSL termination."
        "Used for the Apache configuration file. Defaults to ''.",
    )
    gen_parser.add_argument(
        "--ssl-key-path",
        dest="ssl_key",
        help="Path to the key to use for SSL termination."
        "Used for the Apache configuration file. Defaults to ''.",
    )
    gen_parser.add_argument(
        "--ip-address",
        dest="ip_address",
        help="IP address for web server."
        "Used for security with the 'ssl' option in the Apache configuration file. Defaults to ''.",
    )
    gen_parser.add_argument(
        "--additional-directive",
        dest="additional_directives",
        action="append",
        help="Additional configuration directives to add to the Apache configuration file. Defaults to ''.",
    )
    gen_parser.add_argument(
        "--run-as-user",
        dest="run_as_user",
        help="The user to run the Supervisor Apache service as. Defaults to 'root'.",
    )
    gen_parser.set_defaults(
        func=generate_command,
        client_max_body_size="75M",
        asgi_processes=1,
        conda_prefix=False,
        tethys_port=8000,
        server_port=None,
        overwrite=False,
        pin_level="none",
        micro=False,
        ssl=False,
        ssl_cert="",
        ssl_key="",
        ip_address="",
        additional_directives=[],
        run_as_user="root",
    )


def get_environment_value(value_name):
    value = environ.get(value_name)
    if value is not None:
        return value
    else:
        raise EnvironmentError(
            f'Environment value "{value_name}" must be set before generating this file.'
        )


def get_settings_value(value_name):
    value = getattr(settings, value_name, None)
    if value is not None:
        return value
    else:
        raise ValueError(
            f'Settings value "{value_name}" must be set before generating this file.'
        )


def generate_secret_key():
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(50)]
    )


def empty_context(args):
    context = {}
    return context


def proxy_server_context(args):
    args.server_port = args.server_port or (443 if args.ssl else 80)
    hostname = (
        str(settings.ALLOWED_HOSTS[0])
        if len(settings.ALLOWED_HOSTS) > 0
        else "127.0.0.1"
    )
    workspaces_root = get_settings_value("TETHYS_WORKSPACES_ROOT")
    static_root = get_settings_value("STATIC_ROOT")
    media_root = get_settings_value("MEDIA_ROOT")
    raw_prefix = (get_settings_value("PREFIX_URL") or "").strip()
    cleaned = raw_prefix.strip("/")
    prefix_url = f"/{cleaned}" if cleaned else ""

    context = {
        "ssl": args.ssl,
        "ssl_cert": args.ssl_cert,
        "ssl_key": args.ssl_key,
        "hostname": hostname,
        "ip_address": args.ip_address,
        "static_root": static_root,
        "workspaces_root": workspaces_root,
        "media_root": media_root,
        "prefix_url": prefix_url,
        "client_max_body_size": args.client_max_body_size,
        "port": args.tethys_port,
        "server_port": args.server_port,
        "additional_directives": args.additional_directives,
    }
    return context


def gen_apache_service(args):
    context = {
        "run_as_user": args.run_as_user,
    }
    return context


def gen_asgi_service(args):
    nginx_user = ""
    nginx_conf_path = "/etc/nginx/nginx.conf"
    if Path(nginx_conf_path).exists():
        with Path(nginx_conf_path).open() as nginx_conf:
            for line in nginx_conf.readlines():
                tokens = line.split()
                if len(tokens) > 0 and tokens[0] == "user":
                    nginx_user = tokens[1].strip(";")
                    break

    conda_prefix = (
        args.conda_prefix
        if args.conda_prefix
        else get_environment_value("CONDA_PREFIX")
    )
    conda_home = Path(conda_prefix).parents[1]
    conda_env_name = Path(conda_prefix).name

    context = {
        "nginx_user": nginx_user,
        "port": args.tethys_port,
        "asgi_processes": args.asgi_processes,
        "conda_prefix": conda_prefix,
        "conda_home": conda_home,
        "conda_env_name": conda_env_name,
        "tethys_src": TETHYS_SRC,
        "tethys_home": TETHYS_HOME,
        "is_micromamba": args.micromamba,
    }
    return context


def gen_portal_yaml(args):
    tethys_portal_settings = {}
    tethys_portal_settings.setdefault("version", 2.0)
    tethys_portal_settings.setdefault("name", "")
    tethys_portal_settings.setdefault("apps", {})
    tethys_portal_settings.setdefault("settings", {"SECRET_KEY": generate_secret_key()})
    tethys_portal_settings.setdefault(
        "site_settings", {category: {} for category in SITE_SETTING_CATEGORIES}
    )

    try:
        tethys_portal_settings.update(args.tethys_portal_settings)
    except AttributeError:
        write_info(
            "A Tethys Portal configuration file is being generated. "
            "Please review the file and fill in the appropriate settings."
        )

    context = {
        "version": tethys_portal_settings["version"],
        "name": tethys_portal_settings["name"],
        "apps": yaml.safe_dump({"apps": tethys_portal_settings["apps"]}),
        "settings": yaml.safe_dump({"settings": tethys_portal_settings["settings"]}),
        "site_settings": yaml.safe_dump(
            {"site_settings": tethys_portal_settings["site_settings"]}
        ),
    }
    return context


def gen_secrets_yaml(args):
    setup_django()
    tethys_secrets_settings = {}
    tethys_secrets_settings.setdefault("version", 1.0)
    tethys_secrets_settings.setdefault("secrets", {})
    installed_apps = get_installed_tethys_items(apps=True)

    for one_app in installed_apps.keys():
        if one_app not in tethys_secrets_settings["secrets"]:
            tethys_secrets_settings["secrets"][one_app] = {}
            if (
                "custom_settings_salt_strings"
                not in tethys_secrets_settings["secrets"][one_app]
            ):
                tethys_secrets_settings["secrets"][one_app][
                    "custom_settings_salt_strings"
                ] = {}

        secret_settings = get_secret_custom_settings(one_app)
        for secret_setting in secret_settings:
            tethys_secrets_settings["secrets"][one_app]["custom_settings_salt_strings"][
                secret_setting.name
            ] = ""

    write_info(
        "A Tethys Secrets file is being generated. "
        "Please review the file and fill in the appropriate settings."
    )

    context = {
        "version": tethys_secrets_settings["version"],
        "secrets": yaml.safe_dump({"secrets": tethys_secrets_settings["secrets"]}),
    }
    return context


def derive_version_from_conda_environment(dep_str, level="none"):
    """
    Determine dependency string based on the current tethys environment.

    Args:
        dep_str(str): The dep string from the environment.yml (e.g. 'python>=3.6').
        level(str): Level to lock dependencies to. One of 'major', 'minor', 'patch', or None. Defaults to 'minor'.

    Returns:
        str: the dependency string.
    """
    stdout, stderr, ret = run_command(Commands.LIST, dep_str)

    if ret != 0:
        print(
            f'ERROR: Something went wrong looking up dependency "{dep_str}" in environment'
        )
        print(stderr)
        return dep_str

    lines = stdout.split("\n")

    for line in lines:
        if line.startswith("#"):
            continue

        try:
            package, version, build, channel = line.split()
        except ValueError:
            continue

        if package != dep_str:
            continue

        version_numbers = version.split(".")

        if level == "major":
            if len(version_numbers) >= 2:
                dep_str = f"{package}={version_numbers[0]}.*"
            if len(version_numbers) == 1:
                dep_str = f"{package}={version_numbers[0]}"
        elif level == "minor":
            if len(version_numbers) >= 3:
                dep_str = f"{package}={version_numbers[0]}.{version_numbers[1]}.*"
            elif len(version_numbers) == 2:
                dep_str = f"{package}={version_numbers[0]}.{version_numbers[1]}"
        elif level == "patch":
            if len(version_numbers) > 3:
                dep_str = f"{package}={version_numbers[0]}.{version_numbers[1]}.{version_numbers[2]}.*"
            elif len(version_numbers) >= 1:
                dep_str = f'{package}={".".join(version_numbers)}'

    return dep_str


def gen_meta_yaml(args):
    filename = "micro_environment.yml" if args.micro else "environment.yml"
    package_name = "micro-tethys-platform" if args.micro else "tethys-platform"
    environment_file_path = Path(TETHYS_SRC) / filename
    with Path(environment_file_path).open() as env_file:
        environment = yaml.safe_load(env_file)

    dependencies = environment.get("dependencies", [])
    run_requirements = []

    for dependency in dependencies:
        if not any([operator in dependency for operator in ["=", "<", ">"]]):
            conda_env_version = derive_version_from_conda_environment(
                dependency, level=args.pin_level
            )
            run_requirements.append(conda_env_version)
        else:
            run_requirements.append(dependency)

    context = dict(
        run_requirements=run_requirements,
        tethys_version=tethys_portal.__version__,
        package_name=package_name,
    )
    return context


def gen_vendor_static_files(args):
    context = {
        "json": json.dumps(
            {
                "dependencies": {
                    d.npm_name: d.version for d in vendor_static_dependencies.values()
                }
            }
        )
    }
    return context


def download_vendor_static_files(args, cwd=None):
    cwd = cwd or Path(TETHYS_SRC) / "tethys_portal" / "static"
    try:
        call(["npm", "i"], cwd=cwd)
    except FileNotFoundError:
        install_instructions = (
            "To get npm you must install nodejs. Run the following command to install nodejs:"
            "\n\n\tconda install -c conda-forge nodejs\n"
            if has_module(_conda_python_run_command)
            else "For help installing npm see: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm"
        )
        msg = (
            f"ERROR! The packages from the package.json file could not be installed because npm is not installed.\n"
            f"{install_instructions}\n"
            f'After installing npm you can rerun "tethys gen package_json" '
            f'or you can navigate to {cwd} and run "npm install".'
        )

        write_error(msg)


def parse_setup_py(setup_file_path):
    """
    Parse metadata from a Tethys app setup.py file.
    """
    import ast

    try:
        tree = ast.parse(open(setup_file_path).read())
    except Exception as e:
        write_error(f"Failed to parse setup.py: {e}")
        return None

    metadata = {
        "app_package": "",
        "description": "",
        "author": "",
        "author_email": "",
        "keywords": "",
        "license": "",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id == "app_package":
                try:
                    metadata["app_package"] = ast.literal_eval(node.value)
                except Exception:
                    write_warning(
                        f"Found invalid 'app_package' in setup.py: '{ast.unparse(node.value)}'"
                    )
                    exit(1)

        # setup function
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "setup"
        ):
            for kw in node.keywords:
                if kw.arg in metadata:
                    try:
                        val = ast.literal_eval(kw.value)
                        if kw.arg == "keywords" and isinstance(val, list):
                            val = ", ".join(val)
                        metadata[kw.arg] = val
                    except Exception:
                        write_warning(
                            f"Found invalid '{kw.arg}' in setup.py: '{ast.unparse(kw.value)}'"
                        )
                        exit(1)

    if not metadata["app_package"]:
        write_warning("Could not find 'app_package' in setup.py.")
        exit(1)

    return metadata


def gen_pyproject(args):
    app_dir = get_target_tethys_app_dir(args)

    setup_py_path = app_dir / "setup.py"
    if not setup_py_path.is_file():
        write_error(
            f'The specified Tethys app directory "{app_dir}" does not contain a setup.py file.'
        )
        exit(1)

    else:
        setup_py_metadata = parse_setup_py(setup_py_path)

        return setup_py_metadata


def pyproject_post_process(args):
    file_path = get_destination_path(args, check_existence=False)
    app_folder_path = Path(file_path).parent
    if args.type == GEN_PYPROJECT_OPTION:
        valid_options = ("y", "n", "yes", "no")
        yes_options = ("y", "yes")

        remove_setup_file = input(
            "Would you like to remove the old setup.py file? (y/n):"
        ).lower()

        while remove_setup_file not in valid_options:
            remove_setup_file = input(
                "Invalid option. Remove setup.py file? (y/n): "
            ).lower()

        if remove_setup_file in yes_options:
            setup_py_path = app_folder_path / "setup.py"
            if not setup_py_path.is_file():
                write_error(
                    f'The specified Tethys app directory "{app_folder_path}" does not contain a setup.py file.'
                )
            else:
                setup_py_path.unlink()
                write_info(f'Removed setup.py file at "{setup_py_path}".')


def gen_install(args):
    write_info(
        "Please review the generated install.yml file and fill in the appropriate information "
        "(app name is required)."
    )

    context = {}
    return context


def gen_requirements_txt(args):
    write_warning("WARNING: The requirements.txt is currently only experimental.")
    # pip list --format=freeze | sed '/conda/d'
    output = run(
        [sys.executable, "-m", "pip", "list", "--format=freeze"], capture_output=True
    )
    packages = output.stdout.decode().splitlines()
    packages = [
        p
        for p in packages
        if all(
            [
                s not in p
                for s in [
                    "conda",
                    "tethys-platform",
                    "psycopg2=",
                    "tethysapp.",
                    "tethysext.",
                ]
            ]
        )
    ]
    context = {"packages": packages, "date": datetime.now().strftime("%Y-%m-%d")}
    return context


def get_destination_path(args, check_existence=True):
    # Determine destination file name (defaults to type)
    destination_file = FILE_NAMES[args.type]

    # Default destination path is the tethys_portal source dir
    destination_dir = Path(TETHYS_HOME)

    # Make the Tethys Home directory if it doesn't exist yet.
    if not destination_dir.is_dir():
        destination_dir.mkdir(parents=True, exist_ok=True)

    if args.type in [GEN_SERVICES_OPTION, GEN_INSTALL_OPTION]:
        destination_dir = Path.cwd()

    if args.type == GEN_PYPROJECT_OPTION:
        destination_dir = get_target_tethys_app_dir(args)

    elif args.type == GEN_META_YAML_OPTION:
        destination_dir = Path(TETHYS_SRC) / "conda.recipe"

    elif args.type == GEN_PACKAGE_JSON_OPTION:
        destination_dir = Path(TETHYS_SRC) / "tethys_portal" / "static"

    elif args.type == GEN_REQUIREMENTS_OPTION:
        destination_dir = Path(TETHYS_SRC)

    if args.directory:
        destination_dir = Path(args.directory).absolute()

    if not destination_dir.is_dir():
        write_error('ERROR: "{0}" is not a valid directory.'.format(destination_dir))
        exit(1)

    destination_path = destination_dir / destination_file

    if check_existence:
        check_for_existing_file(destination_path, destination_file, args.overwrite)

    return str(destination_path)


def check_for_existing_file(destination_path, destination_file, overwrite):
    # Check for pre-existing file
    if destination_path.is_file():
        valid_inputs = ("y", "n", "yes", "no")
        no_inputs = ("n", "no")

        if overwrite:
            overwrite_input = "yes"
        else:
            overwrite_input = input(
                'WARNING: "{0}" already exists. '
                "Overwrite? (y/n): ".format(destination_file)
            ).lower()

            while overwrite_input not in valid_inputs:
                overwrite_input = input("Invalid option. Overwrite? (y/n): ").lower()

        if overwrite_input in no_inputs:
            write_warning('Generation of "{0}" cancelled.'.format(destination_file))
            exit(0)


def render_template(file_type, context, destination_path):
    # Determine template path
    gen_templates_dir = Path(__file__).parent.absolute() / "gen_templates"
    template_path = gen_templates_dir / file_type

    # Parse template
    template = Template(template_path.read_text())
    # Render template and write to file
    if template:
        Path(destination_path).write_text(template.render(context))


def write_path_to_console(file_path, args):
    action_performed = getattr(args, "action_performed", "generated")
    write_info(f'File {action_performed} at "{file_path}".')


def get_target_tethys_app_dir(args):
    """Get the target directory for a Tethys app provided in args."""
    if args.directory:
        app_dir = Path(args.directory)
        if not app_dir.is_dir():
            write_error(f'The specified directory "{app_dir}" is not valid.')
            exit(1)
    else:
        app_dir = Path.cwd()

    return app_dir


GEN_COMMANDS = {
    GEN_APACHE_OPTION: proxy_server_context,
    GEN_APACHE_SERVICE_OPTION: gen_apache_service,
    GEN_ASGI_SERVICE_OPTION: gen_asgi_service,
    GEN_NGINX_OPTION: proxy_server_context,
    GEN_NGINX_SERVICE_OPTION: empty_context,
    GEN_PORTAL_OPTION: gen_portal_yaml,
    GEN_SECRETS_OPTION: gen_secrets_yaml,
    GEN_SERVICES_OPTION: empty_context,
    GEN_INSTALL_OPTION: gen_install,
    GEN_META_YAML_OPTION: gen_meta_yaml,
    GEN_PACKAGE_JSON_OPTION: (gen_vendor_static_files, download_vendor_static_files),
    GEN_PYPROJECT_OPTION: (gen_pyproject, pyproject_post_process),
    GEN_REQUIREMENTS_OPTION: gen_requirements_txt,
}


def no_op(args):
    pass


def generate_command(args):
    """
    Generate a settings file for a new installation.
    """
    # Setup variables
    context_func = GEN_COMMANDS[args.type]
    post_process_func = no_op
    if isinstance(context_func, tuple):
        context_func, post_process_func = context_func

    context = context_func(args)

    destination_path = get_destination_path(args)

    render_template(args.type, context, destination_path)

    write_path_to_console(destination_path, args)

    post_process_func(args)
