import configparser
from .jira_client import JiraClient


class ConfigFileInitializer:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser(comment_prefixes=('#', ';'), allow_no_value=True)
        self.config.read(self.config_file_path)

    def initialize_status_mapping(self, jira_client: JiraClient, project_name: str):
        statuses = jira_client.fetch_project_statuses(project_name)

        if not self.config.has_section('StatusMapping'):
            self.config.add_section('StatusMapping')

        for status in statuses:
            if not self.config.has_option('StatusMapping', status.id):
                self.config.set('StatusMapping', status.id, f'TO_DO ; {status.name}')

        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)
