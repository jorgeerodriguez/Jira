"""
Jira Reporting System Package
"""

__version__ = '1.0.0'
__author__ = 'Jorge Rodriguez'

from .config_manager import ConfigManager
from .jira_client import JiraClient
from .report_generator import ReportGenerator
from .email_sender import EmailSender, GmailSender, create_email_sender
from .slack_notifier import SlackNotifier, create_slack_notifier

__all__ = [
    'ConfigManager',
    'JiraClient',
    'ReportGenerator',
    'EmailSender',
    'GmailSender',
    'create_email_sender',
    'SlackNotifier',
    'create_slack_notifier',
]
