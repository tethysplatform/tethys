***************
Quotas Concepts
***************

**Last Updated:** April 2019

This tutorial introduces Tethys Quotas API concepts for Tethys developers. The topics covered include:

* Workspace Quotas
* Creating custom quotas
* Enforcing quotas
* Managing quotas
* Extended concepts from previous tutorials


0. Start From Advanced Solution (Optional)
==========================================

If you wish to use the advanced solution as a starting point:

::

    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout advanced-solution

1. Workspace Quotas
===================

In the :doc:`./advanced` tutorial we refactored the Model to use an SQL database, rather than files. However, we might want to store some data as files in case we want to export them later. This will also allow us to demonstrate the use of the built-in workspace qutoas that come with the :doc:`../../tethys_sdk/tethys_quotas`.

a.Add the :ref:`user_workspace` decorator and a `user_workspace` argument to the ``assign_hydrograph`` controller. Write the hydrograph CSV with the dam id prepended to the filename to the user's workspace. The prepended id will be used later when handling a user deleting a dam they have created.

::

    import os
    from tethys_sdk.workspaces import user_workspace

    ...

    @user_workspace()
    @login_required()
    def assign_hydrograph(request, user_workspace):
        """
        Controller for the Add Hydrograph page.
        """
    ...

            if not has_errors:
                # Process file here
                hydrograph_file = hydrograph_file[0]
                success = assign_hydrograph_to_dam(selected_dam, hydrograph_file)

                # Remove csv related to dam if exists
                for file in os.listdir(user_workspace.path):
                    if file.startswith("{}_".format(selected_dam)):
                        os.remove(os.path.join(user_workspace.path, file))

                # Write csv to user_workspace to test workspace quota functionality
                full_filename = "{}_{}".format(selected_dam, hydrograph_file.name)
                with open(os.path.join(user_workspace.path, full_filename), 'wb+') as destination:
                    for chunk in hydrograph_file.chunks():
                        destination.write(chunk)
                    destination.close()

                # Provide feedback to user

    ...

b. Go to the :ref:`tethys_quotas_resource_quota` section of the admin pages and edit the ``User Workspace Quota`` as follows (must be done on administrator account):

* Default - ``2e-07`` (measured in GB so this converts to 214 bytes which allows for storing about 2 hydrographs to test the quota)
* Active - ``Enabled``
* Impose default - ``Enabled``

c. To test, assign ``hydrograph2.csv`` and ``hydrograph4.csv`` (from :ref:`Sample Hydrographs <sample_hydrographs>`) to two separate dams through the app and then try to go back and assign a third hydrograph (all of this must be done on a non-administrator account). You should get an error page that advises you to visit the storage management pages and clean workspaces. Do this now (see :ref:`tethys_quotas_user_manage` for help) and try again to assign a hydrograph. Because your user workspace is clear you should be able to assign another hydrograph.

.. note::

    Quotas are not enforced on administrator users (i.e. staff/superusers). To manage quotas, login as administrator, but to test them, login as a normal user.

d. Now that hydrograph files are stored to the user's workspace and the user can clear said workspace through their settings page, we will want to do some extra processing when they actually do clear their workspace. If the user deletes their hydrograph files we also want to remove the related hydrographs from the database.

First add ``user_id = Column(Integer)`` as a column in the Dam model class. Also add ``cascade="all,delete"`` as an argument to the `hydrograph` relationship in the ``Dam`` model class and the `points` relationship in the ``Hydrograph`` model class.

::

    class Dam(Base):
        """
        SQLAlchemy Dam DB Model
        """
        __tablename__ = 'dams'

        # Columns
        id = Column(Integer, primary_key=True)
        latitude = Column(Float)
        longitude = Column(Float)
        name = Column(String)
        owner = Column(String)
        river = Column(String)
        date_built = Column(String)
        user_id = Column(Integer)

        # Relationships
        hydrograph = relationship('Hydrograph', cascade="all,delete", back_populates='dam', uselist=False)


        class Hydrograph(Base):
        """
        SQLAlchemy Hydrograph DB Model
        """
        __tablename__ = 'hydrographs'

        # Columns
        id = Column(Integer, primary_key=True)
        dam_id = Column(ForeignKey('dams.id'))

        # Relationships
        dam = relationship('Dam', back_populates='hydrograph')
        points = relationship('HydrographPoint', cascade="all,delete", back_populates='hydrograph')

.. note::

    Adding ``cascade="all,delete"`` as an argument in an sqlalchemey model relationship causes the deletion of related records to be handled automatically. In this case, if hydrograph is removed from the database the hydrograph's points will also be deleted and if a dam is removed the connected hydrograph and its points will be removed.

