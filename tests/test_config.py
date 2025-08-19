import unittest
import logging
import configparser
from src.display_jira_tickets.config import Config

class TestConfig(unittest.TestCase):
    def test_config_loading(self):
        config_string = """
[Jira]
server = https://jira.example.com
username = testuser
api_token = testtoken
language = fr
jql_filter = project = 'TEST'

[Report]
username = reportuser
introduction = Test Report

[Logging]
level = DEBUG
"""
        # Create a dummy config file in memory
        config = configparser.ConfigParser()
        config.read_string(config_string)

        # We need to mock the open call to avoid file system access
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=config_string)):
            with unittest.mock.patch('configparser.ConfigParser.read', lambda self, path: self.read_string(config_string)):
                 config_obj = Config('dummy_path')


        # Test Jira config
        self.assertEqual(config_obj.jira_config.server, "https://jira.example.com")
        self.assertEqual(config_obj.jira_config.username, "testuser")
        self.assertEqual(config_obj.jira_config.api_token, "testtoken")
        self.assertEqual(config_obj.jira_config.language, "fr")
        self.assertEqual(config_obj.jira_config.jql_filter, "project = 'TEST'")

        # Test Report config
        self.assertEqual(config_obj.report_config.username, "reportuser")
        self.assertEqual(config_obj.report_config.introduction, "Test Report")

        # Test Logging config
        self.assertEqual(config_obj.logging_config.level, logging.DEBUG)


if __name__ == '__main__':
    unittest.main()
