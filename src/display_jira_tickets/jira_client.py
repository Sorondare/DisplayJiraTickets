import logging
from jira import JIRA
from .config import JiraConfig
from .issue import Issue, map_status, map_action_from_status


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
        jql_filter = f"{self.config.jql_filter} ORDER BY updated ASC"
        self.logger.info("Fetching issues using JQL: %s", jql_filter)
        try:
            jira_issues = self.jira.search_issues(
                jql_filter,
                maxResults=1000,
                fields="key,summary,status,assignee,issuetype"
            )

            issues = []
            status_cache = {}
            action_cache = {}

            for jira_issue in jira_issues:
                issue_type = jira_issue.fields.issuetype.name
                jira_status = jira_issue.fields.status
                status_id = jira_status.id

                # Cache status mapping
                if status_id in status_cache:
                    status = status_cache[status_id]
                else:
                    status = map_status(jira_status, self.config.status_mapping)
                    status_cache[status_id] = status

                # Cache action mapping
                action_key = (issue_type, status)
                if action_key in action_cache:
                    action = action_cache[action_key]
                else:
                    action = map_action_from_status(issue_type, status)
                    action_cache[action_key] = action

                issues.append(Issue(
                    issue_key=jira_issue.key,
                    issue_type=issue_type,
                    summary=jira_issue.fields.summary,
                    status=status,
                    assignee=jira_issue.fields.assignee.displayName if jira_issue.fields.assignee else None,
                    action=action,
                ))

            for issue in issues:
                self.logger.debug("Extracted issue: %s", issue)

            self.logger.info("Found %d issues.", len(issues))
            return issues
        except Exception as e:
            self.logger.error("Failed to fetch issues from Jira: %s", e)
            raise

    def fetch_jira_statuses(self) -> list:
        self.logger.info("Fetching statuses from Jira server")
        try:
            return self.jira.statuses()
        except Exception as e:
            self.logger.error("Failed to fetch Jira Server issue statuses: %s", e)
            raise
