import logging
import unittest
from unittest.mock import patch
from io import StringIO
from reporter import Reporter, ReportConfig
from issue import Issue, Status, Action


class TestReporter(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.report_config = ReportConfig(username="testuser", introduction="Daily Report")

    def test_generate_report(self):
        issues = [
            Issue("PROJ-1", "Story", "First story", Status.IN_PROGRESS, "testuser", [str(Action.IMPLEMENTATION)], is_in_progress=True),
            Issue("PROJ-2", "Bug", "A bug to fix", Status.TO_DO, "anotheruser", [str(Action.FIX)], is_in_progress=False),
            Issue("PROJ-3", "Story", "A story in review", Status.IN_REVIEW, "testuser", [str(Action.REVIEW)], is_in_progress=True),
            Issue("PROJ-4", "Story", "A story in test", Status.IN_TEST, "testuser", [str(Action.TEST)], is_in_progress=True),
            Issue("PROJ-5", "Story", "A finished story", Status.DONE, "testuser", [str(Action.TEST)], is_in_progress=False),
            Issue("PROJ-6", "Invalid Story", "This one is invalid", None, None, [])
        ]

        reporter = Reporter(self.report_config)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            reporter.generate_report(issues)
            output = fake_out.getvalue().strip().split('\n')

        self.assertEqual(output[0], "Daily Report")
        self.assertIn("* PROJ-1 First story", output)
        self.assertIn(f"  * {Action.IMPLEMENTATION} (en cours)", output)
        self.assertIn("* PROJ-2 A bug to fix", output)
        self.assertIn(f"  * {Action.FIX}", output)
        self.assertIn("* PROJ-3 A story in review", output)
        self.assertIn(f"  * {Action.REVIEW} (en cours)", output)
        self.assertIn("* PROJ-4 A story in test", output)
        self.assertIn(f"  * {Action.TEST} (en cours)", output)
        self.assertIn("* PROJ-5 A finished story", output)
        self.assertIn(f"  * {Action.TEST}", output)
        # Check that the invalid issue is not in the report
        self.assertNotIn("- PROJ-6", "".join(output))


if __name__ == '__main__':
    unittest.main()
