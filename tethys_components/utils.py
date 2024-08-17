import inspect
import os
from channels.db import database_sync_to_async
from reactpy_django.hooks import use_query

async def get_workspace(app_package, user):
    from tethys_apps.harvester import SingletonHarvester
    for app_s in SingletonHarvester().apps:
        if app_s.package == app_package:
            if user:
                workspace = await database_sync_to_async(app_s.get_user_workspace)(user)
            else:
                workspace = await database_sync_to_async(app_s.get_app_workspace)()
            return workspace

def use_workspace(user=None):
    calling_fpath = inspect.stack()[1][0].f_code.co_filename
    app_package = calling_fpath.split(f'{os.sep}tethysapp{os.sep}')[1].split(os.sep)[0]

    workspace_query = use_query(get_workspace, {'app_package': app_package, 'user': user}, postprocessor=None)

    return workspace_query.data

def delayed_execute(seconds, callable, args=[]):
    from threading import Timer
    
    t = Timer(seconds, callable, args)
    t.start()


class Props(dict):
    def __init__(self, **kwargs):
        new_kwargs = {}
        for k, v in kwargs.items():
            if k.endswith("_"):
                new_kwargs[k[:-1]] = v
            elif not k.startswith("on_") and k != "class_name":
                new_kwargs[k.replace('_', '-')] = v
            else:
                new_kwargs[k] = "none" if v is None else v
            setattr(self, k, v)
        super(Props, self).__init__(**new_kwargs)
