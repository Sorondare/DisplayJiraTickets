import pandas as pd
import argparse
import sys
import os

# Define status mappings as constants
STATUS_MAPPING_FR = {
    "À Faire": "TO DO",
    "En cours": "IN PROGRESS",
    "TO REVIEW": "TO REVIEW",
    "Revue en cours": "IN REVIEW",
    "TO DEPLOY": "TO DEPLOY",
    "IN TEST": "IN TEST",
    "TO TEST": "TO TEST",
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

# Define column names as constants
COLUMN_NAMES_FR = {"Issue key": "Clé de ticket", "Summary": "Résumé", "Status": "État", "Assignee": "Personne assignée"}
COLUMN_NAMES_EN = {"Issue key": "Issue Key", "Summary": "Summary", "Status": "Status", "Assignee": "Assignee"}

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

def process_jira_file(filepath, display_tickets, language, username):
    """
    Processes a Jira exported CSV file to group tickets by statuses and display a report.

    Args:
        filepath (str): The path to the Jira exported CSV file.
        display_tickets (bool): Indicates whether to display individual tickets.
        language (str): The language of the Jira column names ('fr' or 'en').
    """
    try:
        # Load the CSV file
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: The specified file ({filepath}) was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        sys.exit(1)

    # Define column names and status mappings based on the selected language
    if language == "fr":
        column_names = COLUMN_NAMES_FR
        status_mapping = STATUS_MAPPING_FR
    elif language == "en":
        column_names = COLUMN_NAMES_EN
        status_mapping = STATUS_MAPPING_EN
    else:
        print("Error: Invalid language specified.  Please use 'en' or 'fr'.")
        sys.exit(1)

    # Check if the expected columns exist
    if not all(col in df.columns for col in column_names.values()):
        print(f"Error: The CSV file does not contain the expected columns for the selected language ('{language}').")
        print(f"  Expected columns: {list(column_names.values())}")
        print(f"  Actual columns: {list(df.columns)}")
        sys.exit(1)

    # Rename the columns
    df = df.rename(columns=column_names)

    # Use the column names corresponding to the selected language.
    status_column = column_names["Status"]
    issue_key_column = column_names["Issue key"]
    summary_column = column_names["Summary"]
    assignee_column = column_names["Assignee"]

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
                    # Add "(en cours)" only if the assignee is "Prénom Nom"
                    if row[assignee_column] == username and row[status_column] != "DONE":
                        action += " (en cours)"
                    print(f"- {row[issue_key_column]} {row[summary_column]} : {action}")
            else:
                print("No tickets with IN statuses.")
        else:
            print(f"Error: The '{issue_key_column}', '{summary_column}', or '{assignee_column}' columns are missing from the CSV file. Unable to display ticket details.")

def main():
    """
    Main function to analyze Jira data from an exported CSV file.
    """
    parser = argparse.ArgumentParser(description="Analyzes Jira data from an exported CSV file and generates a report on statuses.")
    parser.add_argument("csv_file", help="The path to the Jira exported CSV file.")
    parser.add_argument("-t", "--tickets", action="store_true", help="Display the details of individual tickets.")
    parser.add_argument("-l", "--language", default="fr", choices=["en", "fr"], help="The language of the Jira column names (en or fr). Default is fr.")
    parser.add_argument("-u", "--username", help="The user name assigned to the tickets")

    args = parser.parse_args()
    csv_file = args.csv_file
    display_tickets = args.tickets
    language = args.language
    username = args.username

    # Check if the file exists before passing it to the function
    if not os.path.exists(csv_file):
        print(f"Error: The specified file ({csv_file}) does not exist.")
        sys.exit(1)

    process_jira_file(csv_file, display_tickets, language, username)

if __name__ == "__main__":
    main()
