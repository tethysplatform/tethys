from .cli_colors import FG_RED, FG_GREEN, FG_YELLOW, BOLD, pretty_output
from tethys_cli.cli_helpers import setup_django
from django.core.exceptions import ObjectDoesNotExist


def add_scheduler_parser(subparsers):
    # SCHEDULERS COMMANDS
    scheduler_parser = subparsers.add_parser(
        "schedulers", help="Scheduler commands for Tethys Platform."
    )
    scheduler_subparsers = scheduler_parser.add_subparsers(
        title="Commands", dest="sub-command"
    )
    scheduler_subparsers.required = True

    # tethys condor schedulers create
    condor_schedulers_create = scheduler_subparsers.add_parser(
        "create-condor",
        help="Create a Condor Scheduler that can be " "accessed by Tethys Apps.",
    )
    condor_schedulers_create.add_argument(
        "-n",
        "--name",
        required=True,
        help="A unique name for the Condor Scheduler",
        type=str,
    )
    condor_schedulers_create.add_argument(
        "-e",
        "--endpoint",
        required=True,
        type=str,
        help="The endpoint (host) of the service in the form <protocol>//<host>",
    )
    condor_schedulers_create.add_argument(
        "-o",
        "--port",
        required=False,
        default=22,
        type=int,
        help="The port of the service endpoint",
    )
    condor_schedulers_create.add_argument(
        "-u",
        "--username",
        required=True,
        help="The username to connect to the host with",
        type=str,
    )
    group = condor_schedulers_create.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        help="The password associated with the provided username",
    )
    group.add_argument(
        "-f",
        "--private-key-path",
        required=False,
        help="The path to the private ssh key file",
        type=str,
    )
    condor_schedulers_create.add_argument(
        "-k",
        "--private-key-pass",
        required=False,
        type=str,
        help="The password to the private ssh key file",
    )
    condor_schedulers_create.set_defaults(func=condor_scheduler_create_command)

    # tethys dask schedulers create
    dask_schedulers_create = scheduler_subparsers.add_parser(
        "create-dask",
        help="Create a Dask Scheduler that can be " "accessed by Tethys Apps.",
    )
    dask_schedulers_create.add_argument(
        "-n",
        "--name",
        required=True,
        help="A unique name for the Condor Scheduler",
        type=str,
    )
    dask_schedulers_create.add_argument(
        "-e",
        "--endpoint",
        required=True,
        type=str,
        help='The endpoint of the service in the form <protocol>//<host>"',
    )
    dask_schedulers_create.add_argument(
        "-t",
        "--timeout",
        required=False,
        type=int,
        help="The timeout value of the Dask Job",
    )
    dask_schedulers_create.add_argument(
        "-b",
        "--heartbeat-interval",
        required=False,
        help="The heartbeat interval value of the Dask Job",
        type=int,
    )
    dask_schedulers_create.add_argument(
        "-d",
        "--dashboard",
        required=False,
        type=str,
        help="The dashboard type of a DaskJob",
    )
    dask_schedulers_create.set_defaults(func=dask_scheduler_create_command)

    # tethys condor/dask schedulers list

    schedulers_list = scheduler_subparsers.add_parser(
        "list", help="List the existing Schedulers."
    )
    schedulers_list.add_argument(
        "-t",
        "--type",
        required=True,
        help="input: Condor or Dask (List Condor or Dask type)",
        type=str,
    )
    schedulers_list.set_defaults(func=schedulers_list_command)

    # tethys schedulers remove
    schedulers_remove = scheduler_subparsers.add_parser(
        "remove", help="Remove a Scheduler."
    )
    schedulers_remove.add_argument(
        "scheduler_name", help="The unique name of the Scheduler that you are removing."
    )
    schedulers_remove.add_argument(
        "-f", "--force", action="store_true", help="Force removal without confirming."
    )
    schedulers_remove.set_defaults(func=schedulers_remove_command)


def schedulers_remove_command(args):
    setup_django()
    from tethys_compute.models import Scheduler

    scheduler = None
    name = args.scheduler_name
    force = args.force

    try:
        scheduler = Scheduler.objects.get(name=name)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                'Scheduler with name "{}" does not exist.\nCommand aborted.'.format(
                    name
                )
            )
        exit(0)

    if force:
        scheduler.delete()
        with pretty_output(FG_GREEN) as p:
            p.write('Successfully removed Scheduler "{0}"!'.format(name))
        exit(0)
    else:
        proceed = input("Are you sure you want to delete this Scheduler? [y/n]: ")
        while proceed not in ["y", "n", "Y", "N"]:
            proceed = input('Please enter either "y" or "n": ')

        if proceed in ["y", "Y"]:
            scheduler.delete()
            with pretty_output(FG_GREEN) as p:
                p.write('Successfully removed Scheduler "{0}"!'.format(name))
            exit(0)
        else:
            with pretty_output(FG_RED) as p:
                p.write("Aborted. Scheduler not removed.")
            exit(1)


