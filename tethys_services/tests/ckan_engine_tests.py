import os
import random
import string
import unittest

from ..engines import CkanDatasetEngine

try:
    from .test_config import TEST_CKAN_DATASET_SERVICE

except ImportError:
    print('ERROR: To perform tests, you must create a file in the "tests" package called "test_config.py". In this file'
          'provide a dictionary called "TEST_CKAN_DATASET_SERVICE" with keys "API_ENDPOINT" and "APIKEY".')
    exit(1)


def random_string_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


class TestCkanDatasetEngine(unittest.TestCase):

    def setUp(self):
        # Create Test Engine
        self.engine = CkanDatasetEngine(endpoint=TEST_CKAN_DATASET_SERVICE['ENDPOINT'],
                                        apikey=TEST_CKAN_DATASET_SERVICE['APIKEY'])

        # Create Test Dataset
        self.test_dataset_name = random_string_generator(10)
        dataset_result = self.engine.create_dataset(name=self.test_dataset_name, version='1.0')
        self.test_dataset = dataset_result['result']

        # Create Test Resource
        self.test_resource_name = random_string_generator(10)
        self.test_resource_url = 'http://home.byu.edu'
        resource_result = self.engine.create_resource(self.test_dataset_name, url=self.test_resource_url, format='zip')
        self.test_resource = resource_result['result']

    def tearDown(self):
        # Delete test resource and dataset
        self.engine.delete_resource(resource_id=self.test_resource['id'])
        self.engine.delete_dataset(dataset_id=self.test_dataset_name)

    def test_list_datasets_defaults(self):
        # Execute
        result = self.engine.list_datasets()

        # Verify Success
        self.assertTrue(result['success'])

    def test_list_datasets_with_resources(self):
        # Execute
        result = self.engine.list_datasets(with_resources=True)

        # Verify Success
        self.assertTrue(result['success'])

    def test_list_datasets_with_params(self):
        # Setup
        limit = 5
        number_all = len(self.engine.list_datasets()['result'])

        # Execute twice with offsets different
        result_page_1 = self.engine.list_datasets(limit=limit, offset=1)
        result_page_2 = self.engine.list_datasets(limit=limit, offset=2)

        # Verify success
        self.assertTrue(result_page_1['success'])
        self.assertTrue(result_page_2['success'])

        # Count the results
        page_1_count = len(result_page_1['result'])
        page_2_count = len(result_page_2['result'])

        # Verify count (should be less than or equal to limit)
        self.assertLessEqual(page_1_count, limit)
        self.assertLessEqual(page_2_count, limit)

        # If there are more than 5 datasets, the results should be different
        if number_all > 5:
            self.assertNotEqual(result_page_1, result_page_2)

    def test_search_resources(self):
        # Execute
        result = self.engine.search_resources(query={'format': 'zip'})

        # Verify Success
        self.assertTrue(result['success'])

        # Check search results if they exist
        search_results = result['result']['results']

        if len(search_results) > 1:
            for result in search_results:
                self.assertIn('zip', result['format'].lower())

    def test_search_datasets(self):
        # Execute
        result = self.engine.search_datasets(query={'version': '1.0'})

        # Verify Success
        self.assertTrue(result['success'])

        # Check search results if they exist
        search_results = result['result']['results']

        if len(search_results) > 1:
            for result in search_results:
                self.assertIn('version', result['1.0'].lower())

    def test_create_dataset(self):
        # Setup
        new_dataset_name = random_string_generator(10)

        # Execute
        result = self.engine.create_dataset(name=new_dataset_name)

        # Verify Success
        self.assertTrue(result['success'])

        # Should return the new one
        self.assertEqual(new_dataset_name, result['result']['name'])

        # Delete
        self.engine.delete_dataset(dataset_id=new_dataset_name)

    def test_create_resource_url(self):
        # Setup
        new_resource_name = random_string_generator(5)
        new_resource_url = 'http://home.byu.edu'

        # Execute
        result = self.engine.create_resource(dataset_id=self.test_dataset_name,
                                             url=new_resource_url,
                                             name=new_resource_name)

        # Verify Success
        self.assertTrue(result['success'])

        # Verify name and url
        self.assertEqual(new_resource_name, result['result']['name'])
        self.assertEqual(new_resource_url, result['result']['url'])

        # Delete
        self.engine.delete_resource(resource_id=result['result']['id'])

    def test_create_resource_file_upload(self):
        # Prepare
        file_to_upload = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'support', 'upload_test.txt')

        # Execute
        result = self.engine.create_resource(dataset_id=self.test_dataset_name, file=file_to_upload)

        # Verify Success
        self.assertTrue(result['success'], result)

        # Verify name and url_type (which should be upload if file upload)
        self.assertEqual(result['result']['name'], 'upload_test.txt')
        self.assertEqual(result['result']['url_type'], 'upload')

        # Delete
        self.engine.delete_resource(resource_id=result['result']['id'])

    def test_get_dataset(self):
        # Execute
        result = self.engine.get_dataset(dataset_id=self.test_dataset_name)

        # Verify Success
        self.assertTrue(result['success'])

        # Verify Name
        self.assertEqual(result['result']['name'], self.test_dataset_name)

    def test_get_resource(self):
        # Execute
        result = self.engine.get_resource(resource_id=self.test_resource['id'])

        # Verify Success
        self.assertTrue(result['success'])

        # Verify Properties
        self.assertEqual(result['result']['url'], self.test_resource_url)

    def test_update_dataset(self):
        # Setup
        test_version = '2.0'

        # Execute
        result = self.engine.update_dataset(dataset_id=self.test_dataset_name, version=test_version)

        # Verify Success
        self.assertTrue(result['success'])

        # Verify new version property
        self.assertEqual(result['result']['version'], test_version)

    def test_update_resource_property_change(self):
        # Setup
        new_format = 'web'

        # Execute
        result = self.engine.update_resource(resource_id=self.test_resource['id'], format=new_format)

        # Verify Success
        self.assertTrue(result['success'])

        # Verify new format
        self.assertEqual(result['result']['format'], new_format)

    def test_update_resource_url_change(self):
        # Setup
        new_url = 'http://www.utah.edu'

        # Execute
        result = self.engine.update_resource(resource_id=self.test_resource['id'], url=new_url)

        # Verify Success
        self.assertTrue(result['success'])

        # Verify New URL Property
        self.assertEqual(result['result']['url'], new_url)
        self.assertNotEqual(result['result']['url'], self.test_resource['url'])

    def test_update_resource_file_upload(self):
        # Setup
        file_to_upload = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'support', 'upload_test.txt')

        # Execute
        result = self.engine.update_resource(resource_id=self.test_resource['id'], file=file_to_upload)

        # Verify Success
        self.assertTrue(result['success'])

        # Verify Name (should be the same as the file uploaded by default)
        self.assertEqual(result['result']['name'], 'upload_test.txt')

        # URL should be different than original when file upload executes
        self.assertNotEqual(result['result']['url'], self.test_resource['url'])

    def test_delete_resource(self):
        # Execute
        result = self.engine.delete_resource(resource_id=self.test_resource['id'])

        # Verify Success
        self.assertTrue(result['success'])

        # Delete requests should return nothing
        self.assertEqual(result['result'], None)

    def test_delete_dataset(self):
        # Execute
        result = self.engine.delete_dataset(dataset_id=self.test_dataset_name)

        # Confirm Success
        self.assertTrue(result['success'])

        # Delete requests should return nothing
        self.assertEqual(result['result'], None)