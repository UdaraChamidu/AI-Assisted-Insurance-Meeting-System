# Insurance Agent System - Start Development Servers

## Quick Start

### Windows (PowerShell)
```powershell
.\start-dev.ps1
```

### Manual Start

1. **Backend** (Terminal 1):
```bash
cd backend
python main.py
# Runs on http://localhost:8000
```

2. **Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

3. **ngrok** (Terminal 3 - for Twilio webhooks):
```bash
ngrok http 8000
# Creates public URL for webhooks
```

## First Time Setup

1. **Install dependencies:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

2. **Configure environment:**
```bash
# Copy template
cp .env.example .env

# Edit .env with your API keys
# See docs/TWILIO_SETUP.md for details
```

3. **Initialize database:**
```bash
cd backend
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

4. **Create admin user:**
```bash
# Start backend first, then:
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "secure_password",
    "full_name": "Admin User",
    "role": "admin"
  }'
```

## Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ngrok Inspector**: http://localhost:4040 (when running)

## Common Commands

### Backend
```bash
# Run server
python main.py

# Run with auto-reload
uvicorn main:app --reload

# Create database migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Ingest sample documents
python scripts/ingest_documents.py --sample
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check
```

## Troubleshooting

### Backend won't start
- Check `.env` file exists and has valid values
- Verify PostgreSQL is running (if DATABASE_URL is set)
- Check port 8000 is not in use

### Frontend won't start
- Run `npm install` to install dependencies
- Check port 5173 is not in use
- Clear npm cache: `npm cache clean --force`

### ngrok issues
- Verify ngrok is installed: `ngrok version`
- Check authtoken is configured: `ngrok config check`
- Restart ngrok if URL needed

## Documentation

- **Twilio Setup**: `docs/TWILIO_SETUP.md`
- **Production Deploy**: `PRODUCTION.md`
- **Main README**: `README.md`

## Support

Check logs in:
- Backend: Console output where `python main.py` runs
- Frontend: Browser console (F12)
- ngrok: http://localhost:4040
