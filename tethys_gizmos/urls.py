from django.conf.urls import patterns, url, include

ajax_urls = [
    url(r'^get-kml/$', 'tethys_gizmos.views.gizmo_showcase.get_kml', name='get_kml'),
    url(r'^swap-kml/$', 'tethys_gizmos.views.gizmo_showcase.swap_kml', name='swap_kml'),
    url(r'^swap-overlays/$', 'tethys_gizmos.views.gizmo_showcase.swap_overlays', name='swap_overlays'),
    url(r'^fetchclimate/single-request/$', 'tethys_gizmos.views.gizmos.fetchclimate.data_request_single', name='single_request'),
    url(r'^(?P<job_id>[\d.@+-]+)/delete$', 'tethys_gizmos.views.gizmos.jobs_table.delete', name='delete_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/execute', 'tethys_gizmos.views.gizmos.jobs_table.execute', name='execute_job'),
    url(r'^(?P<job_id>[\d.@+-]+)/update-status', 'tethys_gizmos.views.gizmos.jobs_table.update_status', name='update_job_status'),
]

urlpatterns = patterns('',
    url(r'^$', 'tethys_gizmos.views.gizmo_showcase.index', name='showcase'),
    url(r'^editable-map/$', 'tethys_gizmos.views.gizmo_showcase.editable_map', name='editable_map'),
    url(r'^google-map/$', 'tethys_gizmos.views.gizmo_showcase.google_map', name='google_map'),
    url(r'^map-view', 'tethys_gizmos.views.gizmo_showcase.map_view', name='map_view'),
    url(r'^fetch-climate-map/$', 'tethys_gizmos.views.gizmo_showcase.fetchclimate_map', name='fetchclimate_map'),
    url(r'^(?P<job_id>[\d.@+-]+)/results$', 'tethys_gizmos.views.gizmo_showcase.jobs_table_results', name='results'),
    url(r'^sample-jobs$', 'tethys_gizmos.views.gizmo_showcase.create_sample_jobs', name='sample_jobs'),
    url(r'^ajax/', include(ajax_urls)),
)
