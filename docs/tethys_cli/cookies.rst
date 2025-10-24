.. _tethys_cookies_cmd:

cookies command
****************

.. important::

    This feature requires the ``django-cookie-consent`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``django-cookie-consent`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge django-cookie-consent

        # pip
        pip install django-cookie-consent

.. warning::
    These commands are for development use only. Cookies are officially managed via ``cookies.yml`` 
    files stored in the code base of both Tethys Portal and its installed apps. See :ref:`cookie_consent`.

List, create and purge both cookie groups and their respective cookies.

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: cookies