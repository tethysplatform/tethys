"""
********************************************************************************
* Name: gizmo_dependencies.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.conf import settings
from pprint import pprint


def global_dependencies(context):
    """
    Dependencies that are loaded for all tethys gizmos (after gizmo dependencies).
    """
    return('tethys_gizmos/css/tethys_gizmos.css',
           'tethys_gizmos/js/tethys_gizmos.js')


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
    return ('tethys_gizmos/vendor/select2_3.5.1/select2.css',
            'tethys_gizmos/vendor/select2_3.5.1/select2.js')


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
            'tethys_gizmos/css/tethys_map_view.css',
            openlayers_library,
            'tethys_gizmos/js/gizmo_utilities.js',
            'tethys_gizmos/js/tethys_map_view.js')


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
            'tethys_gizmos/vendor/farbtastic/farbtastic.js',
            'tethys_gizmos/js/tethys_editable_map.js')


def google_map_view(context):
    """
    Dependencies for google_map_view gizmo.
    """
    return ('tethys_gizmos/vendor/farbtastic/farbtastic.css',
            'tethys_gizmos/vendor/farbtastic/farbtastic.js',
            'tethys_gizmos/js/tethys_google_map_view.js')


def google_map(context):
    """
    Dependencies for google_map gizmo.
    """
    return ('tethys_gizmos/js/tethys_map.js',)


def fetchclimate(context):
    """
    Dependencies for fetchclimate gizmo.
    """
    return ('tethys_gizmos/vendor/farbtastic/farbtastic.css',
            'tethys_gizmos/vendor/bootstrap_datepicker/css/datepicker3.css',
            'tethys_gizmos/css/fetchclimate/fetchclimate.css',
            'tethys_gizmos/css/fetchclimate/fetchclimate_map.css',
            'tethys_gizmos/css/fetchclimate/fetchclimate_plot.css',
            'tethys_gizmos/vendor/bootstrap_datepicker/js/bootstrap_datepicker.js',
            'tethys_gizmos/js/fetchclimate/fetchclimate_main.js',
            'tethys_gizmos/js/fetchclimate/fetchclimate_date.js',
            'tethys_gizmos/js/fetchclimate/fetchclimate_map.js',
            'tethys_gizmos/vendor/highcharts/js/highcharts.js',
            'tethys_gizmos/vendor/highcharts/js/highcharts-more.js',
            'tethys_gizmos/js/fetchclimate/fetchclimate_plot.js',
            'tethys_gizmos/js/fetchclimate/fetchclimate_data.js')


def plot_view(context):
    """
    Dependencies for D3 Plots.
    """
    return ('tethys_gizmos/css/plot_view.css',
            'tethys_gizmos/vendor/highcharts/js/highcharts.js',
            'tethys_gizmos/vendor/highcharts/js/highcharts-more.js',
            'tethys_gizmos/vendor/highcharts/js/modules/exporting.js',
            'https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js',
            'tethys_gizmos/vendor/d3_tooltip/d3.tip.v0.6.3.js',
            'tethys_gizmos/js/plot_view.js')


def jobs_table(context):
    """
    Dependencies for jobs_table gizmo.
    """
    return ('tethys_gizmos/js/jobs_table.js',)
