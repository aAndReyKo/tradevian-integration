# Tradevian Integration Services

Self-hosted trading platform integration services for **Tradevian** - Professional Prop Trading Journal.

## 🚀 Services

### ✅ MT5 Cloud Service
Self-hosted MetaTrader 5 integration API
- Status: **Production Ready**
- Documentation: [mt5-service/README.md](./mt5-service/README.md)
- Deployment Guide: [mt5-service/DEPLOYMENT.md](./mt5-service/DEPLOYMENT.md)

### 🔜 DXTrade Service (Coming Soon)
DXTrade platform integration

### 🔜 MatchTrader Service (Coming Soon)
MatchTrader platform integration

### 🔜 Tradovate Service (Coming Soon)
Tradovate futures platform integration

## 📋 Overview

This repository contains all trading platform integration services for Tradevian. Each service runs independently on port 8000-8003 and provides REST API for:

- ✅ Account connection and authentication
- ✅ Trade history synchronization
- ✅ Open positions tracking
- ✅ Account information retrieval
- ✅ Real-time data updates

## 🏗️ Architecture

```
┌─────────────────────────┐
│ Tradevian Web App       │
│ (Next.js - Frontend)    │
└──────────┬──────────────┘
           │ HTTP API calls
           ↓
┌─────────────────────────┐
│ Integration Services    │ ← This Repository
│ (Self-hosted on VPS)    │
│                         │
│ ├─ MT5 Service :8000    │
│ ├─ DXTrade :8001        │
│ ├─ MatchTrader :8002    │
│ └─ Tradovate :8003      │
└──────────┬──────────────┘
           │ Platform APIs
           ↓
┌─────────────────────────┐
│ Trading Platforms       │
│ - MT5 Terminal          │
│ - DXTrade Server        │
│ - MatchTrader           │
│ - Tradovate             │
└─────────────────────────┘
```

## 🎯 Why Self-Hosted?

### Benefits
- ✅ **No trading interruption** - Your local trading terminal stays free
- ✅ **24/7 availability** - Always online for synchronization
- ✅ **Multiple users** - Support many users without conflicts
- ✅ **Data privacy** - Your trading data never leaves your control
- ✅ **Cost effective** - $10-30/month vs $50-200/month for hosted services
- ✅ **Customizable** - Modify and extend as needed

### vs Third-Party Services
| Feature | Self-Hosted | MetaApi | TradingView |
|---------|-------------|---------|-------------|
| **Cost** | $10-30/mo | $50-200/mo | $15-60/mo |
| **Data Privacy** | Full control | Third-party | Third-party |
| **Customization** | Unlimited | Limited | Very limited |
| **Trading Block** | No ❌ | No ❌ | Yes ⚠️ |
| **Setup Time** | 15-20 min | Instant | Instant |

## 🚀 Quick Start

### 1. Choose a Service

Start with MT5 (most common):
```bash
cd mt5-service
```

### 2. Local Testing

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your API key

# Run
python main.py
```

Test: `http://localhost:8000/status`

### 3. Deploy to VPS

**Option A: Google Cloud (Recommended)**
- $300 free credits
- Lowest latency for Europe
- Guide: [mt5-service/docs/DEPLOY_GCP.md](./mt5-service/docs/DEPLOY_GCP.md)

**Option B: Generic VPS**
- DigitalOcean, Hetzner, AWS, etc.
- Guide: [mt5-service/DEPLOYMENT.md](./mt5-service/DEPLOYMENT.md)

## 💻 VPS Requirements

| Users | CPU | RAM | Disk | Cost/month |
|-------|-----|-----|------|------------|
| **1-50** | 1 vCPU | 2 GB | 20 GB | **$10-15** |
| **50-200** | 2 vCPU | 4 GB | 30 GB | **$20-30** |
| **200-500** | 4 vCPU | 8 GB | 50 GB | **$40-60** |

**Recommended Regions:**
- 🇵🇱 Warsaw (lowest latency for Ukraine)
- 🇩🇪 Frankfurt
- 🇧🇪 Belgium

## 🔐 Security

All services include:
- ✅ API Key authentication
- ✅ CORS protection
- ✅ Request logging
- ✅ Environment-based configuration
- ✅ SSL/HTTPS support (with Nginx)

**Security Checklist:**
- [ ] Generated strong API key (`openssl rand -base64 32`)
- [ ] Configured firewall (restrict to frontend IP)
- [ ] Setup HTTPS with Let's Encrypt
- [ ] Never committed `.env` to Git
- [ ] Regular security updates (`sudo apt update`)

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/aAndReyKo/tradevian-integration.git
cd tradevian-integration
```

### Install Service

```bash
cd mt5-service  # or dxtrade-service, etc.
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Configure
python main.py  # Test run
```

### Deploy (Auto-start)

```bash
# Copy systemd service
sudo cp systemd/mt5-service.service /etc/systemd/system/

# Edit username in service file
sudo nano /etc/systemd/system/mt5-service.service

# Enable and start
sudo systemctl enable mt5-service
sudo systemctl start mt5-service
sudo systemctl status mt5-service
```

## 🔧 Configuration

Each service uses `.env` file:

```env
# API Key (REQUIRED)
API_KEY=your-secure-api-key-here

# Server
PORT=8000
HOST=0.0.0.0

# CORS (add your frontend domains)
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.com

# Logging
LOG_LEVEL=INFO
```

## 📊 Monitoring

### Check Service Status
```bash
sudo systemctl status mt5-service
```

### View Logs
```bash
# Live logs
sudo journalctl -u mt5-service -f

# Last 50 lines
sudo journalctl -u mt5-service -n 50
```

### Health Check Endpoint
```bash
curl http://your-vps-ip:8000/status
```

## 🛠️ Development

### Run with auto-reload
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## 📚 Documentation

- [MT5 Service README](./mt5-service/README.md) - Features and API
- [MT5 Deployment Guide](./mt5-service/DEPLOYMENT.md) - Step-by-step VPS setup
- [GCP Deployment](./mt5-service/docs/DEPLOY_GCP.md) - Google Cloud specific guide

## 🤝 Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Roadmap

- [x] MT5 Cloud Service
- [ ] DXTrade Integration
- [ ] MatchTrader Integration
- [ ] Tradovate Integration
- [ ] cTrader Integration
- [ ] TradeLocker Integration
- [ ] WebSocket support for real-time updates
- [ ] Docker Compose for all services
- [ ] Kubernetes deployment configs

## 🐛 Troubleshooting

### Service won't start
```bash
sudo journalctl -u mt5-service -n 100
```

### Port already in use
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### MetaTrader5 import error (Linux)
```bash
sudo apt install wine64 wine32 -y
```

### Connection refused
- Check if service is running: `sudo systemctl status mt5-service`
- Check firewall: `sudo ufw status`
- Test locally: `curl http://localhost:8000/status`

## 📄 License

MIT License - See [LICENSE](./LICENSE) file

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/aAndReyKo/tradevian-integration/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aAndReyKo/tradevian-integration/discussions)
- **Email**: support@tradevian.com (coming soon)

## 🌟 Star History

If this project helps you, please give it a star ⭐

---

Built with ❤️ for the Tradevian trading community
