# Update V2 – Major Enhancements

## What’s New

### Password Protection

* Dashboard now requires login
* **Username**: `NitYes`
* **Password**: `hackmeifucan@0101`
* Prevents unauthorized access to the dashboard

### New Data Source: ShareSansar.com

Switched from NepseStock.com to ShareSansar.com for more consistent and reliable data.

Data is now scraped from:

* sharesansar.com/top-gainers
* sharesansar.com/top-losers
* sharesansar.com/top-tradedshares
* sharesansar.com/top-turnovers
* sharesansar.com/top-transactions
* sharesansar.com/top-brokers
* sharesansar.com/ipo

### Playwright-Based Web Scraping

* Replaced `requests` with Playwright
* Better support for JavaScript-rendered pages
* More reliable scraping for dynamic content
* Uses headless browser automation

### Smart Market Closure Detection

**Problem**
Sometimes the market closes unexpectedly (public holidays, emergencies), but websites still display the previous trading day’s data. This caused duplicate entries in the database.

**Solution**
Implemented intelligent data comparison logic:

* Compares the last 50 rows of today’s scraped data with yesterday’s data
* If the data is identical (except date), the market is considered closed
* Comparison is done across 4 major categories:

  * Gainers
  * Losers
  * Traded Shares
  * Turnovers
* If 75% or more categories match, the market is detected as closed
* Data insertion is skipped to prevent duplicates
* An email alert is sent confirming market closure

**Workflow**

```
Day 1: Scrape data → Store in database
Day 2 (market closed):
    Scrape data → Compare with Day 1
    Data identical → Market closed
    Skip insertion → Send alert email
Day 3 (market open):
    Scrape data → Compare with Day 2
    Data different → Market open
    Insert data → Send daily summary
```

### Email Alerts

* Sends a market closure notification when closure is detected
* Explains the reason for closure detection
* Confirms that no duplicate data was inserted

## Technical Changes

### Files Modified

1. **config.py**

   * Added ShareSansar URLs
   * Added dashboard credentials
   * Added market closure detection settings

2. **scraper.py** (fully rewritten)

   * Uses Playwright instead of requests
   * Parses HTML tables using BeautifulSoup
   * Uses proper browser lifecycle handling
   * Improved error handling

3. **database.py**

   * Added `is_market_closed_by_data_comparison()`
   * Added `check_all_tables_for_market_closure()`
   * Intelligent DataFrame comparison logic

4. **dashboard.py**

   * Added basic authentication using dash-auth
   * All dashboard routes are protected

5. **scheduler.py**

   * Integrated market closure detection
   * Runs comparison before inserting data
   * Triggers appropriate email alerts

6. **email_alerts.py**

   * Added `send_market_closure_alert()`

7. **requirements.txt**

   * Added:

     * playwright==1.40.0
     * dash-auth==2.0.0
     * lxml==4.9.3
   * Removed:

     * requests
     * selenium
     * webdriver-manager

8. **start.sh / start.bat**

   * Added Playwright browser installation
   * Displays login credentials on startup

9. **.env / .env.example**

   * Added dashboard username and password configuration

## Installation Changes

### New Setup Steps

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

Or simply run:

* Linux/Mac: `./start.sh`
* Windows: `start.bat`

These scripts handle everything automatically.

## Usage Changes

### Dashboard Access

1. Open [http://localhost:8050](http://localhost:8050)
2. Login using configured credentials
3. Use the dashboard as before

### Data Collection

* Runs daily at 4 PM (Nepal Time)
* Automatically detects market closures
* Prevents duplicate data insertion
* Sends appropriate email notifications

### Market Closure Handling

The system now handles:

1. Saturdays (skipped automatically)
2. Configured holidays (via `MARKET_HOLIDAYS` in config.py)
3. Unexpected closures using data comparison

## Benefits

### Before (V1)

* No authentication
* Unreliable scraping
* Duplicate data during unexpected holidays
* Manual holiday handling

### After (V2)

* Password protected dashboard
* Reliable Playwright-based scraping
* Automatic market closure detection
* Clean database with no duplicates
* Email alerts for closures

## Example Scenario

**Unexpected public holiday**

**V1**

* Scraper runs
* Old cached data is scraped
* Duplicate records inserted
* Misleading daily email sent

**V2**

* Scraper runs
* Data compared with previous day
* Market closure detected
* No insertion performed
* Closure notification email sent

## Breaking Changes

Playwright is now required.

```bash
pip uninstall selenium webdriver-manager
pip install -r requirements.txt
python -m playwright install chromium
```

Or just use the startup scripts.

## Configuration

### Change Dashboard Credentials

Edit `.env`:

```env
DASHBOARD_USERNAME=yourusername
DASHBOARD_PASSWORD=yourpassword
```

### Adjust Market Closure Sensitivity

In `config.py` and `database.py`:

```python
MARKET_CLOSURE_CHECK_ROWS = 50

if closure_ratio >= 0.75:
    # change to 0.5 or 1.0 as needed
```

## Troubleshooting

**Playwright browser not found**

```bash
python -m playwright install chromium
```

**Dashboard login issue**

* Verify credentials in `.env`

**False market closure**

* Reduce threshold in `database.py`

**Force data insertion**

```python
is_market_closed = False
```

## Migration from V1

```bash
cp data/nepse_data.db data/nepse_data.db.backup
git pull
pip install -r requirements.txt
python -m playwright install chromium
```

Update `.env` with dashboard credentials and restart the app.


