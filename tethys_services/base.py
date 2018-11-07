"""
********************************************************************************
* Name: base.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from tethys_dataset_services.valid_engines import VALID_ENGINES, VALID_SPATIAL_ENGINES
from tethys_apps.cli.cli_colors import pretty_output, FG_WHITE


class DatasetService:
    """
    Used to define dataset services for apps.
    """

    def __init__(self, name, type, endpoint, apikey=None, username=None, password=None):
        """
        Constructor
        """
        self.name = name

        # Validate the types
        if type in VALID_ENGINES:
            self.type = type
            self.engine = VALID_ENGINES[type]
        else:
            engine_key_list = list(VALID_ENGINES)
            if len(VALID_ENGINES) > 2:
                comma_separated_types = ', '.join('"{0}"'.format(t) for t in engine_key_list[:-1])
                last_type = '"{0}"'.format(engine_key_list[-1])
                valid_types_string = '{0}, and {1}'.format(comma_separated_types, last_type)
            elif len(VALID_ENGINES) == 2:
                valid_types_string = '"{0}" and "{1}"'.format(engine_key_list[0], engine_key_list[1])
            else:
                valid_types_string = '"{0}"'.format(engine_key_list[0])

            raise ValueError('The value "{0}" is not a valid for argument "type" of DatasetService. Valid values for '
                             '"type" argument include {1}.'.format(type, valid_types_string))

        self.endpoint = endpoint
        self.apikey = apikey
        self.username = username
        self.password = password

        with pretty_output(FG_WHITE) as p:
            p.write('DEPRECATION WARNING: Storing connection credentials for Dataset Services in the app.py is a '
                    'security leak. App configuration for Dataset Services will be deprecated in version 1.2.')

    def __repr__(self):
        """
        String representation
        """
        return '<DatasetService: type={0}, api_endpoint={1}>'.format(self.type, self.endpoint)


class SpatialDatasetService:
    """
    Used to define spatial dataset services for apps.
    """

    def __init__(self, name, type, endpoint, apikey=None, username=None, password=None):
        """
        Constructor
        """
        self.name = name

        # Validate the types
        if type in VALID_SPATIAL_ENGINES:
            self.type = type
            self.engine = VALID_SPATIAL_ENGINES[type]
        else:
            spatial_engine_key_list = list(VALID_SPATIAL_ENGINES)
            if len(VALID_SPATIAL_ENGINES) > 2:
                comma_separated_types = ', '.join('"{0}"'.format(t) for t in spatial_engine_key_list[:-1])
                last_type = '"{0}"'.format(spatial_engine_key_list[-1])
                valid_types_string = '{0}, and {1}'.format(comma_separated_types, last_type)
            elif len(VALID_SPATIAL_ENGINES) == 2:
                valid_types_string = '"{0}" and "{1}"'.format(spatial_engine_key_list[0], spatial_engine_key_list[1])
            else:
                valid_types_string = '"{0}"'.format(spatial_engine_key_list[0])

            raise ValueError('The value "{0}" is not a valid for argument "type" of SpatialDatasetService.'
                             ' Valid values for "type" argument include {1}.'.format(type, valid_types_string))

        self.endpoint = endpoint
        self.apikey = apikey
        self.username = username
        self.password = password

        with pretty_output(FG_WHITE) as p:
            p.write('DEPRECATION WARNING: Storing connection credentials for Spatial Dataset Services '
                    'in the app.py is a security leak. App configuration for Spatial Dataset Services '
                    'will be deprecated in version 1.2.')

    def __repr__(self):
        """
        String representation
        """
        return '<SpatialDatasetService: type={0}, api_endpoint={1}>'.format(self.type, self.endpoint)


class WpsService:
    """
    Used to define dataset services for apps.
    """

    def __init__(self, name, endpoint, username=None, password=None):
        """
        Constructor
        """
        self.name = name
        self.endpoint = endpoint
        self.username = username
        self.password = password

        with pretty_output(FG_WHITE) as p:
            p.write('DEPRECATION WARNING: Storing connection credentials for WPS Services in the app.py is a security '
                    'leak. App configuration for WPS Services will be deprecated in version 1.2.')

    def __repr__(self):
        """
        String representation
        """
        return '<WpsService: name={0}, endpoint={1}>'.format(self.name, self.endpoint)
