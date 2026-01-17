"""
********************************************************************************
* Name: library.py
* Author: Shawn Crawley
* Created On: 2024
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""

import re
from pathlib import Path
from jinja2 import Template
import logging
from functools import partial
from tethys_components import utils
from tethys_components import custom as custom_components
from importlib import import_module

logging.getLogger("reactpy.web.module").setLevel(logging.WARN)

TETHYS_COMPONENTS_ROOT_DPATH = Path(__file__).parent


class _CallableVdom(dict):
    def as_dict(self):
        return dict(self)

    def __getattribute__(self, name):
        if (
            not name.startswith("__")
            and hasattr(utils, f"_{name}_")
            and callable(getattr(utils, f"_{name}_"))
        ):
            func = partial(getattr(utils, f"_{name}_"), self)
            setattr(self, name, func)
            return func
        else:
            return super().__getattribute__(name)

    def __call__(self, *args):
        self["children"] = list(args)
        return self


class _ReCallableVdom(dict):
    def __init__(self, kwargs):
        self.func = staticmethod(kwargs.pop("__creator_func__"))
        self.kwargs = kwargs.pop("__creator_kwargs__")
        super().__init__(**kwargs)

    def __call__(self, *args):
        self.kwargs["children"] = list(args)
        return self.func(**self.kwargs)


class _CustomComponentWrapper:
    def __init__(self, vdom_func, component="", lib=None):
        self.vdom_func = vdom_func
        self.component = component

    def __call__(self, *args, **kwargs):
        if not kwargs:
            if args:
                return self.vdom_func(children=args)
            else:
                return self.vdom_func()
        elif kwargs and not args:
            for k, v in kwargs.items():
                if callable(v):
                    kwargs[k] = utils.args_to_dot_notation_dicts(v)
            vdom = self.vdom_func(**kwargs)
            vdom["__creator_func__"] = self.vdom_func
            vdom["__creator_kwargs__"] = kwargs
            return _ReCallableVdom(vdom)


class _ReactPyElementWrapper:
    def __init__(self, vdom_func, component=""):
        self.vdom_func = vdom_func
        self.component = component

    def __call__(self, *args, **kwargs):
        if args and not kwargs:
            # Classic ReactPy
            pass
        if kwargs and not args:
            for k, v in kwargs.items():
                if callable(v):
                    kwargs[k] = utils.args_to_dot_notation_dicts(v)

            args = [utils.Props(**kwargs)]
            kwargs = {}
        vdom = self.vdom_func(*args, **kwargs)
        return _CallableVdom(vdom)


class _ReactPyHTMLManager:
    """
    Substitutes for "html" in lib.html (lib.<instance of ReactPyManager>)

    Creates a new syntactical way to write ReactPy code. Instead of lib.html.<element>(Props, <children_as_args>)
    with this manager you can now do lib.html.<element>(**props_as_kwargs)(children_as_args)
    """

    def __init__(self):
        from reactpy import html

        self.html = html

    def __getattr__(self, element):
        if hasattr(self.html, element):
            return _ReactPyElementWrapper(getattr(self.html, element))


class ComponentLibraryManager:
    """
    Class for caching/managing ComponentLibrary instances, one per page
    """

    LIBRARIES = {}

    def __init__(self):
        raise RuntimeError("The ComponentLibraryManager should only be used as a class")

    @classmethod
    def get_library(cls, library_name):
        if library_name not in cls.LIBRARIES:
            cls.LIBRARIES[library_name] = ComponentLibrary(library_name)

        return cls.LIBRARIES[library_name]


class Package:
    def __init__(
        self,
        name: str,
        version: str | None = None,
        host: str = "https://esm.sh",
        default_export: str | None = None,
        dependencies: list[str] | None = None,
        treat_as_path: bool = False,
        styles: list[str] | None = None,
        accessor: str | None = None,
    ):
        if "@" in name and not name.startswith("@"):
            new_name, parsed_version = name.rsplit("@", 1)
            if version and parsed_version and version != parsed_version:
                raise ValueError(
                    'The version provided via "@" in the name argument does not match the version argument.'
                )
            elif not version and parsed_version:
                version = parsed_version
            name = new_name

        self.name = name
        self.version = version
        self.host = host
        self.default_export = default_export
        self.dependencies = dependencies or []
        self.treat_as_path = treat_as_path
        self.styles = styles or []
        self.accessor = accessor
        self._reactpy_module = None
        self._components_by_path = {}

    def add_component(self, module_path, component):
        added = False
        if module_path not in self._components_by_path:
            self._components_by_path[module_path] = []

        if component not in self._components_by_path[module_path]:
            self._components_by_path[module_path].append(component)
            added = True

        return added

    def get_components_by_path(self):
        return self._components_by_path

    def copy(self):
        kwargs = {}
        for k in dir(self):
            if k.startswith("_"):
                continue
            value = getattr(self, k)
            if not callable(value):
                kwargs[k] = value
        return Package(**kwargs)

    def compose_javascript_statements(self):
        import_statements = []
        exports_statement = ""
        for i, (module_path, components) in enumerate(
            self.get_components_by_path().items()
        ):
            module_path = f"{module_path}.js" if self.treat_as_path else module_path
            package_root = f"{self.host}/{self.name}"
            if self.version:
                package_root += f"@{self.version}"
            if i == 0:
                exports_statement += "export {"
            non_default_components = [
                c
                for c in components
                if c != self.default_export and self.default_export != "*"
            ]
            if self.default_export == "*":
                for component in components:
                    import_statements.append(
                        f"""import {component} from "{package_root}/{module_path}?deps={(',').join(ComponentLibrary.REACTJS_DEPENDENCIES + self.dependencies)}";"""
                    )
            elif self.default_export and self.default_export in components:
                import_statements.append(
                    f"""import {self.default_export} from "{package_root}/{module_path}?deps={(',').join(ComponentLibrary.REACTJS_DEPENDENCIES + self.dependencies)}";"""
                )
            if non_default_components:
                import_statements.append(
                    f"""import {{{', '.join(non_default_components)}}} from "{package_root}/{module_path}?deps={(',').join(ComponentLibrary.REACTJS_DEPENDENCIES + self.dependencies)}&exports={','.join(non_default_components)}";"""
                )
            if i > 0:
                exports_statement += ", "
            exports_statement += ", ".join(components)
        if exports_statement:
            exports_statement += "};"
        return import_statements, exports_statement


class PackageManager:
    def __init__(self, accessor_to_package_dict=None):
        if accessor_to_package_dict:
            self.add_packages(accessor_to_package_dict)

    def check_package(self, accessor, package_instance):
        if not isinstance(package_instance, Package):
            raise TypeError("The package_instance argument must be of type Package")
        if hasattr(self, accessor):
            raise ValueError(
                'The "{accessor}" accessor already exists on this PackageManager instance.'
            )

    def add_package(self, accessor, package_instance):
        self.check_package(accessor, package_instance)
        package_instance.accessor = accessor
        setattr(self, accessor, package_instance)

    def add_packages(self, accessor_to_package_dict):
        if not isinstance(accessor_to_package_dict, dict):
            raise TypeError(
                "The accessor_to_package_dict argument must be of type dict."
            )
        for accessor, package_instance in accessor_to_package_dict.items():
            self.add_package(accessor, package_instance)


class ComponentLibrary:
    """
    Class for providing access to registered ReactPy/ReactJS components
    """

    TEMPLATE_FPATH = (
        TETHYS_COMPONENTS_ROOT_DPATH
        / "resources"
        / "reactjs_module_wrapper_template.js"
    )
    TEMPLATE = Template(TEMPLATE_FPATH.read_text())
    REACTJS_VERSION = "19.0"
    REACTJS_VERSION_INT = int(REACTJS_VERSION.split(".")[0])
    REACTJS_DEPENDENCIES = [
        f"react@{REACTJS_VERSION}",
        f"react-dom@{REACTJS_VERSION}",
        f"react-is@{REACTJS_VERSION}",
    ]
    INTERNALLY_MANAGED = [
        "html",
        "tethys",
        "hooks",
        "utils",
        "Props",
        "Style",
    ]
    CURATED_PACKAGES = PackageManager(
        {
            "bs": Package(
                name="react-bootstrap@2.10.10",
                styles=[
                    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
                ],
            ),
            "pm": Package(name="pigeon-maps@0.21.6"),
            "rc": Package(name="recharts@2.12.7"),
            "ag": Package(name="react-grid-wrapper.js", host="/static/tethys_apps/js"),
            "rp": Package(name="react-player@3.4.0", default_export="ReactPlayer"),
            "lo": Package(name="react-loading-overlay-ts@2.0.2"),
            "mapgl": Package(
                name="react-map-gl/maplibre",
                version="7.1.7",
                default_export="Map",
                styles=["https://unpkg.com/maplibre-gl@4.7.0/dist/maplibre-gl.css"],
            ),
            "mui": Package(name="@mui/material@5.16.7"),
            "chakra": Package(name="@chakra-ui/react@2.8.2"),
            "icons": Package(name="react-bootstrap-icons@1.11.4"),
            "ollp": Package(
                name="layer-panel.js",
                host="/static/tethys_apps/js",
                styles=[
                    "https://esm.sh/ol-layerswitcher@4.1.2/dist/ol-layerswitcher.css",
                    "https://esm.sh/ol-side-panel@1.0.6/src/SidePanel.css",
                ],
            ),
            "pl": Package(
                name="plotly-chart.js",
                host="/static/tethys_apps/js",
            ),
            "olmod": Package(
                name="ol-mods",
                host="/static/tethys_apps/js",
                default_export="*",
                treat_as_path=True,
            ),
            "ol": Package(
                name="@planet/maps@11.2.0",
                default_export="*",
                treat_as_path=True,
                dependencies=["ol@10.7.0"],
                styles=["https://esm.sh/ol@10.7.0/ol.css"],
            ),
        }
    )

    OVERRIDES = {
        "ol.source.Vector": "olmod.source.Vector",
        "ol.source.Image": "olmod.source.Image",
        "ol.source.TileWMS": "olmod.source.TileWMS",
        "ol.layer.Vector": "olmod.layer.Vector",
        "ol.View": "olmod.View",
        "ol.Overlay": "olmod.Overlay",
        "ol.geom": utils.OlManager("ol.geom"),
        "ol.Feature": utils.OlManager("ol.Feature"),
        "ol.Style": utils.OlManager("ol.Style"),
        "ol.style": utils.OlManager("ol.style"),
        "ol.Map": "olmod.Map",
    }

    def __init__(self, name):
        self.name = name

    def __getattr__(self, package_accessor):
        """
        All library modules are created on the fly the first time.
        This enables dynamic access to ReactJS components via Python (i.e. the ReactPy web module).
        The only downside is that we can't get code suggestions nor auto-completions. The user is
        instructed and expected to refer to the official documentation for the ReactJS library.
        """
        if package_accessor in self.INTERNALLY_MANAGED:
            if package_accessor == "tethys":
                package = CustomComponentManager(self)
            elif package_accessor == "html":
                package = _ReactPyHTMLManager()
            elif package_accessor == "hooks":
                from tethys_components import hooks

                package = hooks
            elif package_accessor == "utils":
                package = utils
            elif package_accessor == "Props":
                package = utils.Props
            elif package_accessor == "Style":
                package = utils.Style
        elif hasattr(self.CURATED_PACKAGES, package_accessor):
            package = DynamicPackageManager(
                library=self,
                package=getattr(self.CURATED_PACKAGES, package_accessor).copy(),
            )
        else:
            try:
                package = import_module(package_accessor)
            except ModuleNotFoundError:
                raise AttributeError(
                    f"No package is registered at accessor {package_accessor} on {self.name} ComponentLibrary."
                )

        setattr(self, package_accessor, package)
        return package

    def render_js_template(self) -> str:
        """
        Renders the library's JavaScript module as a string

        The content of this JavaScript file was adapted from the pattern established by ReactPy,
        as documented here:
        https://reactpy.dev/docs/guides/escape-hatches/javascript-components.html#custom-javascript-components
        """
        packages = []
        for attr in dir(self):
            if attr.startswith("_"):
                continue
            value = getattr(self, attr)
            if isinstance(value, DynamicPackageManager):
                packages.append(value.package)
        context = {
            "packages": packages,
            "reactjs_dependencies": self.REACTJS_DEPENDENCIES,
            "reactjs_version_int": self.REACTJS_VERSION_INT,
        }
        content = self.TEMPLATE.render(context)

        return content

    def register(
        self,
        package,
        accessor,
        styles=None,
        default_export=None,
        treat_as_path=False,
        host="https://esm.sh",
        version=None,
    ):
        """
        Registers a new package to be used by the ComponentLibrary

        Args:
            package(str): The name of the package to register. The version is optional, and if included should be of the format "@X.Y.Z". The package must be found at https://esm.sh, and can be verified there by checking https://esm.sh/<package_name> (e.g. https://esm.sh/reactive-button)
            accessor(str): The unique name that will be used to access the package on the ComponentLibrary (i.e. the "X" in lib.X.ComponentName)
            styles(list<str>): The full URL path to styles that are required for this new component library to render correctly
            default_export(str): The name of the default export if it will be used directly

        **Examples:**

            .. code-block:: python

                @App.page
                def test_reactive_button(lib):
                    lib.register(
                        'reactive-button@1.3.15',
                        'rb',
                        default_export="ReactiveButton"
                    )
                    state, set_state = hooks.use_state('idle');

                    def on_click_handler(event=None):
                        set_state('loading')

                    return lib.rb.ReactiveButton(
                        buttonState=state,
                        idleText="Submit",
                        loadingText="Loading",
                        successText="Done",
                        onClick=on_click_handler
                    )

            .. code-block:: python

                @App.page
                def test_react_grid_layout(lib):
                    lib.register(
                        'react-grid-layout',
                        'rgl',
                        styles=[
                            'https://esm.sh/react-resizable/css/styles.css',
                            'https://esm.sh/react-grid-layout/css/styles.css'
                        ],
                        default_export="GridLayout"
                    )

                    return lib.rgl.GridLayout(...)
        """
        new_package = Package(
            name=package,
            version=version,
            styles=styles,
            default_export=default_export,
            treat_as_path=treat_as_path,
            host=host,
        )
        self.CURATED_PACKAGES.check_package(accessor, new_package)
        if hasattr(self, accessor):
            existing: DynamicPackageManager = getattr(self, accessor)
            if (
                existing.package.name != new_package.name
            ):  # Use new_package.name rather than package since it could get updated by the Package constructor
                raise EnvironmentError(
                    f"Cannot register package {package} to the {self.name} ComponentLibrary. A different package is already registered at {accessor}: {existing.package.name}"
                )
            else:
                # Already registered
                return
        new_package.accessor = accessor
        setattr(
            self, accessor, DynamicPackageManager(library=self, package=new_package)
        )

    def load_dependencies_from_source_code(self, function_or_source_code):
        """
        Pre-loads dependencies, rather than doing so on-the-fly

        This is necessary since loading on the fly does not work
        for nested custom lib components being rendered for the first time after the initial
        load. I spent hours trying to solve the problem of getting the ReactPy-Django Client
        to re-fetch the Javascript containing the updated dependnecies, but I couldn't solve
        it. This was the Plan B - and possibly the better plan since it doesn't require a change
        to the ReactPy/ReactPy-Django source code.

        Significant shortcoming: If someone has a custom component that itself has newly referenced
        library packages nested in conditional logic, these will not be picked up with this method.
        To solve this, we'd need to write a function crawler of sorts that is able to traverse the
        entire potential logic tree of a function and find all calls to the component library.

        Like the "refresh" function above, this is only called in on single place:
        tethys_apps/base/page_handler.py in the global_page_controller

        Args:
            source_code(str): The string representation of the python code to be analyzed for
                calls to the component library (i.e. "lib.X.Y")
        """
        source_code = (
            utils.inspect.getsource(function_or_source_code)
            if callable(function_or_source_code)
            else function_or_source_code
        )
        source_code = utils.remove_comments_and_docstrings(source_code)

        register_matches = re.findall(r"""lib\.register\([^\)]+\)""", source_code)
        if register_matches:
            import ast

            ast_obj = ast.parse(source_code)
            for node in ast.iter_child_nodes(ast_obj.body[0]):
                if isinstance(node, ast.Expr):
                    if isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Attribute):
                            if node.value.func.attr == "register":
                                register_args = []
                                register_kwargs = {}
                                for register_arg in node.value.args:
                                    register_args.append(ast.literal_eval(register_arg))
                                for register_kwarg in node.value.keywords:
                                    register_kwargs[register_kwarg.arg] = (
                                        ast.literal_eval(register_kwarg.value)
                                    )
                                self.register(*register_args, **register_kwargs)

        matches = re.findall(r"\blib\.([^\(]+)\(", source_code)
        for match in matches:
            try:
                path_parts = match.split(".")
                module_name = path_parts[0]

                if module_name == "register":
                    continue

                if module_name == "tethys":
                    self.load_dependencies_from_source_code(
                        getattr(custom_components, path_parts[1])
                    )

                if module_name in self.INTERNALLY_MANAGED:
                    continue
                dynamic_package_manager = getattr(self, module_name)
                for part in path_parts[1:]:
                    dynamic_package_manager = getattr(dynamic_package_manager, part)
                dynamic_package_manager()
            except Exception as e:
                print(f"Couldn't process match {match}")
                print(e)


class CustomComponentManager:
    """Wraps calls to lib.tethys to silently pass the library as the first argument to every custom component"""

    def __init__(self, library):
        self.library = library

    def __getattr__(self, attr):
        if hasattr(custom_components, attr):
            partial_func = partial(getattr(custom_components, attr), self.library)
            wrapped_func = _CustomComponentWrapper(partial_func, attr)
            setattr(self, attr, wrapped_func)
            return wrapped_func
        else:
            raise AttributeError(
                f'The tethys library does not include a component named "{attr}"'
            )


class DynamicPackageManager:

    def __init__(
        self,
        library: ComponentLibrary = None,
        package: Package = None,
        component: str = "",
    ):
        from reactpy import web

        self.library = library
        self.package = package
        self.component = component
        self.web = web

    def __getattr__(self, attr):
        component = f"{self.component}.{attr}" if self.component else attr
        override_key = f"{self.package.accessor}.{component}"
        if override_key in self.library.OVERRIDES:
            override = self.library.OVERRIDES[override_key]
            if callable(override):
                new_instance = override
            else:
                override_accessor, override_component = override.split(".", 1)
                new_instance_base = getattr(
                    self.library, override_accessor
                )  # Get or create the new instance of the override package if it does not exist
                new_instance = getattr(
                    new_instance_base, override_component
                )  # Create the new instance of the override component (a recursive call to this same __getattr__ method)
        else:
            new_instance = DynamicPackageManager(
                library=self.library, package=self.package, component=component
            )
        setattr(self, attr, new_instance)
        return new_instance

    def __call__(self, *args, **kwargs):
        component_parts = self.component.split(".")
        _component = self.component

        if self.package.accessor in ["ol", "olmod"]:
            _component += "." + component_parts[-1]
            if len(component_parts) > 1:
                _component += component_parts[-2].capitalize()

            component_parts = _component.split(".")  # Recalc in case changed

        if self.package.treat_as_path:
            component = export_component = component_parts[-1]
            module_path = (
                "" if len(component_parts) == 1 else "/".join(component_parts[:-1])
            )
        else:
            component = component_parts[0]
            export_component = ".".join(component_parts)
            module_path = ""

        added = self.package.add_component(module_path, component)
        if added:
            self.package._reactpy_module = self.web.module_from_string(
                name=self.library.name,
                content=self.library.render_js_template(),
                resolve_exports=False,
                fallback="⌛",
            )
        return _ReactPyElementWrapper(
            self.web.export(self.package._reactpy_module, export_component),
            self.package.accessor + "." + self.component,
        )(*args, **kwargs)
