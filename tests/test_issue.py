import unittest
from src.display_jira_tickets.issue import (
    Action,
    Status,
    Issue,
    map_status_from_jira_status_name,
    map_action_from_status,
)


class TestIssue(unittest.TestCase):
    def test_map_status_from_jira_status_name_fr(self):
        self.assertEqual(map_status_from_jira_status_name("À faire", "fr"), Status.TO_DO)
        self.assertEqual(map_status_from_jira_status_name("En cours", "fr"), Status.IN_PROGRESS)
        self.assertEqual(map_status_from_jira_status_name("Terminé(e)", "fr"), Status.DONE)
        with self.assertRaises(ValueError):
            map_status_from_jira_status_name("Unknown Status", "fr")
        with self.assertRaises(ValueError):
            map_status_from_jira_status_name("À faire", "es")

    def test_map_status_from_jira_status_name_en(self):
        self.assertEqual(map_status_from_jira_status_name("To Do", "en"), Status.TO_DO)
        self.assertEqual(map_status_from_jira_status_name("In Progress", "en"), Status.IN_PROGRESS)
        self.assertEqual(map_status_from_jira_status_name("Done", "en"), Status.DONE)
        with self.assertRaises(ValueError):
            map_status_from_jira_status_name("Unknown Status", "en")

    def test_map_action_from_status(self):
        self.assertEqual(map_action_from_status("Story", Status.IN_PROGRESS), Action.IMPLEMENTATION)
        self.assertEqual(map_action_from_status("Bug", Status.IN_PROGRESS), Action.FIX)
        self.assertEqual(map_action_from_status("Story", Status.IN_REVIEW), Action.REVIEW)
        self.assertEqual(map_action_from_status("Bug", Status.IN_REVIEW), Action.REVIEW)
        self.assertEqual(map_action_from_status("Story", Status.IN_TEST), Action.TEST)
        with self.assertRaises(ValueError):
            map_action_from_status("Story", "Unknown Status")

    def test_issue_is_valid(self):
        valid_issue = Issue("KEY-1", "Bug", "Summary", Status.TO_DO, "User", Action.EMPTY)
        self.assertTrue(valid_issue.is_valid())
        invalid_issue = Issue(None, "Bug", "Summary", Status.TO_DO, "User", Action.EMPTY)
        self.assertFalse(invalid_issue.is_valid())

    def test_issue_is_bug(self):
        bug_issue = Issue("KEY-1", "Bug", "Summary", Status.TO_DO, "User", Action.EMPTY)
        self.assertTrue(bug_issue.is_bug())
        story_issue = Issue("KEY-1", "Story", "Summary", Status.TO_DO, "User", Action.EMPTY)
        self.assertFalse(story_issue.is_bug())


if __name__ == '__main__':
    unittest.main()
