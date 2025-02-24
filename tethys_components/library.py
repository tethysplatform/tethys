"""
********************************************************************************
* Name: library.py
* Author: Shawn Crawley
* Created On: 2024
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""

from pathlib import Path
from jinja2 import Template
from re import findall
import logging

logging.getLogger("reactpy.web.module").setLevel(logging.WARN)

TETHYS_COMPONENTS_ROOT_DPATH = Path(__file__).parent

class ComponentLibraryManager:
    LIBRARIES = {}

    def __init__(self):
        raise Exception("The ComponentLibraryManager should only be used as a class")

    @classmethod
    def get_library(cls, library_name):
        if library_name not in cls.LIBRARIES:
            cls.LIBRARIES[library_name] = ComponentLibrary(library_name)
        
        return cls.LIBRARIES[library_name]

class ComponentLibrary:
    """
    Class for providing access to registered ReactPy/ReactJS components
    """
    REACTJS_VERSION = "19.0"
    REACTJS_VERSION_INT = int(REACTJS_VERSION.split(".")[0])
    REACTJS_DEPENDENCIES = [
        f"react@{REACTJS_VERSION}",
        f"react-dom@{REACTJS_VERSION}",
        f"react-is@{REACTJS_VERSION}",
        # "@restart/ui@1.6.8",
    ]
    PACKAGE_BY_ACCESSOR = {
        "bs": "react-bootstrap@2.10.2",
        "pm": "pigeon-maps@0.21.6",
        "rc": "recharts@2.12.7",
        "ag": "ag-grid-react@32.2.0",
        "rp": "react-player@2.16.0",
        "lo": "react-loading-overlay-ts@2.0.2",
        "mapgl": "react-map-gl@7.1.7/maplibre",
        # 'mui': '@mui/material@5.16.7',  # This should work once esm releases their next version
        "chakra": "@chakra-ui/react@2.8.2",
        "icons": "react-bootstrap-icons@1.11.4",
        "html": None,  # Managed internally
        "tethys": None,  # Managed internally
        "hooks": None,  # Managed internally
        "utils": None,  # Managed internally
    }
    DEFAULTS = ["rp", "mapgl"]
    STYLE_DEPS = {
        "ag": [
            "https://unpkg.com/@ag-grid-community/styles@32.2.0/ag-grid.css",
            "https://unpkg.com/@ag-grid-community/styles@32.2.0/ag-theme-quartz.css",
        ],
        "bs": [
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
        ],
        "mapgl": ["https://unpkg.com/maplibre-gl@4.7.0/dist/maplibre-gl.css"],
    }
    INTERNALLY_MANAGED_PACKAGES = [
        key for key, val in PACKAGE_BY_ACCESSOR.items() if val is None
    ]

    def __init__(self, package, parent_package=None):
        self.package = package
        self.parent_package = parent_package
        self.components_by_package = {}
        self.package_handles = {}
        self.styles = []
        self.defaults = []
        
        if parent_package:
            self.components_by_package = parent_package.components_by_package
            self.package_handles = parent_package.package_handles
            self.styles = parent_package.styles
            self.defaults = parent_package.defaults
            self.PACKAGE_BY_ACCESSOR = parent_package.PACKAGE_BY_ACCESSOR
            self.STYLE_DEPS = parent_package.STYLE_DEPS
            self.DEFAULTS = parent_package.DEFAULTS

    def __getattr__(self, attr):
        """
        All instance attributes except package and parent_package are created on the fly the first time.
        This enables dynamic access to ReactJS components via Python (i.e. the ReactPy web module).
        The only downside is that we can't get code suggestions nor auto-completions. The user is
        instructed and expected to refer to the official documentation for the ReactJS library.
        """
        if attr in self.PACKAGE_BY_ACCESSOR:
            if attr == "tethys":
                from tethys_components import custom
                lib = custom
            elif attr == "html":
                from reactpy import html
                lib = html
            elif attr == "hooks":
                from tethys_components import hooks
                lib = hooks
            elif attr == "utils":
                from tethys_components import utils
                lib = utils
            else:
                if attr not in self.package_handles:
                    self.package_handles[attr] = ComponentLibrary(
                        attr, parent_package=self
                    )
                    if attr in self.STYLE_DEPS:
                        self.styles.extend(self.STYLE_DEPS[attr])
                setattr(self, attr, self.package_handles[attr])
                lib = self.package_handles[attr]
            return lib
        elif self.parent_package:
            component = attr
            package_name = self.PACKAGE_BY_ACCESSOR[self.package]
            if package_name not in self.components_by_package:
                self.components_by_package[package_name] = []
            if component not in self.components_by_package[package_name]:
                if self.package in self.DEFAULTS:
                    self.defaults.append(component)
                self.components_by_package[package_name].append(component)
                from reactpy import web

                module = web.module_from_string(
                    name=self.parent_package.package,
                    content=self.get_reactjs_module_wrapper_js(),
                    resolve_exports=False,
                )
                setattr(self, attr, web.export(module, component))
            return getattr(self, attr)
        else:
            raise AttributeError(f"Invalid component library package: {attr}")

    def get_reactjs_module_wrapper_js(self):
        """
        Creates the JavaScript file that imports all of the ReactJS components.

        The content of this JavaScript file was adapted from the pattern established by ReactPy,
        as documented here:
        https://reactpy.dev/docs/guides/escape-hatches/javascript-components.html#custom-javascript-components
        """
        template_fpath = (
            TETHYS_COMPONENTS_ROOT_DPATH
            / "resources"
            / "reactjs_module_wrapper_template.js"
        )
        with open(template_fpath) as f:
            template = Template(f.read())
        context = {
            "components_by_package": self.components_by_package,
            "dependencies": self.REACTJS_DEPENDENCIES,
            "named_defaults": self.defaults,
            "style_deps": self.styles,
            "reactjs_version_int": self.REACTJS_VERSION_INT,
        }
        content = template.render(context)

        return content

    def register(self, package, accessor, styles=None, use_default=False):
        """
        Registers a new package to be used by the ComponentLibrary

        Args:
            package(str): The name of the package to register. The version is optional, and if included
                should be of the format "@X.Y.Z". The package must be found at https://esm.sh, and can
                be verified there by checking https://esm.sh/<package_name>
                (i.e. https://esm.sh/reactive-button@1.3.15)
            accessor(str): The name that will be used to access the package on the ComponentLibrary
                (i.e. the "X" in lib.X.ComponentName)
            styles(list<str>): The full URL path to styles that are required for this new component
                library to render correctly
            use_default(bool): Whether or not the component library is accessed via its default export.

        Example:
            from tethys_sdk.components import lib

            lib.register('reactive-button@1.3.15', 'rb', use_default=True)

            # lib.rb.ReactiveButton can now be used in the code below

            @page
            def test_reactive_button():
                state, set_state = hooks.use_state('idle');

                def on_click_handler(event=None):
                    set_state('loading')

                return lib.rb.ReactiveButton(
                    Props(
                        buttonState=state,
                        idleText="Submit",
                        loadingText="Loading",
                        successText="Done",
                        onClick=on_click_handler
                    )
                )

        """
        if accessor in self.PACKAGE_BY_ACCESSOR:
            if self.PACKAGE_BY_ACCESSOR[accessor] != package:
                raise ValueError(
                    f"Accessor {accessor} already exists on the component library. Please choose a new accessor."
                )
            else:
                return
        self.PACKAGE_BY_ACCESSOR[accessor] = package
        if styles:
            self.STYLE_DEPS[accessor] = styles
        if use_default:
            self.DEFAULTS.append(accessor)

    def load_dependencies_from_source_code(self, source_code):
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
        entire

        Like the "refresh" function above, this is only called in on single place:
        tethys_apps/base/page_handler.py in the global_page_controller

        Args:
            source_code(str): The string representation of the python code to be analyzed for
                calls to the component library (i.e. "lib.X.Y")
        """
        matches = findall("\\blib\\.([^\\(]*\\.[^\\(]*)\\(", source_code)
        for match in matches:
            try:
                package_name, component_name = match.split(".")
                if package_name in self.INTERNALLY_MANAGED_PACKAGES:
                    continue
                if package_name not in self.PACKAGE_BY_ACCESSOR:
                    continue
                package = getattr(self, package_name)
                getattr(package, component_name)
            except:
                print(f"Couldn't process match {match}")

Library = None