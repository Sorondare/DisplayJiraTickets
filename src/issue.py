from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any


class Action(StrEnum):
    TO_DO = 'Remise à faire'
    IMPLEMENTATION = 'Implémentation'
    FIX = 'Correction'
    TO_REVIEW = 'Soumission pour revue'
    REVIEW = 'Revue de code'
    TO_TEST = 'Soumission pour test'
    TEST = 'Test'
    DONE = 'Terminé'
    DISCUSSION = 'Échange sur le ticket'
    DESCRIPTION_UPDATE = 'Modification de la description'
    EMPTY = ''


class Status(StrEnum):
    TO_DO = auto()
    IN_PROGRESS = auto()
    TO_REVIEW = auto()
    IN_REVIEW = auto()
    TO_DEPLOY = auto()
    TO_TEST = auto()
    IN_TEST = auto()
    DONE = auto()


ACTION_MAPPING = {
    Status.TO_DO: Action.TO_DO,
    Status.IN_PROGRESS: Action.IMPLEMENTATION,
    Status.TO_REVIEW: Action.TO_REVIEW,
    Status.IN_REVIEW: Action.REVIEW,
    Status.TO_DEPLOY: Action.REVIEW,
    Status.TO_TEST: Action.TO_TEST,
    Status.IN_TEST: Action.TEST,
    Status.DONE: Action.DONE,
}


@dataclass
class Issue:
    """
    Represents a Jira issue.
    """
    issue_key: str
    issue_type: str
    summary: str
    status: Status
    assignee: str | None
    daily_actions: list[str]

    def is_valid(self):
        return self.issue_key is not None and self.summary is not None and self.status is not None

    def is_bug(self):
        return self.issue_type == "Bug"

    def extract_daily_actions(self, jira_issue: Any, report_username: str, status_mapping: dict[str, Status]):
        from datetime import datetime
        # Get the current time in the local timezone, find midnight, and keep timezone awareness
        now = datetime.now().astimezone()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        events = []

        # Parse changelog for status updates
        if hasattr(jira_issue, 'changelog') and hasattr(jira_issue.changelog, 'histories'):
            for history in jira_issue.changelog.histories:
                history_created = datetime.strptime(history.created, "%Y-%m-%dT%H:%M:%S.%f%z")
                if history_created < start_of_day:
                    continue

                # Check author
                author = history.author.displayName if hasattr(history, 'author') and hasattr(history.author, 'displayName') else None
                # Fallback to name or emailAddress if displayName doesn't match perfectly, but we'll try matching displayName first
                author_matches = False
                if author == report_username:
                    author_matches = True
                elif hasattr(history, 'author') and hasattr(history.author, 'name') and history.author.name == report_username:
                    author_matches = True
                elif hasattr(history, 'author') and hasattr(history.author, 'emailAddress') and report_username in history.author.emailAddress:
                    author_matches = True

                if not author_matches:
                    continue

                for item in history.items:
                    if item.field == 'status':
                        # Try to map status
                        try:
                            # Try to create a dummy object to pass to map_status
                            class DummyStatus:
                                def __init__(self, name, status_id):
                                    self.name = name
                                    self.id = status_id
                                    class DummyCat:
                                        key = 'indeterminate'
                                    self.statusCategory = DummyCat()

                            to_status_obj = DummyStatus(item.toString, item.to)
                            new_status = map_status(to_status_obj, status_mapping)

                            action = map_action_from_status(self.issue_type, new_status)
                            events.append((history_created, str(action)))
                        except Exception:
                            pass
                    elif item.field == 'description':
                        events.append((history_created, str(Action.DESCRIPTION_UPDATE)))

        # Parse comments
        if hasattr(jira_issue.fields, 'comment') and hasattr(jira_issue.fields.comment, 'comments'):
            for comment in jira_issue.fields.comment.comments:
                # Check for comment creation
                comment_created = datetime.strptime(comment.created, "%Y-%m-%dT%H:%M:%S.%f%z")
                if comment_created >= start_of_day:
                    author = comment.author.displayName if hasattr(comment, 'author') and hasattr(comment.author, 'displayName') else None
                    author_matches = False
                    if author == report_username:
                        author_matches = True
                    elif hasattr(comment, 'author') and hasattr(comment.author, 'name') and comment.author.name == report_username:
                        author_matches = True
                    elif hasattr(comment, 'author') and hasattr(comment.author, 'emailAddress') and report_username in comment.author.emailAddress:
                        author_matches = True

                    if author_matches:
                        events.append((comment_created, str(Action.DISCUSSION)))

                # Check for comment update
                if hasattr(comment, 'updated') and comment.updated != comment.created:
                    comment_updated = datetime.strptime(comment.updated, "%Y-%m-%dT%H:%M:%S.%f%z")
                    if comment_updated >= start_of_day:
                        update_author = comment.updateAuthor.displayName if hasattr(comment, 'updateAuthor') and hasattr(comment.updateAuthor, 'displayName') else None
                        update_author_matches = False
                        if update_author == report_username:
                            update_author_matches = True
                        elif hasattr(comment, 'updateAuthor') and hasattr(comment.updateAuthor, 'name') and comment.updateAuthor.name == report_username:
                            update_author_matches = True
                        elif hasattr(comment, 'updateAuthor') and hasattr(comment.updateAuthor, 'emailAddress') and report_username in comment.updateAuthor.emailAddress:
                            update_author_matches = True

                        if update_author_matches:
                            events.append((comment_updated, str(Action.DISCUSSION)))

        # Sort events chronologically
        events.sort(key=lambda x: x[0])

        # Deduplicate actions while preserving order
        seen_actions = set()
        daily_actions = []
        for _, action_str in events:
            if action_str and action_str not in seen_actions and action_str != Action.EMPTY:
                seen_actions.add(action_str)
                daily_actions.append(action_str)

        self.daily_actions = daily_actions


def map_status(jira_status: Any, custom_mapping: dict[str, Status]) -> Status:
    if jira_status.id in custom_mapping:
        return custom_mapping[jira_status.id]

    jira_status_name = jira_status.name.lower() if jira_status.name else None
    if jira_status_name is not None and jira_status_name in custom_mapping:
        return custom_mapping[jira_status_name]

    status_category = jira_status.statusCategory.key
    if status_category == 'new':
        return Status.TO_DO
    elif status_category == 'indeterminate':
        return Status.IN_PROGRESS
    elif status_category == 'done':
        return Status.DONE

    raise ValueError(f"Unable to map status: {jira_status.name} (ID: {jira_status.id}, Category: {status_category})")


def map_action_from_status(issue_type: str, status: Status) -> Action:
    try:
        action = ACTION_MAPPING[status]

        if action == Action.IMPLEMENTATION and issue_type == "Bug":
            return Action.FIX
        else:
            return action
    except KeyError:
        raise ValueError(f"Unknown status: {status}")
