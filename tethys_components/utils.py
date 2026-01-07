import inspect
import io
import math
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


def fetch(url: str) -> str:
    """Fetches data from url and returns result as string"""
    from requests import get

    return get(url).text


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


def _background_execute_wrapper(func, args, callback=None):
    result = func(*args)
    if callable(callback):
        callback(result)


class RepeatManager:
    from threading import Timer, Thread

    def __init__(self, repeat_seconds, target, args=None):
        self._running = False
        self.repeat_seconds = repeat_seconds
        self.target = target
        self.args = args or ()
        self._timer = None

    def _repeat_function(self):
        if not self._running:
            return
        self.Thread(
            target=self.target,
            args=self.args,
        ).start()
        self._timer = self.Timer(
            interval=self.repeat_seconds,
            function=self._repeat_function,
        )
        self._timer.start()

    def start(self):
        self._running = True
        self._repeat_function()
        return self

    def cancel(self):
        self._running = False
        self._timer.cancel()

    def is_alive(self):
        return self._running


def background_execute(
    func, args=None, delay_seconds=None, repeat_seconds=None, callback=None
):
    """
    Kick off a task in the background, optionally with a delay

    Args:
        func (Callable): The function that will be executed on a thread in the background
        args (list): A list of arguments that should be passed to the provided function when executed
        delay_seconds (int|float): The number of seconds after which the provided function should be executed
        repeat_seconds (int|float): Will re-execute the provided function every X seconds
        callback (Callable): A function that will be called when the provided function has completed.

    Returns: None
    """
    args = args or ()
    if not isinstance(args, (list, tuple)):
        raise ValueError("args must be a list or tuple")

    if delay_seconds:
        from threading import Timer

        t = Timer(
            interval=delay_seconds,
            function=_background_execute_wrapper,
            args=(func, args, callback),
        )
    elif repeat_seconds:
        t = RepeatManager(
            repeat_seconds=repeat_seconds,
            target=_background_execute_wrapper,
            args=(func, args, callback),
        )
    else:
        from threading import Thread

        t = Thread(
            target=_background_execute_wrapper,
            args=(func, args, callback),
        )

    t.start()
    return t


def transform_coordinate(coordinate, src_proj, target_proj):
    from pyproj import Transformer, CRS

    if isinstance(src_proj, dict):
        source_crs = CRS(src_proj["definition"])
    elif isinstance(src_proj, str):
        source_crs = CRS(src_proj)
    else:
        raise ValueError(
            "src_proj must be a string or dictionary with a definition key"
        )

    if isinstance(target_proj, dict):
        target_crs = CRS(target_proj["definition"])
    elif isinstance(target_proj, str):
        target_crs = CRS(target_proj)
    else:
        raise ValueError(
            "target_proj must be a string or dictionary with a definition key"
        )

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


def _get_legend_url_(vdom_element, resolution=None, params=None):
    if vdom_element["tagName"] not in ["ImageWMSSource", "TileWMSSource"]:
        raise ValueError(
            "The get_legend_url method can only be called on ImageWMSSource or TileWMSSource components"
        )

    from urllib.parse import urlencode, urljoin
    from pyproj import CRS

    if not params:
        params = {}

    source_params = vdom_element["attributes"]["options"]["params"]
    base_url = vdom_element["attributes"]["options"]["url"]
    query_params = {
        "SERVICE": "WMS",
        "VERSION": "1.0.0",
        "REQUEST": "GetLegendGraphic",
        "FORMAT": "image/png",
        **source_params,
    }

    if "LAYER" not in query_params:
        layers = source_params["LAYERS"]
        is_single_layer = not isinstance(layers, list) or len(layers) != 1
        if not is_single_layer:
            print("NOT SINGLE LAYER")
            return None
        query_params["LAYER"] = layers

    if resolution:
        mpu = (
            CRS(
                source_params["projection"]
                if "projection" in source_params
                else "EPSG:3857"
            )
            .axis_info[0]
            .unit_conversion_factor
        )
        pixelSize = 0.00028
        query_params["SCALE"] = (resolution * mpu) / pixelSize

    query_string = urlencode(query_params)
    legend_url = urljoin(base_url, f"?{query_string}")
    return legend_url


