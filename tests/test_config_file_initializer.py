import unittest
from unittest.mock import MagicMock, patch, mock_open
from src.display_jira_tickets.config_file_initializer import ConfigFileInitializer
import configparser

class TestConfigFileInitializer(unittest.TestCase):
    @patch('src.display_jira_tickets.config_file_initializer.JiraClient')
    def test_initialize_status_mapping(self, mock_jira_client_class):
        # Arrange
        mock_jira_client = mock_jira_client_class.return_value

        status1 = MagicMock()
        status1.id = '1'
        status1.name = 'To Do'

        status2 = MagicMock()
        status2.id = '3'
        status2.name = 'In Progress'

        mock_jira_client.fetch_jira_statuses.return_value = [status1, status2]

        with patch('builtins.open', mock_open(read_data='')) as mock_file:
            initializer = ConfigFileInitializer('dummy_path')

            # Act
            initializer.initialize_status_mapping(mock_jira_client, 'Test Project')

            # Assert
            mock_file.assert_called_with('dummy_path', 'w')

            written_config = "".join(call.args[0] for call in mock_file().write.call_args_list)

            config = configparser.ConfigParser()
            config.read_string(written_config)

            self.assertTrue(config.has_section('StatusMapping'))
            self.assertEqual(config.get('StatusMapping', '1').upper(), 'TO_DO')
            self.assertEqual(config.get('StatusMapping', '3').upper(), 'TO_DO')

if __name__ == '__main__':
    unittest.main()
