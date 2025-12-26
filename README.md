#  NEPSE Investment Dashboard

A comprehensive investment analysis dashboard for Nepal Stock Exchange (NEPSE) with automated data collection, intelligent analysis, and email alerts.

##  Features

###  **Automated Data Collection**
- Daily scraping at 4 PM (Nepal Time)
- Automatically skips weekends (Saturdays) and market holidays
- Collects data from 7 categories:
  -  Top Gainers
  -  Top Losers
  -  Top Traded Shares
  -  Top Turnovers
  -  Top Transactions
  -  Top Brokers
  -  IPO Information

###  **Interactive Dashboard**
- **Overview Tab**: Today's market summary with top performers
- **Repeat Analysis Tab**: Find stocks that consistently appear in top lists
  - Drill-down to see date-wise occurrences
  - Adjustable time periods (7, 14, 30, 60, 90 days)
  - Minimum occurrence filters
- **Broker Intelligence Tab**: Analyze top broker activities
- **Stock Lookup Tab**: Search individual stocks across all categories
- **IPO Tracker Tab**: Monitor current and upcoming IPOs
- **Signals & Alerts Tab**: Investment signals based on patterns
  -  Hot Stocks (Repeated Gainers)
  -  Danger Zone (Repeated Losers)
  -  Most Active Stocks

###  **Email Alerts**
- Daily summary after data collection
- Weekly hot stocks alert (repeated gainers)
- Weekly danger stocks alert (repeated losers)
- IPO notifications
- Sent to: **email**

###  **Data Management**
- SQLite database for efficient storage
- Automatic 365-day data retention
- Automatic cleanup of old data

##  Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**
   ```bash
   cd GenerateWealth
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure email settings** (Optional but recommended)
   ```bash
   cp .env.example .env
   ```

   Edit `.env` file and add your email credentials:
   ```
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_TO=codewithnitesh01@gmail.com
   ```

   **Gmail App Password Setup:**
   - Go to Google Account Settings
   - Security → 2-Step Verification (enable it)
   - Search for "App passwords"
   - Generate an app password for "Mail"
   - Use this 16-character password in `.env`

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   - Open browser: http://localhost:8050
   - Dashboard will be live and accessible!

##  Usage Guide

### Running the Full Application
```bash
python app.py
```
This starts:
- Dashboard web server on port 8050
- Background scheduler for daily data collection
- Automatic data cleanup

### Manual Data Scraping
```bash
# Just scrape and store data
python run_scraper.py

# Scrape and send email
python run_scraper.py --send-email

# Scrape and cleanup old data
python run_scraper.py --cleanup
```

### Testing the Scraper
```bash
python scraper.py
```
This will test the scraper and display sample data without storing it.

## 🔧 Configuration

Edit `.env` file to customize:

| Setting | Description | Default |
|---------|-------------|---------|
| `SCRAPE_HOUR` | Daily scrape time (hour) | 16 (4 PM) |
| `SCRAPE_MINUTE` | Daily scrape time (minute) | 0 |
| `DATA_RETENTION_DAYS` | How long to keep data | 365 days |
| `DASHBOARD_PORT` | Dashboard port | 8050 |
| `TIMEZONE` | Timezone for scheduling | Asia/Kathmandu |

##  Deployment Options

### Option 1: Local PC (Recommended for You)

**Pros:**
- Completely free
- Full control
- No restrictions
- Fast access

** Cons:**
- Computer must be running 24/7
- Not accessible outside your network (unless port forwarded)

**Setup:**
```bash
# Just run the app
python app.py

# Keep it running in background (Linux/Mac)
nohup python app.py > logs/app.log 2>&1 &

# Windows: Use Task Scheduler or create a batch file
# and set it to run at startup
```

### Option 2: Render.com (Free Tier)  RECOMMENDED FREE CLOUD

** Pros:**
- Completely FREE (750 hours/month)
- Easy deployment
- HTTPS included
- Perfect for single user

**Cons:**
- Sleeps after 15 min of inactivity
- Wakes up in ~30 seconds when accessed

**Setup:**
1. Create account at https://render.com
2. Create new "Web Service"
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Add environment variables from `.env`
7. Deploy!

**Making it Private (Only You Can Access):**
- Use Render's environment variable to set a password
- Add basic authentication to `app.py` (I can add this if needed)

### Option 3: Railway.app (Free $5 Credit)

** Pros:**
- $5 free credit monthly
- Always on (doesn't sleep)
- Easy deployment

** Cons:**
- Credit may run out if heavy usage
- Requires credit card for verification

**Setup:**
1. Go to https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select your repo
5. Add environment variables
6. Deploy!

### Option 4: Koyeb (Free Tier)

** Pros:**
- Completely free
- Always on
- No credit card required

**Setup:**
1. Go to https://koyeb.com
2. Create new app
3. Deploy from GitHub
4. Set start command: `python app.py`
5. Deploy!

### Option 5: Free Oracle Cloud (Advanced)

** Pros:**
- Always free tier
- Full VM control
- No sleep/downtime
- Very generous limits

** Cons:**
- Complex setup
- Requires some Linux knowledge

**Setup:**
1. Create Oracle Cloud account
2. Create free ARM-based VM
3. Install Python and dependencies
4. Clone repo and run
5. Configure firewall for port 8050

##  Making Dashboard Private (Only You Can Access)

### Method 1: Add Password Protection

I can add a simple login page to the dashboard. Let me know if you want this!

### Method 2: Use SSH Tunnel (for cloud deployment)

```bash
# From your local PC, connect to cloud server
ssh -L 8050:localhost:8050 username@your-server-ip

