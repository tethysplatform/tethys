from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model
from unittest import mock


class PersistentStoreServiceTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_unicode(self):
        pss = service_model.PersistentStoreService(
            name='test_pss',
            username='foo',
            password='pass'
        )
        self.assertEqual('test_pss', str(pss))

    @mock.patch('sqlalchemy.engine.url.URL')
    def test_get_url(self, mock_url):
        pss = service_model.PersistentStoreService(
            name='test_pss',
            username='foo',
            password='pass'
        )

        # Execute
        pss.get_url()

        # Check if called correctly
        mock_url.assert_called_with(database=None, drivername='postgresql', host='localhost',
                                    password='pass', port=5435, username='foo')

    @mock.patch('tethys_services.models.PersistentStoreService.get_url')
    @mock.patch('sqlalchemy.create_engine')
    def test_get_engine(self, mock_ce, mock_url):
        pss = service_model.PersistentStoreService(
            name='test_pss',
            username='foo',
            password='pass'
        )

        mock_url.return_value = 'test_url'
        # Execute
        pss.get_engine()

        # Check if called correctly
        mock_ce.assert_called_with('test_url')
