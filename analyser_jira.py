import argparse
import configparser
import io
import sys

import pandas as pd
from jira import JIRA

# Define status mappings as constants
STATUS_MAPPING_FR = {
    "À faire": "TO DO",
    "En cours": "IN PROGRESS",
    "TO REVIEW": "TO REVIEW",
    "Revue en cours": "IN REVIEW",
    "TO DEPLOY": "TO DEPLOY",
    "TO TEST": "TO TEST",
    "IN TEST": "IN TEST",
    "Terminé(e)": "DONE",
}

STATUS_MAPPING_EN = {
    "TO DO": "TO DO",
    "IN PROGRESS": "IN PROGRESS",
    "TO REVIEW": "TO REVIEW",
    "IN REVIEW": "IN REVIEW",
    "TO DEPLOY": "TO DEPLOY",
    "TO TEST": "TO TEST",
    "IN TEST": "IN TEST",
    "DONE": "DONE",
}

# Define action mappings as a constant
ACTION_MAPPING = {
    "TO DO": "",
    "IN PROGRESS": "Implémentation",
    "TO REVIEW": "Implémentation",
    "IN REVIEW": "Review",
    "TO DEPLOY": "Review",
    "TO TEST": "Review",
    "IN TEST": "Test",
    "DONE": "Test",
}


def categorize_status(status, language):
    """
    Categorizes a Jira ticket status based on the "IN" statuses.

    Args:
        status (str): The Jira ticket status.
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
                'Issue key': issue.key,
                'Summary': issue.fields.summary,
                'Status': issue.fields.status.name,
                'Assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
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


    # Use the column names corresponding to the selected language.
    status_column = "Status"
    issue_key_column = "Issue key"
    summary_column = "Summary"
    assignee_column = "Assignee"

    # Map status values to their translated equivalents
    df[status_column] = df[status_column].map(status_mapping)

    # Apply the function to create a new column
    df["Action"] = df[status_column].apply(lambda x: categorize_status(x, language))

    # Group by status category and count the tickets
    report = df.groupby("Action").size()

    # Display the report
    print("\nReport on statuses:")
    print(report)

    # Display individual tickets by status if requested
    if display_tickets:
        print("\nTickets by status:")
        # Check if the necessary columns exist before displaying them
        if issue_key_column in df.columns and summary_column in df.columns and assignee_column in df.columns:
            tickets_by_in_status = df[df['Action'] != "Other statuses"]
            if not tickets_by_in_status.empty:  # Verify that the dataframe is not empty before displaying it
                for index, row in tickets_by_in_status.iterrows():
                    action = row['Action']
                    # Add "(en cours)" only if the assignee is the user
                    if row[assignee_column] == username and row[status_column] in ("IN PROGRESS", "IN REVIEW", "IN TEST"):
                        action += " (en cours)"
                    print(f"- {row[issue_key_column]} {row[summary_column]} : {action}")
            else:
                print("No tickets with IN statuses.")
        else:
            print(
                f"Error: The '{issue_key_column}', '{summary_column}', or '{assignee_column}' columns are missing from the CSV file. Unable to display ticket details.")


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
