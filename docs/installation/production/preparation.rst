.. _production_preparation:

***********
Preparation
***********

**Last Updated:** May 2020

Server Access
=============

* Credentials
* Sudo / root access

Server Attributes
=================

* Public Hostname and/or IP Address of Server (e.g.: my.example.com)
    * SERVER_DOMAIN_NAME: _________________________
* SSL Certificate

Usernames and Passwords
=======================

* Portal Admin
    * PORTAL_SUPERUSER_USERNAME: _________________________
    * PORTAL_SUPERUSER_EMAIL: _________________________
    * PORTAL_SUPERUSER_PASSWORD: _________________________
* Postgres Password
    * POSTGRES_PASSWORD: _________________________
* Tethys Database User
    * TETHYS_DB_USERNAME: _________________________
    * TETHYS_DB_PASSWORD: _________________________
* Tethys Database Superuser
    * TETHYS_DB_SUPER_USERNAME: _________________________
    * TETHYS_DB_SUPER_PASSWORD: _________________________

Security Enhanced Linux (SELinux)
=================================

(see: `Security-Enhanced Linux <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_, `CentOS SELinux <https://wiki.centos.org/HowTos/SELinux>`_, `RedHat SELinux <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/deployment_guide/ch-selinux>`_)

Tips
====

* Read the Guide: Read through the entire guide before attempting your install so you can anticipate everything you will need.
* Don't Rush It: Set aside at least a full day to your production portal.
* Plan Ahead: Decide on usernames and passwords right now so you aren't tempted to use a default value.
* Do Google: Use Google or your preferred search engine to look up problems when they occur.

