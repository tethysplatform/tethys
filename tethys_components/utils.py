import inspect
from pathlib import Path
from tethys_apps.harvester import SingletonHarvester


def use_workspace(user=None):
    workspace = None
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
    
    if not app_package:
        raise Exception("The use_workspace hook must be called from a tethysapp package. No package was found in the call stack.")

    for app_s in SingletonHarvester().apps:
        if app_s.package == app_package:
            if user:
                workspace = app_s.get_user_workspace(user)
            else:
                workspace = app_s.get_app_workspace()
            break
    
    if not workspace:
        raise Exception("The {app_package} app was not found.")
    
    return workspace


def delayed_execute(callable, delay_seconds, args=None):
    from threading import Timer

    t = Timer(delay_seconds, callable, args or [])
    t.start()


class Props(dict):
    def _snake_to_camel(self, snake):
        parts = snake.split('_')
        if len(parts) == 1:
            camel = snake
        else:
            camel = parts[0] + ''.join(map(lambda x: x.title(), parts[1:]))
        
        return camel
        
    def __init__(self, **kwargs):
        new_kwargs = {}
        for k, v in kwargs.items():
            v = "none" if v is None else v
            if k.endswith("_"):
                new_kwargs[k[:-1]] = v
            new_kwargs[self._snake_to_camel(k)] = v
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
