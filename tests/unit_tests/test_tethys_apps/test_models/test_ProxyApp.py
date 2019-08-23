from django.core.exceptions import ValidationError
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import ProxyApp


class ProxyAppTests(TethysTestCase):

    def set_up(self):
        self.app_name = 'My Proxy App for Testing'
        self.endpoint = 'http://foo.example.com/my-proxy-app'
        self.logo = 'http://foo.example.com/my-proxy-app/logo.png'
        self.description = 'This is an app that is not here.'
        self.tags = '"Water","Earth","Fire","Air"'

    def test_Meta(self):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            logo_url=self.logo,
            description=self.description,
            tags=self.tags
        )
        self.assertEqual('Proxy App', proxy_app._meta.verbose_name)
        self.assertEqual('Proxy Apps', proxy_app._meta.verbose_name_plural)

    def test__str__(self):
        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            logo_url=self.logo,
            description=self.description,
            tags=self.tags
        )

        ret = str(proxy_app)
        self.assertEqual(self.app_name, ret)

    def test_create(self):

        proxy_app = ProxyApp.objects.create(
            name=self.app_name,
            endpoint=self.endpoint,
            logo_url=self.logo,
            description=self.description,
            tags=self.tags
        )
        proxy_app.save()

        ret = ProxyApp.objects.get(name=self.app_name)

        self.assertEqual(self.endpoint, ret.endpoint)
        self.assertEqual(self.logo, ret.logo_url)
        self.assertEqual(self.description, ret.description)
        self.assertEqual(self.tags, ret.tags)
        self.assertTrue(ret.enabled)
        self.assertTrue(ret.show_in_apps_library)

    def test_endpoint_validator(self):
        bad_endpoint = 'not a url'
        http_url = 'http://foo.com'
        https_url = 'https://foo.com'

        # Bad URL
        a = ProxyApp.objects.create(
            name="Bad URL Test",
            endpoint=bad_endpoint,
            logo_url=self.logo,
            description=self.description,
            tags=self.tags
        )

        with self.assertRaises(ValidationError) as cm:
            a.clean_fields()

        self.assertIn('endpoint', str(cm.exception))
        self.assertIn('Invalid Endpoint: Must be prefixed with "http://" or "https://".', str(cm.exception))

        # HTTP
        b = ProxyApp.objects.create(
            name="HTTP URL Test",
            endpoint=http_url,
            logo_url=self.logo,
            description=self.description,
            tags=self.tags
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
            logo_url=self.logo,
            description=self.description,
            tags=self.tags
        )

        c_exception_raised = False

        try:
            c.clean_fields()
        except ValidationError:
            c_exception_raised = True

        self.assertFalse(c_exception_raised)

    def test_log_url_validator(self):
        bad_url = 'not a url'
        http_url = 'http://foo.com'
        https_url = 'https://foo.com'

        # Bad URL
        a = ProxyApp.objects.create(
            name="Bad URL Test",
            endpoint=self.endpoint,
            logo_url=bad_url,
            description=self.description,
            tags=self.tags
        )

        with self.assertRaises(ValidationError) as cm:
            a.clean_fields()

        self.assertIn('logo_url', str(cm.exception))
        self.assertIn('Invalid Endpoint: Must be prefixed with "http://" or "https://".', str(cm.exception))

        # HTTP
        b = ProxyApp.objects.create(
            name="HTTP URL Test",
            endpoint=self.endpoint,
            logo_url=http_url,
            description=self.description,
            tags=self.tags
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
            logo_url=https_url,
            description=self.description,
            tags=self.tags
        )

        c_exception_raised = False

        try:
            c.clean_fields()
        except ValidationError:
            c_exception_raised = True

        self.assertFalse(c_exception_raised)
