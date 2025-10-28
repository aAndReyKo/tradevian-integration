# MT5 Cloud Service

Self-hosted MetaTrader 5 integration API for Tradevian trading journal.

## Features

- 🔌 **Connect to MT5 accounts** - Login with credentials and retrieve account info
- 📊 **Trade history** - Fetch closed trades from the last N days
- 📈 **Open positions** - Get currently open positions
- 🔐 **API Key authentication** - Secure access with custom API keys
- 🌐 **CORS support** - Configure allowed origins
- 📝 **Comprehensive logging** - Track all API requests

## Why Self-Hosted?

Running MT5 integration on a separate server (VPS/cloud) ensures:
- ✅ Your local MT5 Terminal is **NOT blocked** while syncing
- ✅ 24/7 availability for trade synchronization
- ✅ Multiple users can sync without conflicts
- ✅ Better security and control over your data

## Quick Start

### 1. Prerequisites

- Python 3.10+
- MT5 Terminal installed (for local testing)
- Ubuntu 22.04 LTS (for VPS deployment)

### 2. Installation

```bash
# Clone repository
git clone https://github.com/aAndReyKo/tradevian-integration.git
cd tradevian-integration/mt5-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Generate secure API key
openssl rand -base64 32

# Edit .env and paste your API key
nano .env
```

**Important:** Change `API_KEY` to your generated key!

### 4. Run Locally (Testing)

```bash
python main.py
```

Server will start on `http://localhost:8000`

Test: Open `http://localhost:8000/status` in browser

### 5. Deploy to VPS (Production)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete VPS setup instructions.

## API Endpoints

### Health Check
```http
GET /status
```

### Connect to MT5
```http
POST /mt5/connect
Headers:
  X-API-Key: your-api-key
Body:
  {
    "login": 123456,
    "password": "your-password",
    "server": "MetaQuotes-Demo"
  }
```

### Get Trade History
```http
POST /mt5/trades
Headers:
  X-API-Key: your-api-key
Body:
  {
    "login": 123456,
    "password": "your-password",
    "server": "MetaQuotes-Demo",
    "days": 30
  }
```

### Get Open Positions
```http
POST /mt5/positions
Headers:
  X-API-Key: your-api-key
Body:
  {
    "login": 123456,
    "password": "your-password",
    "server": "MetaQuotes-Demo"
  }
```

### Disconnect
```http
POST /mt5/disconnect?connection_id=123456@MetaQuotes-Demo
Headers:
  X-API-Key: your-api-key
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API key for authentication | *(required)* |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |

## Architecture

```
┌─────────────────────────┐
│ Tradevian Web App       │
│ (Next.js)               │
└──────────┬──────────────┘
           │ HTTP requests
           ↓
┌─────────────────────────┐
│ MT5 Cloud Service       │ ← This service
│ (Python FastAPI)        │
│ - Running on VPS        │
│ - Port 8000             │
└──────────┬──────────────┘
           │ MetaTrader5 API
           ↓
┌─────────────────────────┐
│ MT5 Terminal            │
│ (Your trading account)  │
└─────────────────────────┘
```

## Security Best Practices

1. **Strong API Key**: Generate with `openssl rand -base64 32`
2. **Firewall**: Restrict port 8000 to your app's IP only
3. **HTTPS**: Use reverse proxy (Nginx/Caddy) with SSL in production
4. **Environment Variables**: Never commit `.env` file to Git
5. **Regular Updates**: Keep dependencies updated

## Troubleshooting

### Service won't start
```bash
# Check if port is already in use
sudo netstat -tulpn | grep 8000

# Check logs
journalctl -u mt5-service -f
```

### MetaTrader5 import error on Linux
```bash
# Install Wine (required for MT5 on Linux)
sudo apt install wine64 wine32 -y
```

### Connection fails
- Ensure MT5 Terminal is running (on VPS or locally)
- Check credentials (login, password, server name)
- Verify firewall allows port 8000
- Check API key matches in both .env and client

## Development

### Run in development mode with auto-reload
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### View API documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Production Deployment

For production deployment on GCP, AWS, or DigitalOcean, see:
- [Google Cloud Platform deployment guide](./docs/DEPLOY_GCP.md)
- [Generic VPS deployment guide](./DEPLOYMENT.md)

## License

MIT License - See LICENSE file for details

## Support

Issues: https://github.com/aAndReyKo/tradevian-integration/issues
