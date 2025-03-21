***************************************
Part 3 Primer: Publishing and Deploying
***************************************

**Last Updated:** July 2024

Publishing and deploying your Tethys app to a production Tethys Portal server are the final steps in the life cycle of a Tethys app. Unfortunately, deploying is also one of the more challenging aspects of Tethys development. Many of the challenges of installing apps in production can be avoided through preparation and experience. In this tutorial you will learn how to prepare the Earth Engine app for publishing and deployment. You will then publish the app on GitHub and deploy the app on a production Tethys Portal server.

This primer provides simple explanations for some of the concepts you and tools you will need to be familiar with for this tutorial. It also provides links to resources you can use to learn more about each topic. It is highly recommended that you take a little time to read through some of these valuable resources resources before continuing.

Google Earth Engine Service Accounts
====================================

A service account is an account associated with an application instead of a user. Google service accounts can be granted access to certain Google APIs including the Google Earth Engine API. However, enabling the Google Earth Engine API on a service account requires manual review and approval--a process that can take days. You should apply for a service account and register it with Google Earth Engine if you have not already done so before completing this tutorial. See `Google Earth Engine - Service Accounts <https://developers.google.com/earth-engine/guides/service_account>`_ for how this is to be done.

Prepare App for Publishing
==========================

The source code for many Tethys apps are published under open source licenses through online code repositories like GitHub or BitBucket. Doing so allows others to view and reuse your code for their own applications. In the :ref:`publish_app_to_github` tutorial you will learn how to publish your app on GitHub and some of the considerations you should take into account before doing so.

Git
---

Git a version control system originally developed by the creator of Linux that allows you to track revisions of your code over time. If you are unfamiliar with git, we recommend you check out this excellent `Git Tutorial <https://learngitbranching.js.org/>`_ and review the `Git Documentation <https://git-scm.com/doc>`_.

GitHub
------

At it's heart, `GitHub <https://github.com/>`_ is a git repository publishing service. You can upload git repositories containing your code to GitHub and share it publicly. In fact there are over 100 million repositories published on GitHub. GitHub provides a lot of additional capabilities to aid in the collaborative development process including code review tools, automated testing, wikis, and even basic web hosting for documentation or a website about your code. It is important to understand the difference between Git and GitHub. See `GitHub Features <https://github.com/features>`_ to learn more about GitHub.

Open Source Licenses
--------------------

When publishing your code on a site like GitHub, you will want to consider doing so with an open source license to allow others to reuse your code. See `Open Source Initiative <https://opensource.org/licenses>`_ for a list of open source licenses.

Prepare for Deploy
==================

Deploying a Tethys app to a production Tethys Portal can be challenging without proper preparation. This primarily due to the unanticipated differences between the development and production environments and the difficulty to debug problems that arise during installation. Every app is different and will have its own challenges, but there are some common things you should do with every app before you deploy to minimize installation difficulties. Many of these topics will be demonstrated for the Earth Engine app in the :ref:`prepare_for_publish_and_deploy` tutorial.

Dependencies
------------

Ensure that all dependencies required by your app are listed in the :file:`install.yml`. Missing dependencies is a common cause of 500 errors during production app installation.

Package Data
------------

Files other than the Python scripts that are required by your app are called Package Data or Resource Files (e.g. JavaScript, CSS, Images, data files). By default, only Python files are installed when an app is installed in production. You will need to manually specify other files to be included in your :file:`setup.py`. Newer Tethys apps include all files in the :file:`templates` and :file:`static` directories automatically. Additional directories of files can be included easily using the ``find_resource_files()`` function provided by Tethys Platform.

Setup.py Metadata
-----------------

Tethys app projects are Python libraries. You should define metadata for the app in the :file:`setup.py` as you would for any Python library. This is especially true if you plan to publish your app to the Python Package Index or Conda. Some the pertinent metadata includes the version, description, author name and email, and license. You should update the version of your app every time you release the app and we recommend using `Semantic Versioning <https://semver.org/>`_. For more information on the :file:`setup.py` and semantic versioning see `Creating setup.py <https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-py>`_ and `Introduction to Semantic Versioning <https://www.geeksforgeeks.org/introduction-semantic-versioning/>`_

Installing Apps in Production
=============================

Review the :ref:`installing_apps_production` for an overview of app installation in production.
