#!/usr/bin/env python3
"""
NEPSE Investment Dashboard
Main application entry point
"""

import os
import sys
import logging
from datetime import datetime
import threading
from config import Config
from database import NepseDatabase
from scheduler import NepseScheduler
from dashboard import app

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def initialize_app():
    """Initialize the application"""
    logger.info("=" * 60)
    logger.info("NEPSE Investment Dashboard Starting...")
    logger.info("=" * 60)

    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Initialize database
    logger.info("Initializing database...")
    db = NepseDatabase()
    logger.info("Database initialized successfully")

    # Check if .env file exists
    if not os.path.exists('.env'):
        logger.warning(".env file not found! Please create one based on .env.example")
        logger.warning("Email notifications will be disabled until configured")

    logger.info(f"Dashboard will be accessible at: http://localhost:{Config.DASHBOARD_PORT}")
    logger.info(f"Scheduler set to scrape daily at {Config.SCRAPE_HOUR}:{Config.SCRAPE_MINUTE:02d} {Config.TIMEZONE}")
    logger.info(f"Data retention: {Config.DATA_RETENTION_DAYS} days")
    logger.info("=" * 60)


def run_scheduler():
    """Run the scheduler in a separate thread"""
    scheduler = NepseScheduler()
    scheduler.start()

    # Keep scheduler running
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping scheduler...")
        scheduler.stop()


def main():
    """Main application entry point"""
    initialize_app()

    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler started in background")

    # Run dashboard
    logger.info("Starting dashboard server...")
    try:
        app.run_server(
            host=Config.DASHBOARD_HOST,
            port=Config.DASHBOARD_PORT,
            debug=Config.DEBUG_MODE
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
