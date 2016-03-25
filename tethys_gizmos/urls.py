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
from tethys_gizmos.views.gizmos import fetchclimate as fetchclimate_views, jobs_table as jobs_table_views

ajax_urls = [
    url(r'^get-kml/$', gizmo_showcase_views.get_kml, name='get_kml'),
    url(r'^swap-kml/$', gizmo_showcase_views.swap_kml, name='swap_kml'),
    url(r'^swap-overlays/$', gizmo_showcase_views.swap_overlays, name='swap_overlays'),
    url(r'^fetchclimate/single-request/$', fetchclimate_views.data_request_single, name='single_request'),
    url(r'^(?P<job_id>[\d.@+-]+)/delete$', jobs_table_views.delete, name='delete_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/execute', jobs_table_views.execute, name='execute_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/update-row', jobs_table_views.update_row, name='update_job_row'),
    url(r'^(?P<job_id>[\d.@+-]+)/update-status', jobs_table_views.update_status, name='update_job_status'),
]

urlpatterns = [
    url(r'^$', gizmo_showcase_views.index, name='showcase'),
    url(r'^editable-map/$', gizmo_showcase_views.editable_map, name='editable_map'),
    url(r'^google-map/$', gizmo_showcase_views.google_map, name='google_map'),
    url(r'^map-view', gizmo_showcase_views.map_view, name='map_view'),
    url(r'^fetch-climate-map/$', gizmo_showcase_views.fetchclimate_map, name='fetchclimate_map'),
    url(r'^(?P<job_id>[\d.@+-]+)/results$', gizmo_showcase_views.jobs_table_results, name='results'),
    url(r'^sample-jobs$', gizmo_showcase_views.create_sample_jobs, name='sample_jobs'),
    url(r'^ajax/', include(ajax_urls)),
]
