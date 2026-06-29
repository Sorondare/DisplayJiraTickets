import logging

from config import ReportConfig
from issue import Issue


class Reporter:
    def __init__(self, config: ReportConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def generate_report(self, issues: list[Issue]):
        if not issues:
            self.logger.info("No issues found.")
            return

        self.logger.info("Found %d issues.", len(issues))

        self.logger.info("Generating report...")
        report_lines = []
        if self.config.introduction:
            report_lines.append(self.config.introduction)
        for issue in issues:
            if not issue.is_valid():
                self.logger.warning("Invalid issue skipped: %s", issue)
                continue

            if not issue.daily_actions:
                continue

            report_lines.append(f"* {issue.issue_key} {issue.summary}")
            for action in issue.daily_actions:
                report_lines.append(f"  * {action}")

        empty_report_length = 1 if self.config.introduction else 0
        if len(report_lines) == empty_report_length:
            report_lines.append("No issues found.")
            self.logger.info("No issues found.")

        print("\n".join(report_lines))

        self.logger.info("Report generation complete.")
