from pathlib import Path
from reactpy import web
from jinja2 import Template
from re import findall
from unittest.mock import Mock
import logging

reactpy_web_logger = logging.getLogger('reactpy.web.module')
reactpy_web_logger.setLevel(logging.WARN)

TETHYS_COMPONENTS_ROOT_DPATH = Path(__file__).parent

class ComponentLibrary:
    EXPORT_NAME = 'main'
    REACTJS_VERSION = '18.2.0'
    REACTJS_DEPENDENCIES = [
        f'react@{REACTJS_VERSION}',
        f'react-dom@{REACTJS_VERSION}',
        f'react-is@{REACTJS_VERSION}',
        '@restart/ui@1.6.8'
    ]
    PACKAGE_BY_ACCESSOR = {
        'bs': 'react-bootstrap@2.10.2',
        'pm': 'pigeon-maps@0.21.6',
        'rc': 'recharts@2.12.7',
        'ag': 'ag-grid-react@32.0.2',
        'rp': 'react-player@2.16.0',
        # 'mui': '@mui/material@5.16.7',  # This should work once esm releases their next version
        'chakra': '@chakra-ui/react@2.8.2',
        'icons': 'react-bootstrap-icons@1.11.4',
        'html': None,  # Managed internally
        'tethys': None,  # Managed internally,
        'hooks': None,  # Managed internally
    }
    DEFAULTS = ['rp']
    STYLE_DEPS = {
        'ag': [
            'https://unpkg.com/@ag-grid-community/styles@32.0.2/ag-grid.css', 
            'https://unpkg.com/@ag-grid-community/styles@32.0.2/ag-theme-material.css'
        ],
        'bs': ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css']
    }
    INTERNALLY_MANAGED_PACKAGES = [key for key, val in PACKAGE_BY_ACCESSOR.items() if val is None]
    ACCESOR_BY_PACKAGE = {val: key for key, val in PACKAGE_BY_ACCESSOR.items()}
    _ALLOW_LOADING = False
    components_by_package = {}
    package_handles = {}
    styles = []
    defaults = []
    
    def __init__(self, package=None, parent_package=None):
        self.package = package
        self.parent_package = parent_package
    
    def __getattr__(self, attr):
        if attr in self.PACKAGE_BY_ACCESSOR:
            # First time accessing "X" library via lib.X (e.g. lib.bs)
            if attr == 'tethys':
                from tethys_components import custom
                lib = custom
            elif attr == 'html':
                from reactpy import html
                lib = html
            elif attr == 'hooks':
                from tethys_components import hooks
                lib = hooks
            else:
                if attr not in self.package_handles:
                    self.package_handles[attr] = ComponentLibrary(self.package, parent_package=attr)
                    if attr in self.STYLE_DEPS:
                        self.styles.extend(self.STYLE_DEPS[attr])
                lib = self.package_handles[attr]
            return lib
        elif self.parent_package:
            component = attr
            package_name = self.PACKAGE_BY_ACCESSOR[self.parent_package]
            if package_name not in self.components_by_package:
                self.components_by_package[package_name] = []
            if component not in self.components_by_package[package_name]:
                if self.parent_package in self.DEFAULTS:
                    self.defaults.append(component)
                self.components_by_package[package_name].append(component)
                module = web.module_from_string(
                    name=self.EXPORT_NAME,
                    content=self.get_reactjs_module_wrapper_js(),
                    resolve_exports=False
                )
                setattr(self, attr, web.export(module, component))        
            return getattr(self, attr)
        else:
            raise AttributeError(f"Invalid component library package: {attr}")
    
    @classmethod
    def refresh(cls, new_identifier=None):
        cls.components_by_package = {}
        cls.package_handles = {}
        cls.styles = []
        cls.defaults = []
        if new_identifier:
            cls.EXPORT_NAME = new_identifier


    @classmethod
    def get_reactjs_module_wrapper_js(cls):
        template_fpath = TETHYS_COMPONENTS_ROOT_DPATH / 'resources' / 'reactjs_module_wrapper_template.js'
        with open(template_fpath) as f:
            template = Template(f.read())

        content = template.render({
            'components_by_package': cls.components_by_package,
            'dependencies': cls.REACTJS_DEPENDENCIES,
            'named_defaults': cls.defaults,
            'style_deps': cls.styles
        })

        return content
    
    @classmethod
    def register(cls, package, accessor, styles=[], use_default=False):
        '''
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

        '''
        if accessor in cls.PACKAGE_BY_ACCESSOR:
            if cls.PACKAGE_BY_ACCESSOR[accessor] != package:
                raise ValueError(f"Accessor {accessor} already exists on the component library. Please choose a new accessor.")
            else:
                return
        cls.PACKAGE_BY_ACCESSOR[accessor] = package
        if styles:
            cls.STYLE_DEPS[accessor] = styles
        if use_default:
            cls.DEFAULTS.append(accessor)

    def load_dependencies_from_source_code(self, source_code):
        ''' Pre-loads dependencies rather than on-the-fly
        
        This is necessary since loading on the fly does not work
        for nested custom lib components being rendered for the first time after the initial 
        load. I spent hours trying to solve the problem of getting the ReactPy-Django Client
        to re-fetch the Javascript containing the updated dependnecies, but I couldn't solve
        it. This was the Plan B - and possibly the better plan since it doesn't require a change
        to the ReactPy/ReactPy-Django source code.
        '''
        matches = findall('lib\\.([^\\(]*)\\(', source_code)
        for match in matches:
            package_name, component_name = match.split('.')
            if package_name in self.INTERNALLY_MANAGED_PACKAGES: continue
            package = getattr(self, package_name)
            getattr(package, component_name)


Library = ComponentLibrary()
