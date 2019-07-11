import unittest
from unittest import mock
import errno

from django.template import TemplateDoesNotExist
from tethys_apps.template_loaders import TethysTemplateLoader


class TestTethysTemplateLoader(unittest.TestCase):
    def setUp(self):
        self.mock_engine = mock.MagicMock()

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.template_loaders.io.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.template_loaders.BaseLoader')
    def test_get_contents(self, _, mock_file):
        handlers = (mock.mock_open(read_data='mytemplate').return_value, mock_file.return_value)
        mock_file.side_effect = handlers
        origin = mock.MagicMock(name='test_app/css/main.css')

        tethys_template_loader = TethysTemplateLoader(self.mock_engine)

        ret = tethys_template_loader.get_contents(origin)
        self.assertIn('mytemplate', ret)
        mock_file.assert_called_once()

    @mock.patch('tethys_apps.template_loaders.io.open')
    @mock.patch('tethys_apps.template_loaders.BaseLoader')
    def test_get_contents_io_error(self, _, mock_file):
        mock_file.side_effect = IOError
        origin = mock.MagicMock(name='test_app/css/main.css')

        tethys_template_loader = TethysTemplateLoader(self.mock_engine)

        self.assertRaises(IOError, tethys_template_loader.get_contents, origin)
        mock_file.assert_called_once()

    @mock.patch('tethys_apps.template_loaders.io.open', side_effect=IOError(errno.ENOENT, 'foo'))
    @mock.patch('tethys_apps.template_loaders.BaseLoader')
    def test_get_contents_template_does_not_exist(self, _, mock_file):
        origin = mock.MagicMock(name='test_app/css/main.css')

        tethys_template_loader = TethysTemplateLoader(self.mock_engine)

        self.assertRaises(TemplateDoesNotExist, tethys_template_loader.get_contents, origin)
        mock_file.assert_called_once()

    @mock.patch('tethys_apps.template_loaders.BaseLoader')
    @mock.patch('tethys_apps.template_loaders.get_directories_in_tethys')
    def test_get_template_sources(self, mock_gdt, _):
        tethys_template_loader = TethysTemplateLoader(self.mock_engine)
        mock_gdt.return_value = ['/foo/template1']
        expected_template_name = 'foo'

        for origin in tethys_template_loader.get_template_sources(expected_template_name):
            self.assertEqual('/foo/template1/foo', origin.name)
            self.assertEqual('foo', origin.template_name)
            self.assertTrue(isinstance(origin.loader, TethysTemplateLoader))

    @mock.patch('tethys_apps.template_loaders.safe_join')
    @mock.patch('tethys_apps.template_loaders.BaseLoader')
    @mock.patch('tethys_apps.template_loaders.get_directories_in_tethys')
    def test_get_template_sources_exception(self, mock_gdt, _, mock_safe_join):
        from django.core.exceptions import SuspiciousFileOperation

        tethys_template_loader = TethysTemplateLoader(self.mock_engine)
        mock_gdt.return_value = ['/foo/template1', '/foo/template2']
        mock_safe_join.side_effect = [SuspiciousFileOperation, '/foo/template2/foo']
        expected_template_name = 'foo'

        for origin in tethys_template_loader.get_template_sources(expected_template_name):
            self.assertEqual('/foo/template2/foo', origin.name)
            self.assertEqual('foo', origin.template_name)
            self.assertTrue(isinstance(origin.loader, TethysTemplateLoader))
