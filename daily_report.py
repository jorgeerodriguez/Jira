"""
Daily Jira Report Script
Main entry point for generating and sending daily Jira reports
"""

import sys
import logging
from datetime import datetime
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, 'src')

from config_manager import ConfigManager
from jira_client import JiraClient
from report_generator import ReportGenerator
from email_sender import create_email_sender
from slack_notifier import create_slack_notifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyReporter:
    """Orchestrates daily report generation and distribution"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize daily reporter
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.jira_client = None
        self.report_generator = None
        self.email_sender = None
        self.slack_notifier = None
        
    def setup(self) -> bool:
        """
        Setup all components
        
        Returns:
            True if setup successful
        """
        logger.info("Setting up Daily Reporter...")
        
        # Load config
        if not self.config_manager.load_config():
            logger.error("Failed to load configuration")
            return False
        
        # Setup Jira client
        jira_config = self.config_manager.get_jira_config()
        self.jira_client = JiraClient(
            jira_config['server'],
            jira_config['email'],
            jira_config['api_token']
        )
        
        if not self.jira_client.connect():
            logger.error("Failed to connect to Jira")
            return False
        
        # Setup report generator
        self.report_generator = ReportGenerator(self.jira_client)
        
        # Setup email sender (if configured)
        if self.config_manager.has_email_config():
            try:
                email_config = self.config_manager.get_email_config()
                self.email_sender = create_email_sender(email_config)
                logger.info("Email sender configured")
            except Exception as e:
                logger.warning(f"Failed to setup email sender: {e}")
        else:
            logger.info("Email not configured, skipping email setup")
        
        # Setup Slack notifier (if configured)
        if self.config_manager.has_slack_config():
            try:
                slack_config = self.config_manager.get_slack_config()
                self.slack_notifier = create_slack_notifier(slack_config)
                logger.info("Slack notifier configured")
            except Exception as e:
                logger.warning(f"Failed to setup Slack notifier: {e}")
        else:
            logger.info("Slack not configured, skipping Slack setup")
        
        logger.info("Daily Reporter setup complete")
        return True
    
    def generate_report(self, project_keys: Optional[List[str]] = None) -> dict:
        """
        Generate daily digest report
        
        Args:
            project_keys: Optional list of project keys to report on
            
        Returns:
            Daily digest dictionary
        """
        logger.info("Generating daily report...")
        
        if not self.report_generator:
            raise RuntimeError("Reporter not setup. Call setup() first.")
        
        # Use configured project keys or default to specific projects
        if project_keys is None:
            project_keys = self.config_manager.get('report_projects')
            if project_keys is None:
                # Default projects - these should be updated in config.json
                default_projects = self.config_manager.get('default_report_projects', ['DEVOPS', 'EIT'])
                logger.warning(f"No report_projects configured, using defaults: {default_projects}")
                project_keys = default_projects
        
        digest = self.report_generator.generate_daily_digest(project_keys)
        logger.info(f"Report generated with {len(digest.get('projects', []))} projects")
        
        return digest
    
    def send_email_report(self, digest: dict) -> bool:
        """
        Send report via email
        
        Args:
            digest: Daily digest dictionary
            
        Returns:
            True if sent successfully
        """
        if not self.email_sender:
            logger.warning("Email sender not configured, skipping email")
            return False
        
        logger.info("Sending email report...")
        
        # Get recipient list from config
        recipients = self.config_manager.get('email_recipients')
        if not recipients:
            logger.warning("No email recipients configured")
            return False
        
        # Generate text and HTML versions
        report_text = self.report_generator.format_digest_as_text(digest)
        report_html = self.report_generator.format_digest_as_html(digest)
        
        # Send email
        success = self.email_sender.send_report(
            to_emails=recipients,
            report_title=digest['date'],
            report_text=report_text,
            report_html=report_html
        )
        
        if success:
            logger.info("Email report sent successfully")
        else:
            logger.error("Failed to send email report")
        
        return success
    
    def send_slack_report(self, digest: dict) -> bool:
        """
        Send report to Slack
        
        Args:
            digest: Daily digest dictionary
            
        Returns:
            True if sent successfully
        """
        if not self.slack_notifier:
            logger.warning("Slack notifier not configured, skipping Slack")
            return False
        
        logger.info("Sending Slack report...")
        
        # Send formatted report
        success = self.slack_notifier.send_report(digest)
        
        if success:
            logger.info("Slack report sent successfully")
        else:
            logger.error("Failed to send Slack report")
        
        return success
    
    def run(self, project_keys: Optional[List[str]] = None) -> bool:
        """
        Run complete daily report workflow
        
        Args:
            project_keys: Optional list of project keys to report on
            
        Returns:
            True if at least one delivery method succeeded
        """
        logger.info("=" * 80)
        logger.info(f"Starting Daily Jira Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        # Setup
        if not self.setup():
            logger.error("Setup failed, cannot continue")
            return False
        
        # Generate report
        try:
            digest = self.generate_report(project_keys)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}", exc_info=True)
            return False
        
        # Send via configured channels
        email_success = False
        slack_success = False
        
        if self.email_sender:
            email_success = self.send_email_report(digest)
        
        if self.slack_notifier:
            slack_success = self.send_slack_report(digest)
        
        # Summary
        logger.info("=" * 80)
        logger.info("Daily Report Summary:")
        logger.info(f"  Email: {'✓ Sent' if email_success else '✗ Not sent'}")
        logger.info(f"  Slack: {'✓ Sent' if slack_success else '✗ Not sent'}")
        logger.info("=" * 80)
        
        return email_success or slack_success


def main():
    """Main entry point"""
    # Parse command line arguments
    project_keys = None
    if len(sys.argv) > 1:
        project_keys = sys.argv[1].split(',')
        logger.info(f"Using project keys from command line: {project_keys}")
    
    # Create and run reporter
    config_manager = ConfigManager()
    reporter = DailyReporter(config_manager)
    
    try:
        success = reporter.run(project_keys)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
