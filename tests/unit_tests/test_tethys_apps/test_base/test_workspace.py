import unittest
import tethys_apps.base.workspace as base_workspace
import os
import shutil


class TestUrlMap(unittest.TestCase):
    def setUp(self):
        self.root = os.path.abspath(os.path.dirname(__file__))
        self.test_root = os.path.join(self.root, 'test_workspace')
        self.test_root_a = os.path.join(self.test_root, 'test_workspace_a')
        self.test_root2 = os.path.join(self.root, 'test_workspace2')

    def tearDown(self):
        if os.path.isdir(self.test_root):
            shutil.rmtree(self.test_root)
        if os.path.isdir(self.test_root2):
            shutil.rmtree(self.test_root2)

    def test_TethysWorkspace(self):
        # Test Create new workspace folder test_workspace
        result = base_workspace.TethysWorkspace(path=self.test_root)
        workspace = '<TethysWorkspace path="{0}">'.format(self.test_root)

        # Create new folder inside test_workspace
        base_workspace.TethysWorkspace(path=self.test_root_a)

        # Create new folder test_workspace2
        base_workspace.TethysWorkspace(path=self.test_root2)

        self.assertEqual(result.__repr__(), workspace)
        self.assertEqual(result.path, self.test_root)

        # Create Files
        file_list = ['test1.txt', 'test2.txt']
        for file_name in file_list:
            # Create file
            open(os.path.join(self.test_root, file_name), 'a').close()

        # Test files with full path
        result = base_workspace.TethysWorkspace(path=self.test_root).files(full_path=True)
        for file_name in file_list:
            self.assertIn(os.path.join(self.test_root, file_name), result)

        # Test files without full path
        result = base_workspace.TethysWorkspace(path=self.test_root).files()
        for file_name in file_list:
            self.assertIn(file_name, result)

        # Test Directories with full path
        result = base_workspace.TethysWorkspace(path=self.root).directories(full_path=True)
        self.assertIn(self.test_root, result)
        self.assertIn(self.test_root2, result)

        # Test Directories without full path
        result = base_workspace.TethysWorkspace(path=self.root).directories()
        self.assertIn('test_workspace', result)
        self.assertIn('test_workspace2', result)
        self.assertNotIn(self.test_root, result)
        self.assertNotIn(self.test_root2, result)

        # Test Remove file
        base_workspace.TethysWorkspace(path=self.test_root).remove('test2.txt')

        # Verify that the file has been remove
        self.assertFalse(os.path.isfile(os.path.join(self.test_root, 'test2.txt')))

        # Test Remove Directory
        base_workspace.TethysWorkspace(path=self.root).remove(self.test_root2)

        # Verify that the Directory has been remove
        self.assertFalse(os.path.isdir(self.test_root2))

        # Test Clear
        base_workspace.TethysWorkspace(path=self.test_root).clear()

        # Verify that the Directory has been remove
        self.assertFalse(os.path.isdir(self.test_root_a))

        # Verify that the File has been remove
        self.assertFalse(os.path.isfile(os.path.join(self.test_root, 'test1.txt')))

        # Test don't allow overwriting the path property
        workspace = base_workspace.TethysWorkspace(path=self.test_root)
        workspace.path = 'foo'
        self.assertEqual(self.test_root, workspace.path)
