from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase


class TestUrls(TethysTestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_urlpatterns(self):
        url = reverse('gizmos:showcase')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/', url)
        self.assertEqual('index', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_urlpatterns_google_map_view(self):
        url = reverse('gizmos:google_map_view')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/google-map-view/', url)
        self.assertEqual('google_map_view', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_urlpatterns_map_view(self):
        url = reverse('gizmos:map_view')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/map-view', url)
        self.assertEqual('map_view', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_urlpatterns_jobs_table(self):
        url = reverse('gizmos:jobs_table')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/jobs-table', url)
        self.assertEqual('jobs_table_demo', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_urlpatterns_esri_map(self):
        url = reverse('gizmos:esri_map')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/esri-map', url)
        self.assertEqual('esri_map', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_urlpatterns_results(self):
        url = reverse('gizmos:results', kwargs={'job_id': '123'})
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/123/results', url)
        self.assertEqual('jobs_table_results', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_urlpatterns_sample_jobs(self):
        url = reverse('gizmos:sample_jobs')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/sample-jobs', url)
        self.assertEqual('create_sample_jobs', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_ajax_urls_get_kml(self):
        url = reverse('gizmos:get_kml')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/ajax/get-kml/', url)
        self.assertEqual('get_kml', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_ajax_urls_swap_kml(self):
        url = reverse('gizmos:swap_kml')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/ajax/swap-kml/', url)
        self.assertEqual('swap_kml', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_ajax_urls_swap_overlays(self):
        url = reverse('gizmos:swap_overlays')
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/ajax/swap-overlays/', url)
        self.assertEqual('swap_overlays', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmo_showcase', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_ajax_urls_delete_job(self):
        url = reverse('gizmos:delete_job', kwargs={'job_id': '123'})
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/ajax/123/delete', url)
        self.assertEqual('delete', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmos.jobs_table', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_ajax_urls_update_job_row(self):
        url = reverse('gizmos:update_job_row', kwargs={'job_id': '123'})
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/ajax/123/update-row', url)
        self.assertEqual('update_row', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmos.jobs_table', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_ajax_urls_update_workflow_nodes_row(self):
        url = reverse('gizmos:update_workflow_nodes_row', kwargs={'job_id': '123'})
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/ajax/123/update-workflow-nodes-row', url)
        self.assertEqual('update_workflow_nodes_row', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmos.jobs_table', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])

    def test_ajax_urls_bokeh_row(self):
        url = reverse('gizmos:bokeh_row', kwargs={'job_id': '123', 'type': 'test'})
        resolver = resolve(url)
        self.assertEqual('/developer/gizmos/ajax/123/test/insert-bokeh-row', url)
        self.assertEqual('bokeh_row', resolver.func.__name__)
        self.assertEqual('tethys_gizmos.views.gizmos.jobs_table', resolver.func.__module__)
        self.assertEqual('gizmos', resolver.namespaces[0])
