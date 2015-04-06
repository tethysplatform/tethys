from tethys_dataset_services.valid_engines import VALID_ENGINES, VALID_SPATIAL_ENGINES


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
            if len(VALID_ENGINES) > 2:
                comma_separated_types = ', '.join('"{0}"'.format(t) for t in VALID_ENGINES.keys()[:-1])
                last_type = '"{0}"'.format(VALID_ENGINES.keys()[-1])
                valid_types_string = '{0}, and {1}'.format(comma_separated_types, last_type)
            elif len(VALID_ENGINES) == 2:
                valid_types_string = '"{0}" and "{1}"'.format(VALID_ENGINES.keys()[0], VALID_ENGINES.keys()[1])
            else:
                valid_types_string = '"{0}"'.format(VALID_ENGINES.keys()[0])

            raise ValueError('The value "{0}" is not a valid for argument "type" of DatasetService. Valid values for '
                             '"type" argument include {1}.'.format(type, valid_types_string))

        self.endpoint = endpoint
        self.apikey = apikey
        self.username = username
        self.password = password

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
            if len(VALID_SPATIAL_ENGINES) > 2:
                comma_separated_types = ', '.join('"{0}"'.format(t) for t in VALID_SPATIAL_ENGINES.keys()[:-1])
                last_type = '"{0}"'.format(VALID_SPATIAL_ENGINES.keys()[-1])
                valid_types_string = '{0}, and {1}'.format(comma_separated_types, last_type)
            elif len(VALID_SPATIAL_ENGINES) == 2:
                valid_types_string = '"{0}" and "{1}"'.format(VALID_SPATIAL_ENGINES.keys()[0], VALID_SPATIAL_ENGINES.keys()[1])
            else:
                valid_types_string = '"{0}"'.format(VALID_SPATIAL_ENGINES.keys()[0])

            raise ValueError('The value "{0}" is not a valid for argument "type" of SpatialDatasetService. Valid values for '
                             '"type" argument include {1}.'.format(type, valid_types_string))

        self.endpoint = endpoint
        self.apikey = apikey
        self.username = username
        self.password = password

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

    def __repr__(self):
        """
        String representation
        """
        return '<WpsService: name={0}, endpoint={1}>'.format(self.name, self.endpoint)


