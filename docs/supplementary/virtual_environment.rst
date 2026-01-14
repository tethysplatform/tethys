.. _virtual_environment:

*******************
Virtual Environment
*******************

**Last Updated:** April 2025

A virtual environment provides an isolated environment that allows unique dependencies to be maintained separately
from other environments. For example, if you have multiple projects that all depend on Python, but each has a 
different set of dependencies - including different versions of some of the same packages - then having a separate 
virtual environment for each project would not only make sense, but be required since all these projects could not 
each have their dependencies met and coexist within the same environment.

There are various tools for creating and managing virtual environments for Python. For the sake of an introduction in the context of
Tethys Platform, we will provide specific instructions and context for two: `conda <https://docs.conda.io/projects/conda/en/stable/>`_ and `venv <https://docs.python.org/3/library/venv.html>`_.

.. _create_environment:

Create Your Virtual Environment
-------------------------------

A virtual environment is essentially a folder that can store all of the unique dependnecies (i.e. distinctly versioned packages) of your environment. With ``conda``, this folder is managed by ``conda`` itself and should not need to be known or hunted down. With ``venv`` you explicitly choose the location of this folder.

|

.. tabs::

    .. group-tab:: Conda

        Requires `Miniconda <https://www.anaconda.com/docs/getting-started/miniconda/install>`_ or `Anaconda <https://www.anaconda.com/docs/getting-started/anaconda/install>`_

        .. tip::

            Windows Users: Use the Anaconda Powershell Prompt application for your command line

        .. code-block:: bash

            conda create -n <name>
        
        |
        
        Where ``<name>`` can be anything alphanumeric, including hyphens and underscores, but no whitespace. We recommend you choose the name of the project that the environment is for, so in this case you could go with ``tethys``.
        The created environment is stored in a location managed by ``conda`` that you should not need to hunt down.
    
    .. group-tab:: Pip (Windows)

        Requires Python >= 3.3

        .. code-block:: bash

            python -m venv <path>
        
        |
        
        Where ``<path>`` is the absolute or relative path to a folder that will be created to store your environment. You could use ``tethys`` to create this folder in the directory your command line is currently in (i.e. ``.\tethys``).
    
    .. group-tab:: Pip (Linux)

        Requires Python >= 3.3

        .. code-block:: bash

            python -m venv <path>
        
        |
        
        Where ``<path>`` is the absolute or relative path to a folder that will be created to store your environment. You could use ``tethys`` to create this folder in the directory your command line is currently in (i.e. ``./tethys``).
    

.. _activate_environment:

Activate Your Virtual Environment
---------------------------------

Activating a virtual environment essentially switches the context of your command line to that of the specified environment, meaning that when fetching dependencies it will check for them in the active
environment's folder first.

|

.. tabs::

    .. group-tab:: Conda

        .. code-block:: bash

            conda activate <name>
        
        |
        
        Where ``<name>`` is what you chose during :ref:`create_environment` above (e.g. ``tethys``).
    
    .. group-tab:: Pip (Windows)

        .. code-block:: bash

            <path>\Scripts\activate
        
        |
        
        Where ``<path>`` is what you chose during :ref:`create_environment` above (e.g. ``tethys`` [i.e. ``.\tethys``]).
    
    .. group-tab:: Pip (Linux)

        .. code-block:: bash

            source <path>/bin/activate
        
        |
        
        Where ``<path>`` is what you chose during :ref:`create_environment` above (e.g. ``tethys`` [i.e. ``./tethys``]).

.. warning::

    If you forget to activate your virtual environment before executing commands that depend upon it, you'll encounter errors such as the following:

    |

    .. tabs::

        .. tab:: Windows

            .. code-block:: bash

                > tethys start
                'tethys' is not recognized as an internal or external command,
                operable program or batch file.
        
        .. tab:: Linux

            .. code-block:: bash

                $ tethys start
                sh: tethys: command not found

Deactivate Your Virtual Environment
-----------------------------------

Deactivating a virtual environment essentially switches the context of your command line back to the environment you were in prior (usually the default system environment). This leaves your command line as if you had never activated the virtual environment in the first place.

|

.. tabs::

    .. group-tab:: Conda

        .. code-block:: bash

            conda deactivate <name>
        
        |
        
        Where ``<name>`` is what you chose when Creating a Virtual Environment (e.g. ``tethys``).
    
    .. group-tab:: Pip (Windows)

        .. code-block:: bash

            deactivate
    
    .. group-tab:: Pip (Linux)

        .. code-block:: bash

            deactivate
