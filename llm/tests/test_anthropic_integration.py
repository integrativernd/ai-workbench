import os
from django.test import TestCase
from llm.anthropic_integration import get_message, get_basic_message
import json
from config.settings import BASE_DIR, SYSTEM_PROMPT
from tools.config import TOOL_DEFINITIONS
import pickle

search_file_path = 'llm/tests/fixtures/serper_result.json'
with open(os.path.join(BASE_DIR, search_file_path), 'r') as file:
    search_results_fixture = json.load(file)

RECORD_FIXTURES = False
USE_FIXTURES = True

class AnthropicIntegrationTest(TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.join(BASE_DIR, 'llm/tests/fixtures')
        os.makedirs(self.fixtures_dir, exist_ok=True)

    def tearDown(self):
        pass

    def get_or_record_basic_message(self, system_prompt, messages, fixture_name, record_fixtures=RECORD_FIXTURES):
        fixture_path = os.path.join(self.fixtures_dir, f"{fixture_name}.pickle")

        if record_fixtures:
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

    def get_or_record_tool_message(self, system_prompt, messages, fixture_name, record_fixtures=RECORD_FIXTURES):
        fixture_path = os.path.join(self.fixtures_dir, f"{fixture_name}.pickle")

        if record_fixtures:
            message = get_message(system_prompt, TOOL_DEFINITIONS, messages)
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
            "basic_message_test",
            record_fixtures=False,
        )
        self.assertEqual(message.content[0].text, "Pong")

    # def test_performance(self):
    #     message = self.get_or_record_basic_message(
    #         """
    #             Summarize the provided JSON search result data to answer the user's question in a single word.
    #             Return a strict single word response for the purposes of being used in a test case.
    #             Question: What was John Adam's secret name?
    #             Answer: Lando
    #         """,
    #         [
    #             {
    #                 "role": "user",
    #                 "content": f"""
    #                 Question: What was George Washington's secret name?
    #                 SEARCH JSON: {search_results_fixture}
    #                 """,
    #             }
    #         ],
    #         "performance_test",
    #         record_fixtures=False,
    #     )
    #     self.assertEqual(message.content[0].text, "Waldo")

    # def test_get_time_tool_message(self):
    #     message = self.get_or_record_tool_message(
    #         SYSTEM_PROMPT,
    #         [
    #             {
    #                 "role": "user",
    #                 "content": "Please help me plan a business based on your capabilities",
    #             }
    #         ],
    #         "simple_tool_message",
    #         record_fixtures=True,
    #     )

    #     # print(message.content[0].text)
    #     self.assertEqual(len(message.content), 2)
    #     self.assertEqual(message.content[1].name, 'conduct_swot_analysis')
    
    # def test_get_time_tool_message(self):
    #     message = self.get_or_record_tool_message(
    #         SYSTEM_PROMPT,
    #         [
    #             {
    #                 "role": "user",
    #                 "content": "What time is it?",
    #             }
    #         ],
    #         "simple_tool_message",
    #         record_fixtures=True,
    #     )
    #     self.assertEqual(message.content[0].name, 'get_current_time')

    # def test_get_runtime_environment_tool_message(self):
    #     message = self.get_or_record_tool_message(
    #         SYSTEM_PROMPT,
    #         [
    #             {
    #                 "role": "user",
    #                 "content": "What runtime environment are you in?",
    #             }
    #         ],
    #         "runtime_env_query",
    #         record_fixtures=False,
    #     )
    #     self.assertEqual(message.content[0].name, 'get_runtime_environment')

    # def test_multiple_tool_calls(self):
    #     message = self.get_or_record_tool_message(
    #         SYSTEM_PROMPT,
    #         [
    #             {
    #                 "role": "user",
    #                 "content": "What time is it? What runtime environment are you in?",
    #             }
    #         ],
    #         "multiple_tool_calls",
    #         record_fixtures=False,
    #     )
    #     self.assertEqual(len(message.content), 2)
    #     self.assertEqual(message.content[0].name, 'get_time')
    #     self.assertEqual(message.content[1].name, 'get_runtime_environment')
    
    # def test_read_systems_architecture(self):
    #     message = self.get_or_record_tool_message(
    #         SYSTEM_PROMPT,
    #         [
    #             {
    #                 "role": "user",
    #                 "content": "Tell me about your technical systems.",
    #             }
    #         ],
    #         "read_systems_architecture",
    #         record_fixtures=False,
    #     )
    #     self.assertEqual(message.content[0].name, 'read_system_architecture')
    
    # def test_read_systems_architecture_and_update_google_document(self):
    #     message = self.get_or_record_tool_message(
    #         SYSTEM_PROMPT,
    #         [
    #             {
    #                 "role": "user",
    #                 "content": "Update the google document with details about your implementation.",
    #             }
    #         ],
    #         "read_systems_architecture_and_update_google_document",
    #         record_fixtures=False,
    #     )

    #     self.assertEqual(len(message.content), 2)
    #     print(message.content[0].input)
    #     print(message.content[1].input)
    #     self.assertEqual(message.content[0].name, 'read_system_architecture')
    #     self.assertEqual(message.content[1].name, 'update_google_document')
