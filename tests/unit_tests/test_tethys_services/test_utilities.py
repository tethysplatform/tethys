import unittest
import mock

from tethys_services.utilities import ensure_oauth2, initialize_engine_object, list_dataset_engines, get_dataset_engine, \
    list_spatial_dataset_engines, get_spatial_dataset_engine, abstract_is_link, activate_wps, list_wps_service_engines, \
    get_wps_service_engine



class TestUtilites(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @mock.patch('tethys_services.utilities.reverse')
    # @mock.patch('tethys_services.utilities.redirect')
    # def test_ensure_oauth2(self, mock_redirect, mock_reverse):
    #     import pdb
    #     pdb.set_trace()
    #
    #     mock_provider = mock.MagicMock()
    #
    #     mock_request = mock.MagicMock(user='user1', path='path')
    #
    #     mock_user = mock_request.user
    #
    #     mock_redirect_rul = mock.MagicMock()
    #
    #     mock_reverse.return_value = mock_redirect_rul
    #
    #     # call the ensure_oauth2 function
    #     ensure_oauth2(mock_provider)
    #
    #     mock_reverse.assert_called_once_with('social:begin', args=[mock_provider]) + \
    #                                          '?next={0}'.format(mock_request.path)
    #
    #     mock_redirect.assert_called_once_with(mock_redirect_rul)
    #
    #     mock_user.social_auth.get.assert_called_once_with(provider=mock_provider)

    def test_initialize_engine_object(self):
        pass


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
                                                         engine=mock_engine.encode('utf-8'),
                                                         password=mock_password,
                                                         request=None,
                                                         username=mock_user_name,
                                                         )

        mock_dsmodel.all.assert_called_once()

        self.assertEquals(mock_init_return, ret[0])

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

        mock_initialize_engine_object.assert_called_with(engine=mock_site_dataset_services.engine.encode('utf-8'),
                                                         endpoint=mock_site_dataset_services.endpoint,
                                                         apikey=mock_site_dataset_services.apikey,
                                                         username=mock_site_dataset_services.username,
                                                         password=mock_site_dataset_services.password,
                                                         request=None)

        self.assertEquals(mock_init_return, ret)

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

        self.assertEquals(mock_ret, ret[0])
        mock_sds_model.objects.all.assert_called_once()
        mock_initialize.assert_called_once_with(engine=mock_service1.engine.encode('utf-8'),
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

        self.assertEquals(mock_sdo, ret)
        mock_initialize_engine_object.assert_called_once_with(engine=mock_site_sds.engine.encode('utf-8'),
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
