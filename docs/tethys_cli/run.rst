.. _tethys_run_cmd:

run command
***********

Run a single-file Tethys component app with zero configuration ("express mode"). Inspired by tools like ``shiny run`` and ``streamlit run``, this command lets you go from a single Python file to a running app in one step — no portal configuration, no database setup, no ``pip install``, and no login required.

.. important::

    This command only supports :ref:`Component Apps <tethys_components>`. Classic template-based apps are not supported.

Quick Start
===========

Create a file called :file:`app.py`:

.. code-block:: python

    from tethys_sdk.components import ComponentBase


    class App(ComponentBase):
        name = "My Dashboard"


    @App.page
    def home(lib):
        return lib.tethys.Display(
            lib.tethys.Map()
        )

Then run it:

.. code-block:: bash

    tethys run

The first run initializes an isolated environment for the app (a few seconds); then your default browser opens directly to the running app. Edits to :file:`app.py` are picked up automatically while the server is running.

Note that the app class above only sets ``name`` — and even that is optional. In express mode, any required metadata that is not defined on the app class (``package``, ``name``, ``root_url``, ``index``) is derived automatically from the file name. The same file can later be dropped unchanged into the :file:`app.py` of a scaffolded component app project to install it in a full Tethys Portal (see :ref:`scaffold command <tethys_scaffold_cmd>` and the :ref:`Component App Basics tutorial <component_app_basics_tutorial>`).

How It Works
============

``tethys run`` reuses the standard Tethys Portal runtime, configured down to serve a single app:

* An isolated ``TETHYS_HOME`` is created for each app at :file:`~/.tethys/express/<package>_<hash>/`, keyed by the absolute path of the app file. It contains a generated :file:`portal_config.yml` (single-app mode with ``ENABLE_OPEN_PORTAL``) and a SQLite database that is migrated automatically. Your normal portal configuration in ``TETHYS_HOME`` is not touched.
* The app file is loaded directly into the ``tethysapp`` namespace at server startup — it does not need to be installed as a package.
* The app is served at the site root with no login required (open portal mode). State is preserved between runs of the same file; use ``--clean`` to start fresh.

Because the standard portal machinery is used unchanged, an app developed with ``tethys run`` behaves identically when installed in a full Tethys Portal.

Arguments
=========

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: run

Examples
========

.. code-block:: bash

    # Run app.py from the current directory
    tethys run

    # Run a specific file on a specific port without opening a browser
    tethys run my_dashboard.py -p 8080 --no-browser

    # Serve on all interfaces (e.g. to share on a local network)
    tethys run --host 0.0.0.0 -p 8080

    # Discard the app's saved state (database and generated config) and start fresh
    tethys run --clean

    # Disable automatic restart on file changes
    tethys run --no-reload
