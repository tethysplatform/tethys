import unittest
from unittest import mock

from django.core.exceptions import ObjectDoesNotExist
from social_core.exceptions import AuthAlreadyAssociated, AuthException

from tethys_dataset_services.engines import HydroShareDatasetEngine
from tethys_services.utilities import ensure_oauth2, initialize_engine_object, list_dataset_engines, \
    get_dataset_engine, list_spatial_dataset_engines, get_spatial_dataset_engine, abstract_is_link, activate_wps, \
    list_wps_service_engines, get_wps_service_engine
try:
    from urllib2 import HTTPError, URLError
except ImportError:
    from urllib.request import HTTPError, URLError


@ensure_oauth2('hydroshare')
def enforced_controller(request, *args, **kwargs):
    return True


class TestUtilites(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_services.utilities.reverse')
    @mock.patch('tethys_services.utilities.redirect')
    def test_ensure_oauth2(self, mock_redirect, mock_reverse):

        mock_user = mock.MagicMock()

        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_redirect_url = mock.MagicMock()

        mock_reverse.return_value = mock_redirect_url

        enforced_controller(mock_request)

        mock_reverse.assert_called_once_with('social:begin', args=['hydroshare'])

        mock_redirect.assert_called_once()

        mock_user.social_auth.get.assert_called_once_with(provider='hydroshare')

    @mock.patch('tethys_services.utilities.reverse')
    @mock.patch('tethys_services.utilities.redirect')
    def test_ensure_oauth2_ObjectDoesNotExist(self, mock_redirect, mock_reverse):
        from django.core.exceptions import ObjectDoesNotExist

        mock_user = mock.MagicMock()

        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_redirect_url = mock.MagicMock()

        mock_reverse.return_value = mock_redirect_url

        mock_user.social_auth.get.side_effect = ObjectDoesNotExist

        ret = enforced_controller(mock_request)

        mock_reverse.assert_called_once_with('social:begin', args=['hydroshare'])

        mock_redirect.assert_called_once()

        self.assertEqual(mock_redirect(), ret)

    @mock.patch('tethys_services.utilities.reverse')
    @mock.patch('tethys_services.utilities.redirect')
    def test_ensure_oauth2_AttributeError(self, mock_redirect, mock_reverse):
        mock_user = mock.MagicMock()

        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_redirect_url = mock.MagicMock()

        mock_reverse.return_value = mock_redirect_url

        mock_user.social_auth.get.side_effect = AttributeError

        ret = enforced_controller(mock_request)

        mock_reverse.assert_called_once_with('social:begin', args=['hydroshare'])

        mock_redirect.assert_called_once()

        self.assertEqual(mock_redirect(), ret)

    @mock.patch('tethys_services.utilities.reverse')
    @mock.patch('tethys_services.utilities.redirect')
    def test_ensure_oauth2_AuthAlreadyAssociated(self, mock_redirect, mock_reverse):
        from social_core.exceptions import AuthAlreadyAssociated

        mock_user = mock.MagicMock()

        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_redirect_url = mock.MagicMock()

        mock_reverse.return_value = mock_redirect_url

        mock_user.social_auth.get.side_effect = AuthAlreadyAssociated(mock.MagicMock(), mock.MagicMock())

        self.assertRaises(AuthAlreadyAssociated, enforced_controller, mock_request)

        mock_reverse.assert_called_once_with('social:begin', args=['hydroshare'])

        mock_redirect.assert_called_once()

    @mock.patch('tethys_services.utilities.reverse')
    @mock.patch('tethys_services.utilities.redirect')
    def test_ensure_oauth2_Exception(self, mock_redirect, mock_reverse):
        mock_user = mock.MagicMock()

        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_redirect_url = mock.MagicMock()

        mock_reverse.return_value = mock_redirect_url

        mock_user.social_auth.get.side_effect = Exception

        self.assertRaises(Exception, enforced_controller, mock_request)

        mock_reverse.assert_called_once_with('social:begin', args=['hydroshare'])

        mock_redirect.assert_called_once()

    def test_initialize_engine_object(self):
        input_engine = 'tethys_dataset_services.engines.HydroShareDatasetEngine'
        input_end_point = 'http://localhost/api/3/action'

        mock_user = mock.MagicMock()
        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_social = mock.MagicMock()

        mock_user.social_auth.get.return_value = mock_social

        mock_api_key = mock.MagicMock()

        mock_social.extra_data['access_token'].return_value = mock_api_key

        ret = initialize_engine_object(engine=input_engine, endpoint=input_end_point, request=mock_request)

        mock_user.social_auth.get.assert_called_once_with(provider='hydroshare')

        self.assertEqual('http://localhost/api/3/action', ret.endpoint)
        self.assertIsInstance(ret, HydroShareDatasetEngine)

    def test_initialize_engine_object_ObjectDoesNotExist(self):
        input_engine = 'tethys_dataset_services.engines.HydroShareDatasetEngine'
        input_end_point = 'http://localhost/api/3/action'

        mock_user = mock.MagicMock()
        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_social = mock.MagicMock()

        mock_user.social_auth.get.side_effect = [ObjectDoesNotExist, mock_social]

        mock_social.extra_data['access_token'].return_value = None

        self.assertRaises(AuthException, initialize_engine_object, engine=input_engine, endpoint=input_end_point,
                          request=mock_request)

        mock_user.social_auth.get.assert_called_once_with(provider='hydroshare')

    def test_initialize_engine_object_AttributeError(self):
        input_engine = 'tethys_dataset_services.engines.HydroShareDatasetEngine'
        input_end_point = 'http://localhost/api/3/action'

        mock_user = mock.MagicMock()
        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_social = mock.MagicMock()

        mock_user.social_auth.get.side_effect = [AttributeError, mock_social]

        self.assertRaises(AttributeError, initialize_engine_object, engine=input_engine, endpoint=input_end_point,
                          request=mock_request)

        mock_user.social_auth.get.assert_called_once_with(provider='hydroshare')

    def test_initialize_engine_object_AuthAlreadyAssociated(self):
        input_engine = 'tethys_dataset_services.engines.HydroShareDatasetEngine'
        input_end_point = 'http://localhost/api/3/action'

        mock_user = mock.MagicMock()
        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_social = mock.MagicMock()

        mock_user.social_auth.get.side_effect = [AuthAlreadyAssociated(mock.MagicMock(), mock.MagicMock()), mock_social]

        self.assertRaises(AuthAlreadyAssociated, initialize_engine_object, engine=input_engine,
                          endpoint=input_end_point, request=mock_request)

        mock_user.social_auth.get.assert_called_once_with(provider='hydroshare')

    def test_initialize_engine_object_Exception(self):
        input_engine = 'tethys_dataset_services.engines.HydroShareDatasetEngine'
        input_end_point = 'http://localhost/api/3/action'

        mock_user = mock.MagicMock()
        mock_request = mock.MagicMock(user=mock_user, path='path')

        mock_social = mock.MagicMock()

        mock_user.social_auth.get.side_effect = [Exception, mock_social]

        self.assertRaises(Exception, initialize_engine_object, engine=input_engine, endpoint=input_end_point,
                          request=mock_request)

        mock_user.social_auth.get.assert_called_once_with(provider='hydroshare')

    @mock.patch('tethys_services.utilities.DsModel.objects')
    @mock.patch('tethys_services.utilities.initialize_engine_object')
    def test_list_dataset_engines(self, mock_initialize_engine_object, mock_dsmodel):

        mock_engine = mock.MagicMock()
        mock_endpoint = mock.MagicMock()
        mock_api_key = mock.MagicMock()
        mock_user_name = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_request = mock.MagicMock()
        mock_public_endpoint = mock.MagicMock()
        mock_site_dataset_service1 = mock.MagicMock(engine=mock_engine,
                                                    endpoint=mock_endpoint.endpoint,
                                                    apikey=mock_api_key,
                                                    username=mock_user_name,
                                                    password=mock_password,
                                                    request=mock_request,
                                                    public_endpoint=mock_public_endpoint)

        mock_site_dataset_services = [mock_site_dataset_service1]

        mock_dsmodel.all.return_value = mock_site_dataset_services

        mock_init_return = mock.MagicMock()
        mock_init_return.public_endpoint = mock_site_dataset_service1.public_endpoint

        mock_initialize_engine_object.return_value = mock_init_return

        ret = list_dataset_engines()

        mock_initialize_engine_object.assert_called_with(apikey=mock_api_key,
                                                         endpoint=mock_endpoint.endpoint,
                                                         engine=mock_engine,
                                                         password=mock_password,
                                                         request=None,
                                                         username=mock_user_name,
                                                         )

        mock_dsmodel.all.assert_called_once()

        self.assertEqual(mock_init_return, ret[0])

    @mock.patch('tethys_services.utilities.issubclass')
    @mock.patch('tethys_services.utilities.initialize_engine_object')
    def test_get_dataset_engine_app_dataset(self, mock_initialize_engine_object, mock_subclass):
        from tethys_apps.base.app_base import TethysAppBase

        mock_name = 'foo'
        mock_app_class = mock.MagicMock()
        mock_subclass.return_value = True
        mock_app_dataset_services = mock.MagicMock()
        mock_app_dataset_services.name = 'foo'

        mock_app_class().dataset_services.return_value = [mock_app_dataset_services]

        mock_initialize_engine_object.return_value = True

        ret = get_dataset_engine(mock_name, mock_app_class)

        mock_subclass.assert_called_once_with(mock_app_class, TethysAppBase)

        mock_initialize_engine_object.assert_called_with(engine=mock_app_dataset_services.engine,
                                                         endpoint=mock_app_dataset_services.endpoint,
                                                         apikey=mock_app_dataset_services.apikey,
                                                         username=mock_app_dataset_services.username,
                                                         password=mock_app_dataset_services.password,
                                                         request=None)

        self.assertTrue(ret)

    @mock.patch('tethys_services.utilities.issubclass')
    @mock.patch('tethys_services.utilities.initialize_engine_object')
    @mock.patch('tethys_services.utilities.DsModel.objects.all')
    def test_get_dataset_engine_dataset_services(self, mock_ds_model_object_all, mock_initialize_engine_object,
                                                 mock_subclass):
        mock_name = 'foo'

        mock_subclass.return_value = False

        mock_init_return = mock.MagicMock()

        mock_initialize_engine_object.return_value = mock_init_return

        mock_site_dataset_services = mock.MagicMock()

        mock_site_dataset_services.name = 'foo'

        mock_ds_model_object_all.return_value = [mock_site_dataset_services]

        mock_init_return.public_endpoint = mock_site_dataset_services.public_endpoint

        ret = get_dataset_engine(mock_name,  app_class=None)

        mock_initialize_engine_object.assert_called_with(engine=mock_site_dataset_services.engine,
                                                         endpoint=mock_site_dataset_services.endpoint,
                                                         apikey=mock_site_dataset_services.apikey,
                                                         username=mock_site_dataset_services.username,
                                                         password=mock_site_dataset_services.password,
                                                         request=None)

        self.assertEqual(mock_init_return, ret)

    @mock.patch('tethys_services.utilities.initialize_engine_object')
    @mock.patch('tethys_services.utilities.DsModel.objects.all')
    def test_get_dataset_engine_name_error(self, mock_ds_model_object_all, mock_initialize_engine_object):
        mock_name = 'foo'

        mock_site_dataset_services = mock.MagicMock()

        mock_site_dataset_services.name = 'foo'

        mock_ds_model_object_all.return_value = None

        self.assertRaises(NameError, get_dataset_engine, mock_name, app_class=None)

        mock_initialize_engine_object.assert_not_called()

    @mock.patch('tethys_services.utilities.initialize_engine_object')
    @mock.patch('tethys_services.utilities.SdsModel')
    def test_list_spatial_dataset_engines(self, mock_sds_model, mock_initialize):
        mock_service1 = mock.MagicMock()
        mock_sds_model.objects.all.return_value = [mock_service1]
        mock_ret = mock.MagicMock()
        mock_ret.public_endpoint = mock_service1.public_endpoint
        mock_initialize.return_value = mock_ret

        ret = list_spatial_dataset_engines()

        self.assertEqual(mock_ret, ret[0])
        mock_sds_model.objects.all.assert_called_once()
        mock_initialize.assert_called_once_with(engine=mock_service1.engine,
                                                endpoint=mock_service1.endpoint,
                                                apikey=mock_service1.apikey,
                                                username=mock_service1.username,
                                                password=mock_service1.password)

    @mock.patch('tethys_services.utilities.initialize_engine_object')
    @mock.patch('tethys_services.utilities.issubclass')
    def test_get_spatial_dataset_engine_with_app(self, mock_issubclass, mock_initialize_engine_object):
        from tethys_apps.base.app_base import TethysAppBase

        name = 'foo'
        mock_app_class = mock.MagicMock()
        mock_app_sds = mock.MagicMock()
        mock_app_sds.name = 'foo'
        mock_app_class().spatial_dataset_services.return_value = [mock_app_sds]
        mock_issubclass.return_value = True
        mock_initialize_engine_object.return_value = True

        ret = get_spatial_dataset_engine(name=name, app_class=mock_app_class)

        self.assertTrue(ret)
        mock_issubclass.assert_called_once_with(mock_app_class, TethysAppBase)
        mock_initialize_engine_object.assert_called_once_with(engine=mock_app_sds.engine,
                                                              endpoint=mock_app_sds.endpoint,
                                                              apikey=mock_app_sds.apikey,
                                                              username=mock_app_sds.username,
                                                              password=mock_app_sds.password)

    @mock.patch('tethys_services.utilities.initialize_engine_object')
    @mock.patch('tethys_services.utilities.SdsModel')
    def test_get_spatial_dataset_engine_with_site(self, mock_sds_model, mock_initialize_engine_object):
        name = 'foo'
        mock_site_sds = mock.MagicMock()
        mock_site_sds.name = 'foo'
        mock_sds_model.objects.all.return_value = [mock_site_sds]
        mock_sdo = mock.MagicMock()
        mock_sdo.public_endpoint = mock_site_sds.public_endpoint
        mock_initialize_engine_object.return_value = mock_sdo

        ret = get_spatial_dataset_engine(name=name, app_class=None)

        self.assertEqual(mock_sdo, ret)
        mock_initialize_engine_object.assert_called_once_with(engine=mock_site_sds.engine,
                                                              endpoint=mock_site_sds.endpoint,
                                                              apikey=mock_site_sds.apikey,
                                                              username=mock_site_sds.username,
                                                              password=mock_site_sds.password)

    @mock.patch('tethys_services.utilities.SdsModel')
    def test_get_spatial_dataset_engine_with_name_error(self, mock_sds_model):
        name = 'foo'
        mock_sds_model.objects.all.return_value = None

        self.assertRaises(NameError, get_spatial_dataset_engine, name=name, app_class=None)

    def test_abstract_is_link(self):
        mock_process = mock.MagicMock()
        mock_process.abstract = 'http://foo'

        ret = abstract_is_link(mock_process)

        self.assertTrue(ret)

    def test_abstract_is_link_false(self):
        mock_process = mock.MagicMock()
        mock_process.abstract = 'foo_bar'

        ret = abstract_is_link(mock_process)

        self.assertFalse(ret)

    def test_abstract_is_link_attribute_error(self):
        ret = abstract_is_link(process=None)

        self.assertFalse(ret)

    def test_activate_wps(self):
        mock_wps = mock.MagicMock()
        mock_endpoint = mock.MagicMock()
        mock_name = mock.MagicMock()

        ret = activate_wps(mock_wps, mock_endpoint, mock_name)

        mock_wps.getcapabilities.assert_called_once()
        self.assertEqual(mock_wps, ret)

    def test_activate_wps_HTTPError_with_error_code_404(self):
        mock_wps = mock.MagicMock()
        mock_endpoint = mock.MagicMock()
        mock_name = mock.MagicMock()

        mock_wps.getcapabilities.side_effect = HTTPError(url='test_url', code=404, msg='test_message',
                                                         hdrs='test_header', fp=None)

        self.assertRaises(HTTPError, activate_wps, mock_wps, mock_endpoint, mock_name)

    def test_activate_wps_HTTPError(self):
        mock_wps = mock.MagicMock()
        mock_endpoint = mock.MagicMock()
        mock_name = mock.MagicMock()

        mock_wps.getcapabilities.side_effect = HTTPError(url='test_url', code=500, msg='test_message',
                                                         hdrs='test_header', fp=None)

        self.assertRaises(HTTPError, activate_wps, mock_wps, mock_endpoint, mock_name)

    def test_activate_wps_URLError(self):
        mock_wps = mock.MagicMock()
        mock_endpoint = mock.MagicMock()
        mock_name = mock.MagicMock()

        mock_wps.getcapabilities.side_effect = URLError(reason='')

        self.assertIsNone(activate_wps(mock_wps, mock_endpoint, mock_name))

    @mock.patch('tethys_services.utilities.activate_wps')
    @mock.patch('tethys_services.utilities.WebProcessingService')
    @mock.patch('tethys_services.utilities.issubclass')
    def test_get_wps_service_engine_with_app(self, mock_issubclass, mock_wps_obj, mock_activate_wps):
        from tethys_apps.base.app_base import TethysAppBase

        name = 'foo'

        mock_app_ws = mock.MagicMock()
        mock_app_ws.name = 'foo'

        mock_app_class = mock.MagicMock()
        mock_app_class().wps_services.return_value = [mock_app_ws]

        mock_issubclass.return_value = True

        mock_wps_obj.return_value = True

        ret = get_wps_service_engine(name=name, app_class=mock_app_class)

        self.assertTrue(ret)

        mock_issubclass.assert_called_once_with(mock_app_class, TethysAppBase)

        mock_wps_obj.assert_called_once_with(mock_app_ws.endpoint,
                                             username=mock_app_ws.username,
                                             password=mock_app_ws.password,
                                             verbose=False,
                                             skip_caps=True
                                             )

        mock_activate_wps.call_once_with(wps=True, endpoint=mock_app_ws.endpoint, name=mock_app_ws.name)

    @mock.patch('tethys_services.utilities.activate_wps')
    @mock.patch('tethys_services.utilities.WebProcessingService')
    @mock.patch('tethys_services.utilities.WpsModel')
    def test_get_wps_service_engine_with_site(self, mock_wps_model, mock_wps, mock_activate_wps):
        name = 'foo'
        mock_site_ws = mock.MagicMock()
        mock_site_ws.name = 'foo'

        mock_wps_model.objects.all.return_value = [mock_site_ws]

        mock_sdo = mock.MagicMock()
        mock_sdo.public_endpoint = mock_site_ws.public_endpoint

        mock_wps.return_value = mock_sdo

        get_wps_service_engine(name=name, app_class=None)

        mock_wps.assert_called_once_with(mock_site_ws.endpoint,
                                         username=mock_site_ws.username,
                                         password=mock_site_ws.password,
                                         verbose=False,
                                         skip_caps=True)

        mock_activate_wps.call_once_with(wps=mock_sdo, endpoint=mock_site_ws.endpoint, name=mock_site_ws.name)

    @mock.patch('tethys_services.utilities.WpsModel')
    def test_get_wps_service_engine_with_name_error(self, mock_wps_model):
        name = 'foo'
        mock_wps_model.objects.all.return_value = None
        self.assertRaises(NameError, get_wps_service_engine, name=name, app_class=None)

    @mock.patch('tethys_services.utilities.activate_wps')
    @mock.patch('tethys_services.utilities.WebProcessingService')
    @mock.patch('tethys_services.utilities.issubclass')
    def test_list_wps_service_engines_apps(self, mock_issubclass, mock_wps, mock_activate_wps):
        from tethys_apps.base.app_base import TethysAppBase

        mock_app_ws = mock.MagicMock()

        mock_app_ws.name = 'foo'

        mock_app_class = mock.MagicMock()
        mock_app_class().wps_services.return_value = [mock_app_ws]

        mock_issubclass.return_value = True

        mock_wps.return_value = True

        mock_activated_wps = mock.MagicMock()

        mock_activate_wps.return_value = mock_activated_wps

        ret = list_wps_service_engines(app_class=mock_app_class)

        mock_issubclass.assert_called_once_with(mock_app_class, TethysAppBase)

        mock_wps.assert_called_once_with(mock_app_ws.endpoint,
                                         username=mock_app_ws.username,
                                         password=mock_app_ws.password,
                                         verbose=False,
                                         skip_caps=True)

        mock_issubclass.assert_called_once_with(mock_app_class, TethysAppBase)

        self.assertEqual(mock_activate_wps(), ret[0])

    @mock.patch('tethys_services.utilities.activate_wps')
    @mock.patch('tethys_services.utilities.WebProcessingService')
    @mock.patch('tethys_services.utilities.WpsModel')
    def test_list_wps_service_engine_with_site(self, mock_wps_model, mock_wps, mock_activate_wps):
        mock_site_ws = mock.MagicMock()
        mock_site_ws.name = 'foo'

        mock_wps_model.objects.all.return_value = [mock_site_ws]

        mock_sdo = mock.MagicMock()
        mock_sdo.public_endpoint = mock_site_ws.public_endpoint

        mock_wps.return_value = mock_sdo

        mock_activated_wps = mock.MagicMock()

        mock_activate_wps.return_value = mock_activated_wps

        ret = list_wps_service_engines(app_class=None)

        mock_wps.assert_called_once_with(mock_site_ws.endpoint,
                                         username=mock_site_ws.username,
                                         password=mock_site_ws.password,
                                         verbose=False,
                                         skip_caps=True)

        mock_activate_wps.call_once_with(wps=mock_sdo, endpoint=mock_site_ws.endpoint, name=mock_site_ws.name)

        self.assertEqual(mock_activate_wps(), ret[0])
