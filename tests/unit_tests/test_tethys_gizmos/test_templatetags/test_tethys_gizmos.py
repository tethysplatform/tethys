import unittest
import tethys_gizmos.templatetags.tethys_gizmos as gizmos_templatetags
import mock


class TestTethysGizmos(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @mock.patch('tethys_gizmos.templatetags.tethys_gizmos.SingletonHarvester')
    @mock.patch('tethys_apps.harvester.SingletonHarvester')
    def test_TestTethysGizmos(self, mock_harvest):
        mock_harvest.return_value = mock.NonCallableMagicMock(extension_modules=
                                                              {'plotly_view': 'plotly_view'})
        # reload(gizmos_templatetags)
        # TODO: need to get into import gizmos extension code
        result = reload(gizmos_templatetags.HighchartsDateEncoder('2018/08/01'))

        pass
