import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from config import Config
from database import NepseDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailAlerts:
    def __init__(self):
        self.email_from = Config.EMAIL_FROM
        self.email_password = Config.EMAIL_PASSWORD
        self.email_to = Config.EMAIL_TO
        self.db = NepseDatabase()

    def _send_email(self, subject, html_body):
        """Send HTML email"""
        if not self.email_from or not self.email_password:
            logger.warning("Email credentials not configured, skipping email")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Connect to Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.email_from, self.email_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_daily_summary(self, scrape_results):
        """Send daily summary email after scraping"""
        today = datetime.now().strftime('%Y-%m-%d')

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th {{ background-color: #3498db; color: white; padding: 10px; text-align: left; }}
                td {{ border: 1px solid #ddd; padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .positive {{ color: green; font-weight: bold; }}
                .negative {{ color: red; font-weight: bold; }}
                .section {{ margin: 30px 0; }}
            </style>
        </head>
        <body>
            <h2>📊 NEPSE Daily Summary - {today}</h2>
        """

        # Top Gainers
        if scrape_results.get('top_gainers') is not None and not scrape_results['top_gainers'].empty:
            df = scrape_results['top_gainers'].head(5)
            html += """
            <div class="section">
                <h3>📈 Top Gainers</h3>
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>LTP</th>
                        <th>Change %</th>
                        <th>Turnover</th>
                    </tr>
            """
            for _, row in df.iterrows():
                change_class = 'positive' if row.get('change_percent', 0) > 0 else 'negative'
                html += f"""
                    <tr>
                        <td><strong>{row.get('symbol', 'N/A')}</strong></td>
                        <td>{row.get('ltp', 'N/A')}</td>
                        <td class="{change_class}">{row.get('change_percent', 'N/A')}%</td>
                        <td>{row.get('turnover', 'N/A')}</td>
                    </tr>
                """
            html += "</table></div>"

        # Top Losers
        if scrape_results.get('top_losers') is not None and not scrape_results['top_losers'].empty:
            df = scrape_results['top_losers'].head(5)
            html += """
            <div class="section">
                <h3>📉 Top Losers</h3>
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>LTP</th>
                        <th>Change %</th>
                        <th>Turnover</th>
                    </tr>
            """
            for _, row in df.iterrows():
                change_class = 'positive' if row.get('change_percent', 0) > 0 else 'negative'
                html += f"""
                    <tr>
                        <td><strong>{row.get('symbol', 'N/A')}</strong></td>
                        <td>{row.get('ltp', 'N/A')}</td>
                        <td class="{change_class}">{row.get('change_percent', 'N/A')}%</td>
                        <td>{row.get('turnover', 'N/A')}</td>
                    </tr>
                """
            html += "</table></div>"

        # IPO Info
        if scrape_results.get('ipo_info') is not None and not scrape_results['ipo_info'].empty:
            df = scrape_results['ipo_info']
            html += """
            <div class="section">
                <h3>🎯 IPO Information</h3>
                <table>
                    <tr>
                        <th>Company</th>
                        <th>Opening Date</th>
                        <th>Closing Date</th>
                        <th>Price</th>
                        <th>Status</th>
                    </tr>
            """
            for _, row in df.iterrows():
                html += f"""
                    <tr>
                        <td><strong>{row.get('company_name', 'N/A')}</strong></td>
                        <td>{row.get('opening_date', 'N/A')}</td>
                        <td>{row.get('closing_date', 'N/A')}</td>
                        <td>{row.get('price_per_share', 'N/A')}</td>
                        <td>{row.get('status', 'N/A')}</td>
                    </tr>
                """
            html += "</table></div>"

        html += """
            <hr>
            <p><small>This is an automated email from NEPSE Investment Dashboard</small></p>
        </body>
        </html>
        """

        subject = f"📊 NEPSE Daily Summary - {today}"
        return self._send_email(subject, html)

    def send_hot_stocks_alert(self, days=7, min_occurrences=3):
        """Send alert for stocks that repeatedly appear in top gainers"""
        repeat_gainers = self.db.get_repeat_analysis('top_gainers', days=days, min_occurrences=min_occurrences)

        if repeat_gainers.empty:
            logger.info("No hot stocks to report")
            return False

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #27ae60; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th {{ background-color: #27ae60; color: white; padding: 10px; text-align: left; }}
                td {{ border: 1px solid #ddd; padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .highlight {{ background-color: #ffffcc; }}
            </style>
        </head>
        <body>
            <h2>🔥 Hot Stocks Alert - Repeated Gainers ({days} days)</h2>
            <p>These stocks have appeared in top gainers <strong>{min_occurrences}+ times</strong> in the last {days} days:</p>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Occurrences</th>
                    <th>Avg Change %</th>
                    <th>Max Change %</th>
                    <th>Last Seen</th>
                </tr>
        """

        for _, row in repeat_gainers.iterrows():
            html += f"""
                <tr class="highlight">
                    <td><strong>{row['symbol']}</strong></td>
                    <td>{row['occurrences']}</td>
                    <td>{row['avg_change']:.2f}%</td>
                    <td>{row['max_change']:.2f}%</td>
                    <td>{row['last_seen']}</td>
                </tr>
            """

        html += """
            </table>
            <hr>
            <p><small>This is an automated alert from NEPSE Investment Dashboard</small></p>
        </body>
        </html>
        """

        subject = f"🔥 Hot Stocks Alert - {len(repeat_gainers)} Repeated Gainers"
        return self._send_email(subject, html)

    def send_danger_stocks_alert(self, days=7, min_occurrences=3):
        """Send alert for stocks that repeatedly appear in top losers"""
        repeat_losers = self.db.get_repeat_analysis('top_losers', days=days, min_occurrences=min_occurrences)

        if repeat_losers.empty:
            logger.info("No danger stocks to report")
            return False

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #e74c3c; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th {{ background-color: #e74c3c; color: white; padding: 10px; text-align: left; }}
                td {{ border: 1px solid #ddd; padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .warning {{ background-color: #ffebee; }}
            </style>
        </head>
        <body>
            <h2>⚠️ Danger Stocks Alert - Repeated Losers ({days} days)</h2>
            <p>These stocks have appeared in top losers <strong>{min_occurrences}+ times</strong> in the last {days} days:</p>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Occurrences</th>
                    <th>Avg Change %</th>
                    <th>Min Change %</th>
                    <th>Last Seen</th>
                </tr>
        """

        for _, row in repeat_losers.iterrows():
            html += f"""
                <tr class="warning">
                    <td><strong>{row['symbol']}</strong></td>
                    <td>{row['occurrences']}</td>
                    <td>{row['avg_change']:.2f}%</td>
                    <td>{row['min_change']:.2f}%</td>
                    <td>{row['last_seen']}</td>
                </tr>
            """

        html += """
            </table>
            <hr>
            <p><small>This is an automated alert from NEPSE Investment Dashboard</small></p>
        </body>
        </html>
        """

        subject = f"⚠️ Danger Stocks Alert - {len(repeat_losers)} Repeated Losers"
        return self._send_email(subject, html)

    def send_ipo_alert(self):
        """Send alert for new or upcoming IPOs"""
        ipo_data = self.db.get_data('ipo_info', days=30)

        if ipo_data.empty:
            logger.info("No IPO data to report")
            return False

        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #9b59b6; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th { background-color: #9b59b6; color: white; padding: 10px; text-align: left; }
                td { border: 1px solid #ddd; padding: 8px; }
                tr:nth-child(even) { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h2>🎯 IPO Alert - Current & Upcoming Issues</h2>
            <table>
                <tr>
                    <th>Company</th>
                    <th>Scrip</th>
                    <th>Opening Date</th>
                    <th>Closing Date</th>
                    <th>Price</th>
                    <th>Status</th>
                </tr>
        """

        for _, row in ipo_data.iterrows():
            html += f"""
                <tr>
                    <td><strong>{row.get('company_name', 'N/A')}</strong></td>
                    <td>{row.get('scrip', 'N/A')}</td>
                    <td>{row.get('opening_date', 'N/A')}</td>
                    <td>{row.get('closing_date', 'N/A')}</td>
                    <td>{row.get('price_per_share', 'N/A')}</td>
                    <td>{row.get('status', 'N/A')}</td>
                </tr>
            """

        html += """
            </table>
            <hr>
            <p><small>This is an automated alert from NEPSE Investment Dashboard</small></p>
        </body>
        </html>
        """

        subject = f"🎯 IPO Alert - {len(ipo_data)} Current Issues"
        return self._send_email(subject, html)

    def send_market_closure_alert(self):
        """Send alert when market is detected as closed"""
        today = datetime.now().strftime('%Y-%m-%d')

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #e74c3c; }}
                .alert-box {{ background-color: #ffebee; border-left: 5px solid #e74c3c; padding: 20px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h2>🔴 Market Closure Detected - {today}</h2>
            <div class="alert-box">
                <h3>⚠️ Alert</h3>
                <p>The automated scraper detected that the market appears to be <strong>CLOSED</strong> today.</p>
                <p>Scraped data is <strong>identical</strong> to the previous trading day (comparing last 50 rows).</p>
                <p>This could indicate:</p>
                <ul>
                    <li>Public holiday</li>
                    <li>Emergency market closure</li>
                    <li>Website showing cached data</li>
                </ul>
                <p><strong>No new data</strong> was added to the database to avoid duplicates.</p>
            </div>
            <p>Date: {today}</p>
            <p>Detection Method: Last 50 rows comparison across 4 major categories</p>
            <hr>
            <p><small>This is an automated alert from NEPSE Investment Dashboard</small></p>
        </body>
        </html>
        """

        subject = f"🔴 Market Closure Detected - {today}"
        return self._send_email(subject, html)

if __name__ == "__main__":
    # Test email alerts
    alerts = EmailAlerts()
    alerts.send_hot_stocks_alert()
