"""
********************************************************************************
* Name: template_loaders.py
* Author: swainn
* Created On: December 14, 2015
* Copyright: (c) Aquaveo 2015
* License: 
********************************************************************************
"""
import io
import errno
from django.core.exceptions import SuspiciousFileOperation

from django.template import TemplateDoesNotExist, Origin
from django.template.loaders.base import Loader as BaseLoader
from django.utils._os import safe_join

from tethys_apps.utilities import get_directories_in_tethys_apps


class TethysAppsTemplateLoader(BaseLoader):
    """
    Custom Django template loader for tethys apps
    """

    def get_contents(self, origin):
        """
        Returns the contents of template at origin.
        """
        try:
            with io.open(origin.name, encoding=self.engine.file_charset) as fp:
                return fp.read()
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise TemplateDoesNotExist(origin)
            raise

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Return an Origin object pointing to an absolute path in each directory
        in template_dirs. For security reasons, if a path doesn't lie inside
        one of the template_dirs it is excluded from the result set.
        """
        if not template_dirs:
            template_dirs = get_directories_in_tethys_apps(('templates',))
        for template_dir in template_dirs:
            try:
                name = safe_join(template_dir, template_name)
            except SuspiciousFileOperation:
                # The joined path was located outside of this template_dir
                # (it might be inside another one, so this isn't fatal).
                continue

            yield Origin(
                name=name,
                template_name=template_name,
                loader=self,
            )

#
# def tethys_apps_template_loader(template_name, template_dirs=None):
#     """
#     Custom Django template loader for tethys apps
#     """
#     # Search for the template in the list of template directories
#     tethysapp_template_dirs = get_directories_in_tethys_apps(('templates',))
#
#     template = None
#
#     for template_dir in tethysapp_template_dirs:
#         template_path = safe_join(template_dir, template_name)
#
#         try:
#             template = open(template_path).read(), template_name
#             break
#         except IOError:
#             pass
#
#     # If the template is still None, raise the exception
#     if not template:
#         raise TemplateDoesNotExist(template_name)
#
#     return template