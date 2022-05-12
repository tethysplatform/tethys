.. _tethys_gen_cmd:

gen command
***********

Generate supporting files for Tethys installations.

.. note::

    The ``package_json`` option is designed to be used when setting the ``STATICFILES_USE_NPM`` setting to ``True``, which requires that the Tethys Portal JavaScript dependencies be served by Tethys. The ``package_json`` command will generate a :file:`package.json` and then run ``npm install`` to download the JS dependencies.

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: gen