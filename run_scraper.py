#!/usr/bin/env python3
"""
Standalone scraper script for manual execution or testing
"""

import sys
from datetime import datetime
from scraper import NepseScraper
from database import NepseDatabase
from email_alerts import EmailAlerts
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run scraper manually"""
    logger.info("=" * 60)
    logger.info("NEPSE Data Scraper - Manual Run")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Initialize components
    scraper = NepseScraper()
    db = NepseDatabase()
    email_alerts = EmailAlerts()

    # Scrape all data
    logger.info("Starting data scraping...")
    results = scraper.scrape_all()

    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')

    # Store data in database
    total_records = 0
    categories_scraped = []

    for category, df in results.items():
        if df is not None and not df.empty:
            logger.info(f"\n{category.upper()}:")
            logger.info(f"Scraped {len(df)} records")
            print(df.head())

            records = db.insert_data(category, df, today)
            total_records += records
            categories_scraped.append(category)
            logger.info(f"Stored {records} records in database")
        else:
            logger.warning(f"{category}: No data scraped")

    # Log scrape
    db.log_scrape('success', categories_scraped, total_records)

    logger.info("\n" + "=" * 60)
    logger.info(f"Scraping completed: {total_records} total records added")
    logger.info("=" * 60)

    # Ask if user wants to send email
    if '--send-email' in sys.argv:
        logger.info("Sending daily summary email...")
        email_alerts.send_daily_summary(results)
        logger.info("Email sent!")

    # Clean up old data
    if '--cleanup' in sys.argv:
        logger.info("Cleaning up old data...")
        deleted = db.cleanup_old_data()
        logger.info(f"Deleted {deleted} old records")


if __name__ == "__main__":
    main()
