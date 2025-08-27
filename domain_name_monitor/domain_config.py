#!/usr/bin/env python3

"""
Configuration file for the Domain Monitor Application

Customize the domains you want to monitor and notification settings here.
"""

# Domains to monitor (add/remove domains as needed)
DOMAINS_TO_MONITOR = [
    "google.com",
    "github.com",
    "stackoverflow.com",
    "example.com",
    # Add your own domains here:
    # "yourdomain.com",
    # "anotherdomain.org",
]

# User configuration
USER_ID = "kig@kig.re"  # Change this to your email

# Alert settings
ALERT_THRESHOLD_DAYS = 30  # Send alert if expiring within this many days

# Email notification settings
ENABLE_EMAIL_ALERTS = True
EMAIL_RECIPIENTS = [
    "kig@kig.re",  # Change this to your email
    # Add more recipients as needed:
    # "admin@yourdomain.com",
    # "alerts@company.com",
]

# Slack notification settings (optional)
ENABLE_SLACK_ALERTS = False  # Set to True if you want Slack notifications
SLACK_CHANNEL = "#alerts"    # Change this to your preferred channel

# Output settings
SAVE_RESULTS_TO_FILE = True
RESULTS_FILENAME = "domain_check_results.json"