# Now access at http://localhost:8050 on your local browser
```

### Method 3: Firewall Rules (Cloud)

Configure cloud firewall to only allow your home IP address to access port 8050.

##  Project Structure

```
GenerateWealth/
├── app.py                 # Main application
├── scraper.py            # NEPSE data scraper
├── database.py           # Database operations
├── dashboard.py          # Interactive dashboard
├── scheduler.py          # Daily scheduling
├── email_alerts.py       # Email notifications
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
├── .env                  # Your settings (create this)
├── data/
│   └── nepse_data.db     # SQLite database
└── logs/
    ├── app.log           # Application logs
    └── scheduler.log     # Scheduler logs
```

##  Investment Decision Support

### What You Can Do:

1. **Find Hot Stocks**
   - Go to "Signals & Alerts" tab
   - Check "Hot Stocks" section for repeated gainers
   - These stocks show consistent upward momentum

2. **Avoid Danger Stocks**
   - Check "Danger Zone" for repeated losers
   - Avoid or exit positions in these stocks

3. **Analyze Patterns**
   - Use "Repeat Analysis" tab
   - Set time period (e.g., 30 days)
   - Set minimum occurrences (e.g., 3+)
   - Click on stock to see date-wise breakdown

4. **Track Individual Stocks**
   - Use "Stock Lookup" tab
   - Enter symbol (e.g., NABIL)
   - See all occurrences across categories

5. **Monitor Broker Activity**
   - Check "Broker Intelligence"
   - See which brokers are most active
   - Institutional activity indicator

6. **IPO Opportunities**
   - "IPO Tracker" shows upcoming issues
   - Get email alerts for new IPOs

##  Email Notifications

### Daily Email (After 4 PM scrape)
- Top 5 gainers and losers
- Current IPO information
- Market summary

### Weekly Email (Sunday 8 PM)
- Hot stocks alert (3+ appearances as gainer)
- Danger stocks alert (3+ appearances as loser)
- IPO updates

## 🛠️ Troubleshooting

### Dashboard won't start
```bash
# Check if port 8050 is already in use
# Change port in .env file
DASHBOARD_PORT=8051
```

### Email not sending
- Verify Gmail app password is correct
- Check 2-Step Verification is enabled
- Try regenerating app password

### No data showing
```bash
# Run scraper manually first
python run_scraper.py
```

### Database errors
```bash
# Delete and recreate database
rm data/nepse_data.db
python app.py
```

##  Notes

- **Market Hours**: NEPSE trading is Sunday-Friday, 11 AM - 3 PM NPT
- **Scraping Time**: Set to 4 PM to ensure market has closed
- **Saturdays**: Automatically skipped (market closed)
- **Data Source**: Official NEPSE website APIs
- **Data Retention**: 365 days (automatically cleaned up)
- **Email**: Sent to codewithnitesh01@gmail.com

##  Recommended Workflow

1. **First Time Setup** (5 minutes)
   - Install dependencies
   - Configure `.env` file
   - Run `python app.py`

2. **Daily Usage** (2 minutes)
   - Check dashboard at 4:30 PM for today's data
   - Review "Signals & Alerts" tab
   - Check email for summary

3. **Weekly Analysis** (15 minutes)
   - Review weekly hot/danger stocks email
   - Use "Repeat Analysis" for deeper insights
   - Track your watchlist in "Stock Lookup"

4. **Investment Decisions**
   - Use hot stocks for potential entries
   - Avoid danger stocks
   - Monitor broker activity for institutional moves
   - Track IPOs for new opportunities

##  Tips for Better Investment Decisions

1. **Consistent Gainers (3+ times in 7 days)**
   - Strong momentum
   - Consider for swing trading

2. **Consistent Losers (3+ times in 7 days)**
   - Weak fundamentals or sentiment
   - Avoid or short if you have the facility

3. **High Turnover + High Volume**
   - Strong liquidity
   - Easier entry/exit

4. **Broker Concentration**
   - If top brokers are buying heavily
   - Could indicate institutional accumulation

5. **IPO Tracking**
   - Monitor opening/closing dates
   - Research issue price vs market comparisons

##  Support

For issues or questions:
- Check logs in `logs/` directory
- Run manual scraper to test: `python run_scraper.py`
- Email yourself test alerts

##  License

This project is for personal use. Use at your own risk. Not financial advice.

---

**Happy Investing! **

*Remember: This dashboard provides data and patterns. Always do your own research before making investment decisions.*
