****************
Configuring Apps
****************

**Last Updated:** May 21, 2014

A Tethys App is an extension of the CKAN webpage. The Tethys Apps plugin uses the :term:`app configuration file` (:file:`app.py`) file to configure your app and link it to CKAN. Within the :term:`app configuration file` you will find an :term:`app class`. The :term:`app class` inherits from the ``AppBase`` class that is provided by the Tethys Apps plugin. If you have generated your :term:`app package` from the scaffold, your app class name will reflect the name of your app. The :term:`app class` implements methods from ``AppBase`` that are used to make CKAN aware of the controllers, templates, resources, and other identifying characteristics that your app needs to run. There are six methods that you need to implement in your App class:

* registerApp()
* registerControllers()
* registerTemplateDirectories()
* registerPublicDirectories()
* registerResources()
* registerPersistentStores()

Each of these methods accept one argument. During app harvesting, the ``SingletonAppHarvester`` object will call each of these methods and and passes **itself** in as the argument. Your method should call the appropriate ``SingletonAppHarvester`` method on the instance that is passed into the method. A short description of each method and an example is provided with our app called "my_first_app".

.. note::
    
    It is required that your :term:`app configuration file` is located in the :term:`app package` directory as depicted in Figure 1 on the :doc:`../app_project` page. It is also required that the name of the file is "app.py".

registerApp
===========

This method is used to provide identifying information about your app to CKAN. The appropriate ``SingletonAppHarvester`` method to call is ``addApp()``. This method should be called only once.

*addApp(name, index, icon)*

* *name* = the name displayed on the app icon on the :guilabel:`Apps` library page of CKAN.
* *index* = the name of the app index controller for your app (as defined by the ``registerControllers()`` method).
* *icon* = the path to the image that will be used as your app icon.

::

    def registerApp(self, app):
        '''
        Register the app
        '''

        app.addApp(name='My First App',
                   index='my-first-app',
                   icon='my_first_app/images/icon.png')

.. note::

    Notice that the path to the image is relative to a directory with the same name as your app inside the :file:`public` directory. This convention is used to prevent conflicts with other apps. Also notice that ``registerApp()`` takes one argument called "app". The name of the argument is more of a reminder of what needs to be done. In reality, an instance of the ``SingletonAppHarvester`` is passed into **every** method as the argument. Thus, ``addApp()`` is method of the ``SingeltonAppHarvester`` instance, as are all of the methods that are called on the arguments of the register methods.

registerControllers
===================

This method is used to register the controllers of an app. The appropriate ``SingletonAppHarvester`` method to call on the argument is ``addController()``. This method may be called multiple times, once for each controller that is being registered.

*addController(name, url, controller, action)*

* *name* = the name of the controller
* *url* = the url pattern that is mapped to the controller
* *controller* = path to the controller class (use dot notation)
* *action* = the action to call on the controller for this url pattern

::

    def registerControllers(self, controllers):
        '''
        Add controllers
        '''
            
        controllers.addController(name='my-first-app-index',
                                  url='my-first-app',
                                  controller='my_first_app.controllers.index:RootController',
                                  action='index')
            
        controllers.addController(name='my-first-app-action',
                                  url='my-first-app/{action}',
                                  controller='my_first_app.controllers.index:RootController')

In the example above, two contollers are being registered: one named "my-first-app-index" and another named "my-first-app-action". In the first controller, the action is specified while in the second controller the action is part of the url (denoted by the ``{action}`` variable).

registerTemplateDirectories
===========================

This method is used to tell the Tethys Apps plugin where your templates will be located. The appropriate ``SingletonAppHarvester`` method to call is ``addTemplateDirectory()``. Call this method only once.

*addTemplateDirectory(directory)*

* *directory* = path to the directory where your templates are located.

::

    def registerTemplateDirectories(self, templateDirs):
        '''
        Add template directories
        '''

        templateDirs.addTemplateDirectory(directory='my_first_app/templates')

