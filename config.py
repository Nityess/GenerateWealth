import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Email settings
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_TO = os.getenv('EMAIL_TO', 'codewithnitesh01@gmail.com')

    # ShareSansar URLs (using ShareSansar instead of NepseStock)
    PAGES = {
        "Gainers": "https://www.sharesansar.com/top-gainers",
        "Losers": "https://www.sharesansar.com/top-losers",
        "Traded": "https://www.sharesansar.com/top-tradedshares",
        "Turnovers": "https://www.sharesansar.com/top-turnovers",
        "Transactions": "https://www.sharesansar.com/top-transactions",
        "Brokers": "https://www.sharesansar.com/top-brokers"
    }

    IPO_URL = "https://www.sharesansar.com/ipo"

    # Scheduler settings
    SCRAPE_HOUR = int(os.getenv('SCRAPE_HOUR', 16))
    SCRAPE_MINUTE = int(os.getenv('SCRAPE_MINUTE', 0))
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Kathmandu')

    # Data retention
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 365))

    # Dashboard settings
    DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 8050))
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

    # Dashboard password protection
    DASHBOARD_USERNAME = os.getenv('DASHBOARD_USERNAME', 'NitYes')
    DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'hackmeifucan@0101')

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/nepse_data.db')

    # Market closure detection
    MARKET_CLOSURE_CHECK_ROWS = 50  # Compare last 50 rows to detect market closure

    # Market holiday check (can be expanded)
    MARKET_HOLIDAYS = [
        # Add known market holidays in YYYY-MM-DD format
        # '2024-01-01',  # New Year
        # '2024-10-15',  # Dashain
    ]
