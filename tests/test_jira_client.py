import unittest
from unittest.mock import MagicMock, patch

from src.display_jira_tickets.jira_client import JiraClient


class TestJiraClient(unittest.TestCase):
    @patch('src.display_jira_tickets.jira_client.JIRA')
    def test_fetch_project_statuses(self, mock_jira_class):
        # Arrange
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        mock_project = MagicMock()
        mock_project.key = 'TEST'
        mock_jira_instance.project.return_value = mock_project

        mock_jira_instance.statuses.return_value = [
            MagicMock(id='1', name='To Do'),
            MagicMock(id='3', name='In Progress')
        ]

        mock_config = MagicMock()
        mock_config.server = 'http://test.jira.com'
        mock_config.username = 'user'
        mock_config.api_token = 'token'

        client = JiraClient(mock_config)

        # Act
        statuses = client.fetch_jira_statuses()

        # Assert
        self.assertEqual(len(statuses), 2)
        mock_jira_instance.statuses.assert_called_once()

    @patch('src.display_jira_tickets.jira_client.JIRA')
    def test_fetch_issues_optimized_fields(self, mock_jira_class):
        # Arrange
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        # Mock empty response
        mock_jira_instance.search_issues.return_value = []

        mock_config = MagicMock()
        mock_config.server = 'http://test.jira.com'
        mock_config.username = 'user'
        mock_config.api_token = 'token'
        mock_config.jql_filter = 'project=TEST'
        mock_config.status_mapping = {}

        client = JiraClient(mock_config)

        # Act
        client.fetch_issues()

        # Assert
        args, kwargs = mock_jira_instance.search_issues.call_args
        self.assertIn('fields', kwargs)
        self.assertEqual(kwargs['fields'], "key,summary,status,assignee,issuetype,updated")


if __name__ == '__main__':
    unittest.main()
