"""
********************************************************************************
* Name: app_base.py
* Author: Nathan Swain and Scott Christensen
* Created On: August 19, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""

from tethys_compute.job_manager import JobManager


class TethysAppBase(object):
    """
    Base class used to define the app class for Tethys apps.

    Attributes:
      name (string): Name of the app.
      index (string): Lookup term for the index URL of the app.
      icon (string): Location of the image to use for the app icon.
      package (string): Name of the app package.
      root_url (string): Root URL of the app.
      color (string): App theme color as RGB hexadecimal.

    """
    name = ''
    index = ''
    icon = ''
    package = ''
    root_url = ''
    color = ''

    def __repr__(self):
        """
        String representation
        """
        return '<TethysApp: {0}>'.format(self.name)

    def url_map(self):
        """
        Use this method to define the URL Maps for your app. Your ``UrlMap`` objects must be created from a ``UrlMap`` class that is bound to the ``root_url`` of your app. Use the ``url_map_maker()`` function to create the bound ``UrlMap`` class. If you generate your app project from the scaffold, this will be done automatically.

        Returns:
          iterable: A list or tuple of ``UrlMap`` objects.

        Example:

        ::

            def url_maps(self):
                \"""
                Example url_maps method.
                \"""
                # Create UrlMap class that is bound to the root url.
                UrlMap = url_map_maker(self.root_url)

                url_maps = (UrlMap(name='home',
                                   url='my-first-app',
                                   controller='my_first_app.controllers.home'
                                   ),
                )

                return url_maps
        """
        raise NotImplementedError()
    
    def persistent_stores(self):
        """
        Define this method to register persistent store databases for your app. You may define up to 5 persistent stores for an app.

        Returns:
          iterable: A list or tuple of ``PersistentStore`` objects. A persistent store database will be created for each object returned.

        Example:

        ::

            def persistent_stores(self):
                \"""
                Example persistent_stores method.
                \"""

                stores = (PersistentStore(name='example_db',
                                          initializer='init_stores:init_example_db',
                                          spatial=True
                        ),
                )

                return stores
        """
        return None

    def dataset_services(self):
        """
        Use this method to define dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``DatasetService`` objects.

        Example:

        ::

            def dataset_services(self):
                \"""
                Example dataset_services method.
                \"""
                dataset_services = (DatasetService(name='example',
                                                   type='ckan',
                                                   endpoint='http://www.example.com/api/3/action',
                                                   apikey='a-R3llY-n1Ce-@Pi-keY'
                                                   ),
                )

                return dataset_services
        """
        return None

    def spatial_dataset_services(self):
        """
        Use this method to define spatial dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``SpatialDatasetService`` objects.

        Example:

        ::

            def spatial_dataset_services(self):
                \"""
                Example spatial_dataset_services method.
                \"""
                spatial_dataset_services = (SpatialDatasetService(name='example',
                                                                  type='geoserver',
                                                                  endpoint='http://www.example.com/geoserver/rest',
                                                                  username='admin',
                                                                  password='geoserver'
                                                                  ),
                )

                return spatial_dataset_services
        """
        return None

    def wps_services(self):
        """
        Use this method to define web processing service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``WpsService`` objects.

        Example:

        ::

            def wps_services(self):
                \"""
                Example wps_services method.
                \"""
                wps_services = (WpsService(name='example',
                                           endpoint='http://www.example.com/wps/WebProcessingService'
                                           ),
                )

                return wps_services
        """
        return None

    @classmethod
    def job_templates(cls):
        """
        Use this method to define job templates to easily create and submit jobs in your app.

        Returns:
            iterable: A list or tuple of ``JobTemplate`` objects.

        Example:

        ::

            from tethys_compute.job_manager import JobTemplate, JobManager

            @classmethod
            def job_templates(cls):
                \"""
                Example job_templates method.
                \"""
                job_templates = (JobTemplate(name='example',
                                             type=JobManager.JOB_TYPES_DICT['CONDOR'],
                                             parameters={'executable': 'my_script.py',
                                                         'condorpy_template_name': 'vanilla_transfer_files',
                                                         'attributes': {'transfer_output_files': 'example_output'},
                                                         'remote_input_files': ['my_script.py','input_1', 'input_2'],
                                                         'working_directory': os.path.dirname(__file__)}
                                            ),
                                )

                return job_templates
        """
        return None

    @classmethod
    def get_job_manager(cls):
        templates = cls.job_templates()
        job_manager = JobManager(label=cls.package, job_templates=templates)
        return job_manager