.. _publish_app_to_github:

**************************
Publish App Code to GitHub
**************************

**Last Updated:** July 2024

`GitHub <https://github.com/>`_ is among the most popular git repositories and is an excellent place to publish open source code. In this tutorial you will learn how to setup a new GitHub repository and push your code to it. Be sure to properly sanitize your code before pushing it to GitHub (see: :ref:`prepare_for_publish_and_deploy`).

Topics covered in this tutorial include:

* Creating GitHub repositories
* Initializing a local Git repository
* Staging, removing staged files, and committing
* .gitignore
* Adding a remote and Pushing Code to GitHub

.. figure:: ./resources/publish_solution.png
    :width: 800px
    :align: center



0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b prepare-publish-solution prepare-publish-solution-|version|

1. Create GitHub Account or Sign In
===================================

If you don't have a GitHub account yet, sign up using this link: `<https://github.com/signup>`_.

Sign in to your GitHub account using this link: `<https://github.com/login>`_. After logging in, you'll be brought to your dashboard.

2. Create GitHub Repository
===========================

Create a new repository on GitHub as follows:

1. Click on the **New** button located next to the header "Repositories", near the top of the left navigation menu.

2. Select your username as the **Owner**.

3. Enter "tethysapp-earth_engine" as the **Repository name**.

    .. note::

        It is recommended that you use the "tethysapp-" prefix on all Tethys app repositories.

4. Enter the short description for your :file:`setup.py` as the **Description**

5. Leave all other values at their default value and press the **Create repository** button.

    .. note::

        You may have noticed options to initialize your repository with a README, .gitignore, and LICENSE file. These are excellent features for setting up a repository if you don't already have code. However, **DO NOT** use these features for this tutorial.

3. Initialize Local Git Repository
==================================

Before the code can be pushed to GitHub, you will need to initialize a git repository on your local machine and commit your code to it.

1. Change into the directory containing the :file:`setup.py`:

.. code-block:: bash

    cd tethysapp-earth_engine

2. If you started from one of the previous solutions, you will need to purge the git repository before continuing

.. code-block:: bash

    rm -rf .git

3. Initialize a local git repository:

.. code-block:: bash

    git init

4. Stage all files for committing:

.. code-block:: bash

    git add .

5. Review the list of staged files:

.. code-block:: bash

    git status

6. If any of the files in the "Changes to be committed" list contain sensitive information they need to be removed. Also remove any files containing data that are not needed by the app such as Zip archives or Shapfiles that may be in the workspace directories. This can be done as follows:

.. code-block:: bash

    git rm --cached <path to file>

.. tip::

    You can used patterns in git commands to more efficiently add or remove files. For example:

    .. code-block:: bash

        git rm --cached *.json

.. warning::

    **DO NOT** commit your Google Earth Engine service account key file.

7. Once you have removed all files with sensitive data, commit the staged files as follows:

.. code-block:: bash

    git commit -m "First commit."


4. Update gitignore File
========================

The :file:`.gitignore` file is used to specify files that should not be committed or tracked by your git repository. The scaffold for Tethys apps includes a :file:`.gitignore` file with common files that should be ignored for Tethys apps. Any files that you removed in the previous step are good candidates for adding to the :file:`.gitignore`.

1. Check the status of git again:

.. code-block:: bash

    git status

2. Notice that the files that were previously staged to be committed are gone because you committed them in the last step. Any files that you removed, such as Zip files, Shapefiles, the JSON files containing your keys, or the directories containing them should be listed in the "Untracked files" section.

3. Open the :file:`.gitignore` file and add the following lines to exclude Shapefiles, Zip files, and JSON files:

.. code-block::

    *.shp
    *.dbf
    *.shx
    *.zip
    *.json

.. tip::

    You can use the keyboard shortcut **CTRL-H** in Files to toggle showing hidden files (files that begin with a ".") like the :file:`.gitignore`.

4. Check the status of git again:

.. code-block:: bash

    git status

5.  Notice that the files and directories containing the excluded files are no longer listed under "Untracked files". You should also notice that the :file:`.gitignore` file is listed under the "Changes not staged for commit" section.

6. Add any additional files to the :file:`.gitignore` to clear the "Untracked files" list.

7. Stage the :file:`.gitignore` file and commit it:

.. code-block::

    git add .gitignore
    git commit -m "Adds zip files, shapefiles, and json files to gitignore."


5. Push Code to GitHub Repository
=================================

With the code committed to your local git repository, you can push the code to GitHub.

1. Navigate to: `<https://github.com/\<USERNAME\>/tethysapp-earth_engine>`_, replacing ``<USERNAME>`` with your GitHub username.

2. Locate the code block under the heading "... or push an existing repository from the command line" and copy it.

3. Run the commands that you copied to add your GitHub repository as the remote named "origin" and then push the code. It should be similar to these commands:

.. code-block:: bash

    git remote add origin git@github.com:<USERNAME>/tethysapp-earth_engine.git
    git push -u origin main

4. You should see output similar to the following:

.. code-block:: bash

    Enumerating objects: 59, done.
    Counting objects: 100% (59/59), done.
    Delta compression using up to 12 threads
    Compressing objects: 100% (54/54), done.
    Writing objects: 100% (59/59), 2.86 MiB | 1.30 MiB/s, done.
    Total 59 (delta 3), reused 0 (delta 0)
    remote: Resolving deltas: 100% (3/3), done.
    To github.com:<USERNAME>/tethysapp-earth_engine.git
     * [new branch]      main -> main
    Branch 'main' set up to track remote branch 'main' from 'origin'.

5. Navigate to: `<https://github.com/\<USERNAME\>/tethysapp-earth_engine>`_, refreshing the page if necessary to see your code on GitHub.

.. note::

    Notice that the :file:`README.md` is automatically rendered below the list of files. If you view the **LICENSE** file, a layman's summary is provided for the license that you provided.