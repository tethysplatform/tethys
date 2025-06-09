import inspect
import io
import tokenize
from tethys_components import layouts
from typing import Any
from pathlib import Path
from tethys_apps.harvester import SingletonHarvester
from tethys_apps.base.paths import (
    _get_user_workspace,
    _get_app_workspace,
    _get_app_media,
    _get_user_media,
)


class DotNotationDict(dict):
    """Wrapper for event args provided by ReactPy as dicts to allow attribute access"""

    def __getattr__(self, key: str) -> Any:
        val: str = None
        if key in self:
            mod_key = key
        else:
            mod_key = self.snake_to_camel(key)

        if mod_key in self:
            val = self[mod_key]
            if isinstance(val, dict):
                val = DotNotationDict(val)
            elif isinstance(val, list):
                val = [DotNotationDict(v) if isinstance(v, dict) else v for v in val]
            return val
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )

    @staticmethod
    def snake_to_camel(snake_str: str) -> str:
        words = snake_str.split("_")
        camel_case = words[0] + "".join(word.capitalize() for word in words[1:])
        return camel_case


def args_to_dot_notation_dicts(func: callable) -> callable:
    """Wrapper that converts all dict args to AttrDict objects"""

    def wrapped(*data):
        return func(*[DotNotationDict(d) if isinstance(d, dict) else d for d in data])

    return wrapped


def fetch_json(url: str, as_attr_dict: bool = True) -> dict | DotNotationDict:
    """Fetches data expected to be JSON from url and returns result as AttrDict"""
    from requests import get

    result = get(url).json()
    if as_attr_dict:
        result = DotNotationDict(result)
    return result


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
        raise ModuleNotFoundError(
            "This hook must be called from a tethysapp module. No such module was found in the call stack."
        )

    for app_s in SingletonHarvester().apps:
        if app_s.package == app_package:
            app = app_s
            break

    if not app:
        raise EnvironmentError("The {app_package} app was not found.")

    return app


def use_workspace(user=None):
    """
    A custom hook used to access the TethysPath representing the app or user's workspace directory.

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
        workspace.checking_quota = False
        workspace.quota_exceeded = False
        return workspace


def use_resources():
    """
    A custom hook used to access the TethysPath representing the app's resources directory.

    Returns:
        TethysPath representing the app's resources directory
    """
    app = _infer_app_from_stack_trace()
    return app.resources_path


def use_media(user=None):
    """
    A custom hook used to access the TethysPath representing the app or user's media directory.

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
        media.checking_quota = False
        media.quota_exceeded = False
        return media


def use_public():
    """
    A custom hook used to access the TethysPath representing the app's public directory.

    Returns:
        TethysPath representing the app's public directory
    """
    app = _infer_app_from_stack_trace()
    return app.public_path


def background_execute(callable, args=None, delay_seconds=None, repeat_seconds=None):
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

        t = Timer(delay_seconds, callable, args if args else [])
    else:
        from threading import Thread

        t = Thread(target=callable, args=args if args else [])

    t.start()

    if repeat_seconds:
        from threading import Timer
        def repeat_function():
            Thread(target=callable, args=args if args else []).start()
            Timer(repeat_seconds, repeat_function).start()
        repeat_function()


def transform_coordinate(coordinate, src_proj, target_proj):
    from pyproj import Transformer, CRS

    source_crs = CRS(src_proj)
    target_crs = CRS(target_proj)
    transformer = Transformer.from_crs(source_crs, target_crs)
    return transformer.transform(coordinate[0], coordinate[1])


class Props(dict):
    """
    Wrapper for ReactPy component property dictionaries that allow them to be passed as python kwargs instead.
    They are converted back to ReactPy propery dictionaries when accessed.

    Example:
        Instead of lib.html.div({"backgroundColor": "red", "fontSize": "12px"}, "Hello"), you can use lib.html.div(Props(background_color="red, font_size="12px"), "Hello")
    """

    def _snake_to_camel(self, snake):
        parts = snake.split("_")
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


class Style(dict):
    """
    Wrapper for style dictionaries that allow them to be passed as python kwargs instead.
    This namely converts dashes ("-") to underscores for styles

    Example:
        Instead of lib.html.div(style={"background-color": "red", "font-size": "12px"}, "Hello"),
        try using lib.html.div(style=Style(background_color="red, font_size="12px"), "Hello")
    """

    def __init__(self, **kwargs):
        new_kwargs = {}
        for k, v in kwargs.items():
            new_kwargs[k.replace("_", "-")] = v
        super(Style, self).__init__(**new_kwargs)


def _get_layout_component(app, layout):
    if callable(layout) or layout is None:
        layout_func = layout
    elif layout == "default":
        if callable(app.default_layout):
            layout_func = app.default_layout
        else:
            layout_func = getattr(layouts, app.default_layout)
    else:
        layout_func = getattr(layouts, app.default_layout)

    return layout_func


def remove_comments_and_docstrings(source):
    """Taken directly from https://stackoverflow.com/a/62074206"""
    io_obj = io.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += " " * (start_col - last_col)
        if token_type == tokenize.COMMENT:
            pass
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                if prev_toktype != tokenize.NEWLINE:
                    if start_col > 0:
                        out += token_string
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    out = "\n".join(x for x in out.splitlines() if x.strip())
    return out


def _get_db_object(app):
    return app.db_object
