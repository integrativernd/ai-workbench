import os
from django.test import TestCase
from llm.anthropic_integration import get_basic_message
import json
from config.settings import BASE_DIR
import pickle

search_file_path = 'llm/tests/fixtures/serper_result.json'
with open(os.path.join(BASE_DIR, search_file_path), 'r') as file:
    search_results_fixture = json.load(file)

RECORD_FIXTURES = False

class AnthropicIntegrationTest(TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.join(BASE_DIR, 'llm/tests/fixtures')
        os.makedirs(self.fixtures_dir, exist_ok=True)

    def tearDown(self):
        pass

    def get_or_record_basic_message(self, system_prompt, messages, fixture_name):
        fixture_path = os.path.join(self.fixtures_dir, f"{fixture_name}.pickle")

        if RECORD_FIXTURES:
            message = get_basic_message(system_prompt, messages)
            with open(fixture_path, 'wb') as f:
                pickle.dump(message, f)
            return message
        else:
            print('Using fixture')
            if os.path.exists(fixture_path):
                with open(fixture_path, 'rb') as f:
                    return pickle.load(f)
            else:
                raise FileNotFoundError(f"Fixture {fixture_path} not found. Run tests with RECORD_FIXTURES=true to generate it.")

    def test_basic_message(self):
        message = self.get_or_record_basic_message(
            "If you receive ping respond with only Pong and nothing else",
            [
                {
                    "role": "user",
                    "content": "Ping",
                }
            ],
            "basic_message_test"
        )
        self.assertEqual(message.content[0].text, "Pong")

    def test_performance(self):
        message = self.get_or_record_basic_message(
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
                    SEARCH JSON: {search_results_fixture}
                    """,
                }
            ],
            "performance_test"
        )
        self.assertEqual(message.content[0].text, "Waldo")