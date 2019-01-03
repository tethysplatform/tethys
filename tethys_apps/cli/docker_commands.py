"""
********************************************************************************
* Name: docker_commands.py
* Author: Nathan Swain
* Created On: July 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
try:
    import curses
except Exception:
    pass  # curses not available on Windows
from builtins import input
import platform
import subprocess
from subprocess import PIPE
import os
import json
import getpass
from functools import cmp_to_key
from docker.utils import kwargs_from_env, compare_version, create_host_config
from docker.client import Client as DockerClient
from docker.constants import DEFAULT_DOCKER_API_VERSION as MAX_CLIENT_DOCKER_API_VERSION
from tethys_apps.cli.cli_colors import pretty_output, FG_WHITE


__all__ = ['docker_init', 'docker_start',
           'docker_stop', 'docker_status',
           'docker_update', 'docker_remove',
           'docker_ip', 'docker_restart',
           'POSTGIS_INPUT', 'GEOSERVER_INPUT', 'N52WPS_INPUT']

MINIMUM_API_VERSION = '1.12'

OSX = 1
WINDOWS = 2
LINUX = 3

POSTGIS_IMAGE = 'ciwater/postgis:2.1.2'
GEOSERVER_IMAGE = 'ciwater/geoserver:2.8.2-clustered'
N52WPS_IMAGE = 'ciwater/n52wps:3.3.1'

REQUIRED_DOCKER_IMAGES = [POSTGIS_IMAGE,
                          GEOSERVER_IMAGE,
                          N52WPS_IMAGE]

POSTGIS_CONTAINER = 'tethys_postgis'
GEOSERVER_CONTAINER = 'tethys_geoserver'
N52WPS_CONTAINER = 'tethys_wps'

POSTGIS_INPUT = 'postgis'
GEOSERVER_INPUT = 'geoserver'
N52WPS_INPUT = 'wps'

ALL_DOCKER_INPUTS = (POSTGIS_INPUT, GEOSERVER_INPUT, N52WPS_INPUT)

DEFAULT_POSTGIS_PORT = '5435'
DEFAULT_GEOSERVER_PORT = '8181'
DEFAULT_N52WPS_PORT = '8282'

REQUIRED_DOCKER_CONTAINERS = [POSTGIS_CONTAINER,
                              GEOSERVER_CONTAINER,
                              N52WPS_CONTAINER]

DEFAULT_DOCKER_HOST = '127.0.0.1'


def add_max_to_prompt(prompt, max):
    if max is not None:
        prompt += ' (max {0})'.format(max)
    return prompt


def add_default_to_prompt(prompt, default, choices=None):
    if default is not None:
        if choices is not None:
            # Remove default choice from choices and lower case remaining options
            lower_choices = [choice.lower() for choice in choices]
            for index, choice in enumerate(lower_choices):
                if choice.lower() == default.lower():
                    lower_choices.pop(index)

            prompt += ' [{0}/{1}]'.format(default.title(), '/'.join(lower_choices))
        else:
            prompt += ' [{0}]'.format(default)
    return prompt


def close_prompt(prompt):
    prompt += ': '
    return prompt


def validate_numeric_cli_input(value, default=None, max=None):
    if default is not None and value == '':
        return str(default)

    valid = False
    while not valid:
        if default is not None and value == '':
            return str(default)

        try:
            float(value)

        except ValueError:
            prompt = 'Please enter a number'
            prompt = add_max_to_prompt(prompt, max)
            prompt = add_default_to_prompt(prompt, default)
            prompt = close_prompt(prompt)
            value = input(prompt)
            continue

        if max is not None:
            if float(value) > float(max):
                if default is not None:
                    value = input('Maximum allowed value is {0} [{1}]: '.format(max, default))
                else:
                    value = input('Maximum allowed value is {0}: '.format(max))
                continue
        valid = True
    return value


def validate_choice_cli_input(value, choices, default=None):
    if default is not None and value == '':
        return str(default)

    while value.lower() not in choices:
        if default is not None and value == '':
            return str(default)

        prompt = 'Please provide a valid option'
        prompt = add_default_to_prompt(prompt, default, choices)
        prompt = close_prompt(prompt)
        value = input(prompt)

    return value


def validate_directory_cli_input(value, default=None):
    valid = False
    while not valid:
        if default is not None and value == '':
            value = str(default)

        if len(value) > 0 and value[0] != '/':
            value = '/' + value

        if not os.path.isdir(value):
            try:
                os.makedirs(value)
            except OSError as e:
                with pretty_output(FG_WHITE) as p:
                    p.write('{0}: {1}'.format(repr(e), value))
                prompt = 'Please provide a valid directory'
                prompt = add_default_to_prompt(prompt, default)
                prompt = close_prompt(prompt)
                value = input(prompt)
                continue

        valid = True

    return value


def get_api_version(*versions):
    """
    Find the right version of the client to use.
    credits: @kevinastone https://github.com/docker/docker-py/issues/439
    """
    # compare_version is backwards
    def cmp(a, b):
        return -1 * compare_version(a, b)
    return min(versions, key=cmp_to_key(cmp))


def get_docker_client():
    """
    Try to fire up boot2docker and set any environmental variables
    """
    # For Mac
    try:
        # Get boot2docker info (will fail if not Mac)
        process = ['boot2docker', 'info']
        p = subprocess.Popen(process, stdout=PIPE)
        boot2docker_info = json.loads(p.communicate()[0])

        # Defaults
        docker_host = ''
        docker_cert_path = ''
        docker_tls_verify = ''

        # Start the boot2docker VM if it is not already running
        if boot2docker_info['State'] != "running":
            with pretty_output(FG_WHITE) as p:
                p.write('Starting Boot2Docker VM:')
            # Start up the Docker VM
            process = ['boot2docker', 'start']
            subprocess.call(process)

        if ('DOCKER_HOST' not in os.environ) or ('DOCKER_CERT_PATH' not in os.environ) or \
                ('DOCKER_TLS_VERIFY' not in os.environ):
            # Get environmental variable values
            process = ['boot2docker', 'shellinit']
            p = subprocess.Popen(process, stdout=PIPE)
            boot2docker_envs = p.communicate()[0].split()

            for env in boot2docker_envs:
                if 'DOCKER_HOST' in env:
                    docker_host = env.split('=')[1]
                elif 'DOCKER_CERT_PATH' in env:
                    docker_cert_path = env.split('=')[1]
                elif 'DOCKER_TLS_VERIFY' in env:
                    docker_tls_verify = env.split('=')[1]

            # Set environmental variables
            os.environ['DOCKER_TLS_VERIFY'] = docker_tls_verify
            os.environ['DOCKER_HOST'] = docker_host
            os.environ['DOCKER_CERT_PATH'] = docker_cert_path
        else:
            # Handle case when boot2docker is already running
            docker_host = os.environ['DOCKER_HOST'].split('=')[1]

        # Get the arguments form the environment
        client_kwargs = kwargs_from_env(assert_hostname=False)
        client_kwargs['version'] = MINIMUM_API_VERSION

        # Find the right version of the API by creating a DockerClient with the minimum working version
        # Then test to see if the Docker is running a later version than the minimum
        # See: https://github.com/docker/docker-py/issues/439
        version_client = DockerClient(**client_kwargs)
        client_kwargs['version'] = get_api_version(MAX_CLIENT_DOCKER_API_VERSION,
                                                   version_client.version()['ApiVersion'])

        # Create Real Docker client
        docker_client = DockerClient(**client_kwargs)

        # Derive the host address only from string formatted: "tcp://<host>:<port>"
        docker_client.host = docker_host.split(':')[1].strip('//')

        return docker_client

    # For Linux
    except OSError:
        # Find the right version of the API by creating a DockerClient with the minimum working version
        # Then test to see if the Docker is running a later version than the minimum
        # See: https://github.com/docker/docker-py/issues/439
        version_client = DockerClient(base_url='unix://var/run/docker.sock', version=MINIMUM_API_VERSION)
        version = get_api_version(MAX_CLIENT_DOCKER_API_VERSION, version_client.version()['ApiVersion'])
        docker_client = DockerClient(base_url='unix://var/run/docker.sock', version=version)
        docker_client.host = DEFAULT_DOCKER_HOST

        return docker_client


def stop_boot2docker():
    """
    Shut down boot2docker if applicable
    """
    try:
        process = ['boot2docker', 'stop']
        subprocess.call(process)
        with pretty_output(FG_WHITE) as p:
            p.write('Boot2Docker VM Stopped')
    except OSError:
        pass


def get_images_to_install(docker_client, containers=ALL_DOCKER_INPUTS):
    """
    Get a list of the Docker images that are not already installed/pulled.

    Args:
      docker_client(docker.client.Client): docker-py client.

    Returns:
      (list): A list of the image tags that need to be installed.
    """
    # Get list of images
    images_to_install = []
    for container in containers:
        if container == POSTGIS_INPUT:
            images_to_install.append(POSTGIS_IMAGE)
        elif container == GEOSERVER_INPUT:
            images_to_install.append(GEOSERVER_IMAGE)
        elif container == N52WPS_INPUT:
            images_to_install.append(N52WPS_IMAGE)

    # Search through all the images already installed (pulled) and pop them off the list
    images = docker_client.images()
    for image in images:
        tags = image['RepoTags']

        for image_to_install in images_to_install:
            if image_to_install in tags:
                images_to_install.pop(images_to_install.index(image_to_install))

    return images_to_install


def get_containers_to_create(docker_client, containers=ALL_DOCKER_INPUTS):
    """
    Get a list of containers that need to be created.
    """
    # All assumed to need creating by default
    containers_to_create = []
    for container in containers:
        if container == POSTGIS_INPUT:
            containers_to_create.append(POSTGIS_CONTAINER)
        elif container == GEOSERVER_INPUT:
            containers_to_create.append(GEOSERVER_CONTAINER)
        elif container == N52WPS_INPUT:
            containers_to_create.append(N52WPS_CONTAINER)

    # Create containers for each image if not done already
    containers = docker_client.containers(all=True)

    for c in containers:
        names = c['Names']

        for container_to_create in containers_to_create:
            if '/' + container_to_create in names:
                containers_to_create.pop(containers_to_create.index(container_to_create))

    return containers_to_create


def log_pull_stream(stream):
    """
    Handle the printing of pull statuses
    """

    if platform.system() == 'Windows':  # i.e. can't uses curses
        for block in stream:
            lines = [l for l in block.split('\r\n') if l]
            for line in lines:
                json_line = json.loads(line)
                current_id = "{}:".format(json_line['id']) if 'id' in json_line else ''
                current_status = json_line['status'] if 'status' in json_line else ''
                current_progress = json_line['progress'] if 'progress' in json_line else ''

                with pretty_output(FG_WHITE) as p:
                    p.write("{id}{status} {progress}".format(
                        id=current_id,
                        status=current_status,
                        progress=current_progress
                    ))
    else:

        TERMINAL_STATUSES = ['Already exists', 'Download complete', 'Pull complete']
        PROGRESS_STATUSES = ['Downloading', 'Extracting']
        STATUSES = TERMINAL_STATUSES + PROGRESS_STATUSES + ['Pulling fs layer', 'Waiting', 'Verifying Checksum']

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
                lines = [l for l in block.split('\r\n') if l]
                for line in lines:
                    json_line = json.loads(line)
                    current_id = json_line['id'] if 'id' in json_line else None
                    current_status = json_line['status'] if 'status' in json_line else ''
                    current_progress = json_line['progress'] if 'progress' in json_line else ''

                    if current_id is None:
                        # save messages to print after docker images are pulled
                        messages_to_print.append(current_status.strip())
                    else:
                        # use curses window to properly display progress
                        if current_status not in STATUSES:  # Assume this is the header
                            header_rows.append(current_status)
                            header_rows.append('-' * len(current_status))

                        elif current_status in PROGRESS_STATUSES:
                                # add messages with progress to dictionary to print at the bottom of the screen
                                progress_messages[current_id] = {'id': current_id, 'status': current_status,
                                                                 'progress': current_progress}
                        else:
                            # add all other messages to list to show above progress messages
                            message_log.append("{id}: {status} {progress}".format(
                                id=current_id,
                                status=current_status,
                                progress=current_progress
                            ))

                            # remove messages from progress that have completed
                            if current_id in progress_messages:
                                del progress_messages[current_id]

                        # update window

                        # row/column calculations for proper display on screen
                        maxy, maxx = stdscr.getmaxyx()
                        number_of_rows, number_of_columns = maxy, maxx

                        current_progress_messages = sorted(progress_messages.values(),
                                                           key=lambda message: STATUSES.index(message['status']))

                        # row/column calculations for proper display on screen
                        number_of_progress_rows = len(current_progress_messages)
                        number_of_message_rows = number_of_rows - number_of_progress_rows - NUMBER_OF_HEADER_ROWS

                        # slice messages to only those that will fit on the screen
                        current_messages = [''] * number_of_message_rows + message_log
                        current_messages = current_messages[-number_of_message_rows:]

                        rows = header_rows + current_messages + ['{id}: {status} {progress}'.format(**current_message)
                                                                 for current_message in current_progress_messages]

                        for row, message in enumerate(rows):
                            message += ' ' * number_of_columns
                            message = message[:number_of_columns - 1]
                            stdscr.addstr(row, 0, message)

                        stdscr.refresh()

        finally:  # always reset console to normal regardless of success or failure
            curses.echo()
            curses.nocbreak()
            curses.endwin()

        with pretty_output(FG_WHITE) as p:
            p.write('\n'.join(messages_to_print))


def get_docker_container_dicts(docker_client):
    # Check status of containers
    containers = docker_client.containers(all=True)
    container_dicts = dict()

    for container in containers:

        if '/' + POSTGIS_CONTAINER in container['Names']:
            container_dicts[POSTGIS_CONTAINER] = container

        elif '/' + GEOSERVER_CONTAINER in container['Names']:
            container_dicts[GEOSERVER_CONTAINER] = container

        elif '/' + N52WPS_CONTAINER in container['Names']:
            container_dicts[N52WPS_CONTAINER] = container

    return container_dicts


def get_docker_container_image(docker_client):
    """
    Returns a dictionary containing the image each existing container.
    """
    containers = docker_client.containers(all=True)
    images = dict()

    for container in containers:
        names = container['Names']
        image = container['Image']

        for name in names:
            # Container names have a slash before them like this: "/tethys_geoserver"
            if GEOSERVER_CONTAINER == name[1:]:
                images[GEOSERVER_CONTAINER] = image
            elif POSTGIS_CONTAINER == name[1:]:
                images[POSTGIS_CONTAINER] = image
            elif N52WPS_CONTAINER == name[1:]:
                images[N52WPS_CONTAINER] = image
    return images


def get_docker_container_status(docker_client):
    """
    Returns a dictionary representing the container status. If a container is included in the dictionary keys, it is
    installed. If its key is not included, it means it is not installed. If its value is False, it is not running.
    If its value is True, it is running.
    """
    # Check status of containers
    containers = docker_client.containers()
    all_containers = docker_client.containers(all=True)
    container_status = dict()

    # If in all containers list, assume off (False) until verified in only running containers list
    for container in all_containers:
        if '/' + POSTGIS_CONTAINER in container['Names']:
            container_status[POSTGIS_CONTAINER] = False

        elif '/' + GEOSERVER_CONTAINER in container['Names']:
            container_status[GEOSERVER_CONTAINER] = False

        elif '/' + N52WPS_CONTAINER in container['Names']:
            container_status[N52WPS_CONTAINER] = False

    # Verify running containers
    for container in containers:

        if '/' + POSTGIS_CONTAINER in container['Names']:
            container_status[POSTGIS_CONTAINER] = True

        elif '/' + GEOSERVER_CONTAINER in container['Names']:
            container_status[GEOSERVER_CONTAINER] = True

        elif '/' + N52WPS_CONTAINER in container['Names']:
            container_status[N52WPS_CONTAINER] = True

    return container_status


def install_docker_containers(docker_client, force=False, containers=ALL_DOCKER_INPUTS, defaults=False):
    """
    Install all Docker containers
    """
    # Check for containers that need to be created
    containers_to_create = get_containers_to_create(docker_client, containers=containers)

    # PostGIS
    if POSTGIS_CONTAINER in containers_to_create or force:
        with pretty_output(FG_WHITE) as p:
            p.write("\nInstalling the PostGIS Docker container...")

        # Default environmental vars
        tethys_default_pass = 'pass'
        tethys_db_manager_pass = 'pass'
        tethys_super_pass = 'pass'

        # User environmental variables
        if not defaults:
            with pretty_output(FG_WHITE) as p:
                p.write("Provide passwords for the three Tethys database users or press enter to accept the default "
                        "passwords shown in square brackets:")

            # tethys_default
            tethys_default_pass_1 = getpass.getpass('Password for "tethys_default" database user [pass]: ')

            if tethys_default_pass_1 != '':
                tethys_default_pass_2 = getpass.getpass('Confirm password for "tethys_default" database user: ')

                while tethys_default_pass_1 != tethys_default_pass_2:
                    with pretty_output(FG_WHITE) as p:
                        p.write('Passwords do not match, please try again: ')
                    tethys_default_pass_1 = getpass.getpass('Password for "tethys_default" database user [pass]: ')
                    tethys_default_pass_2 = getpass.getpass('Confirm password for "tethys_default" database user: ')

                tethys_default_pass = tethys_default_pass_1
            else:
                tethys_default_pass = 'pass'

            # tethys_db_manager
            tethys_db_manager_pass_1 = getpass.getpass('Password for "tethys_db_manager" database user [pass]: ')

            if tethys_db_manager_pass_1 != '':
                tethys_db_manager_pass_2 = getpass.getpass('Confirm password for "tethys_db_manager" database user: ')

                while tethys_db_manager_pass_1 != tethys_db_manager_pass_2:
                    with pretty_output(FG_WHITE) as p:
                        p.write('Passwords do not match, please try again: ')
                    tethys_db_manager_pass_1 = getpass.getpass('Password for "tethys_db_manager" database user '
                                                               '[pass]: ')
                    tethys_db_manager_pass_2 = getpass.getpass('Confirm password for "tethys_db_manager" database '
                                                               'user: ')

                tethys_db_manager_pass = tethys_db_manager_pass_1
            else:
                tethys_db_manager_pass = 'pass'

            # tethys_super
            tethys_super_pass_1 = getpass.getpass('Password for "tethys_super" database user [pass]: ')

            if tethys_super_pass_1 != '':
                tethys_super_pass_2 = getpass.getpass('Confirm password for "tethys_super" database user: ')

                while tethys_super_pass_1 != tethys_super_pass_2:
                    with pretty_output(FG_WHITE) as p:
                        p.write('Passwords do not match, please try again: ')
                    tethys_super_pass_1 = getpass.getpass('Password for "tethys_super" database user [pass]: ')
                    tethys_super_pass_2 = getpass.getpass('Confirm password for "tethys_super" database user: ')

                tethys_super_pass = tethys_super_pass_1
            else:
                tethys_super_pass = 'pass'

        docker_client.create_container(
            name=POSTGIS_CONTAINER,
            image=POSTGIS_IMAGE,
            environment={'TETHYS_DEFAULT_PASS': tethys_default_pass,
                         'TETHYS_DB_MANAGER_PASS': tethys_db_manager_pass,
                         'TETHYS_SUPER_PASS': tethys_super_pass}
        )

    # GeoServer
    if GEOSERVER_CONTAINER in containers_to_create or force:
        with pretty_output(FG_WHITE) as p:
            p.write("\nInstalling the GeoServer Docker container...")

        if "cluster" in GEOSERVER_IMAGE:

            if not defaults:
                # Environmental variables from user input
                environment = dict()

                with pretty_output(FG_WHITE) as p:
                    p.write("The GeoServer docker can be configured to run in a clustered mode (multiple instances of "
                            "GeoServer running in the docker container) for better performance.\n")

                enabled_nodes = input('Number of GeoServer Instances Enabled (max 4) [1]: ')
                environment['ENABLED_NODES'] = validate_numeric_cli_input(enabled_nodes, 1, 4)

                max_rest_nodes = enabled_nodes if enabled_nodes else 1
                rest_nodes = input('Number of GeoServer Instances with REST API Enabled (max {0}) [1]: '.format(
                    max_rest_nodes))
                environment['REST_NODES'] = validate_numeric_cli_input(rest_nodes, 1, max_rest_nodes)

                with pretty_output(FG_WHITE) as p:
                    p.write("\nGeoServer can be configured with limits to certain types of requests to prevent it from "
                            "becoming overwhelmed. This can be done automatically based on a number of processors or "
                            "each "
                            "limit can be set explicitly.\n")

                flow_control_mode = input('Would you like to specify number of Processors (c) OR set '
                                          'limits explicitly (e) [C/e]: ')
                flow_control_mode = validate_choice_cli_input(flow_control_mode, ['c', 'e'], 'c')

                if flow_control_mode.lower() == 'c':
                    num_cores = input('Number of Processors [4]: ')
                    environment['NUM_CORES'] = validate_numeric_cli_input(num_cores, '4')

                else:
                    max_ows_global = input('Maximum number of simultaneous OGC web service requests '
                                           '(e.g.: WMS, WCS, WFS) [100]: ')
                    environment['MAX_OWS_GLOBAL'] = validate_numeric_cli_input(max_ows_global, '100')

                    max_wms_getmap = input('Maximum number of simultaneous GetMap requests [8]: ')
                    environment['MAX_WMS_GETMAP'] = validate_numeric_cli_input(max_wms_getmap, '8')

                    max_ows_gwc = input('Maximum number of simultaneous GeoWebCache tile renders [16]: ')
                    environment['MAX_OWS_GWC'] = validate_numeric_cli_input(max_ows_gwc, '16')

                max_timeout = input('Maximum request timeout in seconds [60]: ')
                environment['MAX_TIMEOUT'] = validate_numeric_cli_input(max_timeout, '60')

                max_memory = input('Maximum memory to allocate to each GeoServer instance in MB '
                                   '(max 4096) [1024]: ')
                max_memory = validate_numeric_cli_input(max_memory, '1024', max='4096')
                environment['MAX_MEMORY'] = max_memory
                min_memory = input('Minimum memory to allocate to each GeoServer instance in MB '
                                   '(max {0}) [{0}]: '.format(max_memory))
                environment['MIN_MEMORY'] = validate_numeric_cli_input(min_memory, max_memory, max=int(max_memory))

                mount_data_dir = input('Bind the GeoServer data directory to the host? [Y/n]: ')
                mount_data_dir = validate_choice_cli_input(mount_data_dir, ['y', 'n'], 'y')

                if mount_data_dir.lower() == 'y':
                    default_mount_location = os.path.expanduser('~/tethys/geoserver/data')
                    gs_data_volume = '/var/geoserver/data'
                    mount_location = input('Specify location to bind data directory '
                                           '[{0}]: '.format(default_mount_location))
                    mount_location = validate_directory_cli_input(mount_location, default_mount_location)
                    host_config = create_host_config(
                        binds=[
                            ':'.join([mount_location, gs_data_volume])
                        ]
                    )

                    docker_client.create_container(
                        name=GEOSERVER_CONTAINER,
                        image=GEOSERVER_IMAGE,
                        environment=environment,
                        volumes=['/var/log/supervisor', '/var/geoserver/data', '/var/geoserver'],
                        host_config=host_config,
                    )
                else:
                    docker_client.create_container(
                        name=GEOSERVER_CONTAINER,
                        image=GEOSERVER_IMAGE,
                        environment=environment,
                        volumes=['/var/log/supervisor', '/var/geoserver/data', '/var/geoserver'],
                    )

            else:
                # Default environmental variables
                environment = {
                    'ENABLED_NODES': '1',
                    'REST_NODES': '1',
                    'MAX_TIMEOUT': '60',
                    'NUM_CORES': '4',
                    'MAX_MEMORY': '1024',
                    'MIN_MEMORY': '1024',
                }

                host_config = create_host_config(
                    binds=[
                        '/usr/lib/tethys/geoserver/data:/var/geoserver/data'
                    ]
                )

                docker_client.create_container(
                    name=GEOSERVER_CONTAINER,
                    image=GEOSERVER_IMAGE,
                    environment=environment,
                    volumes=['/var/log/supervisor', '/var/geoserver/data', '/var/geoserver'],
                    host_config=host_config
                )
        else:
            pass
            docker_client.create_container(
                name=GEOSERVER_CONTAINER,
                image=GEOSERVER_IMAGE
            )

    # 52 North WPS
    if N52WPS_CONTAINER in containers_to_create or force:
        with pretty_output(FG_WHITE) as p:
            p.write("\nInstalling the 52 North WPS Docker container...")

        # Default environmental vars
        name = 'NONE'
        position = 'NONE'
        address = 'NONE'
        city = 'NONE'
        state = 'NONE'
        country = 'NONE'
        postal_code = 'NONE'
        email = 'NONE'
        phone = 'NONE'
        fax = 'NONE'
        username = 'wps'
        password = 'wps'

        if not defaults:
            with pretty_output(FG_WHITE) as p:
                p.write("Provide contact information for the 52 North Web Processing Service or press enter to accept "
                        "the defaults shown in square brackets: ")

            name = input('Name [NONE]: ')
            if name == '':
                name = 'NONE'

            position = input('Position [NONE]: ')
            if position == '':
                position = 'NONE'

            address = input('Address [NONE]: ')
            if address == '':
                address = 'NONE'

            city = input('City [NONE]: ')
            if city == '':
                city = 'NONE'

            state = input('State [NONE]: ')
            if state == '':
                state = 'NONE'

            country = input('Country [NONE]: ')
            if country == '':
                country = 'NONE'

            postal_code = input('Postal Code [NONE]: ')
            if postal_code == '':
                postal_code = 'NONE'

            email = input('Email [NONE]: ')
            if email == '':
                email = 'NONE'

            phone = input('Phone [NONE]: ')
            if phone == '':
                phone = 'NONE'

            fax = input('Fax [NONE]: ')
            if fax == '':
                fax = 'NONE'

            username = input('Admin Username [wps]: ')

            if username == '':
                username = 'wps'

            password_1 = getpass.getpass('Admin Password [wps]: ')

            if password_1 == '':
                password = 'wps'

            else:
                password_2 = getpass.getpass('Confirm Password: ')

                while password_1 != password_2:
                    with pretty_output(FG_WHITE) as p:
                        p.write('Passwords do not match, please try again.')
                    password_1 = getpass.getpass('Admin Password [wps]: ')
                    password_2 = getpass.getpass('Confirm Password: ')

                password = password_1

        docker_client.create_container(
            name=N52WPS_CONTAINER,
            image=N52WPS_IMAGE,
            environment={'NAME': name,
                         'POSITION': position,
                         'ADDRESS': address,
                         'CITY': city,
                         'STATE': state,
                         'COUNTRY': country,
                         'POSTAL_CODE': postal_code,
                         'EMAIL': email,
                         'PHONE': phone,
                         'FAX': fax,
                         'USERNAME': username,
                         'PASSWORD': password}
        )

    with pretty_output(FG_WHITE) as p:
        p.write("Finished installing Docker containers.")


def start_docker_containers(docker_client, containers=ALL_DOCKER_INPUTS):
    """
    Start Docker containers
    """
    container_images = get_docker_container_image(docker_client)

    for container in containers:
        # Get container dicts
        container_status = get_docker_container_status(docker_client)

        # Start PostGIS
        try:
            if not container_status[POSTGIS_CONTAINER] and container == POSTGIS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('Starting PostGIS container...')
                docker_client.start(container=POSTGIS_CONTAINER,
                                    # restart_policy='always',
                                    port_bindings={5432: DEFAULT_POSTGIS_PORT})
            elif container == POSTGIS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('PostGIS container already running...')
        except KeyError:
            if container == POSTGIS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('PostGIS container not installed...')

        try:
            if not container_status[GEOSERVER_CONTAINER] and container == GEOSERVER_INPUT:
                # Start GeoServer
                with pretty_output(FG_WHITE) as p:
                    p.write('Starting GeoServer container...')
                if 'cluster' in container_images[GEOSERVER_CONTAINER]:
                    docker_client.start(container=GEOSERVER_CONTAINER,
                                        # restart_policy='always',
                                        port_bindings={8181: DEFAULT_GEOSERVER_PORT,
                                                       8081: ('0.0.0.0', 8081),
                                                       8082: ('0.0.0.0', 8082),
                                                       8083: ('0.0.0.0', 8083),
                                                       8084: ('0.0.0.0', 8084)})
                else:
                    docker_client.start(container=GEOSERVER_CONTAINER,
                                        # restart_policy='always',
                                        port_bindings={8080: DEFAULT_GEOSERVER_PORT})
            elif not container or container == GEOSERVER_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('GeoServer container already running...')
        except KeyError:
            if container == GEOSERVER_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('GeoServer container not installed...')

        try:
            if not container_status[N52WPS_CONTAINER] and container == N52WPS_INPUT:
                # Start 52 North WPS
                with pretty_output(FG_WHITE) as p:
                    p.write('Starting 52 North WPS container...')
                docker_client.start(container=N52WPS_CONTAINER,
                                    # restart_policy='always',
                                    port_bindings={8080: DEFAULT_N52WPS_PORT})
            elif container == N52WPS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('52 North WPS container already running...')
        except KeyError:
            if not container or container == N52WPS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('52 North WPS container not installed...')


def stop_docker_containers(docker_client, silent=False, containers=ALL_DOCKER_INPUTS):
    """
    Stop Docker containers
    """
    for container in containers:
        # Get container dicts
        container_status = get_docker_container_status(docker_client)

        # Stop PostGIS
        try:
            if container_status[POSTGIS_CONTAINER] and container == POSTGIS_INPUT:
                if not silent:
                    with pretty_output(FG_WHITE) as p:
                        p.write('Stopping PostGIS container...')

                docker_client.stop(container=POSTGIS_CONTAINER)

            elif not silent and container == POSTGIS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('PostGIS container already stopped.')
        except KeyError:
            if not container or container == POSTGIS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('PostGIS container not installed...')

        # Stop GeoServer
        try:
            if container_status[GEOSERVER_CONTAINER] and container == GEOSERVER_INPUT:
                if not silent:
                    with pretty_output(FG_WHITE) as p:
                        p.write('Stopping GeoServer container...')

                docker_client.stop(container=GEOSERVER_CONTAINER)

            elif not silent and container == GEOSERVER_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('GeoServer container already stopped.')
        except KeyError:
            if not container or container == GEOSERVER_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('GeoServer container not installed...')

        # Stop 52 North WPS
        try:
            if container_status[N52WPS_CONTAINER] and container == N52WPS_INPUT:
                if not silent:
                    with pretty_output(FG_WHITE) as p:
                        p.write('Stopping 52 North WPS container...')

                docker_client.stop(container=N52WPS_CONTAINER)

            elif not silent and container == N52WPS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('52 North WPS container already stopped.')
        except KeyError:
            if not container or container == N52WPS_INPUT:
                with pretty_output(FG_WHITE) as p:
                    p.write('52 North WPS container not installed...')


def remove_docker_containers(docker_client, containers=ALL_DOCKER_INPUTS):
    """
    Remove all docker containers
    """
    # Check for containers that aren't installed
    containers_not_installed = get_containers_to_create(docker_client, containers=containers)

    for container in containers:
        # Remove PostGIS
        if container == POSTGIS_INPUT and POSTGIS_CONTAINER not in containers_not_installed:
            with pretty_output(FG_WHITE) as p:
                p.write('Removing PostGIS...')
            docker_client.remove_container(container=POSTGIS_CONTAINER)

        # Remove GeoServer
        if container == GEOSERVER_INPUT and GEOSERVER_CONTAINER not in containers_not_installed:
            with pretty_output(FG_WHITE) as p:
                p.write('Removing GeoServer...')
            docker_client.remove_container(container=GEOSERVER_CONTAINER, v=True)

        # Remove 52 North WPS
        if container == N52WPS_INPUT and N52WPS_CONTAINER not in containers_not_installed:
            with pretty_output(FG_WHITE) as p:
                p.write('Removing 52 North WPS...')
            docker_client.remove_container(container=N52WPS_CONTAINER)


def docker_init(containers=None, defaults=False):
    """
    Pull Docker images for Tethys Platform and create containers with interactive input.
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()
    containers = ALL_DOCKER_INPUTS if containers is None else containers

    # Check for the correct images
    images_to_install = get_images_to_install(docker_client, containers=containers)

    if len(images_to_install) < 1:
        with pretty_output(FG_WHITE) as p:
            p.write("Docker images already pulled.")
    else:
        with pretty_output(FG_WHITE) as p:
            p.write("Pulling Docker images...")

    # Pull the Docker images
    for image in images_to_install:
        pull_stream = docker_client.pull(image, stream=True)
        log_pull_stream(pull_stream)

    # Install docker containers
    install_docker_containers(docker_client, containers=containers, defaults=defaults)


