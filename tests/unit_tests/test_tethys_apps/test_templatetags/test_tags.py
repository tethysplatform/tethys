import unittest
from unittest import mock
from tethys_apps.templatetags import tags as t


class TestTags(unittest.TestCase):
    def setUp(self):
        # app_list
        self.app_names = ['app1', 'app2', 'app3', 'app4', 'app5', 'app6']
        self.tag_names = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6']

        # Object apps
        self.mock_object_apps = {'configured': []}
        for i, app_name in enumerate(self.app_names):
            mock_app = mock.MagicMock(tags=','.join(self.tag_names[:i+1]))
            mock_app.name = app_name
            self.mock_object_apps['configured'].append(mock_app)

        # Dictionary apps
        self.mock_dict_apps = {'configured': []}

        for i, app_name in enumerate(self.app_names):
            mock_app = dict(tags=','.join(self.tag_names[:i+1]), name=app_name)
            self.mock_dict_apps['configured'].append(mock_app)

    def tearDown(self):
        pass

    def test_get_tag_class(self):
        ret_tag_list = t.get_tag_class(self.mock_object_apps['configured'][-1])
        self.assertEqual(' '.join(sorted(self.tag_names)), ret_tag_list)

    def test_get_tag_class_dict(self):
        ret_tag_list = t.get_tag_class(self.mock_dict_apps['configured'][-1])
        self.assertEqual(' '.join(sorted(self.tag_names)), ret_tag_list)

    def test_get_tags_from_apps(self):
        ret_tag_list = t.get_tags_from_apps(self.mock_object_apps)
        self.assertEqual(sorted(self.tag_names), sorted(ret_tag_list))

    def test_get_tags_from_apps_dict(self):
        ret_tag_list = t.get_tags_from_apps(self.mock_dict_apps)
        self.assertEqual(sorted(self.tag_names), sorted(ret_tag_list))

    def test_get_tags_from_apps_object_disabled(self):
        self.mock_object_apps['configured'].append(mock.MagicMock(tags='disabled', enabled=False))
        ret_tag_list = t.get_tags_from_apps(self.mock_object_apps)
        self.assertNotIn('disabled', ret_tag_list)

    def test_get_tags_from_apps_dict_disabled(self):
        self.mock_dict_apps['configured'].append({'tags': 'disabled', 'enabled': False})
        ret_tag_list = t.get_tags_from_apps(self.mock_dict_apps)
        self.assertNotIn('disabled', ret_tag_list)

    def test_get_tags_from_apps_object_dont_show(self):
        self.mock_object_apps['configured'].append(mock.MagicMock(tags='disabled', show_in_apps_library=False))
        ret_tag_list = t.get_tags_from_apps(self.mock_object_apps)
        self.assertNotIn('disabled', ret_tag_list)

    def test_get_tags_from_apps_dict_dont_show(self):
        self.mock_dict_apps['configured'].append({'tags': 'disabled', 'show_in_apps_library': False})
        ret_tag_list = t.get_tags_from_apps(self.mock_dict_apps)
        self.assertNotIn('disabled', ret_tag_list)
