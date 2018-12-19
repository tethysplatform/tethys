**************************
Tethys Compute Admin Pages
**************************
The Tethys Compute settings in site admin allows an administrator to manage computing clusters, oversee jobs, configure schedulers, and configure settings for computing resources.

* `Jobs`_
* `Schedulers`_

.. figure:: ../images/tethys_compute/tethys_compute_admin.png
    :width: 700px
    :align: left

**Figure 1.** Dashboard for Tethys Compute admin pages.

.. _jobs-label:

Jobs
----
Jobs represent some sort of computation that is sent from an app to a cluster using the :ref:`job-manager-label`. For each job that is created a database record is made to store some of the basic information about the job including: name, user, creation time, and status. The Jobs section in the Tethys Compute admin page allows for basic management of these database records. Jobs cannot be created in the admin pages, but they can be edited.

------------

.. _schedulers-label:


Schedulers
----------
Schedulers are HTCondor nodes that have scheduling rights in the pool they belong to. Schedulers are needed for CondorJob types (see :ref:`job-manager-label` documentation). When creating a new Scheduler there are two required settings: :ref:`scheduler-name-label` and `Host`_ ; an optional setting: `Username`_ ; and then two options for specifying authentication credentials: `Password`_ or `Private key path`_ and `Private key pass`_.

.. figure:: ../images/tethys_compute/tethys_compute_schedulers.png
    :width: 700px
    :align: left

**Figure 2.** Form for creating a new Scheduler.

.. _scheduler-name-label:

Name
....
A name to refer to the scheduler. Can be any string, but must be unique among schedulers.

Host
....
The fully qualified domain name (FQDN) or the IP address of the scheduler.

Username
........
The username that will be used to connect to the scheduler. The default username is 'root'.

Password
........
The password for the user specified by `Username`_ on the scheduler. Either a `Password`_ or a `Private key path`_ must be specified.

Private key path
................
The absolute path to the private key that is configured with the scheduler. Either a `Password`_ or a `Private key path`_ must be specified.

.. Note::
    The shortcut for the home directory: '~/' can be used and will be evaluated to the home directory of the Apache user.

Private key pass
................
The passphrase for the private key. If there is no passphrase then leave this field blank.
