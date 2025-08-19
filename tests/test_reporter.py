import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from src.display_jira_tickets.reporter import Reporter, ReportConfig
from src.display_jira_tickets.issue import Issue, Status, Action


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.report_config = ReportConfig(username="testuser", introduction="Daily Report")

    def test_generate_report(self):
        issues = [
            Issue("PROJ-1", "Story", "First story", Status.IN_PROGRESS, "testuser", Action.IMPLEMENTATION),
            Issue("PROJ-2", "Bug", "A bug to fix", Status.TO_DO, "anotheruser", Action.FIX),
            Issue("PROJ-3", "Story", "A story in review", Status.IN_REVIEW, "testuser", Action.REVIEW),
            Issue("PROJ-4", "Story", "A story in test", Status.IN_TEST, "testuser", Action.TEST),
            Issue("PROJ-5", "Story", "A finished story", Status.DONE, "testuser", Action.TEST),
            Issue("PROJ-6", "Invalid Story", "This one is invalid", None, None, None)
        ]

        reporter = Reporter(self.report_config)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            reporter.generate_report(issues)
            output = fake_out.getvalue().strip().split('\n')

        self.assertEqual(output[0], "Daily Report")
        self.assertIn("PROJ-1 First story : implémentation (en cours)", output)
        self.assertIn("PROJ-2 A bug to fix : fix", output)
        self.assertIn("PROJ-3 A story in review : review (en cours)", output)
        self.assertIn("PROJ-4 A story in test : test (en cours)", output)
        self.assertIn("PROJ-5 A finished story : test", output)
        # Check that the invalid issue is not in the report
        self.assertNotIn("PROJ-6", "".join(output))


if __name__ == '__main__':
    unittest.main()
