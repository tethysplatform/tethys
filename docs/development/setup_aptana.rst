*************************
Using Aptana Studio 3 IDE
*************************

**Last Updated:** May 22, 2014

**UNDER CONSTRUCTION**

You are welcome to use any IDE or text editor that you are comfortable with for developing. One IDE that we have found works well for Tethys App development is called Aptana. It is based on Eclipse, but it is optimized for web development and it comes with the excellent PyDev plugin installed out of the box for developing in Python web applications. There are a few steps that need to be followed to import a new app project into Aptana and set it up for Python development. These steps will be outlined here for convenience. In this tutorial, we will assume that we have created a new app called "my_first_app" located in the :file:`~/tethysdev/ckanapp-my_first_app` directory.

Install Aptana Studio
=====================

Use `these <http://www.samclarke.com/2012/04/how-to-install-aptana-studio-3-on-ubuntu-12-04-lts-precise-pangolin/>`_. instructions for installing Aptana Studio in Ubuntu 12.04.

.. _aptana-setup-interpreter:

Setup Python Interpreter
========================

If you have a fresh installation of Aptana Studio, you will need to create a new Python Interpreter Configuration that uses your CKAN Python virtual environment. All of your apps will use the CKAN Python interpreter for intellisense and running scripts.This will only need to be done once for new workspaces.

1. Open Aptana Studio and select/create a workspace if prompted.

2. From the menu, select **window** | **preferences**.

3. Expand the **PyDev** menu and select **Interpreter-Python** from the list on the left-hand side of the window that appears. It should look similar to :ref:`aptana-figure-1`.

.. _aptana-figure-1:

.. figure:: ../images/aptana-configure-python.png
    :alt: screenshot of Aptana Studio preferences with PyDev interpreter selected
    :figwidth: 80%
    :align: center

    Figure 1. Screenshot of Aptana Studio preferences with PyDev interpreter selected

4. If now interpreter is configured for your CKAN Python, select the **New** button.

