import unittest
import logging
from src.display_jira_tickets.config import Config
from src.display_jira_tickets.issue import Status

class TestConfig(unittest.TestCase):
    def _create_config_from_string(self, config_string: str) -> Config:
        # Helper method to create a Config object from a string by mocking file access.
        # configparser.read() uses open() internally, so we can mock that.
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=config_string)):
            return Config('dummy_path')

    def test_config_loading_basic(self):
        config_string = """
[Jira]
server = https://jira.example.com
username = testuser
api_token = testtoken
jql_filter = project = 'TEST'
project_key = TEST_PROJECT

[Report]
username = reportuser
introduction = Test Report

[Logging]
level = DEBUG
"""
        config_obj = self._create_config_from_string(config_string)

        # Test Jira config
        self.assertEqual(config_obj.jira_config.server, "https://jira.example.com")
        self.assertEqual(config_obj.jira_config.username, "testuser")
        self.assertEqual(config_obj.jira_config.api_token, "testtoken")
        self.assertEqual(config_obj.jira_config.jql_filter, "project = 'TEST'")
        self.assertEqual(config_obj.jira_config.project, "TEST_PROJECT")
        self.assertEqual(config_obj.jira_config.status_mapping, {}) # No mapping section

        # Test Report config
        self.assertEqual(config_obj.report_config.username, "reportuser")
        self.assertEqual(config_obj.report_config.introduction, "Test Report")

        # Test Logging config
        self.assertEqual(config_obj.logging_config.level, logging.DEBUG)

    def test_status_mapping_loading(self):
        config_string = """
[Jira]
server = a
username = b
api_token = c
jql_filter = d
project_key = e

[Report]
username = x
introduction = y

[Logging]
level = INFO

[StatusMapping]
Backlog = TO_DO
In Progress = IN_PROGRESS
1001 = DONE
"""
        config_obj = self._create_config_from_string(config_string)
        expected_mapping = {
            "backlog": Status.TO_DO,
            "in progress": Status.IN_PROGRESS,
            "1001": Status.DONE
        }
        self.assertEqual(config_obj.jira_config.status_mapping, expected_mapping)

    def test_invalid_status_mapping_value(self):
        config_string = """
[Jira]
server = a
username = b
api_token = c
jql_filter = d
project_key = e

[Report]
username = x
introduction = y

[Logging]
level = INFO

[StatusMapping]
Backlog = INVALID_STATUS
"""
        with self.assertRaises(ValueError) as cm:
            self._create_config_from_string(config_string)
        self.assertIn("Invalid status value 'INVALID_STATUS'", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
