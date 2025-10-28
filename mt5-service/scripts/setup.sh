#!/bin/bash

# MT5 Cloud Service - Quick Setup Script
# This script automates the installation and configuration

set -e  # Exit on error

echo "🚀 MT5 Cloud Service - Quick Setup"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please do not run this script as root"
    echo "Run as: ./setup.sh"
    exit 1
fi

echo "📦 Step 1: Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

echo "🍷 Step 2: Installing Wine (for MetaTrader5)..."
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y wine64 wine32

echo "🐍 Step 3: Creating Python virtual environment..."
python3 -m venv venv

echo "📚 Step 4: Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔐 Step 5: Generating API key..."
API_KEY=$(openssl rand -base64 32)

echo "📝 Step 6: Creating .env file..."
cat > .env << EOF
# MT5 Cloud Service Configuration
API_KEY=$API_KEY
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "======================================"
echo "📋 Your API Key (SAVE THIS!):"
echo ""
echo "   $API_KEY"
echo ""
echo "======================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Test the service:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "2. Setup auto-start (systemd):"
echo "   sudo cp systemd/mt5-service.service /etc/systemd/system/"
echo "   sudo nano /etc/systemd/system/mt5-service.service  # Update YOUR_USERNAME"
echo "   sudo systemctl enable mt5-service"
echo "   sudo systemctl start mt5-service"
echo ""
echo "3. Configure firewall:"
echo "   sudo ufw allow 8000/tcp"
echo ""
echo "4. Update your frontend .env.local:"
echo "   NEXT_PUBLIC_MT5_CLOUD_URL=http://YOUR_VPS_IP:8000"
echo "   NEXT_PUBLIC_MT5_API_KEY=$API_KEY"
echo ""
echo "📚 Documentation: https://github.com/aAndReyKo/tradevian-integration"
echo ""
