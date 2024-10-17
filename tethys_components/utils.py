import asyncio
import inspect
from pathlib import Path
from channels.db import database_sync_to_async


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
    from reactpy_django.hooks import use_memo

    app_package = None

    for item in inspect.stack():
        try:
            calling_fpath = Path(item[0].f_code.co_filename)
            app_package = [
                p.name
                for p in [calling_fpath] + list(calling_fpath.parents)
                if p.parent.name == "tethysapp"
            ][0]
            break
        except IndexError:
            pass

    workspace = use_memo(lambda: asyncio.run(get_workspace(app_package, user)))

    return workspace


def delayed_execute(seconds, callable, args=None):
    from threading import Timer

    t = Timer(seconds, callable, args or [])
    t.start()


class Props(dict):
    def __init__(self, **kwargs):
        new_kwargs = {}
        for k, v in kwargs.items():
            v = "none" if v is None else v
            if k.endswith("_"):
                new_kwargs[k[:-1]] = v
            elif not k.startswith("on_") and k != "class_name":
                new_kwargs[k.replace("_", "-")] = v
            else:
                new_kwargs[k] = v
            setattr(self, k, v)
        super(Props, self).__init__(**new_kwargs)


def get_layout_component(app, layout):
    if callable(layout) or layout is None:
        layout_func = layout
    elif layout == "default":
        if callable(app.default_layout):
            layout_func = app.default_layout
        else:
            from tethys_components import layouts

            layout_func = getattr(layouts, app.default_layout)
    else:
        from tethys_components import layouts

        layout_func = getattr(layouts, app.default_layout)

    return layout_func
