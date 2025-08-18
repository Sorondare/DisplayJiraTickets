import logging
from .config import ReportConfig
from .issue import Issue, Status


class Reporter:
    def __init__(self, config: ReportConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def generate_report(self, issues: list[Issue]):
        self.logger.info("Generating report...")
        print(self.config.introduction)
        for issue in issues:
            if issue.is_valid():
                printed_action = issue.action + (
                    " (en cours)"
                    if self.config.username == issue.assignee and issue.status in (Status.IN_PROGRESS, Status.IN_REVIEW, Status.IN_TEST)
                    else ""
                )
                print(f"{issue.issue_key} {issue.summary} : {printed_action}")
            else:
                self.logger.warning("Invalid issue skipped: %s", issue)
        self.logger.info("Report generation complete.")
