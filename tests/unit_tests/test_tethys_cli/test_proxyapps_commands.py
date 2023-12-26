from tethys_apps.models import ProxyApp

from unittest import mock
from io import StringIO
from tethys_cli.proxyapps_commands import add_proxyapp, update_proxyapp, list_apps

from django.test import TestCase
import unittest


class TestProxyAppsCommand(TestCase):
    def setUp(self):
        self.app_name = "My Proxy App for Testing"
        self.endpoint = "http://foo.example.com/my-proxy-app"
        self.back_url = "http://bar.example.com/apps/"
        self.logo = "http://foo.example.com/my-proxy-app/logo.png"
        self.description = "This is an app that is not here."
        self.tags = '"Water","Earth","Fire","Air"'
        self.open_in_new_tab = True

        self.proxy_app = ProxyApp(
            name=self.app_name,
            endpoint=self.endpoint,
            logo_url=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        self.proxy_app.save()
 

    def tearDown(self):
        print("hellos")
        self.proxy_app.delete()
    
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_list_proxy_apps(self,mock_stdout):
        expected_output = "Proxy Apps:\n  My Proxy App for Testing"
        list_apps()
        self.assertEqual(mock_stdout.getvalue().strip(), expected_output)

    