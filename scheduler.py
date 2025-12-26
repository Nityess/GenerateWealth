from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import pytz
from config import Config
from scraper import NepseScraper
from database import NepseDatabase
from email_alerts import EmailAlerts

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NepseScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=Config.TIMEZONE)
        self.scraper = NepseScraper()
        self.db = NepseDatabase()
        self.email_alerts = EmailAlerts()

    def is_market_holiday(self):
        """Check if today is a market holiday"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_day = datetime.now().strftime('%A')

        # Saturday is market holiday in Nepal
        if today_day == 'Saturday':
            logger.info("Today is Saturday (market closed)")
            return True

        # Check configured holidays
        if today in Config.MARKET_HOLIDAYS:
            logger.info(f"Today is a market holiday: {today}")
            return True

        return False

    def daily_scrape_job(self):
        """Main job that runs daily at 4 PM"""
        logger.info("=" * 50)
        logger.info("Starting daily scrape job")

        # Check if market is closed (Saturday or configured holiday)
        if self.is_market_holiday():
            logger.info("Market is closed today (holiday/weekend), skipping scrape")
            self.db.log_scrape('skipped', [], 0, 'Market closed - holiday/weekend')
            return

        try:
            # Scrape all data
            results = self.scraper.scrape_all()

            # Check if market is actually closed by comparing data
            is_market_closed = self.db.check_all_tables_for_market_closure(results)

            if is_market_closed:
                logger.warning("=" * 50)
                logger.warning("⚠️  MARKET APPEARS CLOSED - Data identical to previous day")
                logger.warning("Skipping data insertion to avoid duplicates")
                logger.warning("=" * 50)
                self.db.log_scrape('skipped', [], 0, 'Market closed - data unchanged')

                # Still send email notification about market closure
                logger.info("Sending market closure notification email...")
                self.email_alerts.send_market_closure_alert()

                return

            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')

            # Store data in database
            total_records = 0
            categories_scraped = []

            for category, df in results.items():
                if df is not None and not df.empty:
                    records = self.db.insert_data(category, df, today)
                    total_records += records
                    categories_scraped.append(category)
                    logger.info(f"Stored {records} records for {category}")

            # Log successful scrape
            self.db.log_scrape('success', categories_scraped, total_records)

            logger.info(f"Daily scrape completed: {total_records} records added")

            # Send daily summary email
            logger.info("Sending daily summary email...")
            self.email_alerts.send_daily_summary(results)

            # Clean up old data (beyond retention period)
            deleted = self.db.cleanup_old_data()
            logger.info(f"Cleaned up {deleted} old records")

        except Exception as e:
            logger.error(f"Error during daily scrape: {str(e)}", exc_info=True)
            self.db.log_scrape('failed', [], 0, str(e))

        logger.info("Daily scrape job completed")
        logger.info("=" * 50)

    def weekly_analysis_job(self):
        """Weekly job to send analysis emails (runs every Sunday at 8 PM)"""
        logger.info("Starting weekly analysis job")

        try:
            # Send hot stocks alert
            self.email_alerts.send_hot_stocks_alert(days=7, min_occurrences=3)

            # Send danger stocks alert
            self.email_alerts.send_danger_stocks_alert(days=7, min_occurrences=3)

            # Send IPO alert
            self.email_alerts.send_ipo_alert()

            logger.info("Weekly analysis emails sent")

        except Exception as e:
            logger.error(f"Error during weekly analysis: {str(e)}", exc_info=True)

    def start(self):
        """Start the scheduler"""
        # Ensure logs directory exists
        import os
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Daily scrape at 4 PM (16:00)
        self.scheduler.add_job(
            self.daily_scrape_job,
            CronTrigger(
                hour=Config.SCRAPE_HOUR,
                minute=Config.SCRAPE_MINUTE,
                timezone=Config.TIMEZONE
            ),
            id='daily_scrape',
            name='Daily NEPSE Data Scrape',
            replace_existing=True
        )
        logger.info(f"Scheduled daily scrape at {Config.SCRAPE_HOUR}:{Config.SCRAPE_MINUTE:02d} {Config.TIMEZONE}")

        # Weekly analysis on Sunday at 8 PM (20:00)
        self.scheduler.add_job(
            self.weekly_analysis_job,
            CronTrigger(
                day_of_week='sun',
                hour=20,
                minute=0,
                timezone=Config.TIMEZONE
            ),
            id='weekly_analysis',
            name='Weekly Analysis Emails',
            replace_existing=True
        )
        logger.info("Scheduled weekly analysis on Sundays at 20:00")

        # Start the scheduler
        self.scheduler.start()
        logger.info("Scheduler started successfully")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def run_now(self):
        """Manually trigger the scrape job (for testing)"""
        logger.info("Manually triggering scrape job...")
        self.daily_scrape_job()

if __name__ == "__main__":
    scheduler = NepseScheduler()

    # For testing: run immediately
    print("Running scrape job now for testing...")
    scheduler.run_now()

    # Start scheduler
    print("Starting scheduler...")
    scheduler.start()

    # Keep running
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()
