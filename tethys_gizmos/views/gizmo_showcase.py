# coding=utf-8
"""
********************************************************************************
* Name: gizmo_showcase.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import json
from datetime import datetime
from tethys_sdk.permissions import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import plotly.graph_objs as go
from bokeh.plotting import figure as bokeh_figure

from tethys_sdk.gizmos import Button, ButtonGroup, DatePicker, RangeSlider, SelectInput, TextInput, ToggleSwitch, \
    LinePlot, ScatterPlot, PolarPlot, PiePlot, BarPlot, TimeSeries, AreaRange, PlotlyView, BokehView, TableView, \
    DataTableView, MessageBox, GoogleMapView, MVView, MVDraw, MVLayer, MVLegendClass, MapView, JobsTable, EMView, \
    EMLayer, ESRIMap, CesiumMapView
from tethys_compute.models import TethysJob, BasicJob, CondorWorkflow


def get_geoserver_wms():
    """
    Try to get the built in geoserver wms for this installation if possible.
    Otherwise point at the chpc geoserver.
    """
    return 'https://demo.geo-solutions.it/geoserver/wms'


@login_required()
def index(request):
    """
    Django view for the gizmo showcase page
    """
    # Docs version
    docs_endpoint = 'http://docs.tethysplatform.org/en/latest'

    # Uncomment this line for debugging on the localhost
    # docs_endpoint = 'http://localhost:63342/tethys/docs/_build/html'

    # Button and Button Group
    # Single button
    single_button = Button(display_text='Click Me',
                           name='click_me_name',
                           attributes='onclick=alert(this.name);',
                           submit=True)

    # Horizontal Button Group
    add_button = Button(display_text='Add',
                        icon='glyphicon glyphicon-plus',
                        style='success')
    delete_button = Button(display_text='Delete',
                           icon='glyphicon glyphicon-trash',
                           disabled=True,
                           style='danger')
    horizontal_buttons = ButtonGroup(buttons=[add_button, delete_button])

    # Vertical Button Group
    edit_button = Button(display_text='Edit',
                         icon='glyphicon glyphicon-wrench',
                         style='warning',
                         attributes='id="edit button" new_attr=attr')
    info_button = Button(display_text='Info',
                         icon='glyphicon glyphicon-question-sign',
                         style='info',
                         attributes='name=info')
    apps_button = Button(display_text='Apps',
                         icon='glyphicon glyphicon-home',
                         href='/apps',
                         style='primary')
    vertical_buttons = ButtonGroup(buttons=[edit_button, info_button, apps_button], vertical=True)

    # Date Picker Options
    date_picker = DatePicker(name='date1',
                             display_text='Date',
                             autoclose=True,
                             format='MM d, yyyy',
                             start_date='2/15/2014',
                             start_view='decade',
                             today_button=True,
                             initial='February 15, 2014')

    date_picker_error = DatePicker(name='data2',
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
                                name='select2',
                                multiple=False,
                                options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                initial=['Three'],
                                select2_options={'placeholder': 'Select a number',
                                                 'allowClear': True})

    select_input2_multiple = SelectInput(display_text='Select2 Multiple',
                                         name='select21',
                                         multiple=True,
                                         options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                         initial=['Two', 'One'])

    select_input2_error = SelectInput(display_text='Select2 Disabled',
                                      name='select22',
                                      multiple=False,
                                      options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                                      disabled=True,
                                      error='Here is my error text')

    select_input = SelectInput(display_text='Select',
                               name='select1',
                               multiple=False,
                               original=True,
                               options=[('One', '1'), ('Two', '2'), ('Three', '3')],
                               initial=['Three'])

    select_input_multiple = SelectInput(display_text='Select Multiple',
                                        name='select11',
                                        multiple=True,
                                        original=True,
                                        options=[('One', '1'), ('Two', '2'), ('Three', '3')])

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
    line_plot_view = LinePlot(height='500px',
                              width='500px',
                              engine='highcharts',
                              title='Plot Title',
                              subtitle='Plot Subtitle',
                              spline=True,
                              x_axis_title='Altitude',
                              x_axis_units='km',
                              y_axis_title='Temperature',
                              y_axis_units='°C',
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
                                      'data': [
                                          [0, 15], [10, -50],
                                          [20, -56.5], [30, -46.5],
                                          [40, -22.1],
                                          [50, -2.5], [60, -27.7],
                                          [70, -55.7], [80, -76.5]
                                      ]
                                  }
                              ]
                              )

    # D3 Line Plot View
    d3_line_plot_view = LinePlot(height='500px',
                                 width='100%',
                                 engine='d3',
                                 title='Plot Title',
                                 subtitle='Plot Subtitle',
                                 spline=True,
                                 x_axis_title='Altitude',
                                 x_axis_units='km',
                                 y_axis_title='Temperature',
                                 y_axis_units='°C',
                                 series=[
                                     {
                                         'name': 'Air Temp',
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
                                         'data': [
                                             [0, 15], [10, -50],
                                             [20, -56.5], [30, -46.5],
                                             [40, -22.1],
                                             [50, -2.5], [60, -27.7],
                                             [70, -55.7], [80, -76.5]
                                         ]
                                     }
                                 ]
                                 )

    # Plot Views
    male_dataset = {
        'name': 'Male',
        'color': '#0066ff',
        'data': [
            [174.0, 65.6], [175.3, 71.8], [193.5, 80.7], [186.5, 72.6],
            [187.2, 78.8], [181.5, 74.8], [184.0, 86.4], [184.5, 78.4],
            [175.0, 62.0], [184.0, 81.6], [180.0, 76.6], [177.8, 83.6],
            [192.0, 90.0], [176.0, 74.6], [174.0, 71.0], [184.0, 79.6],
            [192.7, 93.8], [171.5, 70.0], [173.0, 72.4], [176.0, 85.9],
            [176.0, 78.8], [180.5, 77.8], [172.7, 66.2], [176.0, 86.4],
            [173.5, 81.8], [178.0, 89.6], [180.3, 82.8], [180.3, 76.4],
            [164.5, 63.2], [173.0, 60.9], [183.5, 74.8], [175.5, 70.0],
            [188.0, 72.4], [189.2, 84.1], [172.8, 69.1], [170.0, 59.5],
            [182.0, 67.2], [170.0, 61.3], [177.8, 68.6], [184.2, 80.1],
            [186.7, 87.8], [171.4, 84.7], [172.7, 73.4], [175.3, 72.1],
            [180.3, 82.6], [182.9, 88.7], [188.0, 84.1], [177.2, 94.1],
            [172.1, 74.9], [167.0, 59.1], [169.5, 75.6], [174.0, 86.2],
            [172.7, 75.3], [182.2, 87.1], [164.1, 55.2], [163.0, 57.0],
            [171.5, 61.4], [184.2, 76.8], [174.0, 86.8], [174.0, 72.2],
            [177.0, 71.6], [186.0, 84.8], [167.0, 68.2], [171.8, 66.1]
        ]
    }

    female_dataset = {
        'name': 'Female',
        'color': '#ff6600',
        'data': [
            [161.2, 51.6], [167.5, 59.0], [159.5, 49.2], [157.0, 63.0],
            [155.8, 53.6], [170.0, 59.0], [159.1, 47.6], [166.0, 69.8],
            [176.2, 66.8], [160.2, 75.2], [172.5, 55.2], [170.9, 54.2],
            [172.9, 62.5], [153.4, 42.0], [160.0, 50.0], [147.2, 49.8],
            [168.2, 49.2], [175.0, 73.2], [157.0, 47.8], [167.6, 68.8],
            [159.5, 50.6], [175.0, 82.5], [166.8, 57.2], [176.5, 87.8],
            [170.2, 72.8], [174.0, 54.5], [173.0, 59.8], [179.9, 67.3],
            [170.5, 67.8], [160.0, 47.0], [154.4, 46.2], [162.0, 55.0],
            [176.5, 83.0], [160.0, 54.4], [152.0, 45.8], [162.1, 53.6],
            [170.0, 73.2], [160.2, 52.1], [161.3, 67.9], [166.4, 56.6],
            [168.9, 62.3], [163.8, 58.5], [167.6, 54.5], [160.0, 50.2],
            [161.3, 60.3], [167.6, 58.3], [165.1, 56.2], [160.0, 50.2],
            [170.0, 72.9], [157.5, 59.8], [167.6, 61.0], [160.7, 69.1],
            [163.2, 55.9], [152.4, 46.5], [157.5, 54.3], [168.3, 54.8],
            [180.3, 60.7], [165.5, 60.0], [165.0, 62.0], [164.5, 60.3]
        ]
    }

    scatter_plot_view = ScatterPlot(
        width='500px',
        height='500px',
        engine='highcharts',
        title='Scatter Plot',
        subtitle='Scatter Plot',
        x_axis_title='Height',
        x_axis_units='cm',
        y_axis_title='Weight',
        y_axis_units='kg',
        series=[male_dataset, female_dataset]
    )

    # D3 Scatter Plot
    d3_scatter_plot_view = ScatterPlot(
        width='100%',
        height='500px',
        engine='d3',
        title='D3 Scatter Plot',
        subtitle='D3 Scatter Plot',
        x_axis_title='Height',
        x_axis_units='cm',
        y_axis_title='Weight',
        y_axis_units='kg',
        series=[male_dataset, female_dataset]
    )

    # Web Plot
    web_plot = PolarPlot(
        width='500px',
        height='500px',
        engine='highcharts',
        title='Polar Chart',
        subtitle='Polar Chart',
        pane={
            'size': '80%'
        },
        categories=['Infiltration', 'Soil Moisture', 'Precipitation',
                    'Evaporation', 'Roughness', 'Runoff', 'Permeability',
                    'Vegetation'],
        series=[
            {
                'name': 'Park City',
                'data': [0.2, 0.5, 0.1, 0.8, 0.2, 0.6, 0.8, 0.3],
                'pointPlacement': 'on'
            },
            {
                'name': 'Little Dell',
                'data': [0.8, 0.3, 0.2, 0.5, 0.1, 0.8, 0.2, 0.6],
                'pointPlacement': 'on'
            }
        ]
    )

    # Pie Plot
    pie_plot_view = PiePlot(
        width='500px',
        height='500px',
        engine='highcharts',
        title='Pie Chart',
        subtitle='Pie Chart',
        series=[{
            'type': 'pie',
            'name': 'Browser share',
            'data': [
                ['Firefox', 45.0],
                ['IE', 26.8],
                {
                    'name': 'Chrome',
                    'y': 12.8,
                    'sliced': True,
                    'selected': True
                },
                ['Safari', 8.5],
                ['Opera', 6.2],
                ['Others', 0.7]
            ]
        }]
    )

    # D3 Pie Plot
    d3_pie_plot_view = PiePlot(width='100%',
                               height='500px',
                               engine='d3',
                               title='Pie Chart',
                               subtitle='Pie Chart',
                               series=[
                                   {'name': 'Firefox', 'value': 45.0},
                                   {'name': 'IE', 'value': 26.8},
                                   {'name': 'Chrome', 'value': 12.8},
                                   {'name': 'Safari', 'value': 8.5},
                                   {'name': 'Opera', 'value': 8.5},
                                   {'name': 'Others', 'value': 0.7}
                               ])

    # Bar Plot
    bar_plot_view = BarPlot(
        width='500px',
        height='500px',
        engine='highcharts',
        title='Bar Chart',
        subtitle='Bar Chart',
        vertical=False,
        categories=[
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ],
        axis_units='millions',
        axis_title='Population',
        series=[{
            'name': 'Year 1800',
            'data': [107, 31, 635, 203, 2]
        }, {
            'name': 'Year 1900',
            'data': [133, 156, 947, 408, 6]
        }, {
            'name': 'Year 2008',
            'data': [973, 914, 4054, 732, 34]}
        ]
    )

    # D3 Bar Plot
    d3_bar_plot_view = BarPlot(
        width='100%',
        title='Bar Chart',
        subtitle='Bar Chart',
        vertical=True,
        categories=[
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ],
        axis_units='millions',
        axis_title='Population',
        series=[{
            'name': "Year 1800",
            'data': [100, 31, 635, 203, 275, 487, 872, 671, 736, 568, 487, 432]
        }, {
            'name': "Year 1900",
            'data': [133, 200, 947, 408, 682, 328, 917, 171, 482, 140, 176, 237]
        }, {
            'name': "Year 2000",
            'data': [764, 628, 300, 134, 678, 200, 781, 571, 773, 192, 836, 172]
        }, {
            'name': "Year 2008",
            'data': [973, 914, 500, 400, 349, 108, 372, 726, 638, 927, 621, 364]
        }
        ]
    )

    # Time series plot
    timeseries_plot = TimeSeries(
        width='500px',
        height='500px',
        engine='highcharts',
        title='Irregular Timeseries Plot',
        y_axis_title='Snow depth',
        y_axis_units='m',
        series=[{
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
        }, {
            'name': 'Winter test',
            'data': [
                [datetime(2008, 12, 2), 1.8],
                [datetime(2008, 12, 9), 1.6],
                [datetime(2008, 12, 16), 1.6],
                [datetime(2008, 12, 28), 1.67],
                [datetime(2009, 1, 1), 1.81],
                [datetime(2009, 1, 8), 1.78],
                [datetime(2009, 1, 12), 1.98],
                [datetime(2009, 1, 27), 2.84],
                [datetime(2009, 2, 10), 2.80],
                [datetime(2009, 2, 18), 2.80],
                [datetime(2009, 2, 24), 2.92],
                [datetime(2009, 3, 4), 3.49],
                [datetime(2009, 3, 11), 3.79],
                [datetime(2009, 3, 15), 3.73],
                [datetime(2009, 3, 25), 3.61],
                [datetime(2009, 4, 2), 3.76],
                [datetime(2009, 4, 6), 3.82],
                [datetime(2009, 4, 13), 3.8],
                [datetime(2009, 5, 3), 3.1],
                [datetime(2009, 5, 26), 2.1],
                [datetime(2009, 6, 9), 1.25],
                [datetime(2009, 6, 12), 0]
            ]
        }]
    )

    # D3 Time series plot
    d3_timeseries_plot_view = TimeSeries(
        width='100%',
        title='Irregular Timeseries Plot',
        y_axis_title='Snow depth',
        y_axis_units='m',
        series=[{
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
        }, {
            'name': 'Winter test',
            'data': [
                [datetime(2008, 12, 2), 1.8],
                [datetime(2008, 12, 9), 1.6],
                [datetime(2008, 12, 16), 1.6],
                [datetime(2008, 12, 28), 1.67],
                [datetime(2009, 1, 1), 1.81],
                [datetime(2009, 1, 8), 1.78],
                [datetime(2009, 1, 12), 1.98],
                [datetime(2009, 1, 27), 2.84],
                [datetime(2009, 2, 10), 2.80],
                [datetime(2009, 2, 18), 2.80],
                [datetime(2009, 2, 24), 2.92],
                [datetime(2009, 3, 4), 3.49],
                [datetime(2009, 3, 11), 3.79],
                [datetime(2009, 3, 15), 3.73],
                [datetime(2009, 3, 25), 3.61],
                [datetime(2009, 4, 2), 3.76],
                [datetime(2009, 4, 6), 3.82],
                [datetime(2009, 4, 13), 3.8],
                [datetime(2009, 5, 3), 3.1],
                [datetime(2009, 5, 26), 2.1],
                [datetime(2009, 6, 9), 1.25],
                [datetime(2009, 6, 12), 0]
            ]
        }]
    )

    averages = [
        [datetime(2009, 7, 1), 21.5], [datetime(2009, 7, 2), 22.1], [datetime(2009, 7, 3), 23],
        [datetime(2009, 7, 4), 23.8], [datetime(2009, 7, 5), 21.4], [datetime(2009, 7, 6), 21.3],
        [datetime(2009, 7, 7), 18.3], [datetime(2009, 7, 8), 15.4], [datetime(2009, 7, 9), 16.4],
        [datetime(2009, 7, 10), 17.7], [datetime(2009, 7, 11), 17.5], [datetime(2009, 7, 12), 17.6],
        [datetime(2009, 7, 13), 17.7], [datetime(2009, 7, 14), 16.8], [datetime(2009, 7, 15), 17.7],
        [datetime(2009, 7, 16), 16.3], [datetime(2009, 7, 17), 17.8], [datetime(2009, 7, 18), 18.1],
        [datetime(2009, 7, 19), 17.2], [datetime(2009, 7, 20), 14.4],
        [datetime(2009, 7, 21), 13.7], [datetime(2009, 7, 22), 15.7], [datetime(2009, 7, 23), 14.6],
        [datetime(2009, 7, 24), 15.3], [datetime(2009, 7, 25), 15.3], [datetime(2009, 7, 26), 15.8],
        [datetime(2009, 7, 27), 15.2], [datetime(2009, 7, 28), 14.8], [datetime(2009, 7, 29), 14.4],
        [datetime(2009, 7, 30), 15], [datetime(2009, 7, 31), 13.6]
    ]

    ranges = [
        [datetime(2009, 7, 1), 14.3, 27.7], [datetime(2009, 7, 2), 14.5, 27.8], [datetime(2009, 7, 3), 15.5, 29.6],
        [datetime(2009, 7, 4), 16.7, 30.7], [datetime(2009, 7, 5), 16.5, 25.0], [datetime(2009, 7, 6), 17.8, 25.7],
        [datetime(2009, 7, 7), 13.5, 24.8], [datetime(2009, 7, 8), 10.5, 21.4], [datetime(2009, 7, 9), 9.2, 23.8],
        [datetime(2009, 7, 10), 11.6, 21.8], [datetime(2009, 7, 11), 10.7, 23.7], [datetime(2009, 7, 12), 11.0, 23.3],
        [datetime(2009, 7, 13), 11.6, 23.7], [datetime(2009, 7, 14), 11.8, 20.7], [datetime(2009, 7, 15), 12.6, 22.4],
        [datetime(2009, 7, 16), 13.6, 19.6], [datetime(2009, 7, 17), 11.4, 22.6], [datetime(2009, 7, 18), 13.2, 25.0],
        [datetime(2009, 7, 19), 14.2, 21.6], [datetime(2009, 7, 20), 13.1, 17.1], [datetime(2009, 7, 21), 12.2, 15.5],
        [datetime(2009, 7, 22), 12.0, 20.8], [datetime(2009, 7, 23), 12.0, 17.1], [datetime(2009, 7, 24), 12.7, 18.3],
        [datetime(2009, 7, 25), 12.4, 19.4], [datetime(2009, 7, 26), 12.6, 19.9], [datetime(2009, 7, 27), 11.9, 20.2],
        [datetime(2009, 7, 28), 11.0, 19.3], [datetime(2009, 7, 29), 10.8, 17.8], [datetime(2009, 7, 30), 11.8, 18.5],
        [datetime(2009, 7, 31), 10.8, 16.1]
    ]
    # Area Range plot
    area_range_plot = AreaRange(
        width='500px',
        height='500px',
        engine='highcharts',
        title='July Temperatures',
        y_axis_title='Temperature',
        y_axis_units='*C',
        series=[{
            'name': 'Temperature',
            'data': averages,
            'zIndex': 1,
            'marker': {
                'lineWidth': 2,
            }
        }, {
            'name': 'Range',
            'data': ranges,
            'type': 'arearange',
            'lineWidth': 0,
            'linkedTo': ':previous',
            'fillOpacity': 0.3,
            'zIndex': 0
        }]
    )

    # Plotly View
    x = [datetime(year=2013, month=10, day=4),
         datetime(year=2013, month=11, day=5),
         datetime(year=2013, month=12, day=6)]

    my_plotly_view = PlotlyView([go.Scatter(x=x, y=[1, 3, 6])])

    # TODO: Add pandas example when pandas is included with Tethys Platform

    # Bokeh View
    plot = bokeh_figure(plot_height=300)
    plot.circle([1, 2], [3, 4])
    my_bokeh_view = BokehView(plot, height="300px")

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

    # DataTable View
    datatable_default = DataTableView(column_names=('Name', 'Age', 'Job'),
                                      rows=[('Bill', 30, 'contractor'),
                                            ('Fred', 18, 'programmer'),
                                            ('Bob', 26, 'boss')],
                                      searching=False,
                                      orderClasses=False,
                                      lengthMenu=[[10, 25, 50, -1], [10, 25, 50, "All"]],
                                      )

    datatable_with_extension = DataTableView(column_names=('Name', 'Age', 'Job'),
                                             rows=[('Bill', 30, 'contractor'),
                                                   ('Fred', 18, 'programmer'),
                                                   ('Bob', 26, 'boss')],
                                             colReorder=True,
                                             )

    # Message Box
    message_box = MessageBox(name='sampleModal',
                             title='Message Box Title',
                             message='Congratulations! This is a message box.',
                             dismiss_button='Nevermind',
                             affirmative_button='Proceed',
                             width=400,
                             affirmative_attributes='href=javascript:void(0);')

    # Google Map View
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

    # Map View
    # Define view options
    view_options = MVView(
        projection='EPSG:4326',
        center=[-100, 40],
        zoom=3.5,
        maxZoom=18,
        minZoom=2
    )

    # Define drawing options
    drawing_options = MVDraw(output_format='WKT')

    # Define the layers
    map_layers = []

    # Define GeoJSON layer
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
                    'type': 'Polygon',
                    'coordinates': [[[-5e6, -1e6], [-4e6, 1e6], [-3e6, -1e6]]]
                }
            }
        ]
    }

    style = {'ol.style.Style': {
        'stroke': {'ol.style.Stroke': {
            'color': 'blue',
            'width': 2
        }},
        'fill': {'ol.style.Fill': {
            'color': 'green'
        }},
        'image': {'ol.style.Circle': {
            'radius': 10,
            'fill': None,
            'stroke': {'ol.style.Stroke': {
                'color': 'red',
                'width': 2
            }}
        }}
    }}

    geojson_layer = MVLayer(
        source='GeoJSON',
        options=geojson_object,
        layer_options={'style': style},
        legend_title='Test GeoJSON',
        legend_extent=[-46.7, -48.5, 74, 59],
        legend_classes=[
            MVLegendClass('polygon', 'Polygons', fill='green', stroke='blue'),
            MVLegendClass('line', 'Lines', stroke='blue')
        ]
    )

    map_layers.append(geojson_layer)

    if get_geoserver_wms():
        # Define GeoServer Layer
        geoserver_layer = MVLayer(source='ImageWMS',
                                  options={'url': get_geoserver_wms(),
                                           'params': {'LAYERS': 'topp:states'},
                                           'serverType': 'geoserver'},
                                  legend_title='USA Population',
                                  legend_extent=[-126, 24.5, -66.2, 49],
                                  legend_classes=[
                                      MVLegendClass('polygon', 'Low Density', fill='#00ff00', stroke='#000000'),
                                      MVLegendClass('polygon', 'Medium Density', fill='#ff0000', stroke='#000000'),
                                      MVLegendClass('polygon', 'High Density', fill='#0000ff', stroke='#000000')
                                  ])
        map_layers.append(geoserver_layer)

    # Define KML Layer
    kml_layer = MVLayer(source='KML',
                        options={'url': '/static/tethys_gizmos/data/model.kml'},
                        legend_title='Park City Watershed',
                        legend_extent=[-111.60, 40.57, -111.43, 40.70],
                        legend_classes=[
                            MVLegendClass('polygon', 'Watershed Boundary', fill='#ff8000'),
                            MVLegendClass('line', 'Stream Network', stroke='#0000ff'),
                        ])

    map_layers.append(kml_layer)

    # Tiled ArcGIS REST Layer
    arc_gis_layer = MVLayer(source='TileArcGISRest',
                            options={'url': 'http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/' +
                                            'Specialty/ESRI_StateCityHighway_USA/MapServer'},
                            legend_title='ESRI USA Highway',
                            legend_extent=[-173, 17, -65, 72])

    map_layers.append(arc_gis_layer)

    # Define map view options
    map_view_options = MapView(height='600px',
                               width='100%',
                               controls=['ZoomSlider', 'Rotate', 'FullScreen',
                                         {'MousePosition': {'projection': 'EPSG:4326'}},
                                         {'ZoomToExtent': {'projection': 'EPSG:4326',
                                                           'extent': [-130, 22, -65, 54]}
                                          }],
                               layers=map_layers,
                               view=view_options,
                               basemap=['OpenStreetMap',
                                        {'OpenStreetMap': {'url': 'http://tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
                                                           'label': 'Watercolor'}
                                         }],
                               draw=drawing_options,
                               legend=True)

    # ESRI Map Gizmo
    esri_map_view = EMView(center=[-100, 40], zoom=4)
    esri_layer = EMLayer(
        type='FeatureLayer',
        url='http://geoserver.byu.edu/arcgis/rest/services/gaugeviewer/AHPS_gauges/MapServer/0'
    )

    vector_tile = EMLayer(
        type='ImageryLayer',
        url='https://sampleserver6.arcgisonline.com/arcgis/rest/services/NLCDLandCover2001/ImageServer'
    )

    esri_map = ESRIMap(height='400px', width='100%', basemap='topo', view=esri_map_view,
                       layers=[vector_tile, esri_layer])

    # Define the context object
    context = {'docs_endpoint': docs_endpoint,
               'single_button': single_button,
               'horizontal_buttons': horizontal_buttons,
               'vertical_buttons': vertical_buttons,
               'date_picker': date_picker,
               'date_picker_error': date_picker_error,
               'slider1': slider1,
               'slider2': slider2,
               'select_input2': select_input2,
               'select_input2_multiple': select_input2_multiple,
               'select_input2_error': select_input2_error,
               'select_input': select_input,
               'select_input_multiple': select_input_multiple,
               'text_input': text_input,
               'text_error_input': text_error_input,
               'toggle_switch': toggle_switch,
               'toggle_switch_styled': toggle_switch_styled,
               'toggle_switch_disabled': toggle_switch_disabled,
               'line_plot_view': line_plot_view,
               'web_plot': web_plot,
               'timeseries_plot': timeseries_plot,
               'my_plotly_view': my_plotly_view,
               'my_bokeh_view': my_bokeh_view,
               'table_view': table_view,
               'table_view_edit': table_view_edit,
               'datatable_default': datatable_default,
               'datatable_with_extension': datatable_with_extension,
               'message_box': message_box,
               'google_map_view': google_map_view,
               'flash_message': flash_message,
               'map_view_options': map_view_options,
               "esri_map": esri_map,
               'scatter_plot_view': scatter_plot_view,
               'pie_plot_view': pie_plot_view,
               'd3_pie_plot_view': d3_pie_plot_view,
               'd3_line_plot_view': d3_line_plot_view,
               'd3_scatter_plot_view': d3_scatter_plot_view,
               'd3_bar_plot_view': d3_bar_plot_view,
               'd3_timeseries_plot_view': d3_timeseries_plot_view,
               'bar_plot_view': bar_plot_view,
               'area_range_plot': area_range_plot,
               # 'heat_map_plot': heat_map_plot,
               }

    return render(request, 'tethys_gizmos/gizmo_showcase/index.html', context)


def get_kml(request):
    """
    This action is used to pass the kml data to the google map. It must return JSON with the key 'kml_link'.
    """
    kml_links = [
        'http://ciwckan.chpc.utah.edu/dataset/00d54047-8581-4dc2-bdc2-b96f5a635455/resource'
        '/69f8e7df-da87-47cd-90a1-d15dc84e99ba/download/indexclusters.kml']

    return JsonResponse({'kml_links': kml_links})


def swap_kml(request):
    """
    This action is used to pass the kml data to the google map. It must return JSON with the key 'kml_link'.
    """
    for i in range(0, 20000000):
        pass

    kml_links = [
        'http://ciwckan.chpc.utah.edu/dataset/00d54047-8581-4dc2-bdc2-b96f5a635455/resource'
        '/53c7a910-5e00-4af7-803a-e48e0f17a131/download/elevation.kml']

    return HttpResponse(json.dumps(kml_links), content_type='application/json')


def swap_overlays(request):
    """
    This action is used to demonstrate how overlay layers can be swapped out dynamically using the javascript API.
    """

    overlay_json = {
        "type": "GeometryCollection",
        "geometries": [
            {"type": "Polygon",
             "coordinates": [[40.643135583312805, -111.48951530456543],
                             [40.636622594719725, -111.49432182312012],
                             [40.63310531666155, -111.4877986907959],
                             [40.63805550673186, -111.48110389709473],
                             [40.6413120105605, -111.48539543151855]],
             "properties": {"id": 4, "value": 5},
             "crs": {"type": "link",
                     "properties": {
                         "href": "http://spatialreference.org/ref/epsg/4326/proj4/",
                         "type": "proj4"
                     }
                     }
             },
            {"type": "Point",
             "coordinates": [40.629587853312174, -111.50959968566895],
             "properties": {"id": 5, "value": 6},
             "crs": {"type": "link",
                     "properties": {
                         "href": "http://spatialreference.org/ref/epsg/4326/proj4/",
                         "type": "proj4"
                     }
                     }
             },
            {"type": "LineString",
             "coordinates": [[40.62737305910759, -111.50118827819824],
                             [40.61564645424611, -111.5071964263916],
                             [40.61277963772034, -111.48608207702637],
                             [40.62802447679272, -111.49157524108887]],
             "properties": {"id": 6, "value": 7},
             "crs": {"type": "link",
                     "properties": {
                         "href": "http://spatialreference.org/ref/epsg/4326/proj4/",
                         "type": "proj4"
                     }
                     }
             }
        ]
    }

    return HttpResponse(json.dumps(overlay_json), content_type='application/json')


@login_required()
def google_map_view(request):
    """
    Place to display editable google map in an isolated environment
    """

    # Editable Google Map
    google_map_view = GoogleMapView(
        height='600px',
        width='100%',
        reference_kml_action=reverse('gizmos:get_kml'),
        drawing_types_enabled=['POLYGONS', 'POINTS', 'POLYLINES', 'BOXES'],
        initial_drawing_mode='BOXES',
        input_overlays={
            "type": "GeometryCollection",
            "geometries": [
                {"type": "Point",
                 "coordinates": [40.629197012613545, -111.5123462677002],
                 "properties": {"id": 1, "value": 1}
                 },
                {"type": "Polygon",
                 "coordinates": [[40.63193284946615, -111.50153160095215],
                                 [40.617210120505035, -111.50101661682129],
                                 [40.623594711231775, -111.48625373840332],
                                 [40.63193284946615, -111.49123191833496]],
                 "properties": {"id": 2, "value": 2}
                 },
                {"type": "LineString",
                 "coordinates": [[40.65003865742191, -111.49123191833496],
                                 [40.635319920747456, -111.49088859558105],
                                 [40.64912697157757, -111.48127555847168],
                                 [40.634668574229735, -111.48024559020996]],
                 "properties": {"id": 3, "value": 3}
                 },
                {"type": "BoundingBox",
                 "bounds": [-111.54521942138672, 40.597792003905454,
                            -111.46625518798828, 40.66449372533465],
                 "properties": {"id": 4, "value": 4}
                 }
            ]
        },
        output_format='WKT',
    )

    if ('editable_map_submit' in request.POST) and (request.POST['geometry']):
        # Some example code showing how you can decode the JSON into python
        # data structures.
        geometry_string = request.POST['geometry']
        geometry_json = json.loads(geometry_string)
        google_map_view.input_overlays = geometry_json

        # Display the JSON as flash message
        messages.info(request, geometry_string)

    context = {'google_map_view': google_map_view}

    return render(request, 'tethys_gizmos/gizmo_showcase/google_map_view.html', context)


@login_required()
def map_view(request):
    """
    Place to show off the new map view
    """

    # Define view options
    view_options = MVView(
        projection='EPSG:4326',
        center=[-100, 40],
        zoom=3.5,
        maxZoom=18,
        minZoom=2
    )

    # Define drawing options
    drawing_options = MVDraw()

    # Define GeoJSON layer
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
                    'type': 'Polygon',
                    'coordinates': [[[-5e6, -1e6], [-4e6, 1e6], [-3e6, -1e6]]]
                }
            }
        ]
    }

    # Define layers
    map_layers = []

    style_map = {
        'Point': {'ol.style.Style': {
            'image': {'ol.style.Circle': {
                'radius': 5,
                'fill': {'ol.style.Fill': {
                    'color': 'red',
                }},
                'stroke': {'ol.style.Stroke': {
                    'color': 'red',
                    'width': 2
                }}
            }}
        }},
        'LineString': {'ol.style.Style': {
            'stroke': {'ol.style.Stroke': {
                'color': 'green',
                'width': 3
            }}
        }},
        'Polygon': {'ol.style.Style': {
            'stroke': {'ol.style.Stroke': {
                'color': 'blue',
                'width': 1
            }},
            'fill': {'ol.style.Fill': {
                'color': 'rgba(0, 0, 255, 0.1)'
            }}
        }},
    }

    geojson_layer = MVLayer(source='GeoJSON',
                            options=geojson_object,
                            layer_options={'style_map': style_map},
                            legend_title='Test GeoJSON',
                            legend_extent=[-46.7, -48.5, 74, 59],
                            legend_classes=[
                                MVLegendClass('polygon', 'Polygons', fill='rgba(0, 0, 255, 0.1)', stroke='blue'),
                                MVLegendClass('line', 'Lines', stroke='green'),
                                MVLegendClass('point', 'Points', fill='red')
                            ])

    map_layers.append(geojson_layer)

    if get_geoserver_wms():
        # Define GeoServer Layer
        geoserver_layer = MVLayer(source='ImageWMS',
                                  options={'url': get_geoserver_wms(),
                                           'params': {'LAYERS': 'topp:states'},
                                           'serverType': 'geoserver'},
                                  legend_title='USA Population',
                                  legend_extent=[-126, 24.5, -66.2, 49],
                                  legend_classes=[
                                      MVLegendClass('polygon', 'Low Density', fill='#00ff00', stroke='#000000'),
                                      MVLegendClass('polygon', 'Medium Density', fill='#ff0000', stroke='#000000'),
                                      MVLegendClass('polygon', 'High Density', fill='#0000ff', stroke='#000000')
                                  ])

        map_layers.append(geoserver_layer)

    # Define KML Layer
    kml_layer = MVLayer(source='KML',
                        options={'url': '/static/tethys_gizmos/data/model.kml'},
                        legend_title='Park City Watershed',
                        legend_extent=[-111.60, 40.57, -111.43, 40.70],
                        legend_classes=[
                            MVLegendClass('polygon', 'Watershed Boundary', fill='#ff8000'),
                            MVLegendClass('line', 'Stream Network', stroke='#0000ff'),
                        ])

    map_layers.append(kml_layer)

    # Tiled ArcGIS REST Layer
    arc_gis_layer = MVLayer(source='TileArcGISRest',
                            options={'url': 'http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/' +
                                            'Specialty/ESRI_StateCityHighway_USA/MapServer'},
                            legend_title='ESRI USA Highway',
                            legend_extent=[-173, 17, -65, 72])

    map_layers.append(arc_gis_layer)

    # Define map view options
    map_view_options = MapView(
        height='600px',
        width='100%',
        controls=['ZoomSlider', 'Rotate', 'FullScreen',
                  {'MousePosition': {'projection': 'EPSG:4326'}},
                  {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
        layers=map_layers,
        view=view_options,
        basemap='OpenStreetMap',
        draw=drawing_options,
        legend=True
    )

    submitted_geometry = request.POST.get('geometry', None)

    if submitted_geometry is not None:
        messages.info(request, submitted_geometry)

    context = {'map_view': map_view_options}

    return render(request, 'tethys_gizmos/gizmo_showcase/map_view.html', context)


@login_required()
def esri_map(request):

    esri_map_view = EMView(center=[-100, 40], zoom=4)
    esri_layer = EMLayer(
        type='FeatureLayer',
        url='http://geoserver.byu.edu/arcgis/rest/services/gaugeviewer/AHPS_gauges/MapServer/0'
    )

    vector_tile = EMLayer(
        type='ImageryLayer',
        url='https://sampleserver6.arcgisonline.com/arcgis/rest/services/NLCDLandCover2001/ImageServer'
    )

    esri_map = ESRIMap(height='400px', width='100%', basemap='topo',
                       view=esri_map_view, layers=[vector_tile, esri_layer])

    context = {"esri_map": esri_map}

    return render(request, 'tethys_gizmos/gizmo_showcase/esri_map.html', context)


@login_required()
def cesium_map_view(request, type):
    # Get the access token
    cesium_ion_token = request.GET.get('cesium-ion-token', '')

    # Define nav link
    home_link = reverse('gizmos:cesium_map_view', kwargs={'type': 'home'})
    map_layers_link = reverse('gizmos:cesium_map_view', kwargs={'type': 'map_layers'})
    terrain_link = reverse('gizmos:cesium_map_view', kwargs={'type': 'terrain'})
    czml_link = reverse('gizmos:cesium_map_view', kwargs={'type': 'czml'})
    geojson_link = reverse('gizmos:cesium_map_view', kwargs={'type': 'geojson'})
    model_link = reverse('gizmos:cesium_map_view', kwargs={'type': 'model'})
    model2_link = reverse('gizmos:cesium_map_view', kwargs={'type': 'model2'})

    # Add cesium ion token GET parameters of all header links if provided
    if cesium_ion_token:
        home_link += f'?cesium-ion-token={cesium_ion_token}'
        map_layers_link += f'?cesium-ion-token={cesium_ion_token}'
        terrain_link += f'?cesium-ion-token={cesium_ion_token}'
        czml_link += f'?cesium-ion-token={cesium_ion_token}'
        geojson_link += f'?cesium-ion-token={cesium_ion_token}'
        model_link += f'?cesium-ion-token={cesium_ion_token}'
        model2_link += f'?cesium-ion-token={cesium_ion_token}'

    header_link = {"home_link": home_link, "map_layers_link": map_layers_link, "terrain_link": terrain_link,
                   "czml_link": czml_link, "geojson_link": geojson_link, "model_link": model_link,
                   "model2_link": model2_link, "page_type": type}

    # 1. Basic Map
    height = '600px'

    if type == 'home':
        cesium_map_view = CesiumMapView(cesium_ion_token=cesium_ion_token, height=height)

    # 2. Map Layers
    if type == 'map_layers':
        cesium_map_view = CesiumMapView(
            cesium_ion_token=cesium_ion_token,
            height=height,
            draw=True,
            options={'shouldAnimate': False, 'timeline': False, 'homeButton': False},
            layers=[
                {'Open Street Map': {
                    'imageryProvider': {'Cesium.OpenStreetMapImageryProvider': {
                        'url': 'https://a.tile.openstreetmap.org/'
                    }}
                }},
                MVLayer(
                    source='ImageWMS',
                    legend_title='US States',
                    options={
                        'url': 'https://demo.geo-solutions.it/geoserver/wms',
                        'params': {'LAYERS': 'topp:states'},
                        'serverType': 'geoserver'
                    },
                )
            ]
        )

    # 3. Terrain
    if type == 'terrain':
        cesium_map_view = CesiumMapView(
            cesium_ion_token=cesium_ion_token,
            height=height,
            draw=True,
            options={'shouldAnimate': False, 'timeline': False, 'homeButton': False},
            terrain={'terrainProvider': {'Cesium.createWorldTerrain': {'requestVertexNormals': True,
                                                                       'requestWaterMask': True}}},
            view={'flyTo': {
                'destination': {'Cesium.Cartesian3.fromDegrees': [-122.19, 46.25, 5000.0]},
                'orientation': {
                    'direction': {
                        'Cesium.Cartesian3': [-0.04231243104240401, -0.20123236049443421, -0.97862924300734]
                    },
                    'up': {
                        'Cesium.Cartesian3': [-0.47934589305293746, -0.8553216253114552, 0.1966022179118339]
                    }
                }
            }}
        )

    # 4. CZML Object
    if type == 'czml':
        czml_doc = [
            {
                "id": "document",
                "name": "CZML Geometries: Polygon",
                "version": "1.0"
            },
            {
                "id": "redPolygon",
                "name": "Red polygon on surface",
                "polygon": {
                    "positions": {
                        "cartographicDegrees": [
                            -115.0, 37.0, 0,
                            -115.0, 32.0, 0,
                            -107.0, 33.0, 0,
                            -102.0, 31.0, 0,
                            -102.0, 35.0, 0
                        ]
                    },
                    "material": {
                        "solidColor": {
                            "color": {
                                "rgba": [255, 0, 0, 255]
                            }
                        }
                    }
                }
            },
            {
                "id": "greenPolygon",
                "name": "Green extruded polygon",
                "polygon": {
                    "positions": {
                        "cartographicDegrees": [
                            -108.0, 42.0, 0,
                            -100.0, 42.0, 0,
                            -104.0, 40.0, 0
                        ]
                    },
                    "material":
                        {
                            "solidColor":
                                {
                                    "color": {
                                        "rgba": [0, 255, 0, 255]
                                    }
                                }
                        },
                    "extrudedHeight": 500000.0,
                    "closeTop": False,
                    "closeBottom": False
                }
            },
            {
                "id": "orangePolygon",
                "name": "Orange polygon with per-position heights and outline",
                "polygon": {
                    "positions": {
                        "cartographicDegrees": [
                            -108.0, 25.0, 100000,
                            -100.0, 25.0, 100000,
                            -100.0, 30.0, 100000,
                            -108.0, 30.0, 300000
                        ]
                    },
                    "material": {
                        "solidColor": {
                            "color": {
                                "rgba": [255, 100, 0, 100]
                            }
                        }
                    },
                    "extrudedHeight": 0,
                    "perPositionHeight": True,
                    "outline": True,
                    "outlineColor": {
                        "rgba": [0, 0, 0, 255]
                    }
                }
            }
        ]

        cesium_map_view = CesiumMapView(
            cesium_ion_token=cesium_ion_token,
            height=height,
            options={'shouldAnimate': True,
                     'timeline': False,
                     'homeButton': False,
                     'shadows': True,
                     },
            view={'lookAt': {
                'center': {'Cesium.Cartesian3.fromDegrees': [-98.0, 40.0]},
                'offset': {'Cesium.Cartesian3': [0.0, -4790000.0, 3930000.0]},
            }},
            layers={'BingMap': {
                'imageryProvider': {
                    'Cesium.BingMapsImageryProvider': {
                        'url': 'https://dev.virtualearth.net',
                        'key': 'AnYTMwSuR3-CBMzhN0yAYrtl-28rEFe7Kxfg2IWC9csUBCn0nYDFXW1ioNakjX3W',
                        'mapStyle': 'Cesium.BingMapsStyle.AERIAL',
                    },
                }
            }},
            entities=[
                {
                    'source': 'czml',
                    'options': czml_doc
                }
            ],
        )

    # 5. GeoJSON Object
    if type == 'geojson':
        geojson_object = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
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
                        'coordinates': [[35.9326113, -17.6789142], [71.8652227, 17.6789142]]
                    }
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [[-44.9157642, -8.9465739], [-35.9326114, 8.9465739], [-26.9494585, -8.9465739]]
                        ]
                    }
                }
            ]
        }

        cesium_map_view = CesiumMapView(
            cesium_ion_token=cesium_ion_token,
            height=height,
            options={'shouldAnimate': True,
                     'timeline': False,
                     'homeButton': False,
                     'shadows': True,
                     },
            view={'flyTo': {
                'destination': {'Cesium.Cartesian3.fromDegrees': [0, 0, 20000000.0]},
            }},
            layers={'BingMap': {
                'imageryProvider': {
                    'Cesium.BingMapsImageryProvider': {
                        'url': 'https://dev.virtualearth.net',
                        'key': 'AnYTMwSuR3-CBMzhN0yAYrtl-28rEFe7Kxfg2IWC9csUBCn0nYDFXW1ioNakjX3W',
                        'mapStyle': 'Cesium.BingMapsStyle.AERIAL',
                    },
                }
            }},
            entities=[
                {
                    'source': 'geojson',
                    'options': geojson_object
                }
            ],
        )

    # 6. Model
    if type == 'model':
        object1 = '/static/tethys_gizmos/cesium_models/CesiumAir/Cesium_Air.glb'
        cesium_map_view = CesiumMapView(
            cesium_ion_token=cesium_ion_token,
            height=height,
            options={
                'shouldAnimate': True,
                'timeline': True,
                'homeButton': True,
                'shadows': True,
            },
            layers={'BingMap': {'imageryProvider': {
                'Cesium.BingMapsImageryProvider': [{
                    'url': 'https://dev.virtualearth.net',
                    'key': 'AnYTMwSuR3-CBMzhN0yAYrtl-28rEFe7Kxfg2IWC9csUBCn0nYDFXW1ioNakjX3W',
                    'mapStyle': 'Aerial',
                }],
            }}},
            models={
                'Cesium_Airplane': {
                    'model': {
                        'uri': object1,
                        'show': True,
                        'minimumPixelSize': 128,
                        'maximumScale': 20000,
                        'shadows': 'enabled',
                    },
                    'name': object1,
                    'orientation': {
                        'Cesium.Transforms.headingPitchRollQuaternion':
                            [{'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                             {'Cesium.HeadingPitchRoll': [{'Cesium.Math.toRadians': 135}, 0, 0]}]},
                    'position': {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                },
            },
            clock={'clock': {'Cesium.Clock': {
                'startTime': {'Cesium.JulianDate.fromIso8601': ['2017-07-11T00:00:00Z']},
                'stopTime': {'Cesium.JulianDate.fromIso8601': ['2017-07-11T24:00:00Z']},
                'currentTime': {'Cesium.JulianDate.fromIso8601': ['2017-07-11T10:00:00Z']},
                'clockRange': 'Cesium.ClockRange.LOOP_STOP',
                'clockStep': 'Cesium.ClockStep.SYSTEM_CLOCK_MULTIPLIER',
                'multiplier': 1000,
                'shouldAnimate': True
            }}}
        )

    # 7. Multiple Models
    if type == 'model2':
        object1 = '/static/tethys_gizmos/cesium_models/CesiumAir/Cesium_Air.glb'
        object2 = '/static/tethys_gizmos/cesium_models/CesiumBalloon/CesiumBalloon.glb'
        cesium_map_view = CesiumMapView(
            cesium_ion_token=cesium_ion_token,
            height='80%',
            width='80%',
            options={'shouldAnimate': True,
                     'timeline': True,
                     'homeButton': True,
                     'shadows': True,
                     },
            layers={'BingMap': {
                'imageryProvider': {'Cesium.BingMapsImageryProvider': [{
                    'url': 'https://dev.virtualearth.net',
                    'key': 'AnYTMwSuR3-CBMzhN0yAYrtl-28rEFe7Kxfg2IWC9csUBCn0nYDFXW1ioNakjX3W',
                    'mapStyle': 'Aerial',
                }]}
            }},
            models={
                'Cesium_Airplane': {
                    'model': {
                        'uri': object1,
                        'show': True,
                        'minimumPixelSize': 128,
                        'maximumScale': 20000,
                        'shadows': 'enabled',
                    },
                    'name': object1,
                    'orientation': {'Cesium.Transforms.headingPitchRollQuaternion': [
                            {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                            {'Cesium.HeadingPitchRoll': [{'Cesium.Math.toRadians': 135}, 0, 0]}
                        ]},
                    'position': {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                },
                'Cesium_Ballon': {
                    'model': {
                        'uri': object2,
                        'show': True,
                        'minimumPixelSize': 128,
                        'maximumScale': 20000,
                        'shadows': 'enabled',
                    },
                    'name': object2,
                    'orientation': {
                        'Cesium.Transforms.headingPitchRollQuaternion': [
                            {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                            {'Cesium.HeadingPitchRoll': [{'Cesium.Math.toRadians': 135}, 0, 0]}
                        ]
                    },
                    'position': {
                        'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]
                    },

                },
            },
        )

    submitted_geometry = request.POST.get('geometry', None)

    if submitted_geometry is not None:
        messages.info(request, submitted_geometry)

    context = {
        "cesium_map_view": cesium_map_view,
        "cesium_ion_token": cesium_ion_token
    }
    context.update(header_link)

    return render(request, 'tethys_gizmos/gizmo_showcase/cesium_map_view.html', context)


def jobs_table_demo(request):
    jobs = TethysJob.objects.filter(label='gizmos_showcase').order_by('id').select_subclasses()

    # Table View
    jobs_table_options = JobsTable(
        jobs=jobs,
        column_fields=('id', 'name', 'description', 'creation_time'),
        hover=True,
        striped=False,
        bordered=False,
        condensed=False,
        monitor_url='gizmos:results',
        results_url='gizmos:results',
        refresh_interval=10000,
        run_btn=True,
        delete_btn=True,
        show_detailed_status=True,
        actions=['run', 'resubmit', 'log', 'monitor', 'results', 'terminate', 'delete'],
    )

    context = {'jobs_table': jobs_table_options}

    return render(request, 'tethys_gizmos/gizmo_showcase/jobs_table.html', context)


def jobs_table_results(request, job_id):
    return redirect(reverse('gizmos:jobs_table'))


def create_sample_jobs(request):
    def create_job(id, description, status, workflow=False):
        if not workflow:
            job = BasicJob(name='job_{0}'.format(id),
                           user=request.user,
                           description=description,
                           label='gizmos_showcase',
                           _status=status,
                           )
        else:
            job = CondorWorkflow(
                name='job_{0}'.format(id),
                user=request.user,
                description=description,
                label='gizmos_showcase',
                _status=status
            )
        job.save()

    create_job('1', 'Pending job', 'PEN')
    create_job('2', 'Submitted job', 'SUB')
    create_job('3', 'Running job', 'RUN')
    create_job('4', 'Running multi-process job with various statuses', 'VAR')
    create_job('5', 'Job error', 'ERR')
    create_job('6', 'Aborted job', 'ABT')
    create_job('7', 'Completed job', 'COM')
    create_job('8', 'Completed multi-process job with some errors', 'VCP')
    create_job('9', 'Workflow job with multiple nodes.', 'VAR', workflow=True)

    return redirect(reverse('gizmos:jobs_table') + '#jobs_table_docs')