5. In the dialog window that appears set the *Interpreter Name* to "CKAN", **Browse** to the location of your CKAN Python executable (:file:`/usr/lib/ckan/default/bin/python`, and press **OK** (see :ref:`aptana-figure-2`).

.. _aptana-figure-2:

.. figure:: ../images/aptana-select-interpreter.png
    :alt: screenshot of the select interpreter dialog
    :figwidth: 80%
    :align: center

    Figure 2. Screenshot of the select interpreter dialog.

6. The "Selection needed" dialog should appear. Press the **Select All** button and then **OK**.

7. You should now see a Python interpreter listed for CKAN in the Python Interpreters window. Press **Apply** and then **OK** to exit the dialog.


Import App Project
==================

After you have generated a new app using the scaffold (see :doc:`../getting_started/scaffold`), you will need to **import** the :term:`app project` into Aptana to start working with it.This process will need to be done for every app that you develop.

1. Select **File** | **Import...** from the dropdown menu.

2. Exand the **General** menu and select the **Existing Folder as New Project** option from the *Import* wizard that appears (see :ref:`aptana-figure-3`. Press the **Next** button to continue.

.. _aptana-figure-3:

.. figure:: ../images/import-wizard-select-source.png
    :alt: screenshot of the import wizard select source step
    :figwidth: 80%
    :align: center

    Figure 3. Screenshot of Import wizard select source step.

3. Press the **Browse** button in the *Promote to Project* dialog that appears and browse to your app project (e.g.: :file:`~/tethysdev/ckanapp-my_first_app`). Select the :file:`ckanapp-my_first_app` directory and press **OK**. The dialog should look similar to :ref:`aptana-figure-4` when you are done.

.. _aptana-figure-4:

.. figure:: ../images/import-wizard-promote-project.png
    :alt: screenshot of the import wizard promote to project step
    :figwidth: 80%
    :align: center

    Figure 4. Screenshot of Import wizard promote to project step

4. Press the **Finish** button to exit the dialog.

Your :term:`app project` should now be imported, however, there are a few more steps that need to be done to set it up as a Python project. Examine the left hand side of the Aptana window. You should see two tabs: **App Explorer** and **Project Explorer**. Select the **Project Explorer** tab. You should see your :term:`app project` listed in the **Project Explorer** tab if it has been imported correctly. You can expand your project to see the files it contains (see :ref:`aptana-figure-5`).

.. _aptana-figure-5:

.. figure:: ../images/aptana-project-explorer.png
    :alt: screenshot of the project explorer
    :figwidth: 50%
    :align: center

    Figure 5. Screenshot of Project Explorer


Setup PyDev Project
===================

In this step we configure the project we have imported as a PyDev project to enable the Python IDE functionality of Aptana Studio.

1. Select the **Project Explorer** tab in the window on the left hand side of the Aptana window.

2. Right-click on the top directory of your :term:`app project` (e.g.: :file:`ckanapp-my_first_app`). In the context menu that appears, point to **PyDev** and select **Set as PyDev Project**.

3. Right-click on your :term:`app project` directory again and select **Properties** from the context menu.


Configure Python Interpreter
----------------------------

4. Select **PyDev-Interpreter/Grammar** from the list on the left-hand side of the *Properties* window.

5. Select **Python** as the *project type*, **2.7** as the *Grammar Version*, and **CKAN** as the *Interpreter* (see :ref:`aptana-figure-6`). If **CKAN** is not listed as an option in the *Interpreter* select box, exit the dialog and perform the steps in the :ref:`aptana-setup-interpreter` of this document.

6. Press the **Apply** button.

.. _aptana-figure-6:

.. figure:: ../images/aptana-pydev-interpreter.png
    :alt: screenshot of the PyDev interpreter and grammar dialog
    :figwidth: 80%
    :align: center

    Figure 6. Screenshot of the PyDev interpreter and grammar dialog


Configure Python Path
---------------------

7. With the *Properties* window still open, select **PyDev-PYTHONPATH** from the list on the left-hand side.

8. In the **Source Folders** tab, select the **Add source folder** button.

9. Select your :term:`app project` directory (e.g.: :file:`ckanapp-my_first_app`) and press **OK** (see :ref:`aptana-figure-7`).

.. _aptana-figure-7:

.. figure:: ../images/aptana-select-source-folder.png
    :alt: screenshot of select source folder dialogs
    :figwidth: 80%
    :align: center

    Figure 7. Screenshot of the select source folder dialogs

10. Select the **External Libraries** tab. This dialog is used to referece external projects for the current project. The intellisense for Aptana will work a lot better if you set up external libraries. For an :term:`app project`, you will want to reference the Tethys Apps source and the CKAN source.

11. Select the **Add source folder** button.

12. Browse to the CKAN source directory (:file:`/usr/lib/ckan/default/src/ckan`). Select the :file:`ckan` directory and press **OK**.

13. Repeat steps 11 and 12 for the Tethys Apps source directory (:file:`/usr/lib/ckan/default/src/ckan/ckanext/tethys_apps`).

14. Your dialog should look similar to :ref:`aptana-figure-8`. Press the **Apply** button and then **OK** to exit the dialog.

.. _aptana-figure-8:

.. figure:: ../images/aptana-external-libraries.png
    :alt: screenshot of the external libraries dialog
    :figwidth: 80%
    :align: center

    Figure 8. Screenshot of the external libraries dialog

Your :term:`app project` is now configured to work with Python in Aptana Studio.

Setup a Git Repository
======================

You can use Aptana to manage a Git versioning reposistory for your project. To create a new Git repository:

1. Right-click on your :term:`app project` in the **Project Explorer** tab of Aptana.

2. Point to **Team** and select **Share Project...** from the context menu that appears.

3. In the *Configure Git Repository* dialog that appears, select the path to your project from the list box.

4. Press the **Create...** button. This will create a new Git repository in you :term:`app project` directory.

5. Press the **Finish** button.

In the **Project Explorer**, your :term:`app project` should now have a star next to it and the word "master" in brackets. The "master" in brackets next to your :term:`app project` directory indicates the current branch that you are working on (master is the default branch). If you expand your project you will see that many of the files and directories have stars on them and some of the file are highlighted red (see :ref:`aptana-figure-9`). This indicates which files and directores have *untracked* changes in them. To track the changes, we need to *commit* them to your local repository.

.. _aptana-figure-9:

.. figure:: ../images/aptana-pre-commit.png
    :alt: screenshot of the Project Explorer with uncommitted changes
    :figwidth: 60%
    :align: center

    Figure 9. Screenshot of the Project Explorer with uncommitted changes

Commit Changes
--------------

You can commit changes using Aptana Studio like so:

1. Right-click on your :term:`app project` in the **Project Explorer** tab of Aptana.

2. Point to **Team** and select **Commit...** from the context menu that appears.

3. Press the **>>** button to stage all files that have changed.

4. Write a brief commit message to describe the changes in this commit (e.g.: First commit).

5. Press the **Commit** button.

All of the stars and red highlights should disappear after the commit. 

Remote Repository
-----------------

If you have setup a remote repository, you can link your repository to it and push and pull changes using Aptana. First setup the remote repository like so:

1. Right-click on your :term:`app project` in the **Project Explorer** tab of Aptana.

2. Point to **Team** | **Remotes** and select **Add...** from the context menu that appears.

3. Give the remote a name (e.g.: origin) and enter the remote URI (e.g.: git@github.com:user/ckanapp-my_first_app.git). Press **OK**.

Push your code to the repository for the first time:

1. Right-click on your :term:`app project` in the **Project Explorer** tab of Aptana.

2. Point to **Team** | **Remotes** | **Push current branch to** and select the remote to push to (e.g.: origin) from the context menu that appears.


Push and Pull
-------------

After you have setup your remote, you can push and pull changes. Prior to a push or pull, you are required to commit your changes to your local repository. After committing:

1. Right-click on your :term:`app project` in the **Project Explorer** tab of Aptana.

2. Point to **Team** and select either **Push** or **Pull**.

There are many other features of Aptana for working with Git that will not be covered here such as managing branches and adding files to the :file:`.gitignore`.

.. _perspective-views:

Perspectives and Views
======================

Like Eclipse, the Aptana workspace is organized into views and perspectives. Views are different windows in Aptana. For example, the Project Explorer is a view. Other examples of views include the Console, Terminal, and various Editor views. There are many more view that you can add to your workspace. To add a view:

1. Select **Window** | **Show View** | **Other...**.

2. Select the desired view (e.g.: Terminal) and press **OK**.

You can select and drag views and dock them to different areas of the workspace.

A perspective is a predefined collection of views. Usually, provides the views that are needed for a particular type of development or task. The defaul perspective of Aptana is the **Web** perspective. There are also perspectives for PyDev and Debugging that come with Aptana. To switch the perspective:

1. Select **Window** | **Open Perspective** | **Other...**.

2. Select the desired perspective (e.g.: PyDev) and press **OK**.

You'll notice that the views in your workspace rearrange for the perspective. For developing apps in Aptana, we recommend using the **PyDev** perspective.

.. tip::

    Use the **PyDev** perspective when working with a Tethys Apps project in Aptana Studio.

.. tip::

    Use a **Terminal** view in Aptana to start the Paster server during development. The you can see the output from your server in the same window that you are editing your code.

Running Python Scripts
----------------------

If you have any stand alone scripts (like a database initialization script), you can run and debug them in Aptana.

1. Open a stand alone Python script (e.g.: :file:`ckanapp-my_first_app/ckanapp/my_first_app/lib/init_db.py`) using the **Project Explorer**. 

2. Follow the steps for enabling a perspective in the :ref:`perspective-views` section to switch to the **Debug** perspective.

3. Select **Run** | **Run** from the dropdown menu.

4. Select **Python Run** and press **OK** if prompted.

Alternatively, you can select **Run** | **Debug** to enable the debugging Run mode. The **Debug** perspective is configured with views that will aid you in debugging your scripts.

.. tip::

    You can also run and debug scripts using the buttons with the *play* symbol and *bug* symbols, respectively.







