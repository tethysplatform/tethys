import unittest
import tethys_apps.base.handoff as tethys_handoff
from types import FunctionType
from unittest import mock
from tethys_sdk.testing import TethysTestCase


def test_function(*args):

    if args is not None:
        arg_list = []
        for arg in args:
            arg_list.append(arg)
        return arg_list
    else:
        return ''


class TestHandoffManager(unittest.TestCase):
    def setUp(self):
        self.hm = tethys_handoff.HandoffManager

    def tearDown(self):
        pass

    def test_init(self):
        # Mock app
        app = mock.MagicMock()

        # Mock handoff_handlers
        handlers = mock.MagicMock(name='handler_name')
        app.handoff_handlers.return_value = handlers

        # mock _get_valid_handlers
        self.hm._get_valid_handlers = mock.MagicMock(return_value=['valid_handler'])
        result = tethys_handoff.HandoffManager(app=app)

        # Check result
        self.assertEqual(app, result.app)
        self.assertEqual(handlers, result.handlers)
        self.assertEqual(['valid_handler'], result.valid_handlers)

    def test_repr(self):
        # Mock app
        app = mock.MagicMock()

        # Mock handoff_handlers
        handlers = mock.MagicMock()
        handlers.name = 'test_handler'
        app.handoff_handlers.return_value = [handlers]

        # mock _get_valid_handlers
        self.hm._get_valid_handlers = mock.MagicMock(return_value=['valid_handler'])
        result = tethys_handoff.HandoffManager(app=app).__repr__()
        check_string = "<Handoff Manager: app={}, handlers=['{}']>".format(app, handlers.name)

        self.assertEqual(check_string, result)

    def test_get_capabilities(self):
        # Mock app
        app = mock.MagicMock()

        # Mock _get_handoff_manager_for_app
        manager = mock.MagicMock(valid_handlers='test_handlers')
        self.hm._get_handoff_manager_for_app = mock.MagicMock(return_value=manager)

        result = tethys_handoff.HandoffManager(app=app).get_capabilities(app_name='test_app')

        # Check Result
        self.assertEqual('test_handlers', result)

    def test_get_capabilities_external(self):
        # Mock app
        app = mock.MagicMock()

        # Mock _get_handoff_manager_for_app
        handler1 = mock.MagicMock()
        handler1.internal = False
        handler2 = mock.MagicMock()
        # Do not write out handler2
        handler2.internal = True
        manager = mock.MagicMock(valid_handlers=[handler1, handler2])
        self.hm._get_handoff_manager_for_app = mock.MagicMock(return_value=manager)

        result = tethys_handoff.HandoffManager(app=app).get_capabilities(app_name='test_app', external_only=True)

        # Check Result
        self.assertEqual([handler1], result)

    @mock.patch('tethys_apps.base.handoff.json')
    def test_get_capabilities_json(self, mock_json):
        # Mock app
        app = mock.MagicMock()

        # Mock HandoffHandler.__json

        handler1 = mock.MagicMock(name='test_name')
        manager = mock.MagicMock(valid_handlers=[handler1])
        self.hm._get_handoff_manager_for_app = mock.MagicMock(return_value=manager)

        tethys_handoff.HandoffManager(app=app).get_capabilities(app_name='test_app', jsonify=True)

        # Check Result
        rts_call_args = mock_json.dumps.call_args_list
        self.assertEqual('test_name', rts_call_args[0][0][0][0]['_mock_name'])

    def test_get_handler(self):
        app = mock.MagicMock()

        # Mock _get_handoff_manager_for_app
        handler1 = mock.MagicMock()
        handler1.name = 'handler1'
        manager = mock.MagicMock(valid_handlers=[handler1])
        self.hm._get_handoff_manager_for_app = mock.MagicMock(return_value=manager)

        result = tethys_handoff.HandoffManager(app=app).get_handler(handler_name='handler1')

        self.assertEqual('handler1', result.name)

    @mock.patch('tethys_apps.base.handoff.HttpResponseBadRequest')
    def test_handoff_type_error(self, mock_hrbr):
        from django.http import HttpRequest
        request = HttpRequest()

        # Mock app
        app = mock.MagicMock()
        app.name = 'test_app_name'

        # Mock _get_handoff_manager_for_app
        handler1 = mock.MagicMock()
        handler1().internal = False
        handler1().side_effect = TypeError('test message')
        manager = mock.MagicMock(get_handler=handler1)
        self.hm._get_handoff_manager_for_app = mock.MagicMock(return_value=manager)

        tethys_handoff.HandoffManager(app=app).handoff(request=request, handler_name='test_handler')
        rts_call_args = mock_hrbr.call_args_list

        # Check result
        self.assertIn('HTTP 400 Bad Request: test message.',
                      rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.handoff.HttpResponseBadRequest')
    def test_handoff_error(self, mock_hrbr):
        from django.http import HttpRequest
        request = HttpRequest()
        #
        # # Mock app
        app = mock.MagicMock()
        app.name = 'test_app_name'

        # Mock _get_handoff_manager_for_app
        handler1 = mock.MagicMock()
        # Ask Nathan is this how the test should be. because internal = True has
        # nothing to do with the error message.
        handler1().internal = True
        handler1().side_effect = TypeError('test message')
        mapp = mock.MagicMock()
        mapp.name = 'test manager name'
        manager = mock.MagicMock(get_handler=handler1, app=mapp)
        self.hm._get_handoff_manager_for_app = mock.MagicMock(return_value=manager)

        tethys_handoff.HandoffManager(app=app).handoff(request=request, handler_name='test_handler')
        rts_call_args = mock_hrbr.call_args_list

        # Check result
        check_message = "HTTP 400 Bad Request: No handoff handler '{0}' for app '{1}' found".\
            format('test manager name', 'test_handler')
        self.assertIn(check_message, rts_call_args[0][0][0])

    def test_get_valid_handlers(self):
        app = mock.MagicMock(package='test_app')

        # Mock handoff_handlers
        handler1 = mock.MagicMock(handler='controllers.home', valid=True)

        app.handoff_handlers.return_value = [handler1]

        # mock _get_valid_handlers
        result = tethys_handoff.HandoffManager(app=app)._get_valid_handlers()
        # Check result
        self.assertEqual('controllers.home', result[0].handler)


class TestHandoffHandler(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        result = tethys_handoff.HandoffHandler(name='test_name', handler='test_app.handoff.csv', internal=True)

        # Check Result
        self.assertEqual('test_name', result.name)
        self.assertEqual('test_app.handoff.csv', result.handler)
        self.assertTrue(result.internal)
        self.assertIs(type(result.function), FunctionType)

    def test_repr(self):
        result = tethys_handoff.HandoffHandler(name='test_name', handler='test_app.handoff.csv',
                                               internal=True).__repr__()

        # Check Result
        check_string = '<Handoff Handler: name=test_name, handler=test_app.handoff.csv>'
        self.assertEqual(check_string, result)

    def test_dict_json_arguments(self):
        tethys_handoff.HandoffHandler.arguments = ['test_json', 'request']
        result = tethys_handoff.HandoffHandler(name='test_name', handler='test_app.handoff.csv',
                                               internal=True).__dict__()

        # Check Result
        check_dict = {'name': 'test_name', 'arguments': ['test_json']}
        self.assertIsInstance(result, dict)
        self.assertEqual(check_dict, result)

    def test_arguments(self):
        result = tethys_handoff.HandoffHandler(name='test_name', handler='test_app.handoff.csv', internal=True)\
            .arguments

        self.assertEqual(['request', 'csv_url'], result)


class TestGetHandoffManagerFroApp(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_not_app_name(self):
        app = mock.MagicMock()
        result = tethys_handoff.HandoffManager(app=app)._get_handoff_manager_for_app(app_name=None)

        self.assertEqual(app, result.app)

    @mock.patch('tethys_apps.base.handoff.tethys_apps')
    def test_with_app(self, mock_ta):
        app = mock.MagicMock(package='test_app')
        app.get_handoff_manager.return_value = 'test_manager'
        mock_ta.harvester.SingletonHarvester().apps = [app]
        result = tethys_handoff.HandoffManager(app=app)._get_handoff_manager_for_app(app_name='test_app')

        # Check result
        self.assertEqual('test_manager', result)


class TestTestAppHandoff(TethysTestCase):
    def set_up(self):
        self.c = self.get_test_client()
        self.user = self.create_test_user(username="joe", password="secret", email="joe@some_site.com")
        self.c.force_login(self.user)

    def tear_down(self):
        self.user.delete()

    def test_test_app_handoff(self):
        response = self.c.get('/handoff/test-app/test_name/?csv_url=""')

        self.assertEqual(302, response.status_code)
