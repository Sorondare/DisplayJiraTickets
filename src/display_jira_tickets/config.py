import configparser
import logging
from dataclasses import dataclass


from .issue import Status


@dataclass
class JiraConfig:
    server: str
    username: str
    api_token: str
    jql_filter: str
    status_mapping: dict[str, Status]


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

    def _get_jira_config(self, config: configparser.ConfigParser) -> JiraConfig:
        status_mapping = self._get_status_mapping(config)
        return JiraConfig(
            server=config.get('Jira', 'server'),
            username=config.get('Jira', 'username'),
            api_token=config.get('Jira', 'api_token'),
            jql_filter=config.get('Jira', 'jql_filter'),
            status_mapping=status_mapping,
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
