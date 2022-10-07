from tethys_portal import __version__


def add_version_parser(subparsers):
    # Setup list command
    version_parser = subparsers.add_parser(
        "version", help="Print the version of tethys_platform"
    )
    version_parser.set_defaults(func=version_command)


def version_command(args):
    print(__version__)
