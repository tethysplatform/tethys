"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.urls import re_path, include
from tethys_gizmos.views.gizmos import jobs_table as jobs_table_views

ajax_urls = [
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/action/delete$",
        jobs_table_views.delete,
        name="delete_job",
    ),
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/action/resubmit$",
        jobs_table_views.resubmit,
        name="resubmit_job",
    ),
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/action/show-log",
        jobs_table_views.show_log,
        name="show_log",
    ),
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/log-content/(?P<key1>[\w+_-]+)(?:/(?P<key2>.*))?",
        jobs_table_views.get_log_content,
        name="log_content",
    ),
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/update-row",
        jobs_table_views.update_row,
        name="update_job_row",
    ),
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/update-workflow-nodes-row",
        jobs_table_views.update_workflow_nodes_row,
        name="update_workflow_nodes_row",
    ),
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/(?P<type>[\w-]+)/insert-bokeh-row",
        jobs_table_views.bokeh_row,
        name="bokeh_row",
    ),
    re_path(
        r"^(?P<job_id>[\d.@+-]+)/action/(?P<action>[\w+-]+)",
        jobs_table_views.perform_action,
        name="custom_action",
    ),
]

urlpatterns = [
    re_path(r"^ajax/", include(ajax_urls)),
]
