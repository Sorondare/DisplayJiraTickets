import argparse
import configparser
import sys
import logging
from enum import StrEnum, auto

from jira import JIRA


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
    "TO DO": Status.TO_DO,
    "IN PROGRESS": Status.IN_PROGRESS,
    "TO REVIEW": Status.TO_REVIEW,
    "IN REVIEW": Status.IN_REVIEW,
    "TO DEPLOY": Status.TO_DEPLOY,
    "TO TEST": Status.TO_TEST,
    "IN TEST": Status.IN_TEST,
    "DONE": Status.DONE,
}

# Define action mappings as a constant
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

JQL_FILTER = 'project = "Scrum Beoogo" AND (status CHANGED BY currentUser() AFTER startOfDay() OR assignee = currentUser()) AND sprint in openSprints()'

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class Issue:
    """
    Represents a Jira issue.
    """
    def __init__(self, issue_key, issue_type, summary, status, assignee, action):
        self.issue_key = issue_key
        self.issue_type = issue_type
        self.summary = summary
        self.status = status
        self.assignee = assignee
        self.action = action

    def __str__(self):
        return f"[Issue Key: {self.issue_key}, Issue Type: {self.issue_type}, Summary: {self.summary}, Status: {self.status}, Assignee: {self.assignee}]"

    def __repr__(self):
        return f"JiraIssue(issue_key={self.issue_key}, issue_type={self.issue_type}, summary={self.summary}, status={self.status}, assignee={self.assignee})"

    def __eq__(self, other):
        if isinstance(other, Issue):
            return self.issue_key == other.issue_key

    def is_valid(self):
        return self.issue_key is not None and self.summary is not None and self.status is not None

    def is_bug(self):
        return self.issue_type == "Bug"


def map_status_from_jira_status_name(jira_status_name, language):
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


def map_action_from_status(issue_type, status):
    try:
        action = ACTION_MAPPING[status]

        if action == Action.IMPLEMENTATION and issue_type == "Bug":
            return Action.FIX
        else:
            return action
    except KeyError:
        raise ValueError(f"Unknown status: {status}")


def get_jira_data(jira_config, language):
    logger = logging.getLogger(__name__)

    try:
        # Jira connection details from configuration
        jira_server = jira_config.get('Jira', 'server')
        jira_username = jira_config.get('Jira', 'username')
        jira_api_token = jira_config.get('Jira', 'api_token')

        jira_options = {
            'server': jira_server,
        }
        jira = JIRA(options=jira_options, basic_auth=(jira_username, jira_api_token))

        # Search for issues using the JQL query
        logger.debug(f"Searching for issues using JQL query: {JQL_FILTER}")
        logger.info("Retrieving data from Jira...")
        jira_issues = jira.search_issues(JQL_FILTER, maxResults=1000)
        jira_issues.sort(key=lambda i: i.fields.updated)

        # Prepare data for DataFrame.  Include Assignee.
        issues = []
        for jira_issue in jira_issues:
            issue_type = jira_issue.fields.issuetype.name
            status = map_status_from_jira_status_name(jira_issue.fields.status.name, language)
            action = map_action_from_status(issue_type, status)

            issue = Issue(
                issue_key=jira_issue.key,
                issue_type=issue_type,
                summary=jira_issue.fields.summary,
                status=status,
                assignee=jira_issue.fields.assignee.displayName if jira_issue.fields.assignee else None,
                action=action,
            )
            logger.debug(f"Issue extracted: {issue}")

            issues.append(issue)

        return issues

    except Exception as e:
        logger.error(f"Error retrieving data from Jira: {e}")
        return None


def process_jira_data(config, issues):
    logger = logging.getLogger(__name__)

    # Display the report
    logger.info("Reporting issues...")

    username = config.get('Report', 'username')
    introduction = config.get('Report', 'introduction')

    print(introduction)
    for issue in issues:
        if issue.is_valid():
            printed_action = issue.action + (
                " (en cours)"
                if username == issue.assignee and issue.status in (Status.IN_PROGRESS, Status.IN_REVIEW, Status.IN_TEST)
                else ""
            )

            print(f"{issue.issue_key} {issue.summary} : {printed_action}")
        else:
            print(
                f"Error: The '{issue}' is not valid.")


def main():
    """
    Main function to analyze Jira data from an exported CSV file.
    """
    parser = argparse.ArgumentParser(
        description="Analyzes Jira data from an exported CSV file or Jira filter and generates a report on statuses.")
    parser.add_argument("-t", "--tickets", action="store_true", help="Display the details of individual tickets.")
    parser.add_argument("-l", "--language", default="fr", choices=["en", "fr"],
                        help="The language of the Jira status names (en or fr). Default is fr.")
    parser.add_argument("-c", "--config", default="config.ini", help="Path to the configuration file.")

    args = parser.parse_args()
    display_tickets = args.tickets
    language = args.language
    config_file = args.config

    # Load configuration from a file
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)

    logging_level = config.get('Logging', 'level') if config.has_option('Logging', 'level') else logging.INFO
    logging.basicConfig(level=logging_level, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    # Fetch data from Jira using the filter
    issues = get_jira_data(config, language)
    if issues:
        process_jira_data(config, issues)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
