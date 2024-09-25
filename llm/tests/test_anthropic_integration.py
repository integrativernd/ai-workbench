import os
import json
from unittest.mock import patch
from django.test import TestCase
from llm.anthropic_integration import get_basic_message
from config.settings import BASE_DIR

def load_fixture(filename):
    path = os.path.join(BASE_DIR, 'llm', 'tests', 'fixtures', filename)
    if os.path.exists(path):
        with open(path, 'r') as file:
            return json.load(file)
    return None

def save_fixture(filename, data):
    path = os.path.join(BASE_DIR, 'llm', 'tests', 'fixtures', filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
        json.dump(data, file, indent=2)

class AnthropicIntegrationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record_fixtures = os.getenv('RECORD_FIXTURES', '').lower() == 'true'
        cls.search_results_fixture = load_fixture('serper_result.json')

    def setUp(self):
        self.patcher = patch('llm.anthropic_integration.anthropic.Anthropic')
        self.mock_anthropic = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def run_test_with_fixture(self, test_name, prompt, messages, expected_response):
        fixture_filename = f'{test_name}_fixture.json'
        fixture = load_fixture(fixture_filename)

        if self.record_fixtures or fixture is None:
            # Make actual API call
            message = get_basic_message(prompt, messages)
            response = message.content[0].text
            save_fixture(fixture_filename, {'response': response})
        else:
            # Use fixture
            response = fixture['response']
            self.mock_anthropic.return_value.messages.create.return_value.content[0].text = response

        # Run assertion
        self.assertEqual(response, expected_response)

    def test_basic_message(self):
        self.run_test_with_fixture(
            'test_basic_message',
            "If you receive ping respond with only Pong and nothing else",
            [{"role": "user", "content": "Ping"}],
            "Pong"
        )

    def test_performance(self):
        self.run_test_with_fixture(
            'test_performance',
            """
            Summarize the provided JSON search result data to answer the user's question in a single word.
            Return a strict single word response for the purposes of being used in a test case.
            Question: What was John Adam's secret name?
            Answer: Lando
            """,
            [
                {
                    "role": "user",
                    "content": f"""
                    Question: What was George Washington's secret name?
                    SEARCH JSON: {self.search_results_fixture}
                    """,
                }
            ],
            "Waldo"
        )