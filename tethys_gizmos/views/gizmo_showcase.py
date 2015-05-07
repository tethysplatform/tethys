import json
from datetime import datetime
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from tethys_gizmos.gizmo_options import *


def index(request):
    """
    Django view for the gizmo showcase page
    """
    # Button Group Options
    # Click me button
    button_options = ButtonOptions(display_text='Click Me',
                                   name='click_me_name',
                                   attributes='onclick=alert(this.name);',
                                   submit=True)
    single_button = ButtonGroupOptions(buttons=[button_options])

    # Horizontal Buttons
    add_button = ButtonOptions(display_text='Add',
                               icon='glyphicon glyphicon-plus',
                               style='success')
    delete_button = ButtonOptions(display_text='Delete',
                                  icon='glyphicon glyphicon-trash',
                                  disabled=True,
                                  style='danger')
    horizontal_buttons = ButtonGroupOptions(buttons=[add_button, delete_button])

    # Vertical Buttons
    edit_button = ButtonOptions(display_text='Edit',
                                icon='glyphicon glyphicon-wrench',
                                style='warning',
                                attributes='id=edit_button')
    info_button = ButtonOptions(display_text='Info',
                                icon='glyphicon glyphicon-question-sign',
                                style='info',
                                attributes='name=info')
    apps_button = ButtonOptions(display_text='Apps',
                                icon='glyphicon glyphicon-home',
                                href='/apps',
                                style='primary')
    vertical_buttons = ButtonGroupOptions(buttons=[edit_button, info_button, apps_button],
                                          vertical=True)

    # Date Picker Options
    date_picker = DatePickerOptions(name='date1',
                                    display_text='Date',
                                    autoclose=True,
                                    format='MM d, yyyy',
                                    start_date='2/15/2014',
                                    start_view='decade',
                                    today_button=True,
                                    initial='February 15, 2014')

    date_picker_error = DatePickerOptions(name='data2',
                                          display_text='Date',
                                          initial='10/2/2013',
                                          disabled=True,
                                          error='Here is my error text.')

    # Range Slider Data
    slider1 = RangeSlider(display_text='Slider 1',
                          name='slider1',
                          min=0,
                          max=100,
                          initial=50,
                          step=1)
    slider2 = RangeSlider(display_text='Slider 2',
                          name='slider2',
                          min=0,
                          max=1,
                          initial=0.5,
                          step=0.1,
                          disabled=True,
                          error='Incorrect, please choose another value.')

    # Select Input
    select_input2 = SelectInput(display_text='Select2',
                                name='select1',
                                multiple=False,
                                options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                original=['Two'])

    select_input2_multiple = SelectInput(display_text='Select2 Multiple',
                                         name='select2',
                                         multiple=True,
                                         options=[('One', '1'), ('Two', '2'), ('Three', '3')])

    select_input_multiple = SelectInput(display_text='Select Multiple',
                                        name='select2.1',
                                        multiple=True,
                                        original=True,
                                        options=[('One', '1'), ('Two', '2'), ('Three', '3')])

    select_input2_error = SelectInput(display_text='Select2 Disabled',
                                      name='select3',
                                      multiple=False,
                                      options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                      disabled=True,
                                      error='Here is my error text')

    # Text Input
    text_input = TextInput(display_text='Text',
                           name='inputAmount',
                           placeholder='e.g.: 10.00',
                           prepend='$')

    text_error_input = TextInput(display_text='Text Error',
                                 name='inputEmail',
                                 initial='bob@example.com',
                                 disabled=True,
                                 icon_append='glyphicon glyphicon-envelope',
                                 error='Here is my error text')

    # Toggle Switch
    toggle_switch = ToggleSwitch(display_text='Defualt Toggle',
                                 name='toggle1')

    toggle_switch_styled = ToggleSwitch(display_text='Styled Toggle',
                                        name='toggle2',
                                        on_label='Yes',
                                        off_label='No',
                                        on_style='success',
                                        off_style='danger',
                                        initial=True,
                                        size='large')

    toggle_switch_disabled = ToggleSwitch(display_text='Disabled Toggle',
                                          name='toggle3',
                                          on_label='On',
                                          off_label='Off',
                                          on_style='success',
                                          off_style='warning',
                                          size='mini',
                                          initial=False,
                                          disabled=True,
                                          error='Here is my error text')

    # Plot Views
    highcharts_object = HighChartsLinePlot(title={'text': 'Plot Title'},
                                           subtitle={'text': 'Plot Subtitle'},
                                           legend={
                                               'layout': 'vertical',
                                               'align': 'right',
                                               'verticalAlign': 'middle',
                                               'borderWidth': 0
                                           },
                                           xAxis={
                                               'title': {'enabled': True,
                                                         'text': 'Altitude (km)'
                                               },
                                               'labels': {
                                                   'formatter': 'function () { return this.value + " km"; }'
                                               }
                                           },
                                           yAxis={
                                               'title': {
                                                   'enabled': True,
                                                   'text': 'Temperature (*C)'
                                               },
                                               'labels': {'formatter': 'function () { return this.value + " *C"; }'}
                                           },
                                           tooltip={'headerFormat': '<b>{series.name}</b><br/>',
                                                    'pointFormat': '{point.x} km: {point.y}*C'
                                           },
                                           series=[
                                               {
                                                   'name': 'Air Temp',
                                                   'color': '#0066ff',
                                                   'marker': {'enabled': False},
                                                   'data': [
                                                       [0, 5], [10, -70],
                                                       [20, -86.5], [30, -66.5],
                                                       [40, -32.1],
                                                       [50, -12.5], [60, -47.7],
                                                       [70, -85.7], [80, -106.5]
                                                   ]
                                               },
                                               {
                                                   'name': 'Water Temp',
                                                   'color': '#ff6600',
                                                   'data': [[0, 15], [10, -50],
                                                            [20, -56.5], [30, -46.5],
                                                            [40, -22.1],
                                                            [50, -2.5], [60, -27.7],
                                                            [70, -55.7], [80, -76.5]
                                                   ]
                                               }
                                           ]
    )

    line_plot_view = PlotView(highcharts_object=highcharts_object,
                              width='500px',
                              height='500px')

    # Web Plot
    web_plot_object = HighChartsPolarPlot(title={'text': 'Polar Chart'},
                                          pane={
                                              'size': '80%'
                                          },
                                          xAxis={
                                              'categories': ['Infiltration', 'Soil Moisture', 'Precipitation',
                                                             'Evaporation',
                                                             'Roughness', 'Runoff', 'Permeability', 'Vegetation'],
                                              'tickmarkPlacement': 'on',
                                              'lineWidth': 0
                                          },
                                          yAxis={
                                              'gridLineInterpolation': 'polygon',
                                              'lineWidth': 0,
                                              'min': 0
                                          },
                                          series=[{
                                                      'name': 'Park City',
                                                      'data': [0.2, 0.5, 0.1, 0.8, 0.2, 0.6, 0.8, 0.3],
                                                      'pointPlacement': 'on'
                                                  }, {
                                                      'name': 'Little Dell',
                                                      'data': [0.8, 0.3, 0.2, 0.5, 0.1, 0.8, 0.2, 0.6],
                                                      'pointPlacement': 'on'
                                                  }
                                          ]
    )

    web_plot = PlotView(highcharts_object=web_plot_object,
                        width='500px',
                        height='500px')

    # Time series plot
    timeseries_plot_object = {
        'chart': {
            'type': 'area',
            'zoomType': 'x'
        },
        'title': {
            'text': 'Irregular Timeseries Plot'
        },
        'xAxis': {
            'maxZoom': 30 * 24 * 3600000,  # 30 days in milliseconds
            'type': 'datetime'
        },
        'yAxis': {
            'title': {
                'text': 'Snow depth (m)'
            },
            'min': 0
        },
        'legend': {
            'layout': 'vertical',
            'align': 'right',
            'verticalAlign': 'top',
            'x': -350,
            'y': 125,
            'floating': True,
            'borderWidth': 1,
            'backgroundColor': '#FFFFFF'
        },
        'series': [{
                       'name': 'Winter 2007-2008',
                       'data': [
                           [datetime(2008, 12, 2), 0.8],
                           [datetime(2008, 12, 9), 0.6],
                           [datetime(2008, 12, 16), 0.6],
                           [datetime(2008, 12, 28), 0.67],
                           [datetime(2009, 1, 1), 0.81],
                           [datetime(2009, 1, 8), 0.78],
                           [datetime(2009, 1, 12), 0.98],
                           [datetime(2009, 1, 27), 1.84],
                           [datetime(2009, 2, 10), 1.80],
                           [datetime(2009, 2, 18), 1.80],
                           [datetime(2009, 2, 24), 1.92],
                           [datetime(2009, 3, 4), 2.49],
                           [datetime(2009, 3, 11), 2.79],
                           [datetime(2009, 3, 15), 2.73],
                           [datetime(2009, 3, 25), 2.61],
                           [datetime(2009, 4, 2), 2.76],
                           [datetime(2009, 4, 6), 2.82],
                           [datetime(2009, 4, 13), 2.8],
                           [datetime(2009, 5, 3), 2.1],
                           [datetime(2009, 5, 26), 1.1],
                           [datetime(2009, 6, 9), 0.25],
                           [datetime(2009, 6, 12), 0]
                       ]
                   }]
    }

    timeseries_plot = PlotView(highcharts_object=timeseries_plot_object,
                               width='500px',
                               height='500px')

    # Table View
    table_view = TableView(column_names=('Name', 'Age', 'Job'),
                           rows=[('Bill', 30, 'contractor'),
                                 ('Fred', 18, 'programmer'),
                                 ('Bob', 26, 'boss')],
                           hover=True,
                           striped=False,
                           bordered=False,
                           condensed=False)

    table_view_edit = TableView(column_names=('Name', 'Age', 'Job'),
                                rows=[('Bill', 30, 'contractor'),
                                      ('Fred', 18, 'programmer'),
                                      ('Bob', 26, 'boss')],
                                hover=True,
                                striped=True,
                                bordered=False,
                                condensed=False,
                                editable_columns=(False, 'ageInput', 'jobInput'),
                                row_ids=[21, 25, 31])


    # Message Box
    message_box = MessageBox(name='sampleModal',
                             title='Message Box Title',
                             message='Congratulations! This is a message box.',
                             dismiss_button='Nevermind',
                             affirmative_button='Proceed',
                             width=400,
                             affirmative_attributes='href=javascript:void(0);')

    # Editable Google Map
    google_map_view = GoogleMapView(height='600px',
                                    width='100%',
                                    reference_kml_action=reverse('gizmos:get_kml'),
                                    drawing_types_enabled=['POLYGONS', 'POINTS', 'POLYLINES'],
                                    initial_drawing_mode='POINTS',
                                    output_format='WKT')

    flash_message = ''

    if ('editable_map_submit' in request.POST) and (request.POST['geometry']):
        # Some example code showing how you can decode the JSON into python data structures.
        geometry_string = request.POST['geometry']

        # Display the JSON as flash message
        flash_message = geometry_string

    # Fetchclimate
    fetchclimate_array = FetchClimateMap(
        url_parameter=FetchClimateURLParameter(serverUrl='http://fetchclimate2.cloudapp.net'),
        variable_parameters=FetchClimateVariableParameters(variables={
            'prate': [423, 432, 426, 424],
            'elev': []
        }),
        grid_parameters=FetchClimateGridParameters(
            title='Provo Canyon Watershed',
            boundingBox=[40.308836, 40.381579, -111.654462, -111.550778],
            gridResolution=[25, 25]
        ),
        point_parameters=FetchClimatePointParameters(
            title='Clyde Building',
            location=[40.246942, -111.647971]
        )
    )

    # Map View
    view_options = MapViewViewOptions(
        projection='EPSG:4326',
        center=[-100, 40],
        zoom=3.5,
        maxZoom=18,
        minZoom=3
    )

    drawing_options = MapViewDrawOptions(
        controls=['Modify', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
        initial='Point',
        output_format='WKT'
    )

    map_view_options = MapViewOptions(
        height='500px',
        width='100%',
        controls=['ZoomSlider',
                  'Rotate',
                  'FullScreen',
                  {'MousePosition': {'projection': 'EPSG:4326'}}],
        layers=[{'WMS': {'url': 'http://demo.opengeo.org/geoserver/wms',
                         'params': {'LAYERS': 'topp:states'},
                         'serverType': 'geoserver'}}],
        view=view_options,
        basemap='OpenStreetMap',
        draw=drawing_options,
        legend=False
    )

    # Define the context object
    context = {'single_button': single_button,
               'horizontal_buttons': horizontal_buttons,
               'vertical_buttons': vertical_buttons,
               'date_picker': date_picker,
               'date_picker_error': date_picker_error,
               'slider1': slider1,
               'slider2': slider2,
               'select_input2': select_input2,
               'select_input2_multiple': select_input2_multiple,
               'select_input_multiple': select_input_multiple,
               'select_input2_error': select_input2_error,
               'text_input': text_input,
               'text_error_input': text_error_input,
               'toggle_switch': toggle_switch,
               'toggle_switch_styled': toggle_switch_styled,
               'toggle_switch_disabled': toggle_switch_disabled,
               'line_plot_view': line_plot_view,
               'web_plot': web_plot,
               'timeseries_plot': timeseries_plot,
               'table_view': table_view,
               'table_view_edit': table_view_edit,
               'message_box': message_box,
               'google_map_view': google_map_view,
               'flash_message': flash_message,
               'fetchclimate_array': fetchclimate_array,
               'map_view_options': map_view_options,
    }

    return render(request, 'tethys_gizmos/gizmo_showcase/index.html', context)


def get_kml(request):
    """
    This action is used to pass the kml data to the google map. It must return JSON with the key 'kml_link'.
    """
    kml_links = [
        'http://ciwckan.chpc.utah.edu/dataset/00d54047-8581-4dc2-bdc2-b96f5a635455/resource/69f8e7df-da87-47cd-90a1-d15dc84e99ba/download/indexclusters.kml']

    return JsonResponse({'kml_links': kml_links})


def swap_kml(request):
    """
    This action is used to pass the kml data to the google map. It must return JSON with the key 'kml_link'.
    """
    for i in range(0, 20000000):
        pass

    kml_links = [
        'http://ciwckan.chpc.utah.edu/dataset/00d54047-8581-4dc2-bdc2-b96f5a635455/resource/53c7a910-5e00-4af7-803a-e48e0f17a131/download/elevation.kml']

    return HttpResponse(json.dumps(kml_links), content_type='application/json')


def swap_overlays(request):
    """
    This action is used to demonstrate how overlay layers can be swapped out dynamically using the javascript API.
    """

    overlay_json = {"type": "GeometryCollection",
                    "geometries": [{"type": "Polygon",
                                    "coordinates": [[40.643135583312805, -111.48951530456543],
                                                    [40.636622594719725, -111.49432182312012],
                                                    [40.63310531666155, -111.4877986907959],
                                                    [40.63805550673186, -111.48110389709473],
                                                    [40.6413120105605, -111.48539543151855]],
                                    "properties": {"id": 4, "value": 5}, "crs": {"type": "link", "properties": {
                        "href": "http://spatialreference.org/ref/epsg/4326/proj4/", "type": "proj4"}}
                                   },
                                   {"type": "Point",
                                    "coordinates": [40.629587853312174, -111.50959968566895],
                                    "properties": {"id": 5, "value": 6}, "crs": {"type": "link", "properties": {
                                       "href": "http://spatialreference.org/ref/epsg/4326/proj4/", "type": "proj4"}}
                                   },
                                   {"type": "LineString",
                                    "coordinates": [[40.62737305910759, -111.50118827819824],
                                                    [40.61564645424611, -111.5071964263916],
                                                    [40.61277963772034, -111.48608207702637],
                                                    [40.62802447679272, -111.49157524108887]],
                                    "properties": {"id": 6, "value": 7}, "crs": {"type": "link", "properties": {
                                       "href": "http://spatialreference.org/ref/epsg/4326/proj4/", "type": "proj4"}}
                                   }
                    ]
    }

    return HttpResponse(json.dumps(overlay_json), content_type='application/json')


def editable_map(request):
    """
    Place to display editable google map in an isolated environment
    """

    # Editable Google Map
    google_map_view = {'height': '600px',
                       'width': '100%',
                       'reference_kml_action': reverse('gizmos:get_kml'),
                       'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES', 'BOXES'],
                       'initial_drawing_mode': 'BOXES',
                       'input_overlays': {"type": "GeometryCollection",
                                          "geometries": [
                                              {"type": "Point",
                                               "coordinates": [40.629197012613545, -111.5123462677002],
                                               "properties": {"id": 1, "value": 1}},
                                              {"type": "Polygon",
                                               "coordinates": [[40.63193284946615, -111.50153160095215],
                                                               [40.617210120505035, -111.50101661682129],
                                                               [40.623594711231775, -111.48625373840332],
                                                               [40.63193284946615, -111.49123191833496]],
                                               "properties": {"id": 2, "value": 2}},
                                              {"type": "LineString",
                                               "coordinates": [[40.65003865742191, -111.49123191833496],
                                                               [40.635319920747456, -111.49088859558105],
                                                               [40.64912697157757, -111.48127555847168],
                                                               [40.634668574229735, -111.48024559020996]],
                                               "properties": {"id": 3, "value": 3}},
                                              {"type": "BoundingBox",
                                               "bounds": [-111.54521942138672, 40.597792003905454, -111.46625518798828,
                                                          40.66449372533465],
                                               "properties": {"id": 4, "value": 4}
                                              }
                                          ]},
                       'output_format': 'WKT'
    }

    if ('editable_map_submit' in request.POST) and (request.POST['geometry']):
        # Some example code showing how you can decode the JSON into python
        # data structures.
        geometry_string = request.POST['geometry']
        geometry_json = json.loads(geometry_string)
        google_map_view['input_overlays'] = geometry_json

        # Display the JSON as flash message
        messages.info(request, geometry_string)

    context = {'google_map_view': google_map_view}

    return render(request, 'tethys_gizmos/gizmo_showcase/editable_map.html', context)


