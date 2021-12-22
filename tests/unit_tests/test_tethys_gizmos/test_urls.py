from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase


class TestUrls(TethysTestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

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
