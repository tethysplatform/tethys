****************
Issuing Releases
****************

**Last Updated:** December 15, 2015

This article provides an overview of the procedure that should be followed to issue new releases of Tethys Platform.

1. Freeze the Dev Branch
========================

After all tasks for a release have been completed, branch the *dev* branch to a new branch with name "vX.X.0-freeze". This branch will serve as the frozen version of the *dev* branch. All of the following operations should be performed on this frozen version of the dev branch.

2. Update Version References
============================

a. Setup.py

  Update the version parameter in the :file:`setup.py` file if it was not done already.

b. Documentation

  Update the version number in the :file:`docs/conf.py` and all documentation pages that are applicable (e.g.: :file:`docs/index.rst`). Do a search for the version number on the entire :file:`docs` directory to find other places where the version number needs updating or phrasing needs to be changed to refer to the older version in past tense.

3. Update Documentation
=======================

a. What's New Page

  Move the old What's New Page content to the Prior Releases page. Add short descriptions of new features and bug fixes for the new release and link to appropriate documentation.

b. Installation Instructions

  Review installation instructions and update as necessary remembering that when the release is complete, it will be on the master branch.

c. Update Instructions

  Review update instructions from the last release and change as necessary remembering that when the release is complete, it will be on the master branch.

4. Finalize Database Migrations
===============================

Developers should not commit database migrations as they develop. *After freezing the dev branch*, perform the following steps to generate the release migrations:

a. Install the current release version of Tethys *from scratch*.
b. Pull the *frozen dev* branch and update to the new version that will be released.
c. Change into the :file:`/usr/lib/tethys/src` directory and make migrations:

  ::

      (tethys) $ python manage.py makemigrations
      (tethys) $ python manage.py migrate

d. Verify that Tethys works as expected.
e. Inspect the migrations directories of the Tethys django apps (tethys_apps, tethys_compute, tethys_config, tethys_services, etc.) for new migration files, add them to the repository, and commit them.

5. Update Repository
====================

a. Merge Frozen Dev Branch to Master Branch

  Merge the *frozen dev* branch into the *master* branch.

b. Tag the Last Commit with Release Version

  Tag the merge commit as "vX.X.0" and push to the public repository.