import inspect
from pathlib import Path
from tethys_apps.harvester import SingletonHarvester
from tethys_apps.base.paths import (
    _get_user_workspace,
    _get_app_workspace,
    _get_app_media,
    _get_user_media,
)

class _PathsQuery:
    STATUS_CHECKING_QUOTA = 1
    STATUS_QUOTA_EXCEEDED = 2
    
    def __init__(self, status):
        self.status = status
    
    @property
    def checking_quota(self):
        return self.status == self.STATUS_CHECKING_QUOTA

    @property
    def quota_exceeded(self):
        return self.status == self.STATUS_QUOTA_EXCEEDED


def _infer_app_from_stack_trace():
    app_package = None
    app = None

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
        raise Exception(
            "This hook must be called from a tethysapp package. No package was found in the call stack."
        )

    for app_s in SingletonHarvester().apps:
        if app_s.package == app_package:
            app = app_s
            break

    if not app:
        raise Exception("The {app_package} app was not found.")

    return app

def use_workspace(user=None):
    """
    A custom ReactPy hook used to access the TethysPath representing the app or user's workspace directory.

    Args:
        user (auth.models.User): If provided, get the TethysPath for the user's workspace directory, rather than the app's.
    
    Returns:
        PathsQuery object if the state of the underlying query is "loading" or "error"
        TethysPath representing either the app's or user's workspace directory otherwise
    """
    from reactpy_django.hooks import use_query

    app = _infer_app_from_stack_trace()
    if user:
        get_workspace = _get_user_workspace
        get_workspace_args = {"app_or_request": app, "user_or_request": user}
    else:
        get_workspace = _get_app_workspace
        get_workspace_args = {"app_or_request": app}

    workspace_query = use_query(get_workspace, get_workspace_args, postprocessor=None)

    if workspace_query.loading:
        return _PathsQuery(_PathsQuery.STATUS_CHECKING_QUOTA)
    elif workspace_query.error:
        return _PathsQuery(_PathsQuery.STATUS_QUOTA_EXCEEDED)
    else:
        workspace = workspace_query.data
        setattr(workspace, "checking_quota", False)
        setattr(workspace, "quota_exceeded", False)
        return workspace

def use_resources():
    """
    A custom ReactPy hook used to access the TethysPath representing the app's resources directory.
    
    Returns:
        TethysPath representing the app's resources directory
    """
    app = _infer_app_from_stack_trace()
    return app.resources_path

def use_media(user=None):
    """
    A custom ReactPy hook used to access the TethysPath representing the app or user's media directory.

    Args:
        user (auth.models.User): If provided, get the TethysPath for the user's media directory, rather than the app's.
    
    Returns:
        PathsQuery object if the state of the underlying query is "loading" or "error"
        TethysPath representing either the app's or user's media directory otherwise
    """
    from reactpy_django.hooks import use_query

    app = _infer_app_from_stack_trace()
    if user:
        get_media = _get_user_media
        get_media_args = {"app_or_request": app, "user_or_request": user}
    else:
        get_media = _get_app_media
        get_media_args = {"app_or_request": app}

    media_query = use_query(get_media, get_media_args, postprocessor=None)

    if media_query.loading:
        return _PathsQuery(_PathsQuery.STATUS_CHECKING_QUOTA)
    elif media_query.error:
        return _PathsQuery(_PathsQuery.STATUS_QUOTA_EXCEEDED)
    else:
        media = media_query.data
        setattr(media, "checking_quota", False)
        setattr(media, "quota_exceeded", False)
        return media

def use_public():
    """
    A custom ReactPy hook used to access the TethysPath representing the app's public directory.
    
    Returns:
        TethysPath representing the app's public directory
    """
    app = _infer_app_from_stack_trace()
    return app.public_path

def background_execute(callable, args=[], delay_seconds=None):
    """
    Kick off a task in the background, optionally with a delay

    Args:
        callable (Callable): The callable that will be executed on a thread in the background
        args (list): A list of arguments that should be passed to the callable when executed
        delay_seconds (int|float): The number of seconds after which the callable should be executed

    Returns: None
    """
    if delay_seconds:
        from threading import Timer
        t = Timer(delay_seconds, callable, args)
    else:
        from threading import Thread
        t = Thread(callable, args=args)

    t.start()

class Props(dict):
    """
    Wrapper for ReactPy component property dictionaries that allow them to be passed as python kwargs instead.
    They are converted back to ReactPy propery dictionaries when accessed.

    Example:
        Instead of lib.html.div({"backgroundColor": "red", "fontSize": "12px"}, "Hello"), you can use lib.html.div(Props(background_color="red, font_size="12px"), "Hello")
    """
    def _snake_to_camel(self, snake):
        parts = snake.split("_")
        if len(parts) == 1:
            camel = snake
        else:
            camel = parts[0] + "".join(map(lambda x: x.title(), parts[1:]))

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


def _get_layout_component(app, layout):
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
