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
from tethys_gizmos.views.gizmos import jobs_table as jobs_table_views

ajax_urls = [
    url(r'^(?P<job_id>[\d.@+-]+)/terminate', jobs_table_views.terminate, name='terminate_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/delete$', jobs_table_views.delete, name='delete_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/resubmit$', jobs_table_views.resubmit, name='resubmit_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/show-log', jobs_table_views.show_log, name='show_log'),
    url(r'^(?P<job_id>[\d.@+-]+)/log-content/(?P<key1>[\w+_-]+)(?:/(?P<key2>.*))?', jobs_table_views.get_log_content,
        name='log_content'),
    url(r'^(?P<job_id>[\d.@+-]+)/execute', jobs_table_views.execute, name='execute_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/update-row', jobs_table_views.update_row, name='update_job_row'),
    url(r'^(?P<job_id>[\d.@+-]+)/update-workflow-nodes-row', jobs_table_views.update_workflow_nodes_row,
        name='update_workflow_nodes_row'),
    url(r'^(?P<job_id>[\d.@+-]+)/(?P<type>[\w-]+)/insert-bokeh-row', jobs_table_views.bokeh_row, name='bokeh_row'),
]

urlpatterns = [
    url(r'^ajax/', include(ajax_urls)),
]
