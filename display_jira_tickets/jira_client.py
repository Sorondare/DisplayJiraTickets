import logging
from jira import JIRA
from .config import JiraConfig
from .issue import Issue, map_status_from_jira_status_name, map_action_from_status


class JiraClient:
    def __init__(self, config: JiraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.jira = self._connect()

    def _connect(self) -> JIRA:
        self.logger.info("Connecting to Jira server at %s", self.config.server)
        try:
            jira_options = {'server': self.config.server}
            jira = JIRA(
                options=jira_options,
                basic_auth=(self.config.username, self.config.api_token)
            )
            self.logger.info("Successfully connected to Jira.")
            return jira
        except Exception as e:
            self.logger.error("Failed to connect to Jira: %s", e)
            raise

    def fetch_issues(self) -> list[Issue]:
        self.logger.info("Fetching issues using JQL: %s", self.config.jql_filter)
        try:
            jira_issues = self.jira.search_issues(self.config.jql_filter, maxResults=1000)
            jira_issues.sort(key=lambda i: i.fields.updated)

            issues = []
            for jira_issue in jira_issues:
                issue_type = jira_issue.fields.issuetype.name
                status = map_status_from_jira_status_name(jira_issue.fields.status.name, self.config.language)
                action = map_action_from_status(issue_type, status)

                issue = Issue(
                    issue_key=jira_issue.key,
                    issue_type=issue_type,
                    summary=jira_issue.fields.summary,
                    status=status,
                    assignee=jira_issue.fields.assignee.displayName if jira_issue.fields.assignee else None,
                    action=action,
                )
                self.logger.debug("Extracted issue: %s", issue)
                issues.append(issue)

            self.logger.info("Found %d issues.", len(issues))
            return issues
        except Exception as e:
            self.logger.error("Failed to fetch issues from Jira: %s", e)
            raise
