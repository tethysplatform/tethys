import unittest
from tethys_apps.exceptions import (
    TethysAppSettingDoesNotExist,
    TethysAppSettingNotAssigned,
    PersistentStoreDoesNotExist,
    PersistentStoreExists,
    PersistentStoreInitializerError,
    PersistentStorePermissionError,
)


def raise_exception(exc, *args, **kwargs):
    raise exc(*args, **kwargs)


class TestExceptions(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_tethys_app_setting_does_not_exist(self):
        self.assertRaises(
            TethysAppSettingDoesNotExist,
            raise_exception,
            TethysAppSettingDoesNotExist,
            "setting-type",
            "setting-name",
            "app-name",
        )
        exc = TethysAppSettingDoesNotExist("setting-type", "setting-name", "app-name")
        self.assertIn("setting-type", str(exc))
        self.assertIn("setting-name", str(exc))
        self.assertIn("app-name", str(exc))
        self.assertIn("does not exist", str(exc))

    def test_tethys_app_settign_not_assigned(self):
        self.assertRaises(
            TethysAppSettingNotAssigned, raise_exception, TethysAppSettingNotAssigned
        )

    def test_persistent_store_does_not_exist(self):
        self.assertRaises(
            PersistentStoreDoesNotExist, raise_exception, PersistentStoreDoesNotExist
        )

    def test_persistent_store_exists(self):
        self.assertRaises(PersistentStoreExists, raise_exception, PersistentStoreExists)

    def test_persistent_store_permission_error(self):
        self.assertRaises(
            PersistentStorePermissionError,
            raise_exception,
            PersistentStorePermissionError,
        )

    def test_persistent_store_initializer_error(self):
        self.assertRaises(
            PersistentStoreInitializerError,
            raise_exception,
            PersistentStoreInitializerError,
        )
