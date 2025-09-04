from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any


class Action(StrEnum):
    IMPLEMENTATION = 'implémentation'
    FIX = 'fix'
    REVIEW = 'review'
    TEST = 'test'
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
    Status.TO_DO: Action.EMPTY,
    Status.IN_PROGRESS: Action.IMPLEMENTATION,
    Status.TO_REVIEW: Action.IMPLEMENTATION,
    Status.IN_REVIEW: Action.REVIEW,
    Status.TO_DEPLOY: Action.REVIEW,
    Status.TO_TEST: Action.REVIEW,
    Status.IN_TEST: Action.TEST,
    Status.DONE: Action.TEST,
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
    action: Action

    def is_valid(self):
        return self.issue_key is not None and self.summary is not None and self.status is not None

    def is_bug(self):
        return self.issue_type == "Bug"


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