registerPublicDirectories
=========================

This method is used to tell the Tethys Apps plugin where your publicly accessible resources will be stored. These include resources such as images or static documents that need to be accessible to the user. The appropriate ``SingletonAppHarvester`` method to call is ``addPublicDirectory()``. This method can be called multiple times to register multiple public directories.

*addPublicDirectory(directory)*

* *directory* = path to the directory where your public resources are located.

::

    def registerPublicDirectories(self, publicDirs):
        '''
        Add public directories
        '''
             
        publicDirs.addPublicDirectory(directory='my_first_app/public')

.. caution::

    Resources that are located in any of the public directories are made publicly accessible. Take care what you store in your public directories.

registerResources
=================

This method is used to tell the Tethys Apps plugin where your resources will be stored. Resources are served by Fanstatic. Resources that need to be registered are JavaScript and CSS files. The directories that contain these files also need to be registered as public directories (see *addPublicDirectories()* method). The appropriate ``SingletonAppHarvester`` method to call is ``addResource()``:

*addResource(directory, name)*

* *directory* = path to the directory where your resources are located.
* *name* = name of resource that is used when accessing resources

::

    def registerResources(self, staticDirs):
        '''
        Add static directories
        '''
            
        staticDirs.addResource(directory='myapp/public/myapp',
                               name='ckanapp_my_first_app')

registerPersistentStores
========================

This method is used to request persistent stores (databases) for your app. These databases are created automatically when the app is installed. In addition, you can have Tethys Apps automatically run an database initialization script to create the tables for your database when the app is installed. You may request as many of these databases as you need. Unlike the other register methods, the argument that is passed to this method is not an instance of the ``SingletonAppHarvester`` class. Instead, an instance of the ``PersistentStoreHarvester`` is given. There are two ``PersistentStoreHarvester`` methods that can be called in this method: ``addPersistentStore()`` and ``addInitializationScript``.

*addPersistentStore(store_name)*

* *store_name* =  a unique name for your persisent store. This name is used to connect to the store later.

*addInitializationScript(script_path)*

* *script_path* = the path to your database initialization script (use dot notation)

::

    def registerPersistentStores(self, persistentStores):
        '''
        Add one or more persistent stores
        '''
        persistentStores.addPersistentStore('demo_store')
        persistentStores.addInitializationScript('my_first_app.lib.init_db')

For more information about working with persistent stores, see the :doc:`./persistent_stores` section.

Example File
============

If you open the :term:`app configuration file` for your app project, you will find a file similar to this one:

::

    from ckanext.tethys_apps.lib.app_base import AppBase

    class MyFirstAppApp(AppBase):
        '''
        Example implementation of an app (this is the initializer for the app)
        '''
        
        def registerApp(self, app):
            '''
            Register the app
            '''
            
            app.addApp(name='My First App',
                       index='my_first_app',
                       icon='my_first_app/images/icon.gif')
            
            
        def registerControllers(self, controllers):
            '''
            Add controllers
            '''
            
            controllers.addController(name='my_first_app',
                                      url='my-first-app',
                                      controller='my_first_app.controllers.index:MyFirstAppController',
                                      action='index')
            
            
        def registerTemplateDirectories(self, templateDirs):
            '''
            Add template directories
            '''

            templateDirs.addTemplateDirectory(directory='my_first_app/templates')

            
        def registerPublicDirectories(self, publicDirs):
            '''
            Add public directories
            '''
             
            publicDirs.addPublicDirectory(directory='my_first_app/public')
            
        def registerResources(self, staticDirs):
            '''
            Add static directories
            '''
            
            staticDirs.addResource(directory='my_first_app/public/my_first_app',
                                   name='ckanapp_my_first_app')

        def registerPersistentStores(self, persistentStores):
            '''
            Add one or more persistent stores
            '''
            persistentStores.addPersistentStore('demo_store')
            persistentStores.addInitializationScript('my_first_app.lib.init_db')
