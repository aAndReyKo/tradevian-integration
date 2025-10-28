# MT5 Cloud Service - Deployment Guide

Complete guide for deploying MT5 Cloud Service on a VPS (Google Cloud, AWS, DigitalOcean, etc.)

## Prerequisites

- Ubuntu 22.04 LTS VPS
- Root or sudo access
- 2GB+ RAM recommended
- Python 3.10+

## Quick Deploy Script

```bash
# SSH to your VPS
ssh user@your-vps-ip

# Clone repository
git clone https://github.com/aAndReyKo/tradevian-integration.git
cd tradevian-integration/mt5-service

# Run quick setup (installs everything)
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## Manual Step-by-Step Deployment

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python and Dependencies

```bash
sudo apt install python3 python3-pip python3-venv git curl -y
```

### 3. Install Wine (Required for MetaTrader5 on Linux)

```bash
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine64 wine32 -y
```

Verify Wine installation:
```bash
wine --version
```

### 4. Clone Repository

```bash
cd ~
git clone https://github.com/aAndReyKo/tradevian-integration.git
cd tradevian-integration/mt5-service
```

### 5. Setup Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Generate secure API key
openssl rand -base64 32
```

**Copy the generated API key**, then edit `.env`:

```bash
nano .env
```

**Update these values:**
```env
API_KEY=paste-your-generated-key-here
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

### 7. Test Run (Optional but Recommended)

```bash
python main.py
```

Should see:
```
INFO:     Started server process
INFO:main:✅ MT5 Cloud Service started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Press `Ctrl+C` to stop.

Test from browser: `http://YOUR_VPS_IP:8000/status`

### 8. Setup Systemd Service (Auto-start)

**Get your username:**
```bash
whoami
```

**Edit systemd service file:**
```bash
nano systemd/mt5-service.service
```

**Replace ALL instances of `YOUR_USERNAME` with your actual username.**

For example, if your username is `ubuntu`:
```ini
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/tradevian-integration/mt5-service
Environment="PATH=/home/ubuntu/tradevian-integration/mt5-service/venv/bin"
ExecStart=/home/ubuntu/tradevian-integration/mt5-service/venv/bin/python main.py
```

**Copy to systemd directory:**
```bash
sudo cp systemd/mt5-service.service /etc/systemd/system/
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable mt5-service
sudo systemctl start mt5-service
```

**Check status:**
```bash
sudo systemctl status mt5-service
```

Should show `active (running)` ✅

### 9. Configure Firewall

**Allow port 8000:**
```bash
sudo ufw allow 8000/tcp
sudo ufw enable
sudo ufw status
```

**For Google Cloud Platform:**
- Go to VPC network → Firewall rules
- Create rule: `allow-mt5-service`
- Port: `tcp:8000`
- Source: `0.0.0.0/0` (or your app IP for security)

### 10. Test Deployment

**From your local machine:**

```bash
curl http://YOUR_VPS_IP:8000/status
```

Should return:
```json
{
  "status": "ok",
  "message": "MT5 Cloud Service is running",
  "mt5_initialized": true
}
```

## Useful Commands

### View logs
```bash
# Live logs
sudo journalctl -u mt5-service -f

# Last 50 lines
sudo journalctl -u mt5-service -n 50

# Today's logs
sudo journalctl -u mt5-service --since today
```

### Restart service
```bash
sudo systemctl restart mt5-service
```

### Stop service
```bash
sudo systemctl stop mt5-service
```

### Check if service is running
```bash
sudo systemctl status mt5-service
```

### Update code from Git
```bash
cd ~/tradevian-integration/mt5-service
git pull
sudo systemctl restart mt5-service
```

## Update Frontend Configuration

On your **local machine** or **frontend server**, update `.env.local`:

```env
NEXT_PUBLIC_MT5_CLOUD_URL=http://YOUR_VPS_IP:8000
NEXT_PUBLIC_MT5_API_KEY=your-generated-api-key
```

Restart your Next.js app:
```bash
npm run dev  # or pm2 restart if using PM2
```

## Security Hardening

### 1. Restrict Firewall to Specific IP

Instead of allowing `0.0.0.0/0`, allow only your frontend server IP:

```bash
# Replace 123.45.67.89 with your frontend server IP
sudo ufw delete allow 8000/tcp
sudo ufw allow from 123.45.67.89 to any port 8000
```

### 2. Add HTTPS with Nginx

Install Nginx and Certbot:
```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

Create Nginx config:
```bash
sudo nano /etc/nginx/sites-available/mt5-service
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable config:
```bash
sudo ln -s /etc/nginx/sites-available/mt5-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Get SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

### 3. Change API Key Regularly

```bash
cd ~/tradevian-integration/mt5-service
openssl rand -base64 32  # Generate new key
nano .env                 # Update API_KEY
sudo systemctl restart mt5-service
```

Update key in your frontend `.env.local` as well!

## Troubleshooting

### Service won't start

```bash
# Check logs for errors
sudo journalctl -u mt5-service -n 100

# Common issues:
# 1. Wrong username in service file
# 2. Virtual environment path incorrect
# 3. Missing .env file
# 4. Port already in use
```

### Port already in use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### MetaTrader5 import fails

```bash
# Reinstall Wine
sudo apt install --reinstall wine64 wine32 -y

# Check Wine version
wine --version
```

### Connection refused

```bash
# Check if service is running
sudo systemctl status mt5-service

# Check firewall
sudo ufw status

# Test locally
curl http://localhost:8000/status
```

## Performance Tuning

### For high traffic (100+ requests/sec)

Edit `main.py` and change uvicorn config:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4,  # Add multiple workers
        log_level="info"
    )
```

Restart service after changes.

## Monitoring

### Setup monitoring with cron

```bash
# Create monitoring script
nano ~/check-mt5-service.sh
```

```bash
#!/bin/bash
if ! curl -f http://localhost:8000/status > /dev/null 2>&1; then
    echo "MT5 Service is down! Restarting..."
    sudo systemctl restart mt5-service
    # Optional: Send email alert
fi
```

```bash
chmod +x ~/check-mt5-service.sh

# Add to crontab (check every 5 minutes)
crontab -e
```

Add line:
```
*/5 * * * * /home/YOUR_USERNAME/check-mt5-service.sh
```

## Cost Estimation

### VPS Requirements

| Users | CPU | RAM | Disk | Cost/month |
|-------|-----|-----|------|------------|
| 1-50 | 1 vCPU | 2 GB | 20 GB | $10-15 |
| 50-200 | 2 vCPU | 4 GB | 30 GB | $20-30 |
| 200+ | 4 vCPU | 8 GB | 50 GB | $40-60 |

### Provider Recommendations

1. **Google Cloud** ($300 free credits)
   - e2-small: $13/month
   - europe-central2 (Warsaw) - lowest latency for Ukraine

2. **DigitalOcean** ($200 free credits)
   - Basic Droplet: $12/month
   - Frankfurt datacenter

3. **Hetzner** (Cheapest)
   - CX21: €5.83/month (~$6)
   - Nuremberg datacenter

## Support

Issues: https://github.com/aAndReyKo/tradevian-integration/issues

Documentation: https://github.com/aAndReyKo/tradevian-integration
