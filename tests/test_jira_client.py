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

        mock_jira_instance.project_statuses.return_value = [
            MagicMock(id='1', name='To Do'),
            MagicMock(id='3', name='In Progress')
        ]

        mock_config = MagicMock()
        mock_config.server = 'http://test.jira.com'
        mock_config.username = 'user'
        mock_config.api_token = 'token'

        client = JiraClient(mock_config)

        # Act
        statuses = client.fetch_project_statuses('Test Project')

        # Assert
        self.assertEqual(len(statuses), 2)
        mock_jira_instance.project.assert_called_once_with('Test Project')
        mock_jira_instance.project_statuses.assert_called_once_with(mock_project)


if __name__ == '__main__':
    unittest.main()
