from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase
from django.test import override_settings


class TestUrls(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_ajax_urls_delete_job(self):
        url = reverse("gizmos:delete_job", kwargs={"job_id": "123"})
        resolver = resolve(url)
        self.assertEqual("/developer/gizmos/ajax/123/action/delete", url)
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.delete", resolver._func_path
        )
        self.assertEqual("gizmos", resolver.namespaces[0])

    def test_ajax_urls_update_job_row(self):
        url = reverse("gizmos:update_job_row", kwargs={"job_id": "123"})
        resolver = resolve(url)
        self.assertEqual("/developer/gizmos/ajax/123/update-row", url)
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.update_row", resolver._func_path
        )
        self.assertEqual("gizmos", resolver.namespaces[0])

    def test_ajax_urls_update_workflow_nodes_row(self):
        url = reverse("gizmos:update_workflow_nodes_row", kwargs={"job_id": "123"})
        resolver = resolve(url)
        self.assertEqual("/developer/gizmos/ajax/123/update-workflow-nodes-row", url)
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.update_workflow_nodes_row",
            resolver._func_path,
        )
        self.assertEqual("gizmos", resolver.namespaces[0])

    def test_ajax_urls_bokeh_row(self):
        url = reverse("gizmos:bokeh_row", kwargs={"job_id": "123", "type": "test"})
        resolver = resolve(url)
        self.assertEqual("/developer/gizmos/ajax/123/test/insert-bokeh-row", url)
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.bokeh_row", resolver._func_path
        )
        self.assertEqual("gizmos", resolver.namespaces[0])


# we need to test for the JS that is calling the jobs directly
@override_settings(PREFIX_URL="test/prefix")
class TestUrlsWithPrefix(TethysTestCase):
    import sys
    from importlib import reload, import_module
    from django.conf import settings
    from django.urls import clear_url_caches

    @classmethod
    def reload_urlconf(self, urlconf=None):
        self.clear_url_caches()
        if urlconf is None:
            urlconf = self.settings.ROOT_URLCONF
        if urlconf in self.sys.modules:
            self.reload(self.sys.modules[urlconf])
        else:
            self.import_module(urlconf)

    def set_up(self):
        self.reload_urlconf()
        pass

    @override_settings(PREFIX_URL="/")
    def tearDown(self):
        self.reload_urlconf()
        pass

    def test_ajax_urls_delete_job(self):
        url = reverse("gizmos:delete_job", kwargs={"job_id": "123"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/developer/gizmos/ajax/123/action/delete", url)
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.delete", resolver._func_path
        )
        self.assertEqual("gizmos", resolver.namespaces[0])

    def test_ajax_urls_update_job_row(self):
        url = reverse("gizmos:update_job_row", kwargs={"job_id": "123"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/developer/gizmos/ajax/123/update-row", url)
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.update_row", resolver._func_path
        )
        self.assertEqual("gizmos", resolver.namespaces[0])

    def test_ajax_urls_update_workflow_nodes_row(self):
        url = reverse("gizmos:update_workflow_nodes_row", kwargs={"job_id": "123"})
        resolver = resolve(url)
        self.assertEqual(
            "/test/prefix/developer/gizmos/ajax/123/update-workflow-nodes-row", url
        )
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.update_workflow_nodes_row",
            resolver._func_path,
        )
        self.assertEqual("gizmos", resolver.namespaces[0])

    def test_ajax_urls_bokeh_row(self):
        url = reverse("gizmos:bokeh_row", kwargs={"job_id": "123", "type": "test"})
        resolver = resolve(url)
        self.assertEqual(
            "/test/prefix/developer/gizmos/ajax/123/test/insert-bokeh-row", url
        )
        self.assertEqual(
            "tethys_gizmos.views.gizmos.jobs_table.bokeh_row", resolver._func_path
        )
        self.assertEqual("gizmos", resolver.namespaces[0])