def google_map(request):
    """
    Place to display google map view in an isoloted environment
    """
    # Google Map
    google_map = {'height': '600px',
                  'width': '100%',
                  'kml_service': reverse('gizmos:get_kml')}

    messages.warning(request,
                     'WARNING: The "google_map" gizmo has been deprecated and may lose support in future releases of Tethys Platform.')

    context = {'google_map': google_map}

    return render(request, 'tethys_gizmos/gizmo_showcase/google_map.html', context)


def map_view(request):
    """
    Place to show off the new map view
    """

    view_options = MapViewViewOptions(
        projection='EPSG:4326',
        center=[-100, 40],
        zoom=3.5,
        maxZoom=18,
        minZoom=3
    )

    drawing_options = MapViewDrawOptions(
        controls=['Modify', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
        initial='Point',
        output_format='WKT'
    )

    geojson_object = {
      'type': 'FeatureCollection',
      'crs': {
        'type': 'name',
        'properties': {
          'name': 'EPSG:3857'
        }
      },
      'features': [
        {
          'type': 'Feature',
          'geometry': {
            'type': 'Point',
            'coordinates': [0, 0]
          }
        },
        {
          'type': 'Feature',
          'geometry': {
            'type': 'LineString',
            'coordinates': [[4e6, -2e6], [8e6, 2e6]]
          }
        },
        {
          'type': 'Feature',
          'geometry': {
            'type': 'LineString',
            'coordinates': [[4e6, 2e6], [8e6, -2e6]]
          }
        },
        {
          'type': 'Feature',
          'geometry': {
            'type': 'Polygon',
            'coordinates': [[[-5e6, -1e6], [-4e6, 1e6], [-3e6, -1e6]]]
          }
        },
        {
          'type': 'Feature',
          'geometry': {
            'type': 'MultiLineString',
            'coordinates': [
              [[-1e6, -7.5e5], [-1e6, 7.5e5]],
              [[1e6, -7.5e5], [1e6, 7.5e5]],
              [[-7.5e5, -1e6], [7.5e5, -1e6]],
              [[-7.5e5, 1e6], [7.5e5, 1e6]]
            ]
          }
        },
        {
          'type': 'Feature',
          'geometry': {
            'type': 'MultiPolygon',
            'coordinates': [
              [[[-5e6, 6e6], [-5e6, 8e6], [-3e6, 8e6], [-3e6, 6e6]]],
              [[[-2e6, 6e6], [-2e6, 8e6], [0, 8e6], [0, 6e6]]],
              [[[1e6, 6e6], [1e6, 8e6], [3e6, 8e6], [3e6, 6e6]]]
            ]
          }
        },
        {
          'type': 'Feature',
          'geometry': {
            'type': 'GeometryCollection',
            'geometries': [
              {
                'type': 'LineString',
                'coordinates': [[-5e6, -5e6], [0, -5e6]]
              },
              {
                'type': 'Point',
                'coordinates': [4e6, -5e6]
              },
              {
                'type': 'Polygon',
                'coordinates': [[[1e6, -6e6], [2e6, -4e6], [3e6, -6e6]]]
              }
            ]
          }
        }
      ]
    }

    kml_string = '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>parkcity</name><Placemark><name>Mask Map</name><Style><LineStyle><color>FF0000FF</color><width>0.0</width></LineStyle><PolyStyle><color>FF0080FF</color></PolyStyle></Style><Polygon><outerBoundaryIs><LinearRing><coordinates>-111.479706119071821,40.658319075528659 -111.479694504189169,40.65669755286487 -111.480759097024858,40.656693125367809 -111.480747457314777,40.655071602496285 -111.481812024141135,40.655067165437138 -111.481806191755794,40.65425640395523 -111.482870745459365,40.654251957208636 -111.482859055631209,40.652630434153068 -111.483923583327609,40.652625977846327 -111.483917725886357,40.651815216272944 -111.484982240460539,40.651810750280156 -111.484988110785665,40.652621511726515 -111.487117164984724,40.652612550047692 -111.487111268891866,40.651801788856226 -111.489240296363647,40.651792788181176 -111.489252140325647,40.653414309937205 -111.490316679468563,40.653409794623691 -111.49032261469587,40.654220555200908 -111.492451718026416,40.65421149487625 -111.492457679265982,40.655022255080844 -111.495651371097495,40.65500859060338 -111.495645371201888,40.654197830787425 -111.496709921772847,40.654193256464012 -111.496703909236558,40.65338249666322 -111.49776844667808,40.65337791265663 -111.497762421502145,40.652567152871271 -111.498826945814272,40.652562559182073 -111.498820907999757,40.651751799412423 -111.499885419182476,40.651747196041178 -111.499879368730404,40.650936436287502 -111.500943866783786,40.650931823234764 -111.500931740853332,40.649310303645002 -111.499867268564756,40.649314916435337 -111.499861218851166,40.64850415633682 -111.498796759198086,40.648508759184381 -111.498790722611702,40.647697998840016 -111.497726275594118,40.64770259174535 -111.497720252133931,40.646891831155401 -111.496655817751886,40.646896414119063 -111.49663778748031,40.644464131268549 -111.497702183223709,40.644459548695934 -111.4976961607437,40.643648787646242 -111.498760543363588,40.643644195394046 -111.498754508250641,40.642833434360028 -111.499818877747032,40.642828832428819 -111.499806782503356,40.641207310277757 -111.500871125999353,40.641202698799262 -111.500865065870201,40.64039193768248 -111.501929396243298,40.640387316526358 -111.501923323484846,40.639576555426082 -111.502987640735043,40.639571924592907 -111.502981555348356,40.638761163509407 -111.504045859475681,40.638756522999735 -111.504039761461783,40.637945761933274 -111.505104052466251,40.637941111747665 -111.505097941826193,40.63713035069852 -111.506162219707861,40.637125690837543 -111.506149973426631,40.63550416865948 -111.507214225312325,40.635499499256511 -111.508278476948391,40.635494820046475 -111.508272328436163,40.634684059050919 -111.509336566949472,40.634679370167184 -111.509330405815291,40.633868609190046 -111.51039463120587,40.633863910633188 -111.510388457450745,40.633053149674737 -111.511452669718622,40.633048441445318 -111.511446483343647,40.63223768050581 -111.514639080022121,40.632223497383777 -111.514645305010092,40.633034257919824 -111.518902148517469,40.633015209265913 -111.518895872045661,40.63220444927169 -111.519960069414523,40.632199662728944 -111.519947491496595,40.630578142667822 -111.521011662869341,40.630573346592072 -111.52100536142477,40.62976258652543 -111.522069519671831,40.62975778078107 -111.522063205614799,40.628947020736149 -111.523127350736203,40.628942205323739 -111.52419149560022,40.628937380106585 -111.524185156063481,40.62812662022089 -111.525249287801358,40.628121785336546 -111.525242935654802,40.627311025473375 -111.526307054266539,40.627306180922396 -111.52949940854613,40.627291588444507 -111.529493005189252,40.626480829019236 -111.530557109895014,40.626475945390574 -111.530544278229982,40.624854426472773 -111.531608356942044,40.624849533318645 -111.531601928635439,40.624038773826406 -111.532665994220437,40.624033871008457 -111.532640232151849,40.620790832447049 -111.533704246017919,40.62078592038506 -111.533697793292788,40.619975160596866 -111.534761794033443,40.619970238873016 -111.535825794511098,40.619965307347556 -111.535819316323682,40.619154547724627 -111.536883303675452,40.619149606538151 -111.536876812889716,40.618338846940738 -111.537940787115616,40.618333896093802 -111.537934283732596,40.617523136522188 -111.538998244832655,40.617518176015352 -111.538985213139185,40.61589665680922 -111.540049148253203,40.61589168678443 -111.540023036610847,40.612648647557123 -111.53789526898926,40.612658576676608 -111.537888767457716,40.611847816299715 -111.527250042142782,40.611896872556549 -111.527237297011339,40.610275348666541 -111.526173448759479,40.610280200122581 -111.526167089438744,40.609469437867055 -111.525103253784408,40.609474279387065 -111.525096907578032,40.608663516878799 -111.521905437635411,40.608677982239051 -111.521911745274664,40.609488745158849 -111.519784071651117,40.609498340016444 -111.519777789723349,40.608687576823691 -111.517650140789215,40.608697132217166 -111.517643884827436,40.607886368637587 -111.512324822324516,40.607910084984887 -111.512318630890974,40.607099320615639 -111.511254830487559,40.60710403435835 -111.51124865216012,40.60629326974005 -111.505929710655479,40.606316690827839 -111.505923596848234,40.605505925428261 -111.504859820652982,40.605510580122299 -111.50486592160641,40.606321345654301 -111.50380213230919,40.606325990683715 -111.503808220656424,40.607136756232912 -111.502744418257194,40.607141391597139 -111.502738342764331,40.606330625916065 -111.500610762933789,40.6063398669896 -111.500604713395745,40.605529100930681 -111.498477158288708,40.605538302554137 -111.498465111363132,40.603916769567988 -111.497401359148057,40.603921355423566 -111.497395348905087,40.603110588627651 -111.495267869446749,40.603119730689926 -111.495261885151862,40.602308963519029 -111.493134430423581,40.602318066138359 -111.493128472074744,40.601507298593575 -111.491001042079745,40.601516361772148 -111.490995109674884,40.600705593854634 -111.486740298196921,40.600723602153863 -111.486746179198363,40.601534370583721 -111.4856824628787,40.601538848297913 -111.485717676794778,40.606403457229078 -111.484653883120103,40.606407925910517 -111.484659740087125,40.607218693790763 -111.483595933319663,40.607223152801879 -111.483607622257722,40.608844688471478 -111.482543789541822,40.6088491379383 -111.482561286161967,40.611281440960894 -111.483625157447847,40.611276991114302 -111.483636848763425,40.612898525635131 -111.484700745527462,40.612894065735944 -111.484706604400657,40.613704832697174 -111.485770513785127,40.613700362871427 -111.485776385755912,40.61451112959061 -111.486840307760772,40.614506649837757 -111.486863849474844,40.617749715055844 -111.48579987602777,40.61775419531849 -111.485805749192963,40.61856496146325 -111.486869735501898,40.618560481073139 -111.486893282004573,40.621803543993437 -111.485829244242964,40.62180802489339 -111.485835118602822,40.622618790463711 -111.484771067737768,40.622623261688389 -111.484776929471593,40.623434027270996 -111.482648801296605,40.623442940565653 -111.481584736852739,40.623447382508431 -111.481590560228355,40.624258148356091 -111.480526482682009,40.624262580621902 -111.480538104411195,40.625884112224732 -111.479474000895735,40.625888534938831 -111.479485597835662,40.627510066333784 -111.478421468349467,40.627514479495055 -111.478433040495986,40.629136010681599 -111.47736888503745,40.629140414288933 -111.477374658594513,40.62995117983516 -111.476310490031821,40.629955573762466 -111.476322012110472,40.631577104760296 -111.475257817573251,40.631581489131719 -111.475263566093275,40.632392254583046 -111.47419935845133,40.632396629273039 -111.474205094333797,40.633207394733937 -111.475269314847154,40.633203019919506 -111.475315313298566,40.639689138475987 -111.474250989795138,40.639693514286051 -111.474262465994642,40.641315043025422 -111.473198116505017,40.641319409275205 -111.473221020193733,40.644562465872312 -111.472156618959303,40.644566822808542 -111.472162332584617,40.645377586794581 -111.471097918238428,40.645381934044103 -111.471132127585733,40.650246516290103 -111.470067635720795,40.650250854469277 -111.47007332520765,40.651061617898307 -111.469008820228254,40.651065946388265 -111.469048562923135,40.656741288037175 -111.471177753041445,40.656732619518984 -111.471189161726059,40.658354144177515 -111.474383022485966,40.658341067047303 -111.474377279364603,40.657530305147404 -111.477571099358471,40.657517140055859 -111.477576881142724,40.658327901581323 -111.479706119071821,40.658319075528659</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark><Placemark><name>Stream Link 1</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.478605218055137,40.642214142371373,2174.293944999999894 -111.479396954154595,40.642735486909814,2173.814922000000024 -111.480214036673559,40.643247950510435,2173.330473999999867 -111.48113173976077,40.643599481578619,2173.138927999999851</coordinates></LineString></Placemark><Placemark><name>Stream Link 2</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.474452562227242,40.648093796755226,2174.293944999999894 -111.47510158300193,40.647438574658509,2174.293944999999894 -111.475750591107868,40.646783348919882,2174.269009000000096 -111.476399513692101,40.646128078327834,2174.19380799999999 -111.477140165551148,40.645645086193007,2174.070334999999886 -111.478015955141956,40.645345834165106,2173.9056700000001 -111.478778583815355,40.644874781279213,2173.708223000000089 -111.479555551526985,40.644443540568489,2173.500437000000147 -111.480375146784723,40.644069613450107,2173.293944999999894 -111.48113173976077,40.643599481578619,2173.138927999999851</coordinates></LineString></Placemark><Placemark><name>Stream Link 3</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.48113173976077,40.643599481578619,2173.138927999999851 -111.482170871858912,40.643595147446085,2172.813696000000164 -111.483210003742613,40.643590803963491,2172.321163999999953 -111.484109425028564,40.643781375330988,2171.694978999999876 -111.484951503045195,40.64405849643034,2170.819722000000183 -111.485744414671871,40.644419027501861,2169.580113999999867 -111.486588926186187,40.644693285778331,2167.941303999999946 -111.487481158878623,40.644893835961135,2165.908096999999998 -111.488471261158878,40.644964506307126,2163.467071999999916 -111.489510413296557,40.64496010601043,2160.790766000000076 -111.490353628393166,40.645236169703004,2158.427025999999842 -111.491392767128019,40.645231278792501,2155.59470999999985 -111.492398843974868,40.645278280312645,2152.532302999999956 -111.493275135900774,40.645502420789221,2149.421122000000196 -111.494120830682519,40.645783472558186,2146.051986999999826 -111.494963622279556,40.64604284701511,2142.515759999999773 -111.49577691049204,40.646386171911558,2138.731130000000121 -111.496394310144353,40.647022124516994,2134.393083999999817 -111.497029324444995,40.647648694782369,2129.995965000000069 -111.49766435064808,40.648275261409012,2125.598845999999867</coordinates></LineString></Placemark><Placemark><name>Stream Link 4</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.49068737444496,40.612013258464309,2556.050292999999783 -111.490704067793061,40.612823549040556,2540.008416000000125 -111.490419174390368,40.613557887117942,2524.819414000000052 -111.49042510780842,40.614369376174608,2508.723117999999886 -111.490431041468,40.615180865107163,2493.007013999999799 -111.490436975369235,40.615992353933613,2480.82651100000021 -111.490442909511998,40.61680384263596,2470.669370000000072 -111.490678916927308,40.617551555476318,2460.297512999999981 -111.491333756196383,40.618191396240228,2448.991169999999784 -111.491576599405306,40.618937119192019,2438.213979999999992 -111.49158254795455,40.619748607349663,2426.778698999999961 -111.49198860782306,40.62038618213839,2416.765699999999924 -111.492806458043162,40.620742099644325,2406.625868000000082 -111.493547370858764,40.621210939915549,2398.588564000000133 -111.494198061407516,40.621853361437637,2389.700852999999825 -111.494665679029893,40.622536320062956,2384.707092999999986 -111.495271931624544,40.623190530838365,2376.914099999999962 -111.495804980116745,40.623859861040629,2367.124729000000116 -111.496352816354516,40.624522339022633,2356.232664999999997 -111.496375788485324,40.625328620948387,2345.014341999999942 -111.496679206822478,40.626059959900019,2334.643627999999808 -111.496382582997427,40.62679443623734,2324.253267999999935 -111.495951132373662,40.627484559807591,2314.551000999999815 -111.495838419744032,40.628266655627172,2306.595416999999998 -111.49557461593686,40.629003800324199,2298.688187000000198 -111.495275881301069,40.629734798843828,2290.671444999999949 -111.495310503686284,40.630545084723479,2282.182420999999977 -111.495011176351127,40.631276000383082,2274.317165999999816 -111.494747826237429,40.632013229876399,2266.468574999999873 -111.494753815921527,40.632824715794335,2258.238189000000148 -111.494652265340392,40.63360712485121,2250.252826999999797 -111.494464843007009,40.634363406876197,2242.43588200000022 -111.494229824687579,40.635101718136724,2235.692977000000155 -111.493862276649566,40.635817455054287,2228.570268999999826 -111.493662935222773,40.636567626773846,2221.226016000000072 -111.493263306454736,40.63727311361027,2213.727992000000086 -111.492835400047326,40.637964768463064,2206.266552000000047 -111.492541428682301,40.638699598459354,2198.692670999999791 -111.493124187784218,40.639361140594964,2190.498782000000119 -111.493707457354049,40.640022554634569,2182.138398000000052 -111.493973513336584,40.640753587732654,2174.178711000000021</coordinates></LineString></Placemark><Placemark><name>Stream Link 5</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.512226829570224,40.6144322598415,2560.124511999999868 -111.511233053179652,40.614569424506229,2546.625494999999773 -111.510587138524457,40.615227505150131,2542.368938000000071 -111.510562070437587,40.616042892769507,2532.509955999999875 -111.510195083359733,40.616767478268471,2507.082268999999997 -111.509731468370859,40.617468471073408,2478.486374000000069 -111.509740631166636,40.618291518415056,2466.421374000000014 -111.509449276479089,40.619037067363386,2452.149938999999904 -111.50939568083794,40.619839363524846,2444.705000999999811 -111.509199643445982,40.620604285929524,2431.790346000000227 -111.50891826019614,40.621349372998004,2414.719079999999849 -111.508562394757135,40.622074744339635,2403.899483000000146 -111.508109821844968,40.622774511530935,2391.501695999999811 -111.507490193775226,40.623439740842322,2377.514048000000003 -111.506839861744169,40.624097024014411,2366.146428000000014 -111.506189516979163,40.624754303525911,2354.402658999999858 -111.505441703574562,40.625236470140386,2341.001075000000128 -111.504635656266004,40.625634499584159,2323.237470999999914 -111.503930108982914,40.626193836931542,2325.417724999999791</coordinates></LineString></Placemark><Placemark><name>Stream Link 6</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.524568209139233,40.619960237332315,2644.150391000000127 -111.523945442802855,40.62060000783918,2637.465279999999893 -111.523206364525834,40.621054101033913,2625.021712000000207 -111.522578183427484,40.62169103944661,2618.059996999999839 -111.521938167216575,40.622320690927118,2609.76922999999988 -111.521549065853435,40.623014709505782,2597.366907000000083 -111.520921218333797,40.623651765398641,2589.134907000000112 -111.520036408219283,40.623889088987355,2579.469978999999967 -111.519188257451503,40.62417894609279,2568.901871000000028 -111.518343009339873,40.624444598290864,2551.618745000000217 -111.517663714888926,40.624989827285653,2538.201936999999816 -111.51693571163284,40.6254505419639,2525.037727999999788 -111.516190432873586,40.6259015489779,2519.99944000000005 -111.515468340390981,40.626365104095207,2510.753161000000091 -111.514490707982191,40.626472541441217,2491.350054999999884 -111.513614632718685,40.626709509263442,2472.079600000000028 -111.512568908914915,40.626714155204127,2464.419237000000066 -111.511523184879465,40.626718791676616,2449.645598000000064 -111.51053960297368,40.626814206717199,2426.713857000000189 -111.509631800971064,40.627006321737163,2406.517350999999962 -111.508586071899913,40.62701093164258,2392.674618000000009 -111.507540342587149,40.627015532079753,2378.525752999999895 -111.506496614761232,40.627034029899121,2364.314216000000215 -111.505644721577966,40.626744679046126,2349.236448000000109 -111.50490696724664,40.626300256450016,2347.410937999999987 -111.503930108982914,40.626193836931542,2325.417724999999791</coordinates></LineString></Placemark><Placemark><name>Stream Link 7</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.503930108982914,40.626193836931542,2325.417724999999791 -111.503298744753721,40.626831870004324,2319.659849000000122 -111.502667368533835,40.627469899626341,2305.316010000000006 -111.502035980310936,40.62810792579743,2294.632017999999789 -111.501404580108243,40.628745948517242,2284.002351999999973 -111.500784144708717,40.629389704590565,2278.497011999999813 -111.500039698095335,40.629843829903002,2278.203015999999934 -111.499408262587096,40.630481841725363,2267.534553999999844 -111.498776815097258,40.631119850095509,2258.022363999999925 -111.498145355613516,40.631757855013269,2247.281872000000021 -111.49753519822184,40.632401188344176,2241.849830999999995 -111.497096767102249,40.633075537081872,2236.167422999999872 -111.496940496706955,40.633834446345929,2229.533300000000054 -111.496519033864402,40.634512246497032,2217.688388000000032 -111.496152562900065,40.635215482892143,2212.747812999999951 -111.495934053269139,40.635945320380785,2206.672267999999804 -111.495612540618581,40.636658487176966,2199.862844000000223 -111.495121725598935,40.637320438368882,2198.700468999999885 -111.494773602406354,40.63803024968081,2192.817097999999987 -111.494544331363329,40.638757304616746,2190.955010000000129 -111.494383980938693,40.639513844202718,2188.666905000000042 -111.493969397637983,40.64019527004924,2180.807860999999775</coordinates></LineString></Placemark><Placemark><name>Stream Link 8</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.497854789444446,40.636270236706807,2253.855224999999791 -111.497167132357262,40.636964952703828,2239.092556999999942 -111.496475810356827,40.637655936550843,2228.168916999999965 -111.496246667395184,40.638461740739032,2215.77317099999982 -111.495563906657381,40.639158830634933,2200.506714999999986 -111.49464234570172,40.639492873442194,2190.843840999999884 -111.493969397637983,40.64019527004924,2180.807860999999775</coordinates></LineString></Placemark><Placemark><name>Stream Link 9</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.493969397637983,40.64019527004924,2180.807860999999775 -111.493973513336584,40.640753587732654,2174.178711000000021</coordinates></LineString></Placemark><Placemark><name>Stream Link 10</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.493973513336584,40.640753587732654,2174.178711000000021 -111.494152269358224,40.6414764084873,2168.598731000000043 -111.494263948148173,40.64222069874247,2162.915547999999944 -111.494272934541129,40.642991722687526,2157.066087000000152 -111.494894186315776,40.643602020378616,2153.127112000000125 -111.495515031168111,40.644214663511903,2149.179655999999795 -111.495948928782994,40.644868832043272,2145.553870000000188 -111.496246038905042,40.645563240453797,2141.839376999999786 -111.496255691225869,40.646334142365269,2137.80281100000002 -111.496635995582011,40.647006552844424,2133.864928999999847 -111.497271108145483,40.647610145521874,2129.62995600000022 -111.49766435064808,40.648275261409012,2125.598845999999867</coordinates></LineString></Placemark><Placemark><name>Stream Link 11</name><Style><LineStyle><color>FFFF0000</color><width>2</width></LineStyle></Style><LineString><coordinates>-111.49766435064808,40.648275261409012,2125.598845999999867 -111.498254976334479,40.648858005213228,2121.530518999999913 -111.498841918725901,40.649442778123593,2117.843510000000151 -111.499545429122094,40.649839223444019,2116.511646999999812 -111.50023784762233,40.650242424311365,2115.18516499999987 -111.500733911221218,40.650869923714687,2113.721582000000126</coordinates></LineString></Placemark></Document></kml>'
    kml_url = 'http://ciwckan.chpc.utah.edu/dataset/00d54047-8581-4dc2-bdc2-b96f5a635455/resource/e833d531-8b7e-4d35-8ce9-4fe98c5d082a/download/model.kml'
    kml_url = './static/tethys_gizmos/data/model.kml'

    map_view = MapViewOptions(
        height='600px',
        width='100%',
        controls=['ZoomSlider',
                  'Rotate',
                  'FullScreen',
                  {'MousePosition': {'projection': 'EPSG:4326'}},
                  {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
        layers=[MapViewLayer(source='ImageWMS',
                             title='USA Population',
                             options={'url': 'http://192.168.59.103:8181/geoserver/wms',
                                                'params': {'LAYERS': 'topp:states'},
                                                'serverType': 'geoserver'}),
                MapViewLayer(source='GeoJSON',
                             title='Test GeoJSON',
                             options=geojson_object),
                MapViewLayer(source='KML',
                             title='Test URL KML',
                             options={'url': kml_url}),
                MapViewLayer(source='KML',
                             title='Test String KML',
                             options={'kml': kml_string})
                ],
        view=view_options,
        basemap='OpenStreetMap',
        draw=drawing_options,
        legend=True
    )

    context = {'map_view': map_view}

    return render(request, 'tethys_gizmos/gizmo_showcase/map_view.html', context)


def fetchclimate_map(request):
    """
    Place to show off the new map view
    """
    fetchclimate_map = FetchClimateMap(
        url_parameter=FetchClimateURLParameter(serverUrl='http://fetchclimate2.cloudapp.net'),
        variable_parameters=FetchClimateVariableParameters(variables={
            'prate': [423, 432, 426, 424],
            'elev': []
        }),
        map_parameters=FetchClimateMapParameters(
            css={'height': '600px',
                 'width': '100%'},
            map_data=FetchClimateMapData(
                drawing_types_enabled=['RECTANGLE', 'POINTS'],
                initial_drawing_mode='RECTANGLE',
                max_num_grids=2
            )
        ),
        grid_parameters=FetchClimateGridParameters(
            title='Provo Canyon Watershed',
            boundingBox=[40.308836, 40.381579, -111.654462, -111.550778],
            gridResolution=[25, 25]
        ),
        point_parameters=FetchClimatePointParameters(
            title='Clyde Building',
            location=[40.246942, -111.647971],
        ),
        plot_parameters=FetchClimatePlotParameters(dimensions={'width': 500, 'height': 350})
    )

    context = {'fetchclimate_map': fetchclimate_map}

    return render(request, 'tethys_gizmos/gizmo_showcase/fetchclimate_map.html', context)
