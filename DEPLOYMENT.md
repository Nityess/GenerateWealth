#  Deployment Guide - Free Cloud Hosting

Since you mentioned you don't have money for hosting, here are the **BEST FREE** options for deploying your NEPSE Dashboard to the cloud, accessible only to you.

##  Recommended: Render.com (100% Free)

**Why Render.com?**
-  Completely FREE forever
-  No credit card required
-  Easy GitHub integration
-  750 hours/month (enough for 24/7 if managed)
-  HTTPS included
-  Private access possible

**Important Note:**
Free tier sleeps after 15 minutes of inactivity, but wakes up in 30 seconds when you visit.

### Step-by-Step Render Deployment

#### 1. Prepare Your Repository

```bash
# Create a GitHub account if you don't have one
# Go to github.com and sign up

# Push your code to GitHub
git init
git add .
git commit -m "Initial commit: NEPSE Investment Dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/GenerateWealth.git
git push -u origin main
```

#### 2. Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easier integration)

#### 3. Deploy Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select "GenerateWealth" repo
4. Configure:
   - **Name**: nepse-dashboard
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: Free

5. **Environment Variables** (Click "Advanced" → "Add Environment Variable"):
   ```
   EMAIL_FROM = your-email@gmail.com
   EMAIL_PASSWORD = your-app-password
   EMAIL_TO = codewithnitesh01@gmail.com
   DASHBOARD_HOST = 0.0.0.0
   DASHBOARD_PORT = 8050
   ```

6. Click "Create Web Service"

7. Wait 5-10 minutes for deployment

8. Your dashboard will be live at: `https://nepse-dashboard.onrender.com`

#### 4. Make It Private (Only You Can Access)

**Option A: Use Authentication**
Add this to your `.env`:
```
DASHBOARD_USERNAME=nitesh
DASHBOARD_PASSWORD=your-secure-password-123
```

Then I'll add basic auth to the app (let me know if you want this).

**Option B: Keep URL Secret**
- Don't share your Render URL
- Render URLs are hard to guess
- Bookmark it privately

**Option C: IP Whitelist**
- Upgrade to Render paid ($7/month) for IP whitelisting
- Not necessary for you

### 5. Keep It Running 24/7 (Free)

The free tier sleeps after 15 min. To keep it awake:

**Use cron-job.org (Free):**
1. Go to https://cron-job.org
2. Sign up free
3. Create new cron job:
   - URL: `https://your-app.onrender.com`
   - Interval: Every 14 minutes
4. This pings your app to keep it awake

**Or use UptimeRobot (Free):**
1. Go to https://uptimerobot.com
2. Sign up free
3. Add new monitor:
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com`
   - Interval: 5 minutes
4. Keeps your app always on!

---

##  Alternative: Railway.app

**Why Railway?**
- $5 free credit/month
- Doesn't sleep
- Simpler than Render
- Better for 24/7 apps

** Limitations:**
- $5 credit runs out if heavy usage
- Requires credit card (even for free tier)

### Railway Deployment

1. **Sign Up**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose "GenerateWealth"

3. **Configure**
   - Railway auto-detects Python
   - Add environment variables:
     ```
     EMAIL_FROM=your-email@gmail.com
     EMAIL_PASSWORD=your-app-password
     EMAIL_TO=codewithnitesh01@gmail.com
     ```

4. **Deploy**
   - Click "Deploy"
   - Get public URL: `https://generatewealth-production.up.railway.app`

5. **Monitor Credit Usage**
   - Check dashboard for usage
   - $5 usually lasts all month for single user

---

##  Best Free Option: Fly.io

**Why Fly.io?**
- 3 shared VMs free forever
- 160GB bandwidth/month
- No sleep
- Full control

### Fly.io Deployment

1. **Install flyctl**
   ```bash
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh

   # Windows
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Sign Up**
   ```bash
   flyctl auth signup
   ```

3. **Create fly.toml**
   ```bash
   flyctl launch
   # Choose app name: nepse-dashboard
   # Choose region: closest to Nepal (Singapore or Mumbai)
   # Don't deploy yet
   ```

4. **Set Environment Variables**
   ```bash
   flyctl secrets set EMAIL_FROM=your-email@gmail.com
   flyctl secrets set EMAIL_PASSWORD=your-app-password
   flyctl secrets set EMAIL_TO=codewithnitesh01@gmail.com
   ```

5. **Deploy**
   ```bash
   flyctl deploy
   ```

6. **Access**
   - URL: `https://nepse-dashboard.fly.dev`

---

## 🔧 Oracle Cloud (Advanced - 100% Free Forever)

**Why Oracle?**
- Always Free ARM VMs
- No credit card for free tier
- Never sleeps
- Full Linux VM

**Difficulty:** Medium (need Linux knowledge)

### Oracle Cloud Setup

1. **Create Account**
   - Go to https://oracle.com/cloud/free
   - Sign up for "Always Free" tier
   - No credit card required for free resources

2. **Create VM Instance**
   - Compute → Instances → Create Instance
   - Choose "Always Free Eligible" shape (Ampere A1)
   - Select Ubuntu 22.04
   - Download SSH keys

3. **SSH into VM**
   ```bash
   ssh ubuntu@your-vm-ip
   ```

4. **Install Python & Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip git -y

   # Clone your repo
   git clone https://github.com/YOUR-USERNAME/GenerateWealth.git
   cd GenerateWealth

   # Install dependencies
   pip3 install -r requirements.txt

   # Create .env file
   nano .env
   # (Paste your configuration)
   ```

5. **Run as Background Service**
   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/nepse.service
   ```

   Paste:
   ```ini
   [Unit]
   Description=NEPSE Dashboard
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/GenerateWealth
   ExecStart=/usr/bin/python3 app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start
   sudo systemctl enable nepse
   sudo systemctl start nepse
   ```

6. **Configure Firewall**
   ```bash
   # Open port 8050
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8050 -j ACCEPT
   sudo netfilter-persistent save
   ```

7. **Access Dashboard**
   - Go to: `http://your-vm-ip:8050`

---



---


##  Making Your Dashboard Private

### Method 1: Basic Authentication (Recommended)

Add to `config.py`:
```python
DASHBOARD_USERNAME = os.getenv('DASHBOARD_USERNAME', '')
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', '')
```

I can add login functionality if you want!

### Method 2: Secret URL

- Deploy to Render with a random name
- Example: `https://nepse-x8k2m9p1.onrender.com`
- Don't share the URL
- Bookmark it privately

### Method 3: IP Restriction (Advanced)

For Fly.io or Oracle Cloud:
```bash
# Only allow your home IP
sudo iptables -A INPUT -p tcp -s YOUR_HOME_IP --dport 8050 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8050 -j DROP
```

---

##  Troubleshooting Cloud Deployment

### Issue: App crashes on Render
**Solution:** Check logs in Render dashboard
- Click your service → "Logs" tab
- Look for Python errors
- Usually missing environment variables

### Issue: Can't access deployed app
**Solution:** Check port binding
- Ensure `DASHBOARD_HOST=0.0.0.0` in environment variables
- Render needs 0.0.0.0, not localhost

### Issue: Database resets on Render
**Solution:** Render free tier has no persistent storage
- Use external database (free PostgreSQL on Render)
- Or accept database resets on each deployment
- For SQLite, it will reset when app restarts

To prevent database resets on Render:
1. Use Render's "Disks" feature (paid)
2. Or use external PostgreSQL (I can modify code)