def docker_start(containers):
    """
    Start the docker containers
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()
    containers = ALL_DOCKER_INPUTS if containers is None else containers

    # Start the Docker containers
    start_docker_containers(docker_client, containers=containers)


def docker_stop(containers=None, boot2docker=False):
    """
    Stop Docker containers
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()
    containers = ALL_DOCKER_INPUTS if containers is None else containers

    # Stop the Docker containers
    stop_docker_containers(docker_client, containers=containers)

    # Shutdown boot2docker if applicable
    if boot2docker and not containers:
        stop_boot2docker()


def docker_restart(containers=None):
    """
    Restart Docker containers
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()
    containers = ALL_DOCKER_INPUTS if containers is None else containers

    # Stop the Docker containers
    stop_docker_containers(docker_client, containers=containers)

    # Start the Docker containers
    start_docker_containers(docker_client, containers=containers)


def docker_remove(containers=None):
    """
    Remove Docker containers.
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()
    containers = ALL_DOCKER_INPUTS if containers is None else containers

    # Stop the Docker containers
    stop_docker_containers(docker_client, containers=containers)

    # Remove Docker containers
    remove_docker_containers(docker_client, containers=containers)


def docker_status():
    """
    Returns the status of the Docker containers: either Running or Stopped.
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()

    # Get container dicts
    container_status = get_docker_container_status(docker_client)

    # PostGIS
    if POSTGIS_CONTAINER in container_status and container_status[POSTGIS_CONTAINER]:
        with pretty_output(FG_WHITE) as p:
            p.write('PostGIS/Database: Running')
    elif POSTGIS_CONTAINER in container_status and not container_status[POSTGIS_CONTAINER]:
        with pretty_output(FG_WHITE) as p:
            p.write('PostGIS/Database: Stopped')
    else:
        with pretty_output(FG_WHITE) as p:
            p.write('PostGIS/Database: Not Installed')

    # GeoServer
    if GEOSERVER_CONTAINER in container_status and container_status[GEOSERVER_CONTAINER]:
        with pretty_output(FG_WHITE) as p:
            p.write('GeoServer: Running')
    elif GEOSERVER_CONTAINER in container_status and not container_status[GEOSERVER_CONTAINER]:
        with pretty_output(FG_WHITE) as p:
            p.write('GeoServer: Stopped')
    else:
        with pretty_output(FG_WHITE) as p:
            p.write('GeoServer: Not Installed')

    # 52 North WPS
    if N52WPS_CONTAINER in container_status and container_status[N52WPS_CONTAINER]:
        with pretty_output(FG_WHITE) as p:
            p.write('52 North WPS: Running')
    elif N52WPS_CONTAINER in container_status and not container_status[N52WPS_CONTAINER]:
        with pretty_output(FG_WHITE) as p:
            p.write('52 North WPS: Stopped')
    else:
        with pretty_output(FG_WHITE) as p:
            p.write('52 North WPS: Not Installed')


def docker_update(containers=None, defaults=False):
    """
    Remove Docker containers and pull the latest images updates.
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()
    containers = ALL_DOCKER_INPUTS if containers is None else containers

    # Stop containers
    stop_docker_containers(docker_client, containers=containers)

    # Remove containers
    remove_docker_containers(docker_client, containers=containers)

    # Force pull all the images without check to get latest version
    for container in containers:
        if not container:
            required_docker_images = REQUIRED_DOCKER_IMAGES
        elif container == POSTGIS_INPUT:
            required_docker_images = [POSTGIS_IMAGE]
        elif container == GEOSERVER_INPUT:
            required_docker_images = [GEOSERVER_IMAGE]
        elif container == N52WPS_INPUT:
            required_docker_images = [N52WPS_IMAGE]
        else:
            required_docker_images = []

        for image in required_docker_images:
            pull_stream = docker_client.pull(image, stream=True)
            log_pull_stream(pull_stream)

    # Reinstall containers
    install_docker_containers(docker_client, force=True, containers=containers, defaults=defaults)


