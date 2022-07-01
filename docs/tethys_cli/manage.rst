.. _tethys_manage_cmd:

manage command
**************

Manage various aspects of the underlying Tethys Platform Django project. Provides a full pass-through interface for the ``manage.py`` command.

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: manage