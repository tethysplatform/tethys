"""
********************************************************************************
* Name: gizmo_dependencies.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

def global_dependencies(context):
    """
    Dependencies that are loaded for all tethys gizmos (after gizmo dependencies).
    """
    return('tethys_gizmos/css/tethys_gizmos.css',
           'tethys_gizmos/js/tethys_gizmos.js')


def map_view(context):
    """
    Dependencies for map_view gizmo.
    """
    return ('tethys_gizmos/css/tethys_map_view.css',
            'tethys_gizmos/js/gizmo_utilities.js',
            'tethys_gizmos/js/tethys_map_view.js')

def editable_google_map(context):
    """
    Dependencies for editable_google_map gizmo.
    """
    return ('tethys_gizmos/js/tethys_editable_map.js')


def google_map_view(context):
    """
    Dependencies for google_map_view gizmo.
    """
    return ('tethys_gizmos/js/tethys_google_map_view.js')


def google_map(context):
    """
    Dependencies for google_map gizmo.
    """
    return ('tethys_gizmos/js/tethys_map.js',)

def datatable_view(context):
    """
    Dependencies for the table_view gizmo.
    """
    return ('tethys_gizmos/js/datatable_view.js',)

def plot_view(context):
    """
    Dependencies for D3 Plots.
    """
    return ('tethys_gizmos/css/plot_view.css',
            'tethys_gizmos/js/plot_view.js')


def jobs_table(context):
    """
    Dependencies for jobs_table gizmo.
    """
    return ('tethys_gizmos/js/jobs_table.js',)
