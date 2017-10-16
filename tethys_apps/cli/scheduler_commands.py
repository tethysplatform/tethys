from .cli_colors import *
from django.core.exceptions import ObjectDoesNotExist


def scheduler_create_command(args):
    from tethys_compute.models import Scheduler

    name = args.name
    host = args.endpoint
    username = args.username
    password = args.password
    private_key_path = args.private_key_path
    private_key_pass = args.private_key_pass

    existing_scheduler = Scheduler.objects.filter(name=name).first()
    if existing_scheduler:
        with pretty_output(FG_RED) as p:
            p.write('A Scheduler with name "{}" already exists. Command aborted.'.format(name))
        exit(1)

    scheduler = Scheduler(
        name=name,
        host=host,
        username=username,
        password=password,
        private_key_path=private_key_path,
        private_key_pass=private_key_pass
    )

    scheduler.save()

    with pretty_output(FG_GREEN) as p:
        p.write('Scheduler created successfully!')
    exit(0)


def schedulers_list_command(args):
    from tethys_compute.models import Scheduler
    schedulers = Scheduler.objects.all()

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
            p.write('There are no Schedulers registered in Tethys.')


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
        exit(1)

    if force:
        scheduler.delete()
        with pretty_output(FG_GREEN) as p:
            p.write('Successfully removed Scheduler "{0}"!'.format(name))
        exit(0)
    else:
        proceed = raw_input('Are you sure you want to delete this Scheduler? [y/n]: ')
        while proceed not in ['y', 'n', 'Y', 'N']:
            proceed = raw_input('Please enter either "y" or "n": ')

        if proceed in ['y', 'Y']:
            scheduler.delete()
            with pretty_output(FG_GREEN) as p:
                p.write('Successfully removed Scheduler "{0}"!'.format(name))
            exit(0)
        else:
            with pretty_output(FG_RED) as p:
                p.write('Aborted. Scheduler not removed.')
            exit(1)