Then modify the ``add_new_dam`` function like so:

::

    def add_new_dam(location, name, owner, river, date_built, user_id):
        """
        Persist new dam.
        """

        ...

        # Create new Dam record
        new_dam = Dam(
            latitude=latitude,
            longitude=longitude,
            name=name,
            owner=owner,
            river=river,
            date_built=date_built,
            user_id=user_id,
        )

        # Get connection/session to database

        ...

e. Add ``user_id=-1`` when initializing ``dam1`` and ``dam2`` in the ``init_primary_db`` function.

::

    def init_primary_db(engine, first_time):

        ...

            # Initialize database with two dams
            dam1 = Dam(
                latitude=40.406624,
                longitude=-111.529133,
                name="Deer Creek",
                owner="Reclamation",
                river="Provo River",
                date_built="April 12, 1993",
                user_id=-1,
            )

            dam2 = Dam(
                latitude=40.598168,
                longitude=-111.424055,
                name="Jordanelle",
                owner="Reclamation",
                river="Provo River",
                date_built="1941",
                user_id=-1,
            )

            ...

Then make the following changes to the ``add_dam`` controller:

::

    @permission_required('add_dams')
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """

    ...

                user_id = request.user.id

                # Only add the dam if we have not exceed max_dams
                if not max_dams or num_dams < max_dams:
                    add_new_dam(location=location, name=name, owner=owner, river=river, date_built=date_built,
                                user_id=user_id)
                else:

    ...

Now that we have changed the model in the persistent store we will need to re-run ``$ tethys syncstores dam_inventory`` through the command line.

.. important::

    Don't forget to run ``$ tethys syncstores dam_inventory``!

f. Modify the ``assign_hydrograph`` controller again, this time to only allow users to assign hydrographs to dams that they have created.

::

    import os
    from tethys_sdk.workspaces import user_workspace

    ...

    @user_workspace()
    @login_required()
    def assign_hydrograph(request, user_workspace):
        """
        Controller for the Add Hydrograph page.
        """
    ...

        # Get dams from database
        Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
        session = Session()
        dams = session.query(Dam).filter(Dam.user_id == request.user.id)

        # Defaults

    ...

g. Finally, override the ``pre_delete_user_workspace`` method that was added with the :doc:`../../tethys_sdk/tethys_quotas`. Add this to ``app.py``:

::

    @classmethod
    def pre_delete_user_workspace(cls, user):
        from .model import Dam
        Session = cls.get_persistent_store_database('primary_db', as_sessionmaker=True)
        session = Session()

        # Delete all hydrographs connected to dams created by user
        dams = session.query(Dam).filter(Dam.user_id == user.id)

        for dam in dams:
            if dam.hydrograph:
                session.delete(dam.hydrograph)

        session.commit()
        session.close()

2. Custom Dam Quota
===================

With the changes we made to the Dam model, we can now associate each dam with the user that created it and track how many dams each user created. In this part of the tutorial we will create a custom quota to restrict the number of dams a user can create. This will effectively replace the work we did in previous tutorials with the custom setting, `max_dams`. Instead of limiting the number of dams for the whole app through a custom setting we will restrict it per user with a custom quota.

.. note::

    Restricting the number of dams over the whole app could also be achieved through a custom quota instead of a custom setting. After this tutorial, try to create a custom quota that does the same thing as the custom setting to get more experience with quotas!

a. Creating a custom quota is pretty simple. Create a new file called ``dam_quota_handler.py`` and add the following contents:

::

    from tethys_quotas.handlers.base import ResourceQuotaHandler
    from .model import Dam
    from .app import DamInventory as app


    class DamQuotaHandler(ResourceQuotaHandler):
        """
        Defines quotas for dam storage for the persistent store.

        inherits from ResourceQuotaHandler
        """
        codename = "dam_quota"
        name = "Dam Quota"
        description = "Set quota on dam db entry storage for persistent store."
        default = 3  # number of dams that can be created per user
        units = "dam"
        help = "You have exceeded your quota on dams. Please visit the dams page and remove unneeded dams."
        applies_to = ["django.contrib.auth.models.User"]

        def get_current_use(self):
            """
            calculates/retrieves the current number of dams in the database

            Returns:
                Int: current number of dams in database
            """
            # Query database for count of dams
            Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()
            current_use = session.query(Dam).filter(Dam.user_id == self.entity.id).count()

            session.close()

            return current_use

.. note::

    See :ref:`tethys_quotas_rqh` for an explanation of the different parameters.

b. Now go into the portal's ``settings.py`` file and add the dot-path of the handler class you just created in the ``RESOURCE_QUOTA_HANDLERS`` array.

::

    # RESOURCE QUOTAS TO INSTALL
    RESOURCE_QUOTA_HANDLERS = [
        "tethys_quotas.handlers.workspace.WorkspaceQuotaHandler",
        "tethysapp.dam_inventory.dam_quota_handler.DamQuotaHandler",
        # your path `may` be different
    ]

c. After re-starting tethys the ``User Dam Quota`` should be visible in the ``Resource Quota`` section of the admin pages. Click on it and make sure `Active` and `Impose default` are both ``Enabled``.

.. figure:: ../../images/tutorial/quotas/ResourceQuotaView.png
    :width: 600px
    :align: center

d. Go into the app's settings page through the portal admin pages and delete the value for ``max_dams`` in the ``CUSTOM SETTINGS`` section. This will ensure that our custom quota is handling the amount of dams that can be added instead of the custom setting.

.. figure:: ../../images/tutorial/quotas/MaxDamsView.png
    :width: 600px
    :align: center

e. To enforce the new dam quota import the ``@enforce_quota`` decorator and add it to the ``add_dam`` controller.

::

    from tethys_sdk.quotas import enforce_quota

    ...

    @enforce_quota('user_dam_quota')
    @permission_required('add_dams')
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """

    ...

