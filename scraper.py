from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import time
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NepseScraper:
    def __init__(self):
        self.pages = Config.PAGES
        self.ipo_url = Config.IPO_URL
        self.browser = None
        self.playwright = None

    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _fetch_page(self, url, max_retries=3):
        """Fetch page content using Playwright"""
        for attempt in range(max_retries):
            try:
                page = self.browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=60000)

                # Wait for table to load
                page.wait_for_selector('table', timeout=10000)

                content = page.content()
                page.close()

                return content
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None

    def _parse_table(self, html_content, table_index=0):
        """Parse HTML table using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            tables = soup.find_all('table')

            if not tables or len(tables) <= table_index:
                logger.warning(f"No table found at index {table_index}")
                return None

            table = tables[table_index]

            # Extract headers
            headers = []
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

            # If no headers in thead, try first row
            if not headers:
                first_row = table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]

            # Extract data rows
            rows = []
            tbody = table.find('tbody')
            if tbody:
                data_rows = tbody.find_all('tr')
            else:
                data_rows = table.find_all('tr')[1:]  # Skip header row

            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    rows.append(row_data)

            if not headers or not rows:
                logger.warning("Could not extract table data")
                return None

            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers[:len(rows[0])] if len(headers) >= len(rows[0]) else None)

            return df

        except Exception as e:
            logger.error(f"Error parsing table: {str(e)}")
            return None

    def scrape_top_gainers(self):
        """Scrape top gainers from ShareSansar"""
        try:
            logger.info("Scraping top gainers...")
            url = self.pages["Gainers"]

            html_content = self._fetch_page(url)
            if not html_content:
                return None

            df = self._parse_table(html_content)
            if df is None or df.empty:
                return None

            # Normalize column names
            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('%', 'percent')

            # Map to standard columns
            column_mapping = {
                's_no': None,  # Drop serial number
                'symbol': 'symbol',
                'ltp': 'ltp',
                'change_rs': 'change_rs',
                'changepercent': 'change_percent',
                'change': 'change_percent',
                'high': 'high',
                'low': 'low',
                'open': 'open',
                'qty': 'qty',
                'turnover': 'turnover',
                'volume': 'qty'
            }

            # Rename columns
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if new_col is None:
                        df = df.drop(columns=[old_col])
                    else:
                        df = df.rename(columns={old_col: new_col})

            # Convert numeric columns
            numeric_cols = ['ltp', 'change_percent', 'high', 'low', 'open', 'qty', 'turnover']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

            logger.info(f"Scraped {len(df)} top gainers")
            return df

        except Exception as e:
            logger.error(f"Error scraping top gainers: {str(e)}")
            return None

    def scrape_top_losers(self):
        """Scrape top losers from ShareSansar"""
        try:
            logger.info("Scraping top losers...")
            url = self.pages["Losers"]

            html_content = self._fetch_page(url)
            if not html_content:
                return None

            df = self._parse_table(html_content)
            if df is None or df.empty:
                return None

            # Normalize column names
            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('%', 'percent')

            # Map to standard columns
            column_mapping = {
                's_no': None,
                'symbol': 'symbol',
                'ltp': 'ltp',
                'change_rs': 'change_rs',
                'changepercent': 'change_percent',
                'change': 'change_percent',
                'high': 'high',
                'low': 'low',
                'open': 'open',
                'qty': 'qty',
                'turnover': 'turnover',
                'volume': 'qty'
            }

            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if new_col is None:
                        df = df.drop(columns=[old_col])
                    else:
                        df = df.rename(columns={old_col: new_col})

            numeric_cols = ['ltp', 'change_percent', 'high', 'low', 'open', 'qty', 'turnover']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

            logger.info(f"Scraped {len(df)} top losers")
            return df

        except Exception as e:
            logger.error(f"Error scraping top losers: {str(e)}")
            return None

    def scrape_top_traded(self):
        """Scrape top traded shares"""
        try:
            logger.info("Scraping top traded...")
            url = self.pages["Traded"]

            html_content = self._fetch_page(url)
            if not html_content:
                return None

            df = self._parse_table(html_content)
            if df is None or df.empty:
                return None

            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('%', 'percent')

            column_mapping = {
                's_no': None,
                'symbol': 'symbol',
                'qty': 'qty',
                'volume': 'qty',
                'shares_traded': 'qty',
                'ltp': 'ltp',
                'changepercent': 'change_percent',
                'change': 'change_percent',
                'turnover': 'turnover'
            }

            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if new_col is None:
                        df = df.drop(columns=[old_col])
                    else:
                        df = df.rename(columns={old_col: new_col})

            numeric_cols = ['qty', 'ltp', 'change_percent', 'turnover']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

            logger.info(f"Scraped {len(df)} top traded")
            return df

        except Exception as e:
            logger.error(f"Error scraping top traded: {str(e)}")
            return None

    def scrape_top_turnovers(self):
        """Scrape top turnovers"""
        try:
            logger.info("Scraping top turnovers...")
            url = self.pages["Turnovers"]

            html_content = self._fetch_page(url)
            if not html_content:
                return None

            df = self._parse_table(html_content)
            if df is None or df.empty:
                return None

            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('%', 'percent')

            column_mapping = {
                's_no': None,
                'symbol': 'symbol',
                'turnover': 'turnover',
                'ltp': 'ltp',
                'changepercent': 'change_percent',
                'change': 'change_percent',
                'qty': 'qty',
                'volume': 'qty'
            }

            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if new_col is None:
                        df = df.drop(columns=[old_col])
                    else:
                        df = df.rename(columns={old_col: new_col})

            numeric_cols = ['turnover', 'ltp', 'change_percent', 'qty']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

            logger.info(f"Scraped {len(df)} top turnovers")
            return df

        except Exception as e:
            logger.error(f"Error scraping top turnovers: {str(e)}")
            return None

    def scrape_top_transactions(self):
        """Scrape top transactions"""
        try:
            logger.info("Scraping top transactions...")
            url = self.pages["Transactions"]

            html_content = self._fetch_page(url)
            if not html_content:
                return None

            df = self._parse_table(html_content)
            if df is None or df.empty:
                return None

            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('%', 'percent')

            column_mapping = {
                's_no': None,
                'symbol': 'symbol',
                'transactions': 'transactions',
                'total_transaction': 'transactions',
                'ltp': 'ltp',
                'changepercent': 'change_percent',
                'change': 'change_percent',
                'qty': 'qty',
                'volume': 'qty',
                'turnover': 'turnover'
            }

            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if new_col is None:
                        df = df.drop(columns=[old_col])
                    else:
                        df = df.rename(columns={old_col: new_col})

            numeric_cols = ['transactions', 'ltp', 'change_percent', 'qty', 'turnover']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

            logger.info(f"Scraped {len(df)} top transactions")
            return df

        except Exception as e:
            logger.error(f"Error scraping top transactions: {str(e)}")
            return None

    def scrape_top_brokers(self):
        """Scrape top brokers"""
        try:
            logger.info("Scraping top brokers...")
            url = self.pages["Brokers"]

            html_content = self._fetch_page(url)
            if not html_content:
                return None

            df = self._parse_table(html_content)
            if df is None or df.empty:
                return None

            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('%', 'percent')

            column_mapping = {
                's_no': None,
                'broker_no': 'broker_no',
                'broker_name': 'broker_name',
                'buy_contracts': 'buy_contracts',
                'buy_amount': 'buy_amount',
                'sell_contracts': 'sell_contracts',
                'sell_amount': 'sell_amount',
                'total_amount': 'total_amount'
            }

            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if new_col is None:
                        df = df.drop(columns=[old_col])
                    else:
                        df = df.rename(columns={old_col: new_col})

            numeric_cols = ['buy_contracts', 'buy_amount', 'sell_contracts', 'sell_amount', 'total_amount']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

            logger.info(f"Scraped {len(df)} top brokers")
            return df

        except Exception as e:
            logger.error(f"Error scraping top brokers: {str(e)}")
            return None

    def scrape_ipo_info(self):
        """Scrape IPO information"""
        try:
            logger.info("Scraping IPO info...")
            url = self.ipo_url

            html_content = self._fetch_page(url)
            if not html_content:
                return None

            df = self._parse_table(html_content)
            if df is None or df.empty:
                return None

            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('%', 'percent')

            column_mapping = {
                's_no': None,
                'company_name': 'company_name',
                'scrip': 'scrip',
                'opening_date': 'opening_date',
                'closing_date': 'closing_date',
                'issue_manager': 'issue_manager',
                'shares_offered': 'shares_offered',
                'price_per_share': 'price_per_share',
                'min_units': 'min_units',
                'max_units': 'max_units',
                'status': 'status',
                'remarks': 'remarks'
            }

            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if new_col is None:
                        df = df.drop(columns=[old_col])
                    else:
                        df = df.rename(columns={old_col: new_col})

            logger.info(f"Scraped {len(df)} IPO entries")
            return df

        except Exception as e:
            logger.error(f"Error scraping IPO info: {str(e)}")
            return None

    def scrape_all(self):
        """Scrape all categories"""
        results = {}

        with self:  # Use context manager
            results['top_gainers'] = self.scrape_top_gainers()
            results['top_losers'] = self.scrape_top_losers()
            results['top_traded'] = self.scrape_top_traded()
            results['top_turnovers'] = self.scrape_top_turnovers()
            results['top_transactions'] = self.scrape_top_transactions()
            results['top_brokers'] = self.scrape_top_brokers()
            results['ipo_info'] = self.scrape_ipo_info()

        return results


if __name__ == "__main__":
    # Test the scraper
    scraper = NepseScraper()
    results = scraper.scrape_all()

    for category, df in results.items():
        if df is not None and not df.empty:
            print(f"\n{category.UPPER()}:")
            print(df.head())
            print(f"Columns: {df.columns.tolist()}")
        else:
            print(f"\n{category.UPPER()}: No data")
