import configparser
import logging
from dataclasses import dataclass


@dataclass
class JiraConfig:
    server: str
    username: str
    api_token: str
    language: str
    jql_filter: str


@dataclass
class ReportConfig:
    username: str
    introduction: str


@dataclass
class LoggingConfig:
    level: int


class Config:
    def __init__(self, file_path: str):
        config = configparser.ConfigParser()
        config.read(file_path)

        self.jira_config = self._get_jira_config(config)
        self.report_config = self._get_report_config(config)
        self.logging_config = self._get_logging_config(config)

    @staticmethod
    def _get_jira_config(config: configparser.ConfigParser) -> JiraConfig:
        return JiraConfig(
            server=config.get('Jira', 'server'),
            username=config.get('Jira', 'username'),
            api_token=config.get('Jira', 'api_token'),
            language=config.get('Jira', 'language', fallback='en'),
            jql_filter=config.get(
                'Jira',
                'jql_filter',
                fallback='project = "Scrum Beoogo" AND (status CHANGED BY currentUser() AFTER startOfDay() OR assignee = currentUser()) AND sprint in openSprints()'
            )
        )

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
