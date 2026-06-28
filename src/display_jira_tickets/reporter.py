import logging
from .config import ReportConfig
from .issue import Issue, Status


class Reporter:
    def __init__(self, config: ReportConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def generate_report(self, issues: list[Issue]):
        self.logger.info("Generating report...")
        report_lines = ["Ce jour :"]
        if self.config.introduction:
            report_lines.append(self.config.introduction)
        for issue in issues:
            if not issue.is_valid():
                self.logger.warning("Invalid issue skipped: %s", issue)
                continue

            if not issue.daily_actions:
                # No actions for today by the user, skip in report
                continue

            report_lines.append(f"- {issue.issue_key} {issue.summary}")
            for action in issue.daily_actions:
                # Still check if we want to append (en cours) dynamically if it's the current state?
                # Actually, the user wanted direct phrasing based on history, and no need to append "(en cours)" on the list.
                report_lines.append(f"  - {action}")

        print("\n".join(report_lines))
        self.logger.info("Report generation complete.")
