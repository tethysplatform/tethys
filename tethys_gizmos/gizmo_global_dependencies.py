"""
********************************************************************************
* Name: gizmo_global_dependencies.py
* Created On: 2016
* License: BSD 2-Clause
********************************************************************************
"""
from django.conf import settings

def date_picker(context):
    """
    Dependencies for date_picker gizmo.
    """
    return ('tethys_gizmos/vendor/bootstrap_datepicker/css/datepicker3.css',
            'tethys_gizmos/vendor/bootstrap_datepicker/js/bootstrap_datepicker.js')


def select_input(context):
    """
    Dependencies for select2_input gizmo.
    """
    return ('tethys_gizmos/vendor/select2_4.0.2/css/select2.css',
            'tethys_gizmos/vendor/select2_4.0.2/js/select2.min.js')


def highcharts_plot_view(context):
    """
    Dependencies for highcharts_plot_view gizmo.
    """
    return ('tethys_gizmos/vendor/highcharts/js/highcharts.js',
            'tethys_gizmos/vendor/highcharts/js/highcharts-more.js',
            'tethys_gizmos/vendor/highcharts/js/modules/exporting.js')


def map_view(context):
    """
    Dependencies for map_view gizmo.
    """
    openlayers_library = 'tethys_gizmos/vendor/openlayers/ol.js'
    if settings.DEBUG:
        openlayers_library = 'tethys_gizmos/vendor/openlayers/ol-debug.js'

    return ('tethys_gizmos/vendor/openlayers/ol.css',
            openlayers_library)


def toggle_switch(context):
    """
    Dependencies for toggle_switch gizmo.
    """
    return ('tethys_gizmos/vendor/bootstrap_switch/dist/css/bootstrap3/bootstrap-switch.min.css',
            'tethys_gizmos/vendor/bootstrap_switch/dist/js/bootstrap-switch.min.js')


def editable_google_map(context):
    """
    Dependencies for editable_google_map gizmo.
    """
    return ('tethys_gizmos/vendor/farbtastic/farbtastic.css',
            'tethys_gizmos/vendor/farbtastic/farbtastic.js')


def google_map_view(context):
    """
    Dependencies for google_map_view gizmo.
    """
    return ('tethys_gizmos/vendor/farbtastic/farbtastic.css',
            'tethys_gizmos/vendor/farbtastic/farbtastic.js')


def plot_view(context):
    """
    Dependencies for D3 & Highcharts Plots.
    """
    return ('tethys_gizmos/vendor/highcharts/js/highcharts.js',
            'tethys_gizmos/vendor/highcharts/js/highcharts-more.js',
            'tethys_gizmos/vendor/highcharts/js/modules/exporting.js',
            'https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js',
            'tethys_gizmos/vendor/d3_tooltip/d3.tip.v0.6.3.js')

def plotly_view(context):
    """
    Dependencies for Plotly Plots.
    """
    return ('://plotly-load_from_python.js',)
    
def bokeh_view(context):
    """
    Dependencies for Bokeh Plots.
    """
    from bokeh.resources import CDN
    return CDN.js_files+CDN.css_files