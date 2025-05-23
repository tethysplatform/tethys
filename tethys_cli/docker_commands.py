"""
********************************************************************************
* Name: docker_commands.py
* Author: Nathan Swain
* Created On: July 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path

import getpass
from tethys_cli.cli_colors import write_pretty_output, write_error, write_warning
from tethys_apps.utilities import get_tethys_home_dir
from tethys_portal.optional_dependencies import optional_import, has_module

# optional imports
curses = optional_import("curses")  # curses not available on Windows
docker = optional_import("docker")
Mount = optional_import("Mount", from_module="docker.types")
DockerNotFound = optional_import("NotFound", from_module="docker.errors")


__all__ = [
    "docker_init",
    "docker_start",
    "docker_stop",
    "docker_status",
    "docker_update",
    "docker_remove",
    "docker_ip",
    "docker_restart",
    "docker_container_inputs",
]

OSX = 1
WINDOWS = 2
LINUX = 3


def add_docker_parser(subparsers):
    # Setup the docker commands
    docker_parser = subparsers.add_parser(
        "docker", help="Management commands for the Tethys Docker containers."
    )
    docker_parser.add_argument(
        "command",
        help="Docker command to run.",
        choices=[
            "init",
            "start",
            "stop",
            "status",
            "update",
            "remove",
            "ip",
            "restart",
        ],
    )
    docker_parser.add_argument(
        "-d",
        "--defaults",
        action="store_true",
        dest="defaults",
        help="Run command without prompting without interactive input, using defaults instead.",
    )
    docker_parser.add_argument(
        "-c",
        "--containers",
        nargs="+",
        help="Execute the command only on the given container(s).",
        choices=docker_container_inputs,
    )
    docker_parser.add_argument(
        "-b",
        "--boot2docker",
        action="store_true",
        dest="boot2docker",
        help="Stop boot2docker on container stop. Only applicable to stop command.",
    )
    docker_parser.add_argument(
        "-t",
        "--image_tag",
        dest="image_tag",
        help="Create the container using the provided Docker image tag. "
        "Only applicable to the init and update commands for a single container.",
    )
    docker_parser.add_argument(
        "-i",
        "--image_name",
        dest="image_name",
        help="Create the container using the provided Docker image name. "
        "Only applicable to the init and update command for a single container.",
    )
    docker_parser.set_defaults(func=docker_command)


class ContainerMetadata(ABC):
    input = None
    name = None
    display_name = None
    image_name = None
    tag = "latest"
    host_port = None
    container_port = None
    default_host = "127.0.0.1"

    _docker_client = None
    all_containers = None

    def __init__(self, docker_client=None, image_name=None, image_tag=None):
        self._docker_client = docker_client
        self._container = None
        self.image_name = image_name if image_name is not None else self.image_name
        self.tag = image_tag if image_tag is not None else self.tag

    def __repr__(self):
        return f'<{self.__class__.name} name="{self.name}" image="{self.image}">'

    @classmethod
    def get_docker_client(cls):
        """
        Configure DockerClient
        """
        if cls._docker_client is None:
            try:
                cls._docker_client = docker.from_env()
            except docker.errors.DockerException:
                write_error(
                    "The Docker daemon must be running to use the tethys docker command."
                )
                exit(1)

        return cls._docker_client

    @property
    def docker_client(self):
        if self._docker_client is None:
            self._docker_client = self.get_docker_client()
        return self._docker_client

    @classmethod
    def get_containers(
        cls, containers=None, installed=None, image_name=None, image_tag=None
    ):
        if cls.all_containers is None or (
            image_name is not None or image_tag is not None
        ):
            cls.all_containers = [
                C(image_name=image_name, image_tag=image_tag)
                for C in cls.__subclasses__()
            ]

        if containers is None:
            containers = cls.all_containers
        else:
            containers = [c for c in cls.all_containers if c.input in containers]

        if installed is not None:
            containers = [c for c in containers if c.is_installed == installed]

        return containers

    @property
    def is_installed(self):
        return self.container is not None

    @property
    def container(self):
        if self._container is None:
            try:
                self._container = self.docker_client.containers.get(self.name)
            except DockerNotFound:
                self._container = None
        return self._container

    @property
    def port_bindings(self):
        return {self.container_port: self.host_port}

    @property
    def ip(self):
        msg = (
            "\n{name}:" "\n  Host: {host}" "\n  Port: {port}" "\n  Endpoint: {endpoint}"
        )

        return msg.format(
            name=self.display_name,
            host=self.default_host,
            port=self.host_port,
            endpoint=self.endpoint,
        )

    @property
    def image(self):
        return f"{self.image_name}:{self.tag}"

    @property
    @abstractmethod
    def endpoint(self):
        """URL for accessing the service running in the container."""

    @abstractmethod
    def get_container_options(self, defaults):
        """Compiles an options dictionary based on defaults and user input for creating the container."""

    def default_container_options(self):
        return dict(
            name=self.name,
            image=self.image,
            environment={},
            host_config=dict(port_bindings=self.port_bindings),
        )

    def pull(self):
        pull_stream = self.docker_client.api.pull(self.image, stream=True)
        log_pull_stream(pull_stream)

    def create(self, defaults=False):
        write_pretty_output(
            "\nInstalling the {} Docker container...".format(self.display_name)
        )

        options = self.get_container_options(defaults)
        options["host_config"] = self.docker_client.api.create_host_config(
            **options["host_config"]
        )
        self.docker_client.api.create_container(**options)

    def start(self):
        msg = "Starting {} container..."
        write_pretty_output(msg.format(self.display_name))
        msg = None
        try:
            self.container.start()
        except Exception as e:
            msg = (
                "There was an error while attempting to start container {}: {}".format(
                    self.display_name, str(e)
                )
            )
        return msg

    def stop(self, silent=False):
        msg = "Stopping {} container..."
        if not silent:
            write_pretty_output(msg.format(self.display_name))
        try:
            self.container.stop()
            msg = None
        except Exception as e:
            msg = "There was an error while attempting to stop container {}: {}".format(
                self.display_name, str(e)
            )

        return msg

    def remove(self):
        write_pretty_output("Removing {} container...".format(self.display_name))
        self.container.remove()


class PostGisContainerMetadata(ContainerMetadata):
    input = "postgis"
    name = "tethys_postgis"
    display_name = "PostGIS/Database"
    image_name = "postgis/postgis"
    host_port = 5435
    container_port = 5432

    @property
    def endpoint(self):
        return "postgresql://<username>:<password>@{host}:{port}/<database>".format(
            host=self.default_host, port=self.host_port
        )

    def default_container_options(self):
        options = super().default_container_options()
        options.update(
            environment=dict(
                POSTGRES_PASSWORD="mysecretpassword",
            ),
        )
        return options

    def get_container_options(self, defaults):
        # Default options
        options = self.default_container_options()

        # User environmental variables
        if not defaults:
            write_pretty_output(
                "Tethys uses the postgis/postgis image on Docker Hub. "
                "See: https://hub.docker.com/r/postgis/postgis/"
            )

            # POSTGRES_PASSWORD
            prompt = "Password for postgres user (i.e. POSTGRES_PASSWORD)"
            postgres_password = UserInputHelper.get_verified_password(
                prompt, options["environment"]["POSTGRES_PASSWORD"]
            )

            options["environment"].update(
                POSTGRES_PASSWORD=postgres_password,
            )

        return options


class GeoServerContainerMetadata(ContainerMetadata):
    input = "geoserver"
    name = "tethys_geoserver"
    display_name = "GeoServer"
    image_name = "tethysplatform/geoserver"
    tag = "latest"
    host_port = 8181
    container_port = (
        8080  # only for backwards compatibility with non-clustered containers
    )

    @property
    def endpoint(self):
        return "http://{host}:{port}/geoserver/rest".format(
            host=self.default_host, port=self.host_port
        )

    @property
    def node_ports(self):
        if self.is_cluster:
            return [8081, 8082, 8083, 8084]

    @property
    def port_bindings(self):
        if self.is_cluster:
            port_bindings = {8181: self.host_port}
            port_bindings.update({p: p for p in self.node_ports})
            return port_bindings
        else:
            return super().port_bindings

    @property
    def ip(self):
        if self.is_cluster:
            msg = (
                "\n{name}:"
                "\n  Host: {host}"
                "\n  Primary Port: {port}"
                "\n  Node Ports: {node_ports}"
                "\n  Endpoint: {endpoint}"
            )

            return msg.format(
                name=self.display_name,
                host=self.default_host,
                port=self.host_port,
                node_ports=", ".join([str(i) for i in self.node_ports]),
                endpoint=self.endpoint,
            )
        else:
            return super().ip

    @property
    def installed_image(self):
        return self.image if self.container is None else self.container.image.tags[0]

    @property
    def is_cluster(self):
        return (
            "cluster" in self.installed_image
            or "tethysplatform/geoserver" in self.installed_image
        )

    def default_container_options(self):
        options = super().default_container_options()
        options.update(
            environment=dict(
                ENABLED_NODES="1",
                REST_NODES="1",
                MAX_TIMEOUT="60",
                NUM_CORES="4",
                MAX_MEMORY="1024",
                MIN_MEMORY="1024",
            ),
            volumes=[
                "/var/log/supervisor:rw",
                "/var/geoserver/data:rw",
                "/var/geoserver:rw",
            ],
        )
        return options

    def get_container_options(self, defaults):
        # default configuration
        options = self.default_container_options()

        if not self.is_cluster:
            # Then all of the other options are irrelevant
            defaults = True

        if not defaults:
            # Environmental variables from user input
            environment = dict()

            write_pretty_output(
                "The GeoServer docker can be configured to run in a clustered mode (multiple instances of "
                "GeoServer running in the docker container) for better performance.\n"
            )

            environment["ENABLED_NODES"] = UserInputHelper.get_valid_numeric_input(
                prompt="Number of GeoServer Instances Enabled",
                max_val=4,
            )

            environment["REST_NODES"] = UserInputHelper.get_valid_numeric_input(
                prompt="Number of GeoServer Instances with REST API Enabled",
                max_val=int(environment["ENABLED_NODES"]),
            )

            write_pretty_output(
                "\nGeoServer can be configured with limits to certain types of requests to prevent it from "
                "becoming overwhelmed. This can be done automatically based on a number of processors or "
                "each "
                "limit can be set explicitly.\n"
            )

            flow_control_mode = UserInputHelper.get_valid_choice_input(
                prompt="Would you like to specify number of Processors (c) OR set request limits explicitly (e)",
                choices=["c", "e"],
                default="c",
            )

            if flow_control_mode.lower() == "c":
                environment["NUM_CORES"] = UserInputHelper.get_valid_numeric_input(
                    prompt="Number of Processors",
                    max_val=4,  # TODO dynamically figure out what the max is
                )

            else:
                environment["MAX_OWS_GLOBAL"] = UserInputHelper.get_valid_numeric_input(
                    prompt="Maximum number of simultaneous OGC web service requests (e.g.: WMS, WCS, WFS)",
                    default=100,
                )

                environment["MAX_WMS_GETMAP"] = UserInputHelper.get_valid_numeric_input(
                    prompt="Maximum number of simultaneous GetMap requests", default=8
                )

                environment["MAX_OWS_GWC"] = UserInputHelper.get_valid_numeric_input(
                    prompt="Maximum number of simultaneous GeoWebCache tile renders",
                    default=16,
                )

            environment["MAX_TIMEOUT"] = UserInputHelper.get_valid_numeric_input(
                prompt="Maximum request timeout in seconds", default=60
            )

            environment["MAX_MEMORY"] = UserInputHelper.get_valid_numeric_input(
                prompt="Maximum memory to allocate to each GeoServer instance in MB",
                max_val=4096,  # TODO dynamically figure out what the max is
                default=1024,
            )

            max_memory = int(environment["MAX_MEMORY"])
            environment["MIN_MEMORY"] = UserInputHelper.get_valid_numeric_input(
                prompt="Minimum memory to allocate to each GeoServer instance in MB",
                max_val=max_memory,
                default=max_memory,
            )

            options.update(
                environment=environment,
            )

            mount_data_dir = UserInputHelper.get_valid_choice_input(
                prompt="Bind the GeoServer data directory to the host?",
                choices=["y", "n"],
                default="y",
            )

            if mount_data_dir.lower() == "y":
                tethys_home = get_tethys_home_dir()
                default_mount_location = str(Path(tethys_home) / "geoserver" / "data")
                gs_data_volume = "/var/geoserver/data"
                mount_location = UserInputHelper.get_valid_directory_input(
                    prompt="Specify location to bind data directory",
                    default=default_mount_location,
                )
                mounts = [Mount(gs_data_volume, mount_location, type="bind")]
                options["host_config"].update(mounts=mounts)

        return options


class N52WpsContainerMetadata(ContainerMetadata):
    input = "wps"
    name = "tethys_wps"
    display_name = "52 North WPS"
    image_name = "ciwater/n52wps"
    tag = "3.3.1"
    host_port = 8282
    container_port = 8080

    @property
    def endpoint(self):
        return "http://{host}:{port}/wps/WebProcessingService".format(
            host=self.default_host, port=self.host_port
        )

    def default_container_options(self):
        options = super().default_container_options()
        options.update(
            environment=dict(
                NAME="NONE",
                POSITION="NONE",
                ADDRESS="NONE",
                CITY="NONE",
                STATE="NONE",
                COUNTRY="NONE",
                POSTAL_CODE="NONE",
                EMAIL="NONE",
                PHONE="NONE",
                FAX="NONE",
                USERNAME="wps",
                PASSWORD="wps",
            ),
        )
        return options

    def get_container_options(self, defaults):
        # Default environmental vars
        options = self.default_container_options()

        if not defaults:
            write_pretty_output(
                "Provide contact information for the 52 North Web Processing Service or press enter to "
                "accept the defaults shown in square brackets: "
            )

            options["environment"].update(
                NAME=UserInputHelper.get_input_with_default("Name", "NONE"),
                POSITION=UserInputHelper.get_input_with_default("Position", "NONE"),
                ADDRESS=UserInputHelper.get_input_with_default("Address", "NONE"),
                CITY=UserInputHelper.get_input_with_default("City", "NONE"),
                STATE=UserInputHelper.get_input_with_default("State", "NONE"),
                COUNTRY=UserInputHelper.get_input_with_default("Country", "NONE"),
                POSTAL_CODE=UserInputHelper.get_input_with_default(
                    "Postal Code", "NONE"
                ),
                EMAIL=UserInputHelper.get_input_with_default("Email", "NONE"),
                PHONE=UserInputHelper.get_input_with_default("Phone", "NONE"),
                FAX=UserInputHelper.get_input_with_default("Fax", "NONE"),
                USERNAME=UserInputHelper.get_input_with_default(
                    "Admin Username", "wps"
                ),
                PASSWORD=UserInputHelper.get_verified_password("Admin Password", "wps"),
            )

        return options


class ThreddsContainerMetadata(ContainerMetadata):
    input = "thredds"
    name = "tethys_thredds"
    display_name = "THREDDS"
    image_name = "unidata/thredds-docker"
    tag = "5.6"
    host_port = 8383
    container_port = 8080

    @property
    def endpoint(self):
        return "http://{host}:{port}/thredds/".format(
            host=self.default_host, port=self.host_port
        )

    def default_container_options(self):
        options = super().default_container_options()
        options.update(
            environment=dict(
                TDM_PW="CHANGEME!",
                TDS_HOST="http://localhost",
                THREDDS_XMX_SIZE="4G",
                THREDDS_XMS_SIZE="1G",
                TDM_XMX_SIZE="6G",
                TDM_XMS_SIZE="1G",
            ),
            volumes=["/usr/local/tomcat/content/thredds:rw"],
        )
        return options

    def get_container_options(self, defaults):
        # Default environmental vars
        options = self.default_container_options()

        if not defaults:
            environment = dict()

            write_pretty_output(
                "Provide configuration options for the THREDDS container or or press enter to "
                "accept the defaults shown in square brackets: "
            )

            environment["TDM_PW"] = UserInputHelper.get_verified_password(
                prompt="TDM Password",
                default=options["environment"]["TDM_PW"],
            )

            environment["TDS_HOST"] = UserInputHelper.get_input_with_default(
                prompt="TDS Host",
                default=options["environment"]["TDS_HOST"],
            )

            environment["THREDDS_XMX_SIZE"] = UserInputHelper.get_input_with_default(
                prompt="TDS JVM Max Heap Size",
                default=options["environment"]["THREDDS_XMX_SIZE"],
            )

            environment["THREDDS_XMS_SIZE"] = UserInputHelper.get_input_with_default(
                prompt="TDS JVM Min Heap Size",
                default=options["environment"]["THREDDS_XMS_SIZE"],
            )

            environment["TDM_XMX_SIZE"] = UserInputHelper.get_input_with_default(
                prompt="TDM JVM Max Heap Size",
                default=options["environment"]["TDM_XMX_SIZE"],
            )

            environment["TDM_XMS_SIZE"] = UserInputHelper.get_input_with_default(
                prompt="TDM JVM Min Heap Size",
                default=options["environment"]["TDM_XMS_SIZE"],
            )

            options.update(environment=environment)

            mount_data_dir = UserInputHelper.get_valid_choice_input(
                prompt="Bind the THREDDS data directory to the host?",
                choices=["y", "n"],
                default="y",
            )

            if mount_data_dir.lower() == "y":
                tethys_home = get_tethys_home_dir()
                default_mount_location = str(Path(tethys_home) / "thredds")
                thredds_data_volume = "/usr/local/tomcat/content/thredds"
                mount_location = UserInputHelper.get_valid_directory_input(
                    prompt="Specify location to bind the THREDDS data directory",
                    default=default_mount_location,
                )
                mounts = [Mount(thredds_data_volume, mount_location, type="bind")]
                options["host_config"].update(mounts=mounts)

        return options


docker_container_inputs = [c.input for c in ContainerMetadata.get_containers()]


def get_docker_container_statuses(containers=None):
    """
    Returns a dictionary representing the container status. If a container is included in the dictionary keys, it is
    installed. If its key is not included, it means it is not installed. If its value is False, it is not running.
    If its value is True, it is running.
    """
    # Retrieve a Docker client
    docker_client = ContainerMetadata.get_docker_client()

    containers_metadata = ContainerMetadata.get_containers(containers)
    # Check status of containers
    all_containers = [c.name for c in docker_client.containers.list(all=True)]

    # If in all containers list, assume off (False) until verified in running containers list
    container_statuses = {
        c: False if c.name in all_containers else None for c in containers_metadata
    }

    # Verify running containers
    running_containers = [c.name for c in docker_client.containers.list()]
    container_statuses.update(
        {c: True for c in container_statuses.keys() if c.name in running_containers}
    )

    return container_statuses


def pull_docker_images(containers_to_install):
    """
    Pull Docker container images

    Args:
        containers_to_install(list[ContainerMetadata], required):
            list of containers to install
    """
    if len(containers_to_install) < 1:
        write_pretty_output("Docker images already pulled.")
    else:
        write_pretty_output("Pulling Docker images...")

    for container in containers_to_install:
        container.pull()


def install_docker_containers(containers_to_install, defaults=False):
    """
    Install all Docker containers

    Args:
        containers_to_install(list[ContainerMetadata], required):
            list of containers to install
        defaults(bool, optional, default=False):
            if True use all of the default options instead of prompting user to specify options
    """
    for container_metadata in containers_to_install:
        container_metadata.create(defaults)

    write_pretty_output("Finished installing Docker containers.")


def validate_args(args):
    # Image and tag options are only valid for init and update commands
    if (args.image_name or args.image_tag) and args.command not in ("init", "update"):
        write_warning(
            'WARNING: The image name and tag options are only used by the "init" and "update" commands.'
        )

    # Image and tag options are only valid when operating on a single container
    if (args.image_name or args.image_tag) and len(args.containers) > 1:
        write_error(
            "ERROR: The image name and tag options are only valid for operations on a single container."
            'Use the "-c" or "--containers" option to specify a single container to operate on.'
        )
        write_error(
            '       Use the "-c" or "--containers" option to specify a single container to operate on.'
        )
        exit(1)


def docker_init(
    containers=None, defaults=False, force=False, image_name=None, image_tag=None
):
    """
    Pull Docker images for Tethys Platform and create containers with interactive input.
    """
    # Get containers to install
    installed = None if force else False

    # only get containers that are not installed unless forcing to get all
    containers_to_install = ContainerMetadata.get_containers(
        containers, installed=installed, image_name=image_name, image_tag=image_tag
    )

    # Pull the Docker images
    pull_docker_images(containers_to_install)

    # Install docker containers
    install_docker_containers(containers_to_install, defaults=defaults)


def docker_start(containers=None):
    """
    Start the docker containers
    """
    container_statuses = get_docker_container_statuses(containers=containers)

    for container_metadata, status in container_statuses.items():
        already_running = status

        if already_running is None:
            msg = "{} container not installed."
        elif already_running:
            msg = "{} container already running."
        else:
            msg = container_metadata.start()

        if msg is not None:
            write_pretty_output(msg.format(container_metadata.display_name))


def docker_stop(containers=None):
    """
    Stop Docker containers
    """
    container_statuses = get_docker_container_statuses(containers=containers)

    for container_metadata, status in container_statuses.items():
        already_stopped = not status
        if status is None:
            msg = "{} container not installed."
        elif already_stopped:
            msg = "{} container already stopped."
        else:
            msg = container_metadata.stop()

        if msg is not None:
            write_pretty_output(msg.format(container_metadata.display_name))


def docker_restart(containers=None):
    """
    Restart Docker containers
    """
    # Stop the Docker containers
    docker_stop(containers=containers)

    # Start the Docker containers
    docker_start(containers=containers)


def docker_remove(containers=None):
    """
    Remove Docker containers.
    """
    # Stop the Docker containers
    docker_stop(containers=containers)

    # Remove Docker containers
    containers_to_remove = ContainerMetadata.get_containers(containers, installed=True)

    for container in containers_to_remove:
        container.remove()


def docker_status(containers=None):
    """
    Returns the status of the Docker containers: either Running or Stopped.
    """
    # Get container dicts
    container_statuses = get_docker_container_statuses(containers=containers)

    for container, is_running in container_statuses.items():
        if is_running is None:
            msg = "{}: Not Installed"
        elif is_running:
            msg = "{}: Running"
        else:
            msg = "{}: Not Running"
        write_pretty_output(msg.format(container.display_name))


def docker_update(containers=None, defaults=False, image_name=None, image_tag=None):
    """
    Remove Docker containers and pull the latest images updates.
    """
    # Remove containers
    docker_remove(containers=containers)

    # Re-initialize docker containers
    docker_init(
        containers=containers,
        defaults=defaults,
        force=True,
        image_name=image_name,
        image_tag=image_tag,
    )


def docker_ip(containers=None):
    """
    Returns the hosts and ports of the Docker containers.
    """
    # Containers
    container_statuses = get_docker_container_statuses(containers=containers)

    for container_metadata, is_running in container_statuses.items():
        if is_running is None:
            msg = "{name}: Not Installed"
        elif not is_running:
            msg = "{name}: Not Running"
        else:
            msg = container_metadata.ip

        write_pretty_output(msg.format(name=container_metadata.display_name))


def docker_command(args):
    """
    Docker management commands.
    """
    validate_args(args)

    if args.command == "init":
        docker_init(
            containers=args.containers,
            defaults=args.defaults,
            image_name=args.image_name,
            image_tag=args.image_tag,
        )

    elif args.command == "start":
        docker_start(containers=args.containers)

    elif args.command == "stop":
        docker_stop(containers=args.containers)

    elif args.command == "status":
        docker_status(containers=args.containers)

    elif args.command == "update":
        docker_update(
            containers=args.containers,
            defaults=args.defaults,
            image_name=args.image_name,
            image_tag=args.image_tag,
        )

    elif args.command == "remove":
        docker_remove(containers=args.containers)

    elif args.command == "ip":
        docker_ip(containers=args.containers)

    elif args.command == "restart":
        docker_restart(containers=args.containers)


class UserInputHelper:
    @staticmethod
    def get_input_with_default(prompt, default):
        prompt = "{} [{}]:".format(prompt, default)
        return input(prompt) or default

    @staticmethod
    def get_verified_password(prompt, default):
        password_1 = getpass.getpass("{} [{}]: ".format(prompt, default))

        if password_1 == "":
            return default

        else:
            password_2 = getpass.getpass("Confirm Password: ")

            while password_1 != password_2:
                write_pretty_output("Passwords do not match, please try again.")
                password_1 = getpass.getpass("{} [{}]: ".format(prompt, default))
                password_2 = getpass.getpass("Confirm Password: ")

            return password_1

    @staticmethod
    def get_valid_numeric_input(prompt, min_val=1, max_val=None, default=None):
        default = default or min_val
        pre_prompt = ""
        max_prompt = " (max {})".format(max_val) if max_val is not None else ""
        prompt = "{}{} [{}]: ".format(prompt, max_prompt, default)
        while True:
            value = input("{}{}".format(pre_prompt, prompt)) or str(default)
            try:
                value = int(value)
            except ValueError:
                pre_prompt = "Please enter an integer number\n"
                continue

            temp_max = max_val or value
            if value > temp_max or value < min_val:
                pre_prompt = "Number must be between {} and {}\n".format(
                    min_val, max_val
                )
                continue
            break
        return value

    @staticmethod
    def get_valid_choice_input(prompt, choices, default=None):
        choices = list(map(str.lower, choices))
        default = default.lower() or choices[0]
        choices.remove(default)
        choices.insert(0, default)
        pre_prompt = ""
        prompt = "{} [{}]: ".format(prompt, "/".join(choices).capitalize())
        while True:
            value = input("{}{}".format(pre_prompt, prompt)) or str(default)
            value = value.lower()
            if value in choices:
                break

            pre_prompt = "Please provide a valid option\n"

        return value

    @staticmethod
    def get_valid_directory_input(prompt, default=None):
        default = default or ""
        pre_prompt = ""
        prompt = "{} [{}]: ".format(prompt, default)
        while True:
            raw_value = input("{}{}".format(pre_prompt, prompt)) or str(default)
            path = Path(raw_value)

            if len(raw_value) > 0 and not path.is_absolute():
                path = path.absolute()

            if not path.is_dir():
                try:
                    path.mkdir(parents=True)
                except OSError as e:
                    write_pretty_output("{0}: {1}".format(repr(e), path))
                    pre_prompt = "Please provide a valid directory\n"
                    continue

            break

        return str(path)


def log_pull_stream(stream):
    """
    Handle the printing of pull statuses
    """
    if not has_module(curses):
        for block in stream:
            lines = [line for line in block.split(b"\r\n") if line]
            for line in lines:
                json_line = json.loads(line)
                current_id = "{}:".format(json_line["id"]) if "id" in json_line else ""
                current_status = json_line["status"] if "status" in json_line else ""
                current_progress = (
                    json_line["progress"] if "progress" in json_line else ""
                )

                write_pretty_output(
                    "{id}{status} {progress}".format(
                        id=current_id, status=current_status, progress=current_progress
                    )
                )
    else:
        TERMINAL_STATUSES = ["Already exists", "Download complete", "Pull complete"]
        PROGRESS_STATUSES = ["Downloading", "Extracting"]
        STATUSES = (
            TERMINAL_STATUSES
            + PROGRESS_STATUSES
            + ["Pulling fs layer", "Waiting", "Verifying Checksum"]
        )

        NUMBER_OF_HEADER_ROWS = 2

        header_rows = list()
        message_log = list()
        progress_messages = dict()
        messages_to_print = list()

        # prepare console for curses window printing
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()

        try:
            for block in stream:
                lines = [line for line in block.split(b"\r\n") if line]
                for line in lines:
                    json_line = json.loads(line)
                    current_id = json_line["id"] if "id" in json_line else None
                    current_status = (
                        json_line["status"] if "status" in json_line else ""
                    )
                    current_progress = (
                        json_line["progress"] if "progress" in json_line else ""
                    )

                    if current_id is None:
                        # save messages to print after docker images are pulled
                        messages_to_print.append(current_status.strip())
                    else:
                        # use curses window to properly display progress
                        if current_status not in STATUSES:  # Assume this is the header
                            header_rows.append(current_status)
                            header_rows.append("-" * len(current_status))

                        elif current_status in PROGRESS_STATUSES:
                            # add messages with progress to dictionary to print at the bottom of the screen
                            progress_messages[current_id] = {
                                "id": current_id,
                                "status": current_status,
                                "progress": current_progress,
                            }
                        else:
                            # add all other messages to list to show above progress messages
                            message_log.append(
                                "{id}: {status} {progress}".format(
                                    id=current_id,
                                    status=current_status,
                                    progress=current_progress,
                                )
                            )

                            # remove messages from progress that have completed
                            if current_id in progress_messages:
                                del progress_messages[current_id]

                        # update window

                        # row/column calculations for proper display on screen
                        maxy, maxx = stdscr.getmaxyx()
                        number_of_rows, number_of_columns = maxy, maxx

                        current_progress_messages = sorted(
                            progress_messages.values(),
                            key=lambda message: STATUSES.index(message["status"]),
                        )

                        # row/column calculations for proper display on screen
                        number_of_progress_rows = len(current_progress_messages)
                        number_of_message_rows = (
                            number_of_rows
                            - number_of_progress_rows
                            - NUMBER_OF_HEADER_ROWS
                        )

                        # slice messages to only those that will fit on the screen
                        current_messages = [""] * number_of_message_rows + message_log
                        current_messages = current_messages[-number_of_message_rows:]

                        rows = (
                            header_rows
                            + current_messages
                            + [
                                "{id}: {status} {progress}".format(**current_message)
                                for current_message in current_progress_messages
                            ]
                        )

                        for row, message in enumerate(rows):
                            message += " " * number_of_columns
                            message = message[: number_of_columns - 1]
                            try:
                                stdscr.addstr(row, 0, message)
                            except curses.error:
                                pass

                        stdscr.refresh()

        finally:  # always reset console to normal regardless of success or failure
            curses.echo()
            curses.nocbreak()
            curses.endwin()

        write_pretty_output("\n".join(messages_to_print))
