import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock
from issue import (
    Action,
    Status,
    Issue,
    map_status,
    map_action_from_status,
)

# Helper mock class for Jira status objects
class MockJiraStatus:
    def __init__(self, id, name, status_category_key):
        self.id = id
        self.name = name
        self.statusCategory = Mock()
        self.statusCategory.key = status_category_key


class TestMapStatus(unittest.TestCase):
    def setUp(self):
        self.custom_mapping = {
            "1001": Status.TO_REVIEW,
            "in test": Status.IN_TEST,
            "1002": Status.DONE,
        }

    def test_map_by_id(self):
        # This status ID is in our custom mapping
        jira_status = MockJiraStatus("1001", "Code Review", "indeterminate")
        status = map_status(jira_status, self.custom_mapping)
        self.assertEqual(status, Status.TO_REVIEW)

    def test_map_by_name(self):
        # This status name is in our custom mapping
        jira_status = MockJiraStatus("1005", "In Test", "indeterminate")
        status = map_status(jira_status, self.custom_mapping)
        self.assertEqual(status, Status.IN_TEST)

    def test_id_has_priority_over_name(self):
        # Both ID and name are in the mapping, ID should win
        jira_status = MockJiraStatus("1002", "In Test", "done")
        status = map_status(jira_status, self.custom_mapping)
        self.assertEqual(status, Status.DONE)

    def test_fallback_to_category_new(self):
        # This status is not in the mapping, should fallback to 'new' category
        jira_status = MockJiraStatus("1", "To Do", "new")
        status = map_status(jira_status, {}) # Empty mapping
        self.assertEqual(status, Status.TO_DO)

    def test_fallback_to_category_indeterminate(self):
        # This status is not in the mapping, should fallback to 'indeterminate'
        jira_status = MockJiraStatus("3", "In Progress", "indeterminate")
        status = map_status(jira_status, {}) # Empty mapping
        self.assertEqual(status, Status.IN_PROGRESS)

    def test_fallback_to_category_done(self):
        # This status is not in the mapping, should fallback to 'done'
        jira_status = MockJiraStatus("10000", "Done", "done")
        status = map_status(jira_status, {}) # Empty mapping
        self.assertEqual(status, Status.DONE)

    def test_unmappable_status_raises_error(self):
        # This status has an unknown category and is not in the mapping
        jira_status = MockJiraStatus("99", "Unknown", "unknown_category")
        with self.assertRaises(ValueError) as cm:
            map_status(jira_status, {})
        self.assertIn("Unable to map status", str(cm.exception))


class TestIssue(unittest.TestCase):

    def test_map_action_from_status(self):
        self.assertEqual(map_action_from_status("Story", Status.IN_PROGRESS), Action.IMPLEMENTATION)
        self.assertEqual(map_action_from_status("Bug", Status.IN_PROGRESS), Action.FIX)
        self.assertEqual(map_action_from_status("Story", Status.IN_REVIEW), Action.REVIEW)
        self.assertEqual(map_action_from_status("Bug", Status.IN_REVIEW), Action.REVIEW)
        self.assertEqual(map_action_from_status("Story", Status.IN_TEST), Action.TEST)
        with self.assertRaises(ValueError):
            map_action_from_status("Story", "Unknown Status")

    def test_issue_is_valid(self):
        valid_issue = Issue("KEY-1", "Bug", "Summary", Status.TO_DO, "User", [])
        self.assertTrue(valid_issue.is_valid())
        invalid_issue = Issue(None, "Bug", "Summary", Status.TO_DO, "User", [])
        self.assertFalse(invalid_issue.is_valid())

    def test_issue_is_bug(self):
        bug_issue = Issue("KEY-1", "Bug", "Summary", Status.TO_DO, "User", [])
        self.assertTrue(bug_issue.is_bug())
        story_issue = Issue("KEY-1", "Story", "Summary", Status.TO_DO, "User", [])
        self.assertFalse(story_issue.is_bug())


class TestExtractDailyActions(unittest.TestCase):
    USERNAME = "User"

    def setUp(self):
        self.base_time = datetime.now().astimezone().replace(
            hour=8, minute=0, second=0, microsecond=0
        )

    def _timestamp(self, minutes):
        return (self.base_time + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    def _status_history(self, minutes, to_name, to_id):
        history = Mock()
        history.created = self._timestamp(minutes)
        history.author = Mock()
        history.author.displayName = self.USERNAME
        item = Mock()
        item.field = 'status'
        item.toString = to_name
        item.to = to_id
        history.items = [item]
        return history

    def _comment(self, minutes):
        comment = Mock(spec=['created', 'updated', 'author'])
        comment.created = self._timestamp(minutes)
        comment.updated = comment.created
        comment.author = Mock()
        comment.author.displayName = self.USERNAME
        return comment

    def _jira_issue(self, histories, comments):
        jira_issue = Mock()
        jira_issue.changelog.histories = histories
        jira_issue.fields.comment.comments = comments
        return jira_issue

    def test_action_redone_later_reappears_in_order(self):
        issue = Issue("KEY-1", "Story", "Summary", Status.IN_PROGRESS, self.USERNAME, [])
        jira_issue = self._jira_issue(
            histories=[
                self._status_history(0, "In Progress", "3"),
                self._status_history(60, "Code Review", "1001"),
                self._status_history(120, "In Progress", "3"),
            ],
            comments=[],
        )
        issue.extract_daily_actions(jira_issue, self.USERNAME, {"1001": Status.IN_REVIEW})
        self.assertEqual(
            issue.daily_actions,
            [str(Action.IMPLEMENTATION), str(Action.REVIEW), str(Action.IMPLEMENTATION)],
        )

    def test_consecutive_duplicates_are_collapsed(self):
        issue = Issue("KEY-1", "Story", "Summary", Status.IN_PROGRESS, self.USERNAME, [])
        jira_issue = self._jira_issue(
            histories=[self._status_history(0, "In Progress", "3")],
            comments=[self._comment(30), self._comment(45), self._comment(50)],
        )
        issue.extract_daily_actions(jira_issue, self.USERNAME, {})
        self.assertEqual(
            issue.daily_actions,
            [str(Action.IMPLEMENTATION), str(Action.DISCUSSION)],
        )


if __name__ == '__main__':
    unittest.main()
