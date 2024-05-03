.. _tethys_manage_cmd:

manage command
**************

Manage various aspects of the underlying Tethys Platform Django project. Provides a full pass-through interface for the ``manage.py`` command.

.. warning::

    The ``collectworkspaces`` and ``collectall`` commands are deprecated and will be removed in Tethys 5.0. For more information please refer to the new ref:`tethys_paths_api` documentation.

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: manage