def docker_ip():
    """
    Returns the hosts and ports of the Docker containers.
    """
    # Retrieve a Docker client
    docker_client = get_docker_client()

    # Containers
    containers = get_docker_container_dicts(docker_client)
    container_status = get_docker_container_status(docker_client)
    docker_host = docker_client.host

    # PostGIS
    try:
        if container_status[POSTGIS_CONTAINER]:
            postgis_container = containers[POSTGIS_CONTAINER]
            postgis_port = postgis_container['Ports'][0]['PublicPort']
            with pretty_output(FG_WHITE) as p:
                p.write('\nPostGIS/Database:')
                p.write('  Host: {0}'.format(docker_host))
                p.write('  Port: {0}'.format(postgis_port))
                p.write('  Endpoint: postgresql://<username>:<password>@{}:{}/<database>'.format(
                    docker_host, postgis_port
                ))

        else:
            with pretty_output(FG_WHITE) as p:
                p.write('\nPostGIS/Database: Not Running.')
    except KeyError:
        # If key error is raised, it is likely not installed.
        with pretty_output(FG_WHITE) as p:
            p.write('\nPostGIS/Database: Not Installed.')

    # GeoServer
    try:
        if container_status[GEOSERVER_CONTAINER]:
            geoserver_container = containers[GEOSERVER_CONTAINER]

            node_ports = []
            for port in geoserver_container['Ports']:
                if port['PublicPort'] != 8181:
                    node_ports.append(str(port['PublicPort']))

            with pretty_output(FG_WHITE) as p:
                p.write('\nGeoServer:')
                p.write('  Host: {}'.format(docker_host))
                p.write('  Primary Port: 8181')
                p.write('  Node Ports: {}'.format(', '.join(node_ports)))
                p.write('  Endpoint: http://{}:8181/geoserver/rest'.format(docker_host))

        else:
            with pretty_output(FG_WHITE) as p:
                p.write('\nGeoServer: Not Running.')
    except KeyError:
        # If key error is raised, it is likely not installed.
        with pretty_output(FG_WHITE) as p:
            p.write('\nGeoServer: Not Installed.')

    # 52 North WPS
    try:
        if container_status[N52WPS_CONTAINER]:
            n52wps_container = containers[N52WPS_CONTAINER]
            n52wps_port = n52wps_container['Ports'][0]['PublicPort']
            with pretty_output(FG_WHITE) as p:
                p.write('\n52 North WPS:')
                p.write('  Host: {}'.format(docker_host))
                p.write('  Port: {}'.format(n52wps_port))
                p.write('  Endpoint: http://{}:{}/wps/WebProcessingService\n'.format(docker_host, n52wps_port))

        else:
            with pretty_output(FG_WHITE) as p:
                p.write('\n52 North WPS: Not Running.')
    except KeyError:
        # If key error is raised, it is likely not installed.
        with pretty_output(FG_WHITE) as p:
            p.write('\n52 North WPS: Not Installed.')


def docker_command(args):
    """
    Docker management commands.
    """
    if args.command == 'init':
        docker_init(containers=args.containers, defaults=args.defaults)

    elif args.command == 'start':
        docker_start(containers=args.containers)

    elif args.command == 'stop':
        docker_stop(containers=args.containers, boot2docker=args.boot2docker)

    elif args.command == 'status':
        docker_status()

    elif args.command == 'update':
        docker_update(containers=args.containers, defaults=args.defaults)

    elif args.command == 'remove':
        docker_remove(containers=args.containers)

    elif args.command == 'ip':
        docker_ip()

    elif args.command == 'restart':
        docker_restart(containers=args.containers)