def _get_feature_info_url_(
    vdom_element, map_coordinate, map_resolution, map_proj, layer_proj, params=None
):
    if vdom_element["tagName"] not in ["ImageWMSSource", "TileWMSSource"]:
        raise ValueError(
            "The get_feature_info_url method can only be called on ImageWMSSource or TileWMSSource components"
        )

    from urllib.parse import urlencode, urljoin
    from pyproj import CRS

    if not params:
        params = {}

    GETFEATUREINFO_IMAGE_SIZE = [101, 101]
    DECIMALS = 4

    if map_proj != layer_proj:
        # TODO: Implement transformation of map coordinates to layer coordinates
        raise NotImplementedError(
            "get_feature_info_url has not yet been implemented for layers with different projections than the map"
        )

    extent = _get_for_view_and_size(
        map_coordinate,
        map_resolution,
        0,
        GETFEATUREINFO_IMAGE_SIZE,
    )
    x = round(math.floor((map_coordinate[0] - extent[0]) / map_resolution), DECIMALS)
    y = round(math.floor((extent[3] - map_coordinate[1]) / map_resolution), DECIMALS)

    axisOrientation = "".join([a.direction[0] for a in CRS(map_proj).axis_info])
    bbox = (
        [extent[1], extent[0], extent[3], extent[2]]
        if axisOrientation == "ne"
        else extent
    )

    source_params = vdom_element["attributes"]["options"]["params"]
    base_url = vdom_element["attributes"]["options"]["url"]
    query_params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": source_params["LAYERS"],
        "STYLES": "",
        "CRS": map_proj,  # Map's projection
        "BBOX": ",".join(str(x) for x in bbox),  # In map's projection
        "WIDTH": GETFEATUREINFO_IMAGE_SIZE[0],
        "HEIGHT": GETFEATUREINFO_IMAGE_SIZE[1],
        "QUERY_LAYERS": source_params["LAYERS"],
        "INFO_FORMAT": "application/json",
        "I": x,  # X ordinate of query point on map, in pixels. 0 is left side.
        "J": y,  # Y ordinate of query point on map, in pixels. 0 is top.
        **source_params,
        **params,
    }

    query_string = urlencode(query_params)
    feature_info_url = urljoin(base_url, f"?{query_string}")
    return feature_info_url


def _get_for_view_and_size(center, resolution, rotation, size):
    [x0, y0, x1, y1, x2, y2, x3, y3, _, _] = _get_rotated_viewport(
        center,
        resolution,
        rotation,
        size,
    )
    return [
        min(x0, x1, x2, x3),
        min(y0, y1, y2, y3),
        max(x0, x1, x2, x3),
        max(y0, y1, y2, y3),
    ]


def _get_rotated_viewport(center, resolution, rotation, size):
    dx = (resolution * size[0]) / 2
    dy = (resolution * size[1]) / 2
    cosRotation = math.cos(rotation)
    sinRotation = math.sin(rotation)
    xCos = dx * cosRotation
    xSin = dx * sinRotation
    yCos = dy * cosRotation
    ySin = dy * sinRotation
    x = center[0]
    y = center[1]

    return [
        x - xCos + ySin,
        y - xSin - yCos,
        x - xCos - ySin,
        y - xSin + yCos,
        x + xCos - ySin,
        y + xSin + yCos,
        x + xCos + ySin,
        y + xSin - yCos,
        x - xCos + ySin,
        y - xSin - yCos,
    ]


def find_by_tag(element, tag_name: str):
    """Recursively finds all elements with a specific tag name."""
    if isinstance(element, dict):
        found_elements = []
        if element.get("tagName") == tag_name:
            found_elements.append(element)

        # Recursively search children
        children = element.get("children")
        if children:
            found_elements.extend(find_by_tag(children, tag_name))

        return found_elements

    elif isinstance(element, list):
        found_elements = []
        for child in element:
            found_elements.extend(find_by_tag(child, tag_name))
        return found_elements
    else:
        # Ignore non-element types (like strings or numbers)
        return []


class OlManager:
    """
    A utility class for dynamically building OpenLayers (OL) configuration dictionaries.
    This class uses dynamic attribute access to construct nested namespace paths
    and generate configuration objects for OpenLayers components. It enables a
    fluent interface for creating OL geometry and feature configurations.
    Example:
        >>> manager = OlManager("ol")
        >>> result = manager.geom.Point(coords=[0, 0])
        >>> result
        {'type': 'ol.geom.Point', 'coords': [0, 0]}
    """

    def __init__(self, attr):
        """
        Initialize the OlManager with an attribute path.
        Args:
            attr (str): The OpenLayers namespace path (e.g., "ol", "ol.geom").
        """
        self.attr = attr

    def __getattr__(self, attr):
        """
        Dynamically create nested OlManager instances for attribute access.
        This method intercepts attribute access and creates new OlManager instances
        with extended namespace paths. The new instance is cached as an attribute
        for subsequent access.
        Args:
            attr (str): The attribute name to append to the current namespace.
        Returns:
            OlManager: A new OlManager instance with the extended namespace path.
        """
        new_instance = OlManager(f"{self.attr}.{attr}")
        setattr(self, attr, new_instance)
        return new_instance

    def __call__(self, *args, **kwargs):
        """
        Generate an OpenLayers configuration dictionary.
        Converts the OlManager instance into a configuration dictionary with the
        accumulated namespace path as the 'type' field. Special handling for
        geometry objects: if the namespace contains "ol.geom" and a single
        positional argument is provided, it is converted to a 'geom' keyword argument.
        Args:
            *args: Positional arguments. For ol.geom objects, a single argument
                   is treated as the geometry parameter.
            **kwargs: Keyword arguments to include in the configuration dictionary.
        Returns:
            dict: A configuration dictionary with 'type' and additional parameters.
        """
        if args:
            if "ol.geom" in self.attr and len(args) == 1:
                kwargs["geom"] = args[0]
        return dict(type=self.attr, **kwargs)
