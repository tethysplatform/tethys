'''
********************************************************************************
* Name: New App Paste Template/Scaffold
* Author: Nathan Swain
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer
from paste.script.create_distro import Command
import sys

# Horrible hack to change the behaviour of Paste itself
# Since this module is only imported when commands are
# run, this will not affect any other paster commands.
import re
Command._bad_chars_re = re.compile('[^a-zA-Z0-9_-]')

class CkanappTemplate(Template):

    """
    Template to build a skeleton Tethys Apps package
    """

    _template_dir = 'template/'
    summary = 'CKAN extension project template'
    template_renderer = staticmethod(paste_script_template_renderer)

    vars = [
        var('proper_name', 'e.g.: "My App" for project name "myapp"'),
        var('version', 'Version (like 0.1)'),
        var('description', 'One-line description of the app'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name'),
    ]

    def check_vars(self, vars, cmd):
        vars = Template.check_vars(self, vars, cmd)
        if not vars['project'].startswith('ckanapp-'):
            print "\nError: Expected the project name to start with 'ckanapp-'"
            sys.exit(1)
        vars['project'] = vars['project'][len('ckanapp-'):]
        vars['proper_no_spaces'] = ''.join(vars['proper_name'].split())
        vars['project_url'] = '-'.join(vars['proper_name'].split()).lower()
        return vars
