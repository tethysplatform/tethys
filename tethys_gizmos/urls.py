"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.conf.urls import url, include
from tethys_gizmos.views import gizmo_showcase as gizmo_showcase_views
from tethys_gizmos.views.gizmos import jobs_table as jobs_table_views

ajax_urls = [
    url(r'^get-kml/$', gizmo_showcase_views.get_kml, name='get_kml'),
    url(r'^swap-kml/$', gizmo_showcase_views.swap_kml, name='swap_kml'),
    url(r'^swap-overlays/$', gizmo_showcase_views.swap_overlays, name='swap_overlays'),
    url(r'^(?P<job_id>[\d.@+-]+)/terminate', jobs_table_views.terminate, name='terminate_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/delete$', jobs_table_views.delete, name='delete_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/resubmit$', jobs_table_views.resubmit, name='resubmit_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/show-log', jobs_table_views.show_log, name='show_log'),
    url(r'^(?P<job_id>[\d.@+-]+)/execute', jobs_table_views.execute, name='execute_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/update-row', jobs_table_views.update_row, name='update_job_row'),
    url(r'^(?P<job_id>[\d.@+-]+)/update-workflow-nodes-row', jobs_table_views.update_workflow_nodes_row,
        name='update_workflow_nodes_row'),
    url(r'^(?P<job_id>[\d.@+-]+)/(?P<type>[\w-]+)/insert-bokeh-row', jobs_table_views.bokeh_row, name='bokeh_row'),
]

urlpatterns = [
    url(r'^$', gizmo_showcase_views.index, name='showcase'),
    url(r'^google-map-view/$', gizmo_showcase_views.google_map_view, name='google_map_view'),
    url(r'^map-view', gizmo_showcase_views.map_view, name='map_view'),
    url(r'^(?P<type>[\w-]+)/cesium-map-view', gizmo_showcase_views.cesium_map_view, name='cesium_map_view'),
    url(r'^jobs-table', gizmo_showcase_views.jobs_table_demo, name='jobs_table'),
    url(r'^esri-map', gizmo_showcase_views.esri_map, name='esri_map'),
    url(r'^(?P<job_id>[\d.@+-]+)/results$', gizmo_showcase_views.jobs_table_results, name='results'),
    url(r'^sample-jobs$', gizmo_showcase_views.create_sample_jobs, name='sample_jobs'),
    url(r'^ajax/', include(ajax_urls)),
]
