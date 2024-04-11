import unittest
from unittest import mock
from tethys_apps.templatetags import tags as t


class TestTags(unittest.TestCase):
    def setUp(self):
        # app_list
        self.app_names = ["app1", "app2", "app3", "app4", "app5", "app6"]
        self.tag_names = ["tag1", "tag_2", "tag 3", "tag four", "Tag Five", "tag6"]
        self.tag_classes = ["tag1", "tag_2", "tag-3", "tag-four", "tag-five", "tag6"]
        self.tag_pairs = [
            ("tag1", "Tag1"),
            ("tag_2", "Tag_2"),
            ("tag-3", "Tag 3"),
            ("tag-four", "Tag Four"),
            ("tag-five", "Tag Five"),
            ("tag6", "Tag6"),
        ]

        # Object apps
        self.mock_object_apps = {"configured": []}
        for i, app_name in enumerate(self.app_names):
            mock_app = mock.MagicMock(tags=",".join(self.tag_names[: i + 1]))
            mock_app.name = app_name
            self.mock_object_apps["configured"].append(mock_app)

        # Dictionary apps
        self.mock_dict_apps = {"configured": []}

        for i, app_name in enumerate(self.app_names):
            mock_app = dict(tags=",".join(self.tag_names[: i + 1]), name=app_name)
            self.mock_dict_apps["configured"].append(mock_app)

    def tearDown(self):
        pass

    def test_get_tag_class(self):
        ret_tag_str = t.get_tag_class(self.mock_object_apps["configured"][-1])
        ret_tag_list = ret_tag_str.split(" ")
        self.assertEqual(sorted(self.tag_classes), sorted(ret_tag_list))

    def test_get_tag_class_dict(self):
        ret_tag_str = t.get_tag_class(self.mock_dict_apps["configured"][-1])
        ret_tag_list = ret_tag_str.split(" ")
        self.assertEqual(sorted(self.tag_classes), sorted(ret_tag_list))

    def test_get_tags_from_apps(self):
        ret_tag_list = t.get_tags_from_apps(self.mock_object_apps)
        self.assertEqual(sorted(self.tag_pairs), sorted(ret_tag_list))

    def test_get_tags_from_apps_dict(self):
        ret_tag_list = t.get_tags_from_apps(self.mock_dict_apps)
        self.assertEqual(sorted(self.tag_pairs), sorted(ret_tag_list))

    def test_get_tags_from_apps_object_disabled(self):
        self.mock_object_apps["configured"].append(
            mock.MagicMock(tags="disabled", enabled=False)
        )
        ret_tag_list = t.get_tags_from_apps(self.mock_object_apps)
        self.assertNotIn("disabled", ret_tag_list)

    def test_get_tags_from_apps_dict_disabled(self):
        self.mock_dict_apps["configured"].append({"tags": "disabled", "enabled": False})
        ret_tag_list = t.get_tags_from_apps(self.mock_dict_apps)
        self.assertNotIn("disabled", ret_tag_list)

    def test_get_tags_from_apps_object_dont_show(self):
        self.mock_object_apps["configured"].append(
            mock.MagicMock(tags="disabled", show_in_apps_library=False)
        )
        ret_tag_list = t.get_tags_from_apps(self.mock_object_apps)
        self.assertNotIn("disabled", ret_tag_list)

    def test_get_tags_from_apps_dict_dont_show(self):
        self.mock_dict_apps["configured"].append(
            {"tags": "disabled", "show_in_apps_library": False}
        )
        ret_tag_list = t.get_tags_from_apps(self.mock_dict_apps)
        self.assertNotIn("disabled", ret_tag_list)

    def test_url(self):
        app = {"package": "test"}
        controller_name = "controller"
        ret = t.url(app, controller_name)
        self.assertEqual(ret, f"{app['package']}:{controller_name}")

    def test_public(self):
        app = {"package": "test"}
        static_path = "path/to/static"
        ret = t.public(app, static_path)
        self.assertEqual(ret, f"{app['package']}/{static_path}")
