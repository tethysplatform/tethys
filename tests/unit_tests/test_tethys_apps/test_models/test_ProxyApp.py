from unittest import mock
from django.core.exceptions import ValidationError
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import ProxyApp
from django.contrib.auth.models import Permission


class ProxyAppTests(TethysTestCase):
    def set_up(self):
        self.app_name = "My Proxy App for Testing"
        self.endpoint = "http://foo.example.com/my-proxy-app"
        self.back_url = "http://bar.example.com/apps/"
        self.logo = "http://foo.example.com/my-proxy-app/logo.png"
        self.description = "This is an app that is not here."
        self.tags = '"Water","Earth","Fire","Air"'
        self.open_in_new_tab = True

    def test_Meta(self):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        self.assertEqual("Proxy App", proxy_app._meta.verbose_name)
        self.assertEqual("Proxy Apps", proxy_app._meta.verbose_name_plural)

    def test_properties(self):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        self.assertTrue(proxy_app.proxied)
        self.assertEqual(self.endpoint, proxy_app.url)
        self.assertEqual(self.logo, proxy_app.icon)
        self.assertEqual(self.back_url, proxy_app.back_url)
        self.assertEqual(self.description, proxy_app.description)
        self.assertEqual(self.tags, proxy_app.tags)
        self.assertEqual(self.open_in_new_tab, proxy_app.open_in_new_tab)

    def test__str__(self):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )

        ret = str(proxy_app)
        self.assertEqual(self.app_name, ret)

    def test_create(self):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
        )
        proxy_app.save()

        ret = ProxyApp.objects.get(name=self.app_name)

        self.assertEqual(self.endpoint, ret.endpoint)
        self.assertEqual(self.logo, ret.icon)
        self.assertEqual(self.back_url, ret.back_url)
        self.assertEqual(self.description, ret.description)
        self.assertEqual(self.tags, ret.tags)
        self.assertTrue(ret.enabled)
        self.assertTrue(ret.show_in_apps_library)
        self.assertTrue(ret.open_in_new_tab)

    def test_endpoint_validation(self):
        bad_endpoint = "not a url"
        http_url = "http://foo.com"
        https_url = "https://foo.com"

        # Bad URL
        a = ProxyApp.objects.create(
            name="Bad URL Test",
            endpoint=bad_endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
        )

        with self.assertRaises(ValidationError) as cm:
            a.clean_fields()

        self.assertIn("endpoint", str(cm.exception))
        self.assertEqual(
            "{'endpoint': ['Enter a valid URL.']}",
            str(cm.exception),
        )

        # HTTP
        b = ProxyApp.objects.create(
            name="HTTP URL Test",
            endpoint=http_url,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
        )
        b_exception_raised = False

        try:
            b.clean_fields()
        except ValidationError:
            b_exception_raised = True

        self.assertFalse(b_exception_raised)

        # HTTPS
        c = ProxyApp.objects.create(
            name="HTTPS URL Test",
            endpoint=https_url,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
        )

        c_exception_raised = False

        try:
            c.clean_fields()
        except ValidationError:
            c_exception_raised = True

        self.assertFalse(c_exception_raised)

    def test_icon_validation(self):
        static_file = "statc/image.png"
        http_url = "http://foo.com"
        https_url = "https://foo.com"

        # static file
        a = ProxyApp.objects.create(
            name="Bad URL Test",
            endpoint=self.endpoint,
            icon=static_file,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
        )
        a_exception_raised = False

        try:
            a.clean_fields()
        except ValidationError:
            a_exception_raised = True

        self.assertFalse(a_exception_raised)

        # HTTP
        b = ProxyApp.objects.create(
            name="HTTP URL Test",
            endpoint=self.endpoint,
            icon=http_url,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
        )
        b_exception_raised = False

        try:
            b.clean_fields()
        except ValidationError:
            b_exception_raised = True

        self.assertFalse(b_exception_raised)

        # HTTPS
        c = ProxyApp.objects.create(
            name="HTTPS URL Test",
            endpoint=self.endpoint,
            icon=https_url,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
        )

        c_exception_raised = False

        try:
            c.clean_fields()
        except ValidationError:
            c_exception_raised = True

        self.assertFalse(c_exception_raised)

    def test_back_url_validation(self):
        bad_url = "not a url"
        http_url = "http://foo.com"
        https_url = "https://foo.com"

        # Bad URL
        a = ProxyApp.objects.create(
            name="Bad URL Test",
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=bad_url,
            description=self.description,
            tags=self.tags,
        )

        with self.assertRaises(ValidationError) as cm:
            a.clean_fields()

        self.assertIn("back_url", str(cm.exception))
        self.assertEqual(
            "{'back_url': ['Enter a valid URL.']}",
            str(cm.exception),
        )

        # HTTP
        b = ProxyApp.objects.create(
            name="HTTP URL Test",
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=http_url,
            description=self.description,
            tags=self.tags,
        )
        b_exception_raised = False

        try:
            b.clean_fields()
        except ValidationError:
            b_exception_raised = True

        self.assertFalse(b_exception_raised)

        # HTTPS
        c = ProxyApp.objects.create(
            name="HTTPS URL Test",
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=https_url,
            description=self.description,
            tags=self.tags,
        )

        c_exception_raised = False

        try:
            c.clean_fields()
        except ValidationError:
            c_exception_raised = True

        self.assertFalse(c_exception_raised)

    @mock.patch("tethys_apps.models.ProxyApp.update_app_permission")
    def test_permission_name_change(self, mock_uap):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        proxy_app.save()
        proxy_app.name = "new name"
        proxy_app.save()

        mock_uap.assert_called_once()

    @mock.patch("tethys_apps.models.Permission")
    def test_update_app_permission(self, mock_perm):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        proxy_app.save()
        proxy_app.update_app_permission()
        mock_perm.objects.get().save.assert_called()

    @mock.patch("tethys_apps.models.ProxyApp.register_app_permission")
    def test_update_app_permission_exception(self, mock_reg):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        proxy_app.save()
        proxy_app.update_app_permission()
        self.assertEqual(2, len(mock_reg.call_args_list))

    def test_delete_exception(self):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        proxy_app.save()
        Permission.objects.get(codename=proxy_app.permission_codename).delete()
        proxy_app.delete()

    def test_save_no_package(self):
        proxy_app = ProxyApp()
        proxy_app.name = self.app_name
        proxy_app.save()
        self.assertEqual(proxy_app.package, self.app_name)
