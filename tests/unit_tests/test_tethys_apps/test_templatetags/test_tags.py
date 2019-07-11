import unittest
from unittest import mock
from tethys_apps.templatetags import tags as t


class TestTags(unittest.TestCase):
    def setUp(self):
        # app_list
        self.app_names = ['app1', 'app2', 'app3', 'app4', 'app5', 'app6']
        self.tag_names = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6']
        self.mock_apps = {'configured': []}
        for i, ap in enumerate(self.app_names):
            mock_app = mock.MagicMock(tags=','.join(self.tag_names[:i+1]))
            mock_app.name = ap
            self.mock_apps['configured'].append(mock_app)

    def tearDown(self):
        pass

    def test_get_tags_from_apps(self):
        ret_tag_list = t.get_tags_from_apps(self.mock_apps)
        self.assertEqual(sorted(self.tag_names), sorted(ret_tag_list))

    def test_get_tag_class(self):
        ret_tag_list = t.get_tag_class(self.mock_apps['configured'][-1])
        self.assertEqual(' '.join(sorted(self.tag_names)), ret_tag_list)
