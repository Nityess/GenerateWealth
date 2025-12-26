# 🚀 Quick Start Guide - 5 Minutes to Dashboard

## For Complete Beginners

### Step 1: Install Python (if not already installed)

**Windows:**
1. Download Python from https://python.org/downloads
2. Run installer, **CHECK** "Add Python to PATH"
3. Click "Install Now"

**Mac:**
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

### Step 2: Download the Project

```bash
# If you have git installed
git clone https://github.com/YOUR-USERNAME/GenerateWealth.git
cd GenerateWealth

# Or download ZIP from GitHub and extract
```

### Step 3: Easy Start (Choose Your OS)

**Windows:**
- Double-click `start.bat`
- Wait for installation to complete
- Browser will open automatically

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

### Step 4: Configure Email (Optional)

1. Open `.env` file in any text editor
2. Add your Gmail credentials:
   ```
   EMAIL_FROM=youremail@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_TO=codewithnitesh01@gmail.com
   ```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Search "App passwords"
4. Generate password for "Mail"
5. Copy 16-character password to `.env`

### Step 5: Access Dashboard

Open browser to: **http://localhost:8050**

---

## Manual Installation (Alternative)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env (copy from example)
cp .env.example .env
# Edit .env with your settings

# 3. Run the application
python app.py

# 4. Open browser
# Go to http://localhost:8050
```

---

## First Time Usage

### 1. Test the Scraper (Get Some Data)

```bash
# Run scraper manually to get initial data
python run_scraper.py
```

This will:
- Fetch data from NEPSE
- Store in database
- Show you what was scraped

### 2. Explore the Dashboard

Navigate through these tabs:
1. **Overview** - See today's top gainers/losers
2. **Repeat Analysis** - Find consistent performers
3. **Stock Lookup** - Search individual stocks
4. **Signals & Alerts** - Investment signals

### 3. Set Up Automation (Optional)

The app automatically scrapes data daily at 4 PM Nepal time when running.

**To run 24/7 on your PC:**

**Windows:**
- Run `start.bat`
- Minimize the window (don't close it)
- Keep PC running

**Mac/Linux:**
```bash
# Run in background
nohup python app.py > logs/app.log 2>&1 &

# Check if running
ps aux | grep app.py

# Stop later
pkill -f app.py
```

---

## Common Issues & Solutions

### ❌ "Python not found"
**Solution:** Install Python 3.8+ and add to PATH

### ❌ "Port 8050 already in use"
**Solution:** Edit `.env`, change `DASHBOARD_PORT=8051`

### ❌ "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### ❌ "Permission denied" (Mac/Linux)
**Solution:**
```bash
chmod +x start.sh
```

### ❌ No data showing in dashboard
**Solution:** Run scraper first:
```bash
python run_scraper.py
```

---

## What Happens Daily?

When the app is running:
- **4:00 PM** - Automatically scrapes NEPSE data
- **4:05 PM** - Sends you email summary (if configured)
- **Sunday 8 PM** - Weekly analysis emails

---

## Accessing from Phone/Tablet (Same Network)

1. Find your computer's IP address:
   - **Windows:** `ipconfig` (look for IPv4)
   - **Mac/Linux:** `ifconfig` (look for inet)

2. On phone/tablet browser, go to:
   ```
   http://YOUR-COMPUTER-IP:8050
   ```

Example: `http://192.168.1.100:8050`

---

## Free Cloud Deployment (Access from Anywhere)

If you want to access from anywhere without keeping your PC on:

**Easiest Option - Render.com (Free):**

1. Push code to GitHub
2. Go to https://render.com
3. Sign up with GitHub
4. New Web Service → Select your repo
5. Set start command: `python app.py`
6. Deploy!

**Detailed guide:** See `DEPLOYMENT.md`

---

## Commands Cheat Sheet

```bash
# Start dashboard
python app.py

# Manual scrape (no email)
python run_scraper.py

# Manual scrape with email
python run_scraper.py --send-email

# Manual scrape with cleanup
python run_scraper.py --cleanup

# Test scraper only (no database)
python scraper.py

# Stop running app (Mac/Linux)
pkill -f app.py

# Check logs
cat logs/app.log
cat logs/scheduler.log
```

---

## Project Structure

```
GenerateWealth/
├── app.py              ← Start here (main app)
├── start.sh/bat        ← Easy startup scripts
├── run_scraper.py      ← Manual data collection
├── .env                ← Your configuration
├── README.md           ← Full documentation
├── DEPLOYMENT.md       ← Cloud deployment guide
└── QUICKSTART.md       ← This file
```

---

## Next Steps

1. ✅ Get the dashboard running
2. ✅ Run scraper to get initial data
3. ✅ Configure email alerts
4. ✅ Explore all dashboard tabs
5. ⭐ Deploy to cloud (optional)

---

## Getting Help

1. Check `README.md` for detailed docs
2. Check `logs/` directory for errors
3. Try running scraper manually: `python run_scraper.py`

---

## Pro Tips

1. **Run scraper now** - Don't wait for 4 PM:
   ```bash
   python run_scraper.py
   ```

2. **Change scrape time** - Edit `.env`:
   ```
   SCRAPE_HOUR=17  # Change to 5 PM
   ```

3. **Extend data retention** - Edit `.env`:
   ```
   DATA_RETENTION_DAYS=730  # Keep 2 years of data
   ```

4. **Keep app running** - Use `nohup` or deploy to cloud

---

**That's it! You're ready to make better investment decisions with data! 📊💰**

For detailed documentation, see: `README.md`
For cloud deployment, see: `DEPLOYMENT.md`
