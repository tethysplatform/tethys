from getpass import getpass
from django.contrib.auth import authenticate
from .cli_colors import *


def console_superuser_required(func):
    def _wrapped(args):
        credentials = args.authenticate
        username = None
        password = None

        if credentials:
            cred_parts = credentials.split(':')
            if len(cred_parts) > 0:
                username = cred_parts[0]
            if len(cred_parts) > 1:
                password = cred_parts[1]
        if not username:
            username = raw_input('username: ')
        if not password:
            password = getpass('password: ')
        user = authenticate(username=username, password=password)
        if not user:
            with pretty_output(FG_RED) as p:
                p.write('The username or password provided was incorrect. Command aborted.')
            exit(1)
        if not user.is_superuser:
            with pretty_output(FG_RED) as p:
                p.write('You are not authorized to perform this action.')
            exit(1)

        return func(args)

    return _wrapped


def add_geoserver_rest_to_endpoint(endpoint):
    parts = endpoint.split('//')
    protocol = parts[0]
    parts2 = parts[1].split(':')
    host = parts2[0]
    port_and_path = parts2[1]
    port = port_and_path.split('/')[0]

    return '{0}//{1}:{2}/geoserver/rest/'.format(protocol, host, port)