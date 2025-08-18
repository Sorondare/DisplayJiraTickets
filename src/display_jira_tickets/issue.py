from dataclasses import dataclass
from enum import StrEnum, auto


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


# Define status mappings as constants
STATUS_MAPPING_FR = {
    "À faire": Status.TO_DO,
    "En cours": Status.IN_PROGRESS,
    "TO REVIEW": Status.TO_REVIEW,
    "Revue en cours": Status.IN_REVIEW,
    "TO DEPLOY": Status.TO_DEPLOY,
    "TO TEST": Status.TO_TEST,
    "IN TEST": Status.IN_TEST,
    "Terminé(e)": Status.DONE,
}

STATUS_MAPPING_EN = {
    "To Do": Status.TO_DO,
    "In Progress": Status.IN_PROGRESS,
    "TO REVIEW": Status.TO_REVIEW,
    "In Review": Status.IN_REVIEW,
    "TO DEPLOY": Status.TO_DEPLOY,
    "TO TEST": Status.TO_TEST,
    "IN TEST": Status.IN_TEST,
    "Done": Status.DONE,
}

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


def map_status_from_jira_status_name(jira_status_name: str, language: str) -> Status:
    if language == "fr":
        status_mapping = STATUS_MAPPING_FR
    elif language == "en":
        status_mapping = STATUS_MAPPING_EN
    else:
        raise ValueError("Error: Invalid language specified. Please use 'en' or 'fr'.")

    try:
        return status_mapping[jira_status_name]
    except KeyError:
        raise ValueError(f"Unknown status: {jira_status_name} for language: {language}")


def map_action_from_status(issue_type: str, status: Status) -> Action:
    try:
        action = ACTION_MAPPING[status]

        if action == Action.IMPLEMENTATION and issue_type == "Bug":
            return Action.FIX
        else:
            return action
    except KeyError:
        raise ValueError(f"Unknown status: {status}")