def condor_scheduler_create_command(args):
    setup_django()
    from tethys_compute.models.condor.condor_scheduler import CondorScheduler

    name = args.name
    host = args.endpoint
    port = args.port
    username = args.username
    password = args.password
    private_key_path = args.private_key_path
    private_key_pass = args.private_key_pass

    existing_scheduler = CondorScheduler.objects.filter(name=name).first()
    if existing_scheduler:
        with pretty_output(FG_YELLOW) as p:
            p.write(
                'A Condor Scheduler with name "{}" already exists. Command aborted.'.format(
                    name
                )
            )
        exit(0)

    scheduler = CondorScheduler(
        name=name,
        host=host,
        port=port,
        username=username,
        password=password,
        private_key_path=private_key_path,
        private_key_pass=private_key_pass,
    )

    scheduler.save()

    with pretty_output(FG_GREEN) as p:
        p.write("Condor Scheduler created successfully!")

    exit(0)


def dask_scheduler_create_command(args):
    setup_django()
    from tethys_compute.models.dask.dask_scheduler import DaskScheduler

    name = args.name
    host = args.endpoint
    timeout = args.timeout
    heartbeat_interval = args.heartbeat_interval
    dashboard = args.dashboard

    existing_scheduler = DaskScheduler.objects.filter(name=name).first()
    if existing_scheduler:
        with pretty_output(FG_YELLOW) as p:
            p.write(
                'A Dask Scheduler with name "{}" already exists. Command aborted.'.format(
                    name
                )
            )
        exit(0)

    scheduler = DaskScheduler(
        name=name,
        host=host,
        timeout=timeout,
        heartbeat_interval=heartbeat_interval,
        dashboard=dashboard,
    )

    scheduler.save()

    with pretty_output(FG_GREEN) as p:
        p.write("Dask Scheduler created successfully!")
    exit(0)


def schedulers_list_command(args):
    setup_django()
    schedule_type = args.type.lower()
    if schedule_type == "condor":
        from tethys_compute.models.condor.condor_scheduler import CondorScheduler

        schedulers = CondorScheduler.objects.all()
        num_schedulers = len(schedulers)

        if num_schedulers > 0:
            with pretty_output(BOLD) as p:
                p.write(
                    "{0: <30}{1: <25}{2: <6}{3: <10}{4: <10}{5: <50}{6: <10}".format(
                        "Name",
                        "Host",
                        "Port",
                        "Username",
                        "Password",
                        "Private Key Path",
                        "Private Key Pass",
                    )
                )
            for scheduler in schedulers:
                p.write(
                    "{0: <30}{1: <25}{2: <6}{3: <10}{4: <10}{5: <50}{6: <10}".format(
                        scheduler.name,
                        scheduler.host,
                        scheduler.port,
                        scheduler.username,
                        "******" if scheduler.password else "None",
                        scheduler.private_key_path,
                        "******" if scheduler.private_key_pass else "None",
                    )
                )
        else:
            with pretty_output(BOLD) as p:
                p.write("There are no Condor Schedulers registered in Tethys.")
    elif schedule_type == "dask":
        from tethys_compute.models.dask.dask_scheduler import DaskScheduler

        schedulers = DaskScheduler.objects.all()
        num_schedulers = len(schedulers)

        if num_schedulers > 0:
            with pretty_output(BOLD) as p:
                p.write(
                    "{0: <30}{1: <25}{2: <10}{3: <30}{4: <50}".format(
                        "Name", "Host", "Timeout", "Heartbeat Interval", "Dashboard"
                    )
                )
            for scheduler in schedulers:
                p.write(
                    "{0: <30}{1: <25}{2: <10}{3: <30}{4: <50}".format(
                        scheduler.name,
                        scheduler.host,
                        scheduler.timeout,
                        scheduler.heartbeat_interval,
                        scheduler.dashboard,
                    )
                )
        else:
            with pretty_output(BOLD) as p:
                p.write("There are no Dask Schedulers registered in Tethys.")
