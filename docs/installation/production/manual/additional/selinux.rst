.. _production_selinux_config:

***********************
Security-Enhanced Linux
***********************

**Last Updated:** September 2022

.. warning::

    What follows is given for illustration purposes only and is not meant to be our official recommendation nor is it guaranteed to work. Ultimately, if you plan to use SELinux on your Tethys Portal server, you are responsible to learn how to configure it appropriately based on your organization's policies. **USE THESE INSTRUCTIONS AT YOUR OWN RISK.**



.. note::

    The following code examples contain the following variables in angle brackets. Replace the variables with the appropriate value described here:

    * ``<TETHYS_HOME>``: Path to the Tethys home directory that you noted in the :ref:`production_portal_config` step.
    * ``<STATIC_ROOT>``: Path to the directory with the static files that you setup in the :ref:`production_static_workspaces_dirs` step.
    * ``<TETHYS_WORKSPACES_ROOT>``: Path to the directory with the app workspaces files that you setup in the :ref:`production_static_workspaces_dirs` step.

Check SELinux Enforcing Status
==============================

You can verify that SELinux is enabled by running the following command:

.. code-block::

    getenforce

If this command returns "Enforcing", as it does here, then SELinux is enabled and enforcing the extra layers of security.

To properly test SELinux, you'll need to set it to enforcing mode. This can be done like so:

.. code-block::

    setenforce 1

SELinux Labels
==============

Under SELinux, all files and processes are labeled with a type. You can view the SELinux type of files with the ``-Z`` option of the ``ls`` command. For example, check the SELinux labels for the files in the ``TETHYS_HOME`` directory as follows:

.. code-block::

    ls -Z ~/.tethys

The type is the 3rd entry, after the second colon.

Label Tethys Files
------------------

To allow NGINX to access the files in ``TETHYS_HOME`` or our static and workspace directories, we first need to label the files with the correct SELinux type.

First, label the NGINX configuration file as an HTTP config type:

.. code-block::

    sudo semanage fcontext -a -t httpd_config_t <TETHYS_HOME>/tethys_nginx.conf

Then run ``restorcon`` on the file to apply the changes:

.. code-block::

    sudo restorecon -v <TETHYS_HOME>/tethys_nginx.conf

List the directory with SELinux labels to verify the type was applied properly:

.. code-block::

    ls -Z ~/.tethys

Next, label the ``TETHYS_HOME`` and ``STATIC_ROOT`` directories as HTTP content type:

.. code-block::

    sudo semanage fcontext -a -t httpd_sys_content_t "<TETHYS_HOME>(/.*)?"
    sudo semanage fcontext -a -t httpd_sys_content_t "<STATIC_ROOT>(/.*)?"

The ``httpd_sys_content_t`` type only grants READ access by HTTP processes. Since the workspaces often are working directories for apps, we need to grant READ and WRITE access. This can be done by applying the ``httpd_sys_rw_content_t`` type as follows:

.. code-block::

    sudo semanage fcontext -a -t httpd_sys_rw_content_t "<TETHYS_WORKSPACES_ROOT>(/.*)?"

Finally, run restorecon recursively on each of the directories to apply the changes. There are quite a few files in these directories, so we'll capture the output and send it to /dev/null to prevent our console being overwhelmed with output.

.. code-block::

    sudo restorecon -R -v <TETHYS_HOME> > /dev/null
    sudo restorecon -R -v <STATIC_ROOT> > /dev/null
    sudo restorecon -R -v <TETHYS_WORKSPACES_ROOT> > /dev/null

Verify that the types are correct in the various directories using ls:

.. code-block::

    ls -Z <TETHYS_HOME>
    ls -Z <STATIC_ROOT>
    ls -Z <TETHYS_WORKSPACES_ROOT>


Label NGINX Process
-------------------

Verify that the NGINX process is labeled with the httpd type:

.. code-block::

    ps auZ | grep nginx

SELinux Policies
================

Labeling the files and processes with SELinux types is only part of the battle. Access will only be granted to the files if there is an SELinux policy that grants it. The next step we need to perform is to create an SELinux policy that does just this.

SELinux Policy for Tethys
-------------------------

Create a file called :file:`<TETHYS_HOME>/tethys-selinux-policy.te` with the following contents:

.. code-block::

    module tethys-selinux-policy 1.0;
    require {type httpd_t; type init_t; class unix_stream_socket connectto; }
    #============= httpd_t ==============
    allow httpd_t init_t:unix_stream_socket connectto;

Check and compile the SELinux security policy module into a binary representation using the ``checkmodule`` command:

.. code-block::

    checkmodule -M -m -o /home/tethys/.tethys/tethys-selinux-policy.mod /home/tethys/.tethys/tethys-selinux-policy.te

Use ``semodule_package`` to create an SELinux policy module (``.pp``) from the binary policy module (``.mod``):

.. code-block::

    semodule_package -o /home/tethys/.tethys/tethys-selinux-policy.pp -m /home/tethys/.tethys/tethys-selinux-policy.mod

Finally, install the SELinux policy module using the ``semodule`` command with the install option:

.. code-block::

    sudo semodule -i /home/tethys/.tethys/tethys-selinux-policy.pp

SELinux Troubleshooting
=======================

The following article may provide help on troubleshooting `SELinux: A sysadmin's guid to SELinux: 42 answers to the big questions <https://opensource.com/article/18/7/sysadmin-guide-selinux>`_.
