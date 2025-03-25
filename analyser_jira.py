import argparse
import configparser
import io
import sys
from enum import StrEnum, auto

import pandas as pd
from jira import JIRA


class Action(StrEnum):
    IMPLEMENTATION = 'implémentation'
    FIX = 'fix'
    REVIEW = 'review'
    TEST = 'test'
    EMPTY = ''


class Column(StrEnum):
    ISSUE_KEY = auto()
    ISSUE_TYPE = auto()
    SUMMARY = auto()
    STATUS = auto()
    ASSIGNEE = auto()


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


def categorize_status(status, language):
    """
    Categorizes a Jira ticket status based on the "IN" statuses.

    Args:
        status (Status): The Jira ticket status.
        language (str): The language for status mapping ('fr' or 'en').

    Returns:
        str: The status category ("implémentation", "review", "test", "" or "Other statuses").
    """
    action_mapping = ACTION_MAPPING

    try:
        return action_mapping[status]
    except KeyError:
        raise ValueError(f"Unknown status: {status} for language: {language}")


def get_jira_data(jira_config):
    """
    Retrieves Jira data as a CSV string using a filter name or ID.

    Args:
        jira_config (configparser.ConfigParser): The configuration object containing Jira settings.

    Returns:
        str: The CSV data as a string, or None on error.
    """
    try:
        # Jira connection details from configuration
        jira_server = jira_config.get('Jira', 'server')
        jira_username = jira_config.get('Jira', 'username')
        jira_api_token = jira_config.get('Jira', 'api_token')
        jira_filter_id = jira_config.get('Jira', 'filter_id')

        jira_options = {
            'server': jira_server,
        }
        jira = JIRA(options=jira_options, basic_auth=(jira_username, jira_api_token))

        # Get the filter
        try:
            filter_obj = jira.filter(jira_filter_id)
        except Exception:
            print(f"Error: Filter '{jira_filter_id}' not found.")
            return None

        # Construct the JQL query from the filter
        jql_query = filter_obj.jql

        # Search for issues using the JQL query
        issues = jira.search_issues(jql_query, maxResults=1000)

        # Prepare data for DataFrame.  Include Assignee.
        data = []
        for issue in issues:
            data.append({
                Column.ISSUE_KEY: issue.key,
                Column.ISSUE_TYPE: issue.fields.issuetype.name,
                Column.SUMMARY: issue.fields.summary,
                Column.STATUS: issue.fields.status.name,
                Column.ASSIGNEE: issue.fields.assignee.displayName if issue.fields.assignee else None,
            })

        # Create a DataFrame from the issues data
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV string
        csv_data = df.to_csv(index=False, encoding='utf-8')
        return csv_data

    except Exception as e:
        print(f"Error retrieving data from Jira: {e}")
        return None


def process_jira_data(csv_data, display_tickets, language, username):
    """
    Processes Jira data from a CSV string, groups tickets by statuses, and displays a report.

    Args:
        csv_data (str): The CSV data as a string.
        display_tickets (bool): Indicates whether to display individual tickets.
        language (str): The language of the Jira column names ('fr' or 'en').
        username (str): The username to check for assignee.
    """
    try:
        # Load the CSV data from the string
        df = pd.read_csv(io.StringIO(csv_data))
    except Exception as e:
        print(f"Error reading CSV data: {e}")
        sys.exit(1)

    # Define column names and status mappings based on the selected language
    if language == "fr":
        status_mapping = STATUS_MAPPING_FR
    elif language == "en":
        status_mapping = STATUS_MAPPING_EN
    else:
        print("Error: Invalid language specified.  Please use 'en' or 'fr'.")
        sys.exit(1)

    # Map status values to their translated equivalents
    df[Column.STATUS] = df[Column.STATUS].map(status_mapping)

    # Apply the function to create a new column
    df["Action"] = df[Column.STATUS].apply(lambda x: categorize_status(x, language))

    # Group by status category and count the tickets
    report = df.groupby("Action").size()

    # Display the report
    print("\nReport on statuses:")
    print(report)

    # Display individual tickets by status if requested
    if display_tickets:
        print("\nTickets by status:")
        # Check if the necessary columns exist before displaying them
        if Column.ISSUE_KEY in df.columns and Column.SUMMARY in df.columns and Column.ASSIGNEE in df.columns:
            tickets_by_in_status = df[df['Action'] != "Other statuses"]
            if not tickets_by_in_status.empty:  # Verify that the dataframe is not empty before displaying it
                for index, row in tickets_by_in_status.iterrows():
                    action = row['Action']
                    if row[Column.ISSUE_TYPE] == "Bug" and action == Action.IMPLEMENTATION:
                        action = Action.FIX

                    # Add "(en cours)" only if the assignee is the user
                    if row[Column.ASSIGNEE] == username and row[Column.STATUS] in (Status.IN_PROGRESS, Status.IN_REVIEW, Status.IN_TEST):
                        action += " (en cours)"
                    print(f"- {row[Column.ISSUE_KEY]} {row[Column.SUMMARY]} : {action}")
            else:
                print("No tickets with IN statuses.")
        else:
            print(
                f"Error: The '{Column.ISSUE_KEY}', '{Column.SUMMARY}', or '{Column.ASSIGNEE}' columns are missing from the CSV file. Unable to display ticket details.")


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

    # Load configuration from file
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)

    # Get username from config
    username = config.get('User', 'name')

    # Fetch data from Jira using the filter
    csv_data = get_jira_data(config)
    if csv_data:
        process_jira_data(csv_data, display_tickets, language, username)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
