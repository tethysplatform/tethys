from .cli_colors import FG_RED, FG_GREEN, FG_YELLOW, BOLD, pretty_output
from django.core.exceptions import ObjectDoesNotExist


def schedulers_remove_command(args):
    from tethys_compute.models import Scheduler
    scheduler = None
    name = args.scheduler_name
    force = args.force

    try:
        scheduler = Scheduler.objects.get(name=name)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('Scheduler with name "{}" does not exist.\nCommand aborted.'.format(name))
        exit(0)

    if force:
        scheduler.delete()
        with pretty_output(FG_GREEN) as p:
            p.write('Successfully removed Scheduler "{0}"!'.format(name))
        exit(0)
    else:
        proceed = input('Are you sure you want to delete this Scheduler? [y/n]: ')
        while proceed not in ['y', 'n', 'Y', 'N']:
            proceed = input('Please enter either "y" or "n": ')

        if proceed in ['y', 'Y']:
            scheduler.delete()
            with pretty_output(FG_GREEN) as p:
                p.write('Successfully removed Scheduler "{0}"!'.format(name))
            exit(0)
        else:
            with pretty_output(FG_RED) as p:
                p.write('Aborted. Scheduler not removed.')
            exit(1)


def condor_scheduler_create_command(args):
    from tethys_compute.models.condor.condor_scheduler import CondorScheduler

    name = args.name
    host = args.endpoint
    username = args.username
    password = args.password
    private_key_path = args.private_key_path
    private_key_pass = args.private_key_pass

    existing_scheduler = CondorScheduler.objects.filter(name=name).first()
    if existing_scheduler:
        with pretty_output(FG_YELLOW) as p:
            p.write('A Condor Scheduler with name "{}" already exists. Command aborted.'.format(name))
        exit(0)

    scheduler = CondorScheduler(
        name=name,
        host=host,
        username=username,
        password=password,
        private_key_path=private_key_path,
        private_key_pass=private_key_pass
    )

    scheduler.save()

    with pretty_output(FG_GREEN) as p:
        p.write('Condor Scheduler created successfully!')
    exit(0)


def dask_scheduler_create_command(args):
    from tethys_compute.models.dask.dask_scheduler import DaskScheduler

    name = args.name
    host = args.endpoint
    timeout = args.timeout
    heartbeat_interval = args.heartbeat_interval
    dashboard = args.dashboard

    existing_scheduler = DaskScheduler.objects.filter(name=name).first()
    if existing_scheduler:
        with pretty_output(FG_YELLOW) as p:
            p.write('A Dask Scheduler with name "{}" already exists. Command aborted.'.format(name))
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
        p.write('Dask Scheduler created successfully!')
    exit(0)


def schedulers_list_command(args):
    schedule_type = args.type.lower()
    if schedule_type == 'condor':
        from tethys_compute.models.condor.condor_scheduler import CondorScheduler

        schedulers = CondorScheduler.objects.all()
        num_schedulers = len(schedulers)

        if num_schedulers > 0:
            with pretty_output(BOLD) as p:
                p.write('{0: <30}{1: <25}{2: <10}{3: <10}{4: <50}{5: <10}'.format(
                    'Name', 'Host', 'Username', 'Password', 'Private Key Path', 'Private Key Pass'
                ))
            for scheduler in schedulers:
                p.write('{0: <30}{1: <25}{2: <10}{3: <10}{4: <50}{5: <10}'.format(
                    scheduler.name, scheduler.host, scheduler.username, '******' if scheduler.password else 'None',
                    scheduler.private_key_path, '******' if scheduler.private_key_pass else 'None'
                ))
        else:
            with pretty_output(BOLD) as p:
                p.write('There are no Condor Schedulers registered in Tethys.')
    elif schedule_type == 'dask':
        from tethys_compute.models.dask.dask_scheduler import DaskScheduler

        schedulers = DaskScheduler.objects.all()
        num_schedulers = len(schedulers)

        if num_schedulers > 0:
            with pretty_output(BOLD) as p:
                p.write('{0: <30}{1: <25}{2: <10}{3: <30}{4: <50}'.format(
                    'Name', 'Host', 'Timeout', 'Heartbeat Interval', 'Dashboard'
                ))
            for scheduler in schedulers:
                p.write('{0: <30}{1: <25}{2: <10}{3: <30}{4: <50}'.format(
                    scheduler.name, scheduler.host, scheduler.timeout, scheduler.heartbeat_interval, scheduler.dashboard
                ))
        else:
            with pretty_output(BOLD) as p:
                p.write('There are no Dask Schedulers registered in Tethys.')
