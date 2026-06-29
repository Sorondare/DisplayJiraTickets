import configparser
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from issue import Status

if TYPE_CHECKING:
    from jira_client import JiraClient


@dataclass
class JiraConfig:
    server: str
    username: str
    api_token: str
    project: str
    status_mapping: dict[str, Status]
    static_ticket_filtering: set[Status]


@dataclass
class ReportConfig:
    username: str
    introduction: str


@dataclass
class LoggingConfig:
    level: int


class Config:
    def __init__(self, file_path: Path):
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found at {file_path}")

        config = configparser.ConfigParser()
        config.read(file_path)

        self.jira_config = self._get_jira_config(config)
        self.report_config = self._get_report_config(config)
        self.logging_config = self._get_logging_config(config)

    def _get_jira_config(self, config: configparser.ConfigParser) -> JiraConfig:
        status_mapping = self._get_status_mapping(config)
        static_ticket_filtering_str = config.get('Jira', 'static_ticket_filtering', fallback='TO_DO, DONE')
        static_ticket_filtering = {Status[s.strip().upper()] for s in static_ticket_filtering_str.split(',') if s.strip()}

        return JiraConfig(
            server=config.get('Jira', 'server'),
            username=config.get('Jira', 'username'),
            api_token=config.get('Jira', 'api_token'),
            project=config.get('Jira', 'project_key'),
            status_mapping=status_mapping,
            static_ticket_filtering=static_ticket_filtering,
        )

    @staticmethod
    def _get_status_mapping(config: configparser.ConfigParser) -> dict[str, Status]:
        status_mapping = {}
        if config.has_section('StatusMapping'):
            for key, value in config.items('StatusMapping'):
                try:
                    status_mapping[key] = Status[value.upper()]
                except KeyError:
                    raise ValueError(f"Invalid status value '{value}' in StatusMapping."
                                     f"Available statuses are: {[s.name for s in Status]}")
        return status_mapping

    @staticmethod
    def _get_report_config(config: configparser.ConfigParser) -> ReportConfig:
        return ReportConfig(
            username=config.get('Report', 'username'),
            introduction=config.get('Report', 'introduction', fallback=''),
        )

    @staticmethod
    def _get_logging_config(config: configparser.ConfigParser) -> LoggingConfig:
        level_str = config.get('Logging', 'level', fallback='INFO').upper()
        level = getattr(logging, level_str, logging.INFO)
        return LoggingConfig(level=level)


class ConfigFileInitializer:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser(comment_prefixes=('#', ';'), allow_no_value=True)
        self.config.read(self.config_file_path)

    def initialize_status_mapping(self, jira_client: 'JiraClient', project_name: str):
        statuses = jira_client.fetch_jira_statuses()

        if not self.config.has_section('StatusMapping'):
            self.config.add_section('StatusMapping')

        for status in statuses:
            if not self.config.has_option('StatusMapping', status.id):
                self.config.set('StatusMapping', f'# {status.name}')
                self.config.set('StatusMapping', status.id, Status.TO_DO)

        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)
