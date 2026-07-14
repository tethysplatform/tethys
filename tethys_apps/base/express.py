"""
********************************************************************************
* Name: express.py
* Author: Gage Larsen
* Created On: July 2026
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""

import ast
import inspect
import logging
import re
import sys
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_file_location
from os import environ
from pathlib import Path

TETHYS_EXPRESS_APP_ENV = "TETHYS_EXPRESS_APP"

tethys_log = logging.getLogger("tethys." + __name__)


def get_express_app_file():
    """
    Get the path to the single-file app being run by ``tethys run``, if any.

    Returns:
        Path or None: resolved path to the app file, or None if not in express mode.
    """
    value = environ.get(TETHYS_EXPRESS_APP_ENV)
    return Path(value).resolve() if value else None


def find_component_app_class_node(app_file):
    """
    Find the AST node of the ComponentBase subclass defined in the given file.

    Returns:
        ast.ClassDef or None: the class definition node, or None if no such class is found.
    """
    try:
        tree = ast.parse(Path(app_file).read_text())
    except (OSError, SyntaxError):
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = (
                    base.attr
                    if isinstance(base, ast.Attribute)
                    else getattr(base, "id", None)
                )
                if base_name == "ComponentBase":
                    return node
    return None


def _source_stem(app_file):
    """
    Get the name-worthy stem for the app file. Uses the parent directory name for
    generically-named files (e.g. app.py) so "dashboards/app.py" is named "dashboards".
    """
    app_file = Path(app_file)
    if app_file.stem == "app" and app_file.parent.name:
        return app_file.parent.name
    return app_file.stem


def derive_package_name(app_file):
    """
    Derive a valid app package name from the app file name (e.g. my-dashboard.py -> my_dashboard).
    """
    package = re.sub(r"\W", "_", _source_stem(app_file)).lower()
    if package[0].isdigit():
        package = f"app_{package}"
    return package


def get_express_package_name(app_file):
    """
    Get the package name of the express app. An explicit ``package`` attribute on the
    app class wins, otherwise it is derived from the file name.
    """
    class_node = find_component_app_class_node(app_file)
    if class_node is not None:
        for statement in class_node.body:
            if (
                isinstance(statement, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "package"
                    for target in statement.targets
                )
                and isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            ):
                return statement.value.value
    return derive_package_name(app_file)


def synthesize_express_metadata(app_class):
    """
    Fill in required app metadata on the express app class so a bare single-file app can
    omit it. Called by ``ComponentBase.__init_subclass__`` when the class is defined, which
    ensures the metadata is in place before any ``@App.page`` decorators are evaluated.
    No-op unless the class is defined in the file being run by ``tethys run``.
    """
    app_file = get_express_app_file()
    if app_file is None:
        return

    module = sys.modules.get(app_class.__module__)
    module_file = getattr(module, "__file__", None)
    if module_file is None or Path(module_file).resolve() != app_file:
        return

    if not app_class.package:
        app_class.package = derive_package_name(app_file)
    if not app_class.name:
        app_class.name = (
            _source_stem(app_file).replace("_", " ").replace("-", " ").title()
        )
    if not app_class.root_url:
        app_class.root_url = app_class.package.replace("_", "-")
    if not getattr(app_class, "exit_url", None):
        app_class.exit_url = "/"
    if not hasattr(app_class, "default_layout"):
        app_class.default_layout = "NavHeader"
    if not hasattr(app_class, "nav_links"):
        app_class.nav_links = "auto"


def harvest_express_app():
    """
    Load the single-file app pointed to by the TETHYS_EXPRESS_APP environment variable and
    register it under the ``tethysapp`` namespace so the harvester can find it.

    Returns:
        str or None: the app package name, or None if not running in express mode.
    """
    app_file = get_express_app_file()
    if app_file is None:
        return None

    _ensure_tethysapp_namespace()

    package = get_express_package_name(app_file)
    module_name = f"tethysapp.{package}.app"
    if module_name in sys.modules:
        return package

    try:
        _load_express_module(package, module_name, app_file)
    except Exception:
        for name in (module_name, f"tethysapp.{package}"):
            sys.modules.pop(name, None)
        tethys_log.exception(
            f'Express app "{app_file}" not loaded because of the following error:'
        )
        print(
            f'\033[91mError: The app "{app_file}" could not be loaded. '
            f"See the error above for details.\033[0m"
        )
        raise SystemExit(1)

    return package


def _ensure_tethysapp_namespace():
    """
    Make ``import tethysapp`` work even when no apps are installed in the environment.
    """
    try:
        import tethysapp  # noqa: F401
    except ImportError:
        namespace_spec = ModuleSpec("tethysapp", None, is_package=True)
        sys.modules["tethysapp"] = module_from_spec(namespace_spec)


def _load_express_module(package, module_name, app_file):
    """
    Load the app file as the module ``tethysapp.<package>.app`` and register it (and a
    synthetic parent package) in ``sys.modules`` so it imports and reloads like an
    installed app.
    """
    # import here to prevent circular imports
    from tethys_apps.base import controller as controller_module
    from tethys_apps.base.component_base import ComponentBase

    package_name = f"tethysapp.{package}"
    package_spec = ModuleSpec(package_name, None, is_package=True)
    package_spec.submodule_search_locations = [str(app_file.parent)]
    package_module = module_from_spec(package_spec)

    module_spec = spec_from_file_location(module_name, app_file)
    module = module_from_spec(module_spec)

    sys.modules[package_name] = package_module
    sys.modules[module_name] = module

    controllers_before = len(controller_module.app_controllers_list)
    module_spec.loader.exec_module(module)
    package_module.app = module

    app_class = None
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if (
            issubclass(obj, ComponentBase)
            and obj is not ComponentBase
            and obj.__module__ == module_name
        ):
            app_class = obj
            break

    if app_class is None:
        raise TypeError(
            f'No app class found in "{app_file}". A Tethys express app must define a '
            f"class that subclasses ComponentBase (from tethys_sdk.components)."
        )

    # Default the index to the first page defined in the file
    if not app_class.index:
        registered_pages = controller_module.app_controllers_list[controllers_before:]
        if registered_pages:
            app_class.index = registered_pages[0]["name"]

    return app_class
