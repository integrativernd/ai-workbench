from django.test import TestCase
from django.conf import settings
import os
import json

# Import the function we want to test
from tools.browse import get_web_page_content  # Adjust the import path as needed

RECORD_FIXTURES = False

class WebScraperTestCase(TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.join(settings.BASE_DIR, 'tools', 'tests', 'fixtures')
        os.makedirs(self.fixtures_dir, exist_ok=True)

    def get_or_record_web_content(self, url, fixture_name):
        fixture_path = os.path.join(self.fixtures_dir, f"{fixture_name}.json")

        if RECORD_FIXTURES:
            # Call the actual function
            content = get_web_page_content(url)
            # Save the content to a fixture file
            with open(fixture_path, 'w') as f:
                json.dump({'content': content}, f)
            return content
        else:
            if os.path.exists(fixture_path):
                with open(fixture_path, 'r') as f:
                    return json.load(f)['content']
            else:
                raise FileNotFoundError(f"Fixture {fixture_path} not found. Run tests with RECORD_FIXTURES=true to generate it.")

    def test_get_web_page_content(self):
        url = "https://example.com"
        fixture_name = "example_com_content"

        # Get or record the content
        content = self.get_or_record_web_content(url, fixture_name)

        # Basic assertion to check if content is not empty
        self.assertIn('Example Domain', content)
