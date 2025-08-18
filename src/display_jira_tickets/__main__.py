import argparse
import logging
import sys
from .config import Config
from .jira_client import JiraClient
from .reporter import Reporter

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def main():
    parser = argparse.ArgumentParser(description="Displays a summary of daily Jira tickets.")
    parser.add_argument("-c", "--config", default="config.ini", help="Path to the configuration file.")
    args = parser.parse_args()

    try:
        config = Config(args.config)
    except FileNotFoundError:
        logging.error("Configuration file not found at %s", args.config)
        sys.exit(1)
    except Exception as e:
        logging.error("Error reading configuration file: %s", e)
        sys.exit(1)

    logging.basicConfig(level=config.logging_config.level, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    try:
        jira_client = JiraClient(config.jira_config)
        issues = jira_client.fetch_issues()

        reporter = Reporter(config.report_config)
        reporter.generate_report(issues)
    except Exception as e:
        logging.error("An error occurred during execution: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
