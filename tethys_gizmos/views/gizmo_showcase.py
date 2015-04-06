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

    map_view = MapViewOptions(
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
