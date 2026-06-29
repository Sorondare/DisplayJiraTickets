import logging
from jira import JIRA
from config import JiraConfig
from issue import Issue, map_status, map_action_from_status


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

    def fetch_issues(self, report_username: str) -> list[Issue]:
        jql_filter_updated = f'project = "{self.config.project}" AND updated >= startOfDay() ORDER BY updated ASC'
        jql_filter_assigned = f'project = "{self.config.project}" AND assignee = "{report_username}" AND resolution = Unresolved AND sprint in openSprints()'
        self.logger.info("Fetching updated issues using JQL: %s", jql_filter_updated)
        try:
            jira_issues_updated = self.jira.search_issues(
                jql_filter_updated,
                maxResults=1000,
                fields="key,summary,status,assignee,issuetype,comment",
                expand="changelog"
            )

            self.logger.info("Fetching assigned issues using JQL: %s", jql_filter_assigned)
            jira_issues_assigned = self.jira.search_issues(
                jql_filter_assigned,
                maxResults=1000,
                fields="key,summary,status,assignee,issuetype,comment",
                expand="changelog"
            )

            issues_dict = {}
            all_jira_issues = list(jira_issues_updated) + list(jira_issues_assigned)
            for jira_issue in all_jira_issues:
                if jira_issue.key in issues_dict:
                    continue

                issue_type = jira_issue.fields.issuetype.name
                current_status = map_status(jira_issue.fields.status, self.config.status_mapping)
                assignee = jira_issue.fields.assignee.displayName if jira_issue.fields.assignee else None

                issue_obj = Issue(
                    issue_key=jira_issue.key,
                    issue_type=issue_type,
                    summary=jira_issue.fields.summary,
                    status=current_status,
                    assignee=assignee,
                    daily_actions=[]
                )
                issue_obj.extract_daily_actions(jira_issue, report_username, self.config.status_mapping)
                issues_dict[issue_obj.issue_key] = issue_obj

            issues = list(issues_dict.values())

            for issue in issues:
                if not issue.daily_actions and issue.status not in self.config.static_ticket_filtering and issue.assignee == report_username:
                    # Tâche qui n'a pas bougé et qui n'est pas dans les statuts filtrés
                    action = map_action_from_status(issue.issue_type, issue.status)
                    issue.daily_actions.append(str(action))

            if self.logger.isEnabledFor(logging.DEBUG):
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
