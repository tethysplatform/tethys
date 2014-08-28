import json
from datetime import datetime
import ckan.plugins as p
from ckan.lib.base import BaseController, h, abort
from pylons.decorators import jsonify

class SnippetShowcaseController(BaseController):

    def index(self):
        t = p.toolkit
        c = t.c
        _ = t._

        # Button Group Data
        c.single_button = {'buttons': [{'display_text': 'Click Me',
                                        'name': 'click_me_name',
                                        'attributes': 'onclick=alert(this.name);',
                                        'type': 'submit'}
                                       ]}

        c.horizontal_buttons = {'buttons': [{'display_text': 'Add',
                                             'icon': 'icon-plus',
                                             'style': 'success'},
                                            {'display_text': 'Delete',
                                             'icon': 'icon-trash',
                                             'disabled': True,
                                             'style': 'danger'}
                                            ]}

        c.vertical_buttons = {'buttons': [
                                           {'display_text': 'Edit',
                                            'icon': 'icon-wrench',
                                            'style': 'warning',
                                            'attributes':'id=edit_button'},
                                           {'display_text': 'Info',
                                            'icon': 'icon-question-sign',
                                            'style': 'info',
                                            'attributes': 'name=info'},
                                           {'display_text': 'Apps',
                                            'icon': 'icon-home',
                                            'href': h.url_for('apps'),
                                            'style': 'primary'}
                                           ],
                               'vertical': True}

        # Date Picker Data
        c.date_picker = {'display_text': 'Date',
                         'name': 'date1',
                         'autoclose': True,
                         'format': 'MM d, yyyy',
                         'start_date': '2/15/2014',
                         'start_view': 'decade',
                         'today_button': True,
                         'initial': 'February 15, 2014'}

        c.date_picker_error = {'display_text': 'Date',
                               'name': 'date2',
                               'initial': '10/2/2013',
                               'disabled': True,
                               'error': 'Here is my error text'}

        # Range Slider Data
        c.slider1 = {'display_text': 'Slider 1',
                     'name': 'slider1',
                     'min': 0,
                     'max': 100,
                     'initial': 50,
                     'step': 1}
        c.slider2 = {'display_text': 'Slider 2',
                     'name': 'slider2',
                     'min': 0,
                     'max': 1,
                     'initial': 0.5,
                     'step': 0.1,
                     'disabled': True,
                     'error': 'Incorrect, please choose another value.'}

        # Select Input
        c.select_input = {'display_text': 'Select',
                          'name': 'select1',
                          'multiple': False,
                          'options': [('One', '1'), ('Two', '2'), ('Three', '3')],
                          'initial': ['Two']}

        c.select_input_multiple = {'display_text': 'Select Multiple',
                                   'name': 'select2',
                                   'multiple': True,
                                   'options': [('One', '1'), ('Two', '2'), ('Three', '3')]}

        c.select_input_error = {'display_text': 'Select Disabled',
                                'name': 'select3',
                                'multiple': False,
                                'options': [('One', '1'), ('Two', '2'), ('Three', '3')],
                                'disabled': True,
                                'error': 'Here is my error text'}

        # Text Input
        c.text_input = {'display_text': 'Text',
                        'name': 'inputAmount',
                        'placeholder': 'e.g.: 10.00',
                        'prepend': '$'}

        c.text_error_input = {'display_text': 'Text Error',
                              'name': 'inputEmail',
                              'initial': 'bob@example.com',
                              'disabled': True,
                              'icon_append':'icon-envelope',
                              'error': 'Here is my error text'}

        # Toggle Switch
        c.toggle_switch = {'display_text': 'Defualt Toggle',
                           'name': 'toggle1'}

        c.toggle_switch_styled = {'display_text': 'Styled Toggle',
                                  'name': 'toggle2',
                                  'on_label': 'Yes',
                                  'off_label': 'No',
                                  'on_style': 'success',
                                  'off_style': 'danger',
                                  'initial': True,
                                  'size': 'large'}

        c.toggle_switch_disabled = {'display_text': 'Disabled Toggle',
                                    'name': 'toggle3',
                                    'on_label': 'On',
                                    'off_label': 'Off',
                                    'on_style': 'success',
                                    'off_style': 'warning',
                                    'size': 'mini',
                                    'initial': False,
                                    'disabled': True,
                                    'error': 'Here is my error text'}

        # Plot Views
        highcharts_object = {'chart': {
                                'type': 'spline'
                            },
                            'title': {
                                'text': 'Plot Title'
                            },
                            'subtitle': {
                                'text': 'Plot Subtitle'
                            },
                            'legend': {
                                'layout': 'vertical',
                                'align': 'right',
                                'verticalAlign': 'middle',
                                'borderWidth': 0
                            },
                            'xAxis': {
                                'title': {
                                    'enabled': True,
                                    'text': 'Altitude (km)'
                                },
                                'labels': {
                                    'formatter': 'function () { return this.value + " km"; }'
                                }
                            },
                            'yAxis': {
                                'title': {
                                    'enabled': True,
                                    'text': 'Temperature (*C)'
                                },
                                'labels': {
                                    'formatter': 'function () { return this.value + " *C"; }'
                                }
                            },
                            'tooltip': {
                                'headerFormat': '<b>{series.name}</b><br/>',
                                'pointFormat': '{point.x} km: {point.y}*C'
                             },
                            'series': [{
                                'name': 'Air Temp',
                                'color': '#0066ff',
                                'dashStyle': 'ShortDash',
                                'marker' : {'enabled': False},
                                'data': [[0, 5], [10, -70], [20, -86.5], [30, -66.5], [40, -32.1],
                                         [50, -12.5], [60, -47.7], [70, -85.7], [80, -106.5]]
                                },{
                                'name': 'Water Temp',
                                'color': '#ff6600',
                                'data': [[0, 15], [10, -50], [20, -56.5], [30, -46.5], [40, -22.1],
                                         [50, -2.5], [60, -27.7], [70, -55.7], [80, -76.5]]}
                            ]}

        c.line_plot_view = {'highcharts_object': highcharts_object,
                            'width': '500px',
                            'height': '500px'}

        # Web Plot
        web_plot_object = {'chart': {
                                'polar': True,
                                'type': 'line'
                            },
                            'title': {
                                'text': 'Polar Chart'
                            },
                            'pane': {
                                'size': '80%'
                            },
                            'xAxis': {
                                'categories': ['Infiltration', 'Soil Moisture', 'Precipitation', 'Evaporation',
                                               'Roughness', 'Runoff', 'Permeability', 'Vegetation'],
                                'tickmarkPlacement': 'on',
                                'lineWidth': 0
                            },
                            'yAxis': {
                                'gridLineInterpolation': 'polygon',
                                'lineWidth': 0,
                                'min': 0
                            },
                            'series': [{
                                'name': 'Park City',
                                'data': [0.2, 0.5, 0.1, 0.8, 0.2, 0.6, 0.8, 0.3],
                                'pointPlacement': 'on'
                            }, {
                                'name': 'Little Dell',
                                'data': [0.8, 0.3, 0.2, 0.5, 0.1, 0.8, 0.2, 0.6],
                                'pointPlacement': 'on'
                            }
                            ]}


        c.web_plot = {'highcharts_object': web_plot_object,
                      'width': '500px',
                      'height': '500px'}

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
                'maxZoom': 30 * 24 * 3600000, # 30 days in milliseconds
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
                    [datetime(2008, 12,  2), 0.8 ],
                    [datetime(2008, 12,  9), 0.6 ],
                    [datetime(2008, 12, 16), 0.6 ],
                    [datetime(2008, 12, 28), 0.67],
                    [datetime(2009,  1,  1), 0.81],
                    [datetime(2009,  1,  8), 0.78],
                    [datetime(2009,  1, 12), 0.98],
                    [datetime(2009,  1, 27), 1.84],
                    [datetime(2009,  2, 10), 1.80],
                    [datetime(2009,  2, 18), 1.80],
                    [datetime(2009,  2, 24), 1.92],
                    [datetime(2009,  3,  4), 2.49],
                    [datetime(2009,  3, 11), 2.79],
                    [datetime(2009,  3, 15), 2.73],
                    [datetime(2009,  3, 25), 2.61],
                    [datetime(2009,  4,  2), 2.76],
                    [datetime(2009,  4,  6), 2.82],
                    [datetime(2009,  4, 13), 2.8 ],
                    [datetime(2009,  5,  3), 2.1 ],
                    [datetime(2009,  5, 26), 1.1 ],
                    [datetime(2009,  6,  9), 0.25],
                    [datetime(2009,  6, 12), 0   ]
                ]
            }]
        }

        c.timeseries_plot = {'highcharts_object': timeseries_plot_object,
                             'width': '500px',
                             'height': '500px'}

        # Table View
        c.table_view = {'column_names': ('Name', 'Age', 'Job'),
                        'rows': [('Bill', 30, 'contractor'),
                                 ('Fred', 18, 'programmer'),
                                 ('Bob', 26, 'boss')],
                        'hover': True,
                        'striped': False,
                        'bordered': False,
                        'condensed': False}

        c.table_view_edit = {'column_names': ('Name', 'Age', 'Job'),
                             'rows': [('Bill', 30, 'contractor'),
                                      ('Fred', 18, 'programmer'),
                                      ('Bob', 26, 'boss')],
                             'hover': True,
                             'striped': True,
                             'bordered': False,
                             'condensed': False,
                             'editable_columns': (False, 'ageInput', 'jobInput'),
                             'row_ids': [21, 25, 31]}


        # Message Box
        c.message_box = {'name': 'sampleModal',
                         'title': 'Message Box Title',
                         'message': 'Congratulations! This is a message box.',
                         'dismiss_button': 'Nevermind',
                         'affirmative_button': 'Proceed',
                         'width': 400,
                         'affirmative_attributes': 'href=javascript:void(0);'}

        # Editable Google Map
        c.editable_google_map = {'height': '600px',
                                 'width': '100%',
                                 'reference_kml_action': h.url_for('snippet-showcase-action', action='get_kml'),
                                 'maps_api_key': 'AIzaSyAswFfpH07XyrhFEjClWzXHwwhGzEhiYws',
                                 'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES'],
                                 'initial_drawing_mode': 'POINTS',
                                 'output_format': 'WKT'}

        c.flash_message = ''

        if ('editable_map_submit' in t.request.params) and (t.request.params['geometry']):
            # Some example code showing how you can decode the JSON into python 
            # data structures.
            geometry_string = t.request.params['geometry']

            # Display the JSON as flash message
            c.flash_message = geometry_string

        #Fetchclimate 
        c.fetchclimate_array = {
                                  'serverUrl':'http://fetchclimate2.cloudapp.net',
                                  'variables': {
                                    'prate':[423,432,426,424],
                                    'elev':[]
                                  },
                                    'grid' : {
                                      'title' : 'Provo Canyon Watershed',
                                      'boundingBox' : [40.308836,40.381579,-111.654462,-111.550778],
                                      'gridResolution':[25,25]
                                  },
                                    'point' : {
                                      'title' : 'Clyde Building',
                                      'location':[40.246942,-111.647971],
                                  },
                                  'dataEvent':True
                                }


        return t.render('snippets_showcase/index.html')

    @jsonify
    def get_kml(self):
        '''
        This action is used to pass the kml data to the google map. It must
        return JSON with the key 'kml_link'.
        '''
        kml_links = ['http://ciwweb.chpc.utah.edu/dataset/00d54047-8581-4dc2-bdc2-b96f5a635455/resource/a656ecc5-5ddc-415a-ad12-aab50adc4818/download/elepolyterrain.kml']
        
        for i in range(10000000):
            pass
        
        return {'kml_link':kml_links}

    @jsonify
    def swap_kml(self):
        '''
        This action is used to pass the kml data to the google map. It must
        return JSON with the key 'kml_link'.
        '''
        for i in range(0, 20000000):
            pass

        kml_links = ['http://ciwweb.chpc.utah.edu/dataset/00d54047-8581-4dc2-bdc2-b96f5a635455/resource/1bb2db00-9944-4084-9ff7-b7897f483088/download/littledellcluster.kml']
        return {'kml_link':kml_links}
    
    @jsonify
    def swap_overlays(self):
        '''
        This action is used to demonstrate how overlay layers can be swapped out
        dynamically using the javascript API.
        '''
        
        overlay_json = {"type":"GeometryCollection",
                        "geometries":[{"type":"Polygon",
                                       "coordinates":[[40.643135583312805,-111.48951530456543],[40.636622594719725,-111.49432182312012],[40.63310531666155,-111.4877986907959],[40.63805550673186,-111.48110389709473],[40.6413120105605,-111.48539543151855]],
                                       "properties":{"id":4,"value":5},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}},
                                      {"type":"Point",
                                       "coordinates":[40.629587853312174,-111.50959968566895],
                                       "properties":{"id":5,"value":6},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}},
                                      {"type":"LineString",
                                       "coordinates":[[40.62737305910759,-111.50118827819824],[40.61564645424611,-111.5071964263916],[40.61277963772034,-111.48608207702637],[40.62802447679272,-111.49157524108887]],
                                       "properties":{"id":6,"value":7},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}}]}
        
        return {'overlay_json': overlay_json}

    def editable_map(self):
        '''
        Place to display editable google map in an isolated environment
        '''
        t = p.toolkit
        c = t.c
        _ = t._

        # Editable Google Map
