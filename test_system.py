"""
Quick Test Script
Tests the basic functionality of the reporting system without sending emails/Slack messages
"""

import sys
import logging
import tempfile
import os
from datetime import datetime

sys.path.insert(0, 'src')

from config_manager import ConfigManager
from jira_client import JiraClient
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_config():
    """Test configuration loading"""
    logger.info("Testing configuration loading...")
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    if config:
        logger.info("✓ Configuration loaded successfully")
        logger.info(f"  Jira Server: {config.get('jira_server', 'Not set')}")
        logger.info(f"  Email configured: {config_manager.has_email_config()}")
        logger.info(f"  Slack configured: {config_manager.has_slack_config()}")
        return True
    else:
        logger.error("✗ Failed to load configuration")
        return False


def test_jira_connection(config_manager):
    """Test Jira connection"""
    logger.info("\nTesting Jira connection...")
    
    jira_config = config_manager.get_jira_config()
    jira_client = JiraClient(
        jira_config['server'],
        jira_config['email'],
        jira_config['api_token']
    )
    
    if jira_client.connect():
        logger.info("✓ Connected to Jira successfully")
        
        # Test fetching projects
        try:
            projects = jira_client.get_projects()
            logger.info(f"✓ Found {len(projects)} projects")
            logger.info(f"  Sample projects: {', '.join([p.key for p in projects[:5]])}")
            return jira_client
        except Exception as e:
            logger.error(f"✗ Failed to fetch projects: {e}")
            return None
    else:
        logger.error("✗ Failed to connect to Jira")
        return None


def test_report_generation(jira_client):
    """Test report generation"""
    logger.info("\nTesting report generation...")
    
    try:
        report_generator = ReportGenerator(jira_client)
        
        # Test with a single project
        projects = jira_client.get_projects()
        if not projects:
            logger.warning("⚠ No projects found to test with")
            return False
        
        test_project = projects[0].key
        logger.info(f"  Testing with project: {test_project}")
        
        # Generate status summary
        status_summary = report_generator.generate_status_summary(test_project)
        logger.info(f"✓ Status summary generated: {status_summary['total_issues']} total issues")
        
        # Generate blocked issues report
        blocked_report = report_generator.generate_blocked_issues_report(test_project)
        logger.info(f"✓ Blocked issues report generated: {blocked_report['total_blocked']} blocked")
        
        # Generate in-progress report
        in_progress = report_generator.generate_in_progress_report(test_project)
        logger.info(f"✓ In-progress report generated: {in_progress['total_in_progress']} in progress")
        
        # Generate daily digest (limited to first 2 projects for testing)
        digest = report_generator.generate_daily_digest([p.key for p in projects[:2]])
        logger.info(f"✓ Daily digest generated with {len(digest['projects'])} projects")
        
        # Test formatting
        text_report = report_generator.format_digest_as_text(digest)
        logger.info(f"✓ Text report formatted ({len(text_report)} characters)")
        
        html_report = report_generator.format_digest_as_html(digest)
        logger.info(f"✓ HTML report formatted ({len(html_report)} characters)")
        
        # Save sample reports with timestamp to avoid conflicts
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        text_path = os.path.join(temp_dir, f'sample_report_{timestamp}.txt')
        html_path = os.path.join(temp_dir, f'sample_report_{timestamp}.html')
        
        with open(text_path, 'w') as f:
            f.write(text_report)
        logger.info(f"✓ Sample text report saved to {text_path}")
        
        with open(html_path, 'w') as f:
            f.write(html_report)
        logger.info(f"✓ Sample HTML report saved to {html_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Report generation failed: {e}", exc_info=True)
        return False


def main():
    """Main test function"""
    logger.info("=" * 80)
    logger.info("Jira Reporting System - Quick Test")
    logger.info("=" * 80)
    
    # Test configuration
    config_manager = ConfigManager()
    if not test_config():
        logger.error("\nConfiguration test failed. Please check your config.json file.")
        return False
    
    # Test Jira connection
    jira_client = test_jira_connection(config_manager)
    if not jira_client:
        logger.error("\nJira connection test failed. Please check your Jira credentials.")
        return False
    
    # Test report generation
    if not test_report_generation(jira_client):
        logger.error("\nReport generation test failed.")
        return False
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("All tests passed! ✓")
    logger.info("=" * 80)
    temp_dir = tempfile.gettempdir()
    logger.info("\nNext steps:")
    logger.info(f"1. Check sample reports in {temp_dir} (sample_report_*.txt and *.html)")
    logger.info("2. Configure email and/or Slack in config.json")
    logger.info("3. Run: python daily_report.py")
    logger.info("4. Set up scheduling with: python scheduler.py")
    logger.info("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}", exc_info=True)
        sys.exit(1)
