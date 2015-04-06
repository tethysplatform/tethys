from .base import TethysGizmoOptions

__all__ = ['FetchClimateMap', 'FetchClimateURLParameter', 'FetchClimateMapData', 'FetchClimateMapParameters',
           'FetchClimatePlotParameters', 'FetchClimateVariableParameters', 'FetchClimateGridParameters',
           'FetchClimatePointParameters']


class FetchClimateURLParameter(TethysGizmoOptions):
    """
    URL Parameter

    This gizmo can be used to get climate data based off of a bounding box over an area or a point.
    It is based off of Microsoft Research. See the `FetchClimate page reference
    <http://research.microsoft.com/en-us/projects/fetchclimate/>`_ for more info.

    Attributes:
    serverUrl(str): The URL to the FetchClimate server (e.g 'serverUrl':'http://fetchclimate2.cloudapp.net')
    """

    def __init__(self, serverUrl='http://fetchclimate2.cloudapp.net', ):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.serverUrl = serverUrl


class FetchClimateMapData(TethysGizmoOptions):
    """
    Map Parameters - map_data

    Attributes:
    api_key(str): API key for Google maps.
    drawing_types_enabled(str): A list of the types of geometries the user will be allowed to draw.
    Valid types are: RECTANGLE, and POINTS. (e.g.: drawing_types_enabled=['RECTANGLE','POINTS'])
    initial_drawing_mode(str): A string representing the drawing mode that will be enabled by default.
    Valid modes are: 'RECTANGLE', 'POINTS'. The mode used must be one of the drawing_types_enabled that the user is allowed to draw.
    max_num_grids(int): The maximum number of grids allowed for the user. Default is unlimited. (e.g. 'max_num_grids':0).
    max_num_points(int): The maximum number of points allowed for the user. Default is unlimited. (e.g 'max_num_points':0).
    """

    def __init__(self, api_key='', drawing_types_enabled=['RECTANGLE'], initial_drawing_mode='RECTANGLE', max_num_grids=0, max_num_points=0):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.api_key = api_key
        self.drawing_types_enabled = drawing_types_enabled
        self.initial_drawing_mode = initial_drawing_mode
        self.max_num_grids = max_num_grids
        self.max_num_points = max_num_points


class FetchClimateMapParameters(TethysGizmoOptions):
    """
    Map Parameters
    Optional if grid or point included. Otherwise, required!

    Attributes:
    css(dict):Custom css elements. FORMAT:{'css-element-name': 'css-value'}.
    If no width or height included, 500px X 500px assumed.
    map_data(dict): Data needed to create the map.
    """

    def __init__(self, css={}, map_data=FetchClimateMapData()):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.css = css
        self.map_data = map_data


class FetchClimatePlotParameters(TethysGizmoOptions):
    """
    Plot Parameters

    Attributes:
    dimensions(dict): The integer is in pixels for width (`Highcharts width reference
    <http://api.highcharts.com/highcharts#chart.width>`_) or height (`Highcharts height reference
    <http://api.highcharts.com/highcharts#chart.height>`_). Not required to be defined.
    """

    def __init__(self, dimensions={'width': 100, 'height': 500}):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.dimensions = dimensions


class FetchClimateVariableParameters(TethysGizmoOptions):
    """
    Variable Parameters

    To find out which variables you can use and their parameters, go to your service url
    with '/api/coniguration' at the end. (e.g. `http://fetchclimate2.cloudapp.net/api/configuration
    <http://fetchclimate2.cloudapp.net/api/configuration>`_). Look in "EnvironmentalVariables" for the
    variable names. Then, to find the data source ID's of sources available, go to "DataSources".

    Attributes:
    variables(dict): Must have variable defined. It is in the format {'variable_name':[variable_id,variable_id,variable_id]}.
    """

    def __init__(self, variables={'precip':[]}):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.variables = variables


class FetchClimateGridParameters(TethysGizmoOptions):
    """
    Grid Parameters

    Optional if there is a map or point included. Otherwise, it is required! No map needed. If map included, it will initialize with input grid.

    Attributes:
    title(str): The name of the grid area.
    boundingBox(dict): An array of length 4 with bounding lat and long. e.g.[min lat, max lat, min lon, max long].
    gridResolution(dict): An array of length 2. Number of grid cells in lat and lon directions. e.g.[lat resolution,lon resolution].
    """

    def __init__(self, title='', boundingBox=[], gridResolution=[]):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.title = title
        self.boundingBox = boundingBox
        self.gridResolution = gridResolution


class FetchClimatePointParameters(TethysGizmoOptions):
    """
    Point Parameters

    Optional if there is a map or grid included. Otherwise, it is required! No map needed.
    If map included, it will initialize with input point.

    Attributes:
    title(str): The name of the point location.
    location(dict): An array of length 2 with lat and lon of point. e.g.[lat,lon].
    """

    def __init__(self, title='', location=[]):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.title = title
        self.location = location


class FetchClimateMap(TethysGizmoOptions):
    """
    Plot Parameters

    Attributes:
    dimensions(dict): The integer is in pixels for width (`Highcharts width reference
    <http://api.highcharts.com/highcharts#chart.width>`_) or height (`Highcharts height reference
    <http://api.highcharts.com/highcharts#chart.height>`_). Not required to be defined.
    """

    def __init__(self, url_parameter=FetchClimateURLParameter(), map_parameters=FetchClimateMapParameters(),
                 plot_parameters=FetchClimatePlotParameters(), variable_parameters=FetchClimateVariableParameters(),
                 grid_parameters=FetchClimateGridParameters(), point_parameters=FetchClimatePointParameters()):
        """
        Constructor
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        self.url_parameter = url_parameter
        self.map_parameters = map_parameters
        self.plot_parameters = plot_parameters
        self.variable_parameters = variable_parameters
        self.grid_parameters = grid_parameters
        self.point_parameters = point_parameters


