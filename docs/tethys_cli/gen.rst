.. _tethys_gen_cmd:

gen command
***********

Generate supporting files for Tethys installations.

.. note::

    The ``vendor_js`` options is designed to be used when setting the ``STATICFILES_USE_CDN`` setting to ``False``, which requires that the Tethys Portal JavaScript dependencies be served by Tethys. The ``vendor_js`` command will generate a :file:`package.json` and then run ``npm install`` to download the JS dependencies.

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: gen