.. note::

    We used the codename ``user_dam_quota`` instead of just ``dam_quota`` because Tethys Quotas appends what the quota ``applies_to`` (from the :ref:`tethys_quotas_rqh` class parameters) to the codename to differentiate between quotas on users or on apps.

    If we wanted to enforce our custom dam quota on an app as a whole we would need to add ``"tethys_apps.models.TethysApp"`` to the ``applies_to`` parameter in our ``DamQuotaHandler`` and then change the codename to ``tethysapp_dam_quota``.

f. You can now test this by logging into a non-administrator account and trying to create more than 3 dams. You should be taken to another error page telling you that you have reached the limit on dams you can create.

3. Dam Quota Management
=======================

As is, the app would never allow a user to add a new dam once the quota was reached unless the portal administrator changed the dam quota default value (or made the quota inactive) or removed dams created by that user from the database. We will now add a way for a user to remove dams they have created through the ``list_dams`` controller.

a. Add this ``delete_dam`` url map to ``app.py``:

::

    UrlMap(
        name='delete_dam',
        url='dam-inventory/delete_dam/{dam_id}',
        controller='dam_inventory.controllers.delete_dam'
    ),

b. Create the ``delete_dam`` function in ``controllers.py``:

::

    @user_workspace()
    @login_required()
    def delete_dam(request, user_workspace, dam_id):
        """
        Controller for the deleting a dam.
        """
        Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
        session = Session()

        # Delete hydrograph file related to dam if exists
        for file in os.listdir(user_workspace.path):
            if file.startswith("{}_".format(int(dam_id))):
                os.remove(os.path.join(user_workspace.path, file))

        # Delete dam object
        dam = session.query(Dam).get(int(dam_id))
        session.delete(dam)
        session.commit()
        session.close()

        messages.success(request, "{} Dam has been successfully deleted.".format(dam.name))

        return redirect(reverse('dam_inventory:dams'))

c. Refactor the ``list_dams`` controller to add a `Delete` button for each dam. The code will restrict user's to deleting only dams that they created.

::

    @login_required()
    def list_dams(request):
        """
        Show all dams in a table view.
        """
        dams = get_all_dams()
        table_rows = []

        for dam in dams:

        ...

            if dam.user_id == request.user.id:
                url = reverse('dam_inventory:delete_dam', kwargs={'dam_id': dam.id})
                dam_delete = format_html('<a class="btn btn-danger" href="{}">Delete Dam</a>'.format(url))
            else:
                dam_delete = format_html('<a class="btn btn-danger disabled" title="You are not the creator of the dam" '
                                         'style="pointer-events: auto;">Delete Dam</a>')

            table_rows.append(
                (
                    dam.name, dam.owner,
                    dam.river, dam.date_built,
                    dam_hydrograph, dam_delete
                )
            )

        dams_table = DataTableView(
            column_names=('Name', 'Owner', 'River', 'Date Built', 'Hydrograph', 'Manage'),
            rows=table_rows,
            searching=False,
            orderClasses=False,
            lengthMenu=[[10, 25, 50, -1], [10, 25, 50, "All"]],
        )

        ...

d. Test by deleting a dam or two (while logged in as the non-administrator) and trying to add new dams. This time you shouldn't be redirected to the error page, but should be able to add a dam like normal because you brought the number of dams created by the current user below the quota's default value.

4. Solution
===========

This concludes the Quotas Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

::

    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout quotas-solution