#         c.editable_google_map = {'height': '700px',
#                                  'width': '100%',
#                                  'reference_kml_action': h.url_for('snippet-showcase-action', action='get_kml'),
#                                  'maps_api_key': 'AIzaSyAswFfpH07XyrhFEjClWzXHwwhGzEhiYws',
#                                  'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES'],
#                                  'initial_drawing_mode': 'POINTS',
#                                  'output_format': 'WKT',
#                                  'input_overlays': {'type':'WKTGeometryCollection',
#                                                     'geometries':[
#                                                                   {'type':'Point',
#                                                                    'wkt':'POINT(-111.5123462677002 40.629197012613545)',
#                                                                    'properties':{'id':1,'value':1}
#                                                                    },
#                                                                   {'type':'Polygon',
#                                                                    'wkt':'POLYGON((-111.50153160095215 40.63193284946615, -111.50101661682129 40.617210120505035, -111.48625373840332 40.623594711231775, -111.49123191833496 40.63193284946615, -111.50153160095215 40.63193284946615))',
#                                                                    'properties':{'id':2,'value':2}
#                                                                    },
#                                                                   {'type':'PolyLine',
#                                                                    'wkt':'POLYLINE(-111.49123191833496 40.65003865742191, -111.49088859558105 40.635319920747456, -111.48127555847168 40.64912697157757, -111.48024559020996 40.634668574229735)',
#                                                                    'properties':{'id':3,'value':3}
#                                                                    }
#                                                                   ]
#                                                     }
#                                  }
        
        c.editable_google_map = {'height': '700px',
                                 'width': '100%',
                                 'reference_kml_action': h.url_for('snippet-showcase-action', action='get_kml'),
                                 'maps_api_key': 'AIzaSyB-0nvmHhbOaaiYx6UN36145lWjUq5c2tg',
                                 'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES'],
                                 'initial_drawing_mode': 'POINTS',
                                 'input_overlays': {"type":"GeometryCollection",
                                                    "geometries":[
                                                                  {"type":"Point",
                                                                   "coordinates":[40.629197012613545,-111.5123462677002],
                                                                   "properties":{"id":1,"value":1}},
                                                                  {"type":"Polygon",
                                                                   "coordinates":[[40.63193284946615,-111.50153160095215],[40.617210120505035,-111.50101661682129],[40.623594711231775,-111.48625373840332],[40.63193284946615,-111.49123191833496]],
                                                                   "properties":{"id":2,"value":2}},
                                                                  {"type":"LineString",
                                                                   "coordinates":[[40.65003865742191,-111.49123191833496],[40.635319920747456,-111.49088859558105],[40.64912697157757,-111.48127555847168],[40.634668574229735,-111.48024559020996]],
                                                                   "properties":{"id":3,"value":3}}
                                                    ]},
                                 'color_ramp': {'1': '#ff0000',
                                                '2': '#ffff00',
                                                '3': '#00ff00',
                                                '4': '#0000ff'}
                                 }

        c.flash_message = ''
        print t.request.params
        if ('editable_map_submit' in t.request.params) and (t.request.params['geometry']):
            # Some example code showing how you can decode the JSON into python 
            # data structures.
            geometry_string = t.request.params['geometry']
            geometry_json = json.loads(geometry_string)
            c.editable_google_map['input_overlays'] = geometry_json

            # Display the JSON as flash message
            c.flash_message = geometry_string

        return t.render('snippets_showcase/editable_map.html')

    def google_map(self):
        '''
        Place to display google map view in an isoloted environment
        '''
        t = p.toolkit
        c = t.c
        _ = t._

        # Google Map
        c.google_map = {'height': '700px',
                        'width': '100%',
                        'kml_service': h.url_for('snippet-showcase-action', action='get_kml'),
                        'maps_api_key':'AIzaSyAswFfpH07XyrhFEjClWzXHwwhGzEhiYws'}

        return t.render('snippets_showcase/google_map.html')
    
    def map_view(self):
        '''
        Place to show off the new map view
        '''
        t = p.toolkit
        c = t.c
        
        c.map_view = {'map_type':'google-earth',                #map types: 'google-earth', 'google-map', 'open-layers'
                      'height': '700px',
                      'width': '100%',
                      'legend': True,                           # true shows legend, false hides it
                      'legend_options': {'addLayers':False},     # options: addLayers,
                       
                      # array of links to map layers
                      'layer_data': ['http://tethys.byu.edu/storage/f/2013-11-13T18%3A58%3A10.477Z/soil-poly-v2.kml',
                                     #'http://tethys.byu.edu/storage/f/2013-11-22T18%3A02%3A16.551Z/ele-poly-terrain.kml'
                                    ],
                      
                      # url to retrieve an object containing an array of layer links
                      'kml_service': h.url_for('snippet-showcase-action', action='get_kml'),
                      
                      #Google Maps api key if Google Maps is used  
                      'maps_api_key':'AIzaSyAswFfpH07XyrhFEjClWzXHwwhGzEhiYws'}
        
        return t.render('snippets_showcase/map_view.html')
    def fetchclimate_map(self):
        '''
        Place to show off the new map view
        '''
        t = p.toolkit
        c = t.c

        c.fetchclimate_map = {
                    'serverUrl':'http://fetchclimate2.cloudapp.net',
                    'variables': {
                      'prate':[423,432,426,424],
                      'elev':[]
                    },
                    'map': { 
                      'css' : {'height': '600px',
                              'width': '100%'},
                      'map_data' : {
                        'api_key': 'AIzaSyAswFfpH07XyrhFEjClWzXHwwhGzEhiYws',
                        'drawing_types_enabled': ['RECTANGLE', 'POINTS'],
                        'initial_drawing_mode': 'RECTANGLE',
                        'max_num_grids' : 2
                      }
                    },
                    'grid' : {
                                'title' : 'Provo Canyon Watershed',
                                'boundingBox' : [40.308836,40.381579,-111.654462,-111.550778],
                                'gridResolution':[25,25]
                    },
                    'point' : {
                                'title' : 'Clyde Building',
                                'location':[40.246942,-111.647971],
                    },
                    'plot': {
                      'css' : {'height': '600px',
                              'width': '600px'}
                    }
                  }

        return t.render('snippets_showcase/fetchclimate_map.html')
        
        
