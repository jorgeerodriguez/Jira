"""
Scheduler Script for Automated Daily Reports
Runs the daily report at scheduled times
"""

import schedule
import time
import logging
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, 'src')

from daily_report import DailyReporter
from config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jira_reports.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_daily_report():
    """Run the daily report"""
    logger.info("=" * 80)
    logger.info(f"Scheduled report triggered at {datetime.now()}")
    logger.info("=" * 80)
    
    try:
        config_manager = ConfigManager()
        reporter = DailyReporter(config_manager)
        success = reporter.run()
        
        if success:
            logger.info("Scheduled report completed successfully")
        else:
            logger.error("Scheduled report failed")
    except Exception as e:
        logger.error(f"Error running scheduled report: {e}", exc_info=True)


def main():
    """Main scheduler loop"""
    # Load configuration to get schedule time
    config_manager = ConfigManager()
    config_manager.load_config()
    
    # Get schedule time from config or use default
    schedule_time = config_manager.get('report_schedule_time', '09:00')
    
    logger.info("=" * 80)
    logger.info("Jira Daily Report Scheduler Started")
    logger.info(f"Reports will be sent daily at {schedule_time}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 80)
    
    # Schedule the daily report
    schedule.every().day.at(schedule_time).do(run_daily_report)
    
    # Optional: Run immediately on startup for testing
    # run_daily_report()
    
    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
