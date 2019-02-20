"""
********************************************************************************
* Name: tests_models.py
* Author: nswain
* Created On: August 29, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
# import unittest
# from unittest import mock
# import tethys_apps.models
# from __builtin__ import __import__ as real_import
#
#
# def mock_import(name, globals={}, locals={}, fromlist=[], level=-1):
#     if name == 'tethys_services.models' and len(fromlist) == 4:
#         raise RuntimeError
#     return real_import(name, globals, locals, fromlist, level)
#
#
# class ModelsTests(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#     @mock.patch('__builtin__.__import__', side_effect=mock_import)
#     @mock.patch('tethys_apps.models.log')
#     def test_service_models_import_error(self, mock_log, _):
#         # mock_log.exception.side_effect = SystemExit
#         tethys_apps.models.logging = mock.MagicMock
#         try:
#             reload(tethys_apps.models)
#         except SystemExit:
#             pass
#
#         # mock_log.exception.assert_called_with('An error occurred while trying to import tethys service models.')
