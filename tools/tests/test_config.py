import os
import json
import pickle
from django.test import TestCase
from unittest.mock import patch
import requests

from tools.config import TOOL_MAP

RECORD_FIXTURES = False

class ToolConfigTest(TestCase):
    # def setUp(self):
        # self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        # os.makedirs(self.fixtures_dir, exist_ok=True)
        # self.api_key = os.environ.get('SERPER_API_KEY')
        # if not self.api_key:
        #     raise EnvironmentError("SERPER_API_KEY is not set in the environment.")

    def test_tool_map(self):
        self.assertTrue(TOOL_MAP)
        self.assertTrue(isinstance(TOOL_MAP, dict))
        self.assertEqual(list(TOOL_MAP.keys()), [
            'google_search',
            'review_web_page',
        ])
        # Assert the search execute function is defined and
        # is a callable function
        self.assertTrue(TOOL_MAP['google_search'].get('execute'))
        self.assertTrue(callable(TOOL_MAP['google_search']['execute']))