import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from config import Config
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NepseDatabase:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self._ensure_db_directory()
        self._init_database()

    def _ensure_db_directory(self):
        """Create data directory if it doesn't exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")

    def _init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Top Gainers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_gainers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                symbol TEXT NOT NULL,
                ltp REAL,
                change_percent REAL,
                high REAL,
                low REAL,
                open REAL,
                qty INTEGER,
                turnover REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        ''')

        # Top Losers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_losers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                symbol TEXT NOT NULL,
                ltp REAL,
                change_percent REAL,
                high REAL,
                low REAL,
                open REAL,
                qty INTEGER,
                turnover REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        ''')

        # Top Traded table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_traded (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                symbol TEXT NOT NULL,
                qty INTEGER,
                ltp REAL,
                change_percent REAL,
                turnover REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        ''')

        # Top Turnovers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_turnovers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                symbol TEXT NOT NULL,
                turnover REAL,
                ltp REAL,
                change_percent REAL,
                qty INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        ''')

        # Top Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                symbol TEXT NOT NULL,
                transactions INTEGER,
                ltp REAL,
                change_percent REAL,
                qty INTEGER,
                turnover REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        ''')

        # Top Brokers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_brokers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                broker_no TEXT NOT NULL,
                broker_name TEXT,
                buy_contracts INTEGER,
                buy_amount REAL,
                sell_contracts INTEGER,
                sell_amount REAL,
                total_amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, broker_no)
            )
        ''')

        # IPO Information table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ipo_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_scraped DATE NOT NULL,
                company_name TEXT NOT NULL,
                scrip TEXT,
                opening_date DATE,
                closing_date DATE,
                issue_manager TEXT,
                shares_offered INTEGER,
                price_per_share REAL,
                min_units INTEGER,
                max_units INTEGER,
                status TEXT,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date_scraped, company_name, opening_date)
            )
        ''')

        # Scraper log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraper_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scrape_date DATE NOT NULL,
                scrape_time TIME NOT NULL,
                status TEXT NOT NULL,
                categories_scraped TEXT,
                records_added INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def insert_data(self, table_name, df, date):
        """Insert data into specified table"""
        if df is None or df.empty:
            logger.warning(f"No data to insert for {table_name}")
            return 0

        conn = sqlite3.connect(self.db_path)
        df['date'] = date

        try:
            # Insert or replace to handle duplicates
            df.to_sql(table_name, conn, if_exists='append', index=False)
            rows_added = len(df)
            logger.info(f"Inserted {rows_added} rows into {table_name}")
            conn.commit()
            return rows_added
        except sqlite3.IntegrityError:
            # Handle duplicates by updating
            logger.warning(f"Duplicate entries found for {table_name}, skipping")
            return 0
        finally:
            conn.close()

    def get_data(self, table_name, days=None):
        """Retrieve data from specified table"""
        conn = sqlite3.connect(self.db_path)

        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = f"SELECT * FROM {table_name} WHERE date >= ? ORDER BY date DESC"
            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        else:
            query = f"SELECT * FROM {table_name} ORDER BY date DESC"
            df = pd.read_sql_query(query, conn)

        conn.close()
        return df

    def get_repeat_analysis(self, table_name, days=30, min_occurrences=2):
        """Get stocks that appear multiple times in the specified table"""
        conn = sqlite3.connect(self.db_path)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = f'''
            SELECT
                symbol,
                COUNT(*) as occurrences,
                AVG(change_percent) as avg_change,
                MAX(change_percent) as max_change,
                MIN(change_percent) as min_change,
                MAX(date) as last_seen,
                GROUP_CONCAT(date) as dates
            FROM {table_name}
            WHERE date >= ?
            GROUP BY symbol
            HAVING COUNT(*) >= ?
            ORDER BY occurrences DESC, avg_change DESC
        '''

        df = pd.read_sql_query(query, conn, params=(cutoff_date, min_occurrences))
        conn.close()
        return df

    def cleanup_old_data(self):
        """Remove data older than retention period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=Config.DATA_RETENTION_DAYS)).strftime('%Y-%m-%d')

        tables = ['top_gainers', 'top_losers', 'top_traded', 'top_turnovers',
                  'top_transactions', 'top_brokers', 'ipo_info']

        total_deleted = 0
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE date < ?", (cutoff_date,))
            deleted = cursor.rowcount
            total_deleted += deleted
            logger.info(f"Deleted {deleted} old records from {table}")

        conn.commit()
        conn.close()
        logger.info(f"Total {total_deleted} old records deleted")
        return total_deleted

    def log_scrape(self, status, categories_scraped, records_added, error_message=None):
        """Log scraping activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute('''
            INSERT INTO scraper_log (scrape_date, scrape_time, status, categories_scraped,
                                     records_added, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S'), status,
              ','.join(categories_scraped), records_added, error_message))

        conn.commit()
        conn.close()

    def get_scraper_logs(self, days=7):
        """Get recent scraper logs"""
        conn = sqlite3.connect(self.db_path)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = '''
            SELECT * FROM scraper_log
            WHERE scrape_date >= ?
            ORDER BY scrape_date DESC, scrape_time DESC
        '''

        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        return df

    def is_market_closed_by_data_comparison(self, table_name, new_data):
        """
        Check if market is closed by comparing new data with last stored data.
        If the last 50 rows (or all rows if less than 50) are exactly the same
        (except date column), it indicates market is closed.

        Args:
            table_name: Name of the table to check
            new_data: DataFrame of newly scraped data

        Returns:
            Boolean: True if market appears closed, False otherwise
        """
        try:
            if new_data is None or new_data.empty:
                logger.warning(f"No new data provided for {table_name}")
                return False

            # Get last stored data
            conn = sqlite3.connect(self.db_path)

            # Get the most recent date's data
            query = f'''
                SELECT * FROM {table_name}
                WHERE date = (SELECT MAX(date) FROM {table_name})
                ORDER BY symbol
                LIMIT {Config.MARKET_CLOSURE_CHECK_ROWS}
            '''

            last_data = pd.read_sql_query(query, conn)
            conn.close()

            if last_data.empty:
                # No previous data, so we can't compare - assume market is open
                logger.info(f"No previous data for {table_name}, assuming market is open")
                return False

            # Prepare dataframes for comparison
            # Drop date, id, and created_at columns for comparison
            cols_to_drop = ['date', 'id', 'created_at', 'date_scraped']

            last_data_compare = last_data.drop(columns=[col for col in cols_to_drop if col in last_data.columns], errors='ignore')
            new_data_compare = new_data.drop(columns=[col for col in cols_to_drop if col in new_data.columns], errors='ignore')

            # Sort by symbol for fair comparison
            if 'symbol' in last_data_compare.columns and 'symbol' in new_data_compare.columns:
                last_data_compare = last_data_compare.sort_values('symbol').reset_index(drop=True)
                new_data_compare = new_data_compare.sort_values('symbol').reset_index(drop=True)

            # Take first N rows from both (N = min of both lengths or MARKET_CLOSURE_CHECK_ROWS)
            n_rows = min(len(last_data_compare), len(new_data_compare), Config.MARKET_CLOSURE_CHECK_ROWS)
            last_data_compare = last_data_compare.head(n_rows)
            new_data_compare = new_data_compare.head(n_rows)

            # Compare dataframes
            if last_data_compare.equals(new_data_compare):
                logger.warning(f"Market appears closed for {table_name} - data identical to previous day")
                return True
            else:
                logger.info(f"Market appears open for {table_name} - data has changed")
                return False

        except Exception as e:
            logger.error(f"Error checking market closure for {table_name}: {str(e)}")
            # In case of error, assume market is open to avoid missing data
            return False

    def check_all_tables_for_market_closure(self, scrape_results):
        """
        Check all scraped data to determine if market is closed.
        If majority of tables show identical data, market is likely closed.

        Args:
            scrape_results: Dictionary of table_name -> DataFrame

        Returns:
            Boolean: True if market appears closed, False if open
        """
        try:
            tables_to_check = ['top_gainers', 'top_losers', 'top_traded', 'top_turnovers']
            closure_checks = []

            for table_name in tables_to_check:
                if table_name in scrape_results and scrape_results[table_name] is not None:
                    is_closed = self.is_market_closed_by_data_comparison(table_name, scrape_results[table_name])
                    closure_checks.append(is_closed)

            if not closure_checks:
                return False

            # If 75% or more tables show identical data, market is closed
            closed_count = sum(closure_checks)
            total_count = len(closure_checks)
            closure_ratio = closed_count / total_count

            if closure_ratio >= 0.75:
                logger.warning(f"Market appears CLOSED - {closed_count}/{total_count} tables show identical data")
                return True
            else:
                logger.info(f"Market appears OPEN - {closed_count}/{total_count} tables show identical data")
                return False

        except Exception as e:
            logger.error(f"Error in comprehensive market closure check: {str(e)}")
            return False
