.. _tethys_cookies_cmd:

cookies command
****************

.. warning::
    These commands are for development use only. Cookies are officially managed via ``cookies.yml`` 
    files stored in the code base of both Tethys Portal and its installed apps. See :ref:`cookie_consent`.

.. important::
    This command is only available if the ``django-cookie-consent`` Python module is installed.
    Otherwise, the ``tethys`` command will behave as if it does not exist.

List, create and purge both cookie groups and their respective cookies.

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: cookies