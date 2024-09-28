import os
import json
import pickle
from django.test import TestCase
from unittest.mock import patch
import requests

# Import the function we want to test
from tools.search import get_search_data  # Adjust the import path as needed

RECORD_FIXTURES = False

class SearchToolTestCase(TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        os.makedirs(self.fixtures_dir, exist_ok=True)
        self.api_key = os.environ.get('SERPER_API_KEY')
        if not self.api_key:
            raise EnvironmentError("SERPER_API_KEY is not set in the environment.")

    def get_or_record_search_data(self, query, fixture_name):
        fixture_path = os.path.join(self.fixtures_dir, f"{fixture_name}.pickle")

        if RECORD_FIXTURES:
            response = get_search_data(query)
            with open(fixture_path, 'wb') as f:
                pickle.dump(response, f)
            return response
        else:
            if os.path.exists(fixture_path):
                with open(fixture_path, 'rb') as f:
                    return pickle.load(f)
            else:
                raise FileNotFoundError(f"Fixture {fixture_path} not found. Run tests with RECORD_FIXTURES=true to generate it.")

    def test_get_search_data(self):
        """
        This test calls get_search_data function with a query and checks the response data.
        """

        query = "What is the capital of France?"
        result = self.get_or_record_search_data(query, "capital_of_france")

        # Parse the result to check its structure
        parsed_result = json.loads(result)
        
        self.assertIn('organic', parsed_result)
        self.assertTrue(len(parsed_result['organic']) > 0)
        self.assertIn('title', parsed_result['organic'][0])
        self.assertIn('link', parsed_result['organic'][0])
        self.assertIn('snippet', parsed_result['organic'][0])

    @patch.dict(os.environ, {'SERPER_API_KEY': ''})
    def test_get_search_data_missing_api_key(self):
        # query = "What is the capital of France?"
        
        with self.assertRaises(EnvironmentError):
            SearchToolTestCase().setUp()  # This will raise the EnvironmentError

    def test_get_search_data_api_error(self):
        query = "What is the capital of France?"

        # Patch the requests.request to simulate an API error
        with patch('tools.search.requests.request') as mock_request:
            mock_request.side_effect = requests.RequestException("API Error")
            with self.assertRaises(requests.RequestException):
                get_search_data(query)