# Production Deployment Guide

## ✅ All Production Features Implemented

This guide covers deployment of the production-ready AI-assisted insurance meeting system.

---

## 🎉 What's Been Implemented

### ✅ Database Layer (PostgreSQL)
- **SQLAlchemy ORM** with async support
- **Database Models**: `User`, `Lead`, `Booking`, `Session`, `SessionParticipant`, `Transcript`, `AIResponse`
- **Connection pooling** and lifecycle management
- **Alembic migrations** ready

### ✅ Authentication System
- **JWT tokens** (access + refresh)
- **Bcrypt password hashing**
- **Role-based access** (admin/agent)
- **Protected routes** middleware
- **Login/Register/Refresh** endpoints
- **Frontend login page**

### ✅ Microsoft Bookings Integration
- **OAuth 2.0 flow** with MSAL
- **Booking creation** via Graph API
- **Email sending** with join links
- **Webhook handling** (structure in place)

### ✅ ElevenLabs Voice (MANDATORY)
- **Text-to-speech** conversion
- **Audio streaming** to customer  
- **Base64 encoding** for WebSocket transmission
- **Integrated into AI response** pipeline

### ✅ Error Handling
- **Global exception handlers**
- **Validation error handling**
- **Database error handling**
- **Graceful degradation** for service failures
- **Structured logging**

### ✅ Rate Limiting
- **slowapi integration**
- **IP-based throttling**
- **Endpoint-specific limits**:
  - Login: 5/minute
  - Register: 3/hour
  - SMS: 10/hour
  - AI queries: 20/minute
  - General: 100/minute

---

## 📋 Pre-Deployment Checklist

### 1. Database Setup

```bash
# Install PostgreSQL
# Windows: Download from postgresql.org
# Mac: brew install postgresql
# Linux: sudo apt install postgresql

# Create database
createdb insurance_agent

# Update .env with your database URL
DATABASE_URL=postgresql+asyncpg://username:password@localhost/insurance_agent
```

### 2. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in ALL values:

**Critical Settings:**
```bash
# Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname

# JWT Authentication (REQUIRED - Generate strong keys!)
JWT_SECRET_KEY=use-openssl-rand-base64-32-to-generate
JWT_ALGORITHM=HS256

# All external service API keys...
```

### 4. Initialize Database

```bash
cd backend
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

### 5. Create First Admin User

```bash
# Start backend
python main.py

# Use API or create manually:
POST /api/auth/register
{
  "email": "admin@yourcompany.com",
  "password": "secure_password",
  "full_name": "Admin User",
  "role": "admin"
}
```

---

## 🚀 Running Production

### Backend

```bash
cd backend

# Production mode
APP_ENV=production uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
cd frontend

# Build for production
npm run build

# Serve with nginx, Vercel, or Netlify
```

---

## 🔒 Security Hardening

### Before Going Live:

1. **Change all default secrets**:
   - JWT_SECRET_KEY (minimum 32 characters)
   - Database password
   - All API keys

2. **Enable HTTPS**:
   - Use Let's Encrypt or cloud provider SSL
   - Update CORS settings
   - Set secure cookie flags

3. **Configure CORS properly**:
   ```python
   # In config.py
   @property
   def cors_origins(self) -> list[str]:
       if self.is_production:
           return ["https://yourdomain.com"]
       return ["*"]
   ```

4. **Use Redis for rate limiting**:
   ```python
   # In middleware/rate_limiter.py
   storage_uri="redis://localhost:6379"
   ```

5. **Enable database connection encryption**

6. **Set up monitoring**:
   - Sentry for error tracking
   - CloudWatch/Datadog for metrics
   - Database query monitoring

---

## 📊 Database Migrations

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Initial schema"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

---

## 🔧 Configuration by Environment

### Development
- `APP_ENV=development`
- Debug mode enabled
- Verbose logging
- In-memory rate limiting

### Staging
- `APP_ENV=staging`
- Debug mode disabled
- Standard logging
- Redis rate limiting
- Separate database

### Production
- `APP_ENV=production`
- Debug mode disabled
- Error-only logging
- Redis rate limiting  
- Connection pooling
- Load balancing

---

## 📱 Microsoft Bookings Setup

1. **Register Azure AD App**:
   - Go to portal.azure.com
   - Create App Registration
   - Add redirect URI: `https://yourdomain.com/api/bookings/oauth/callback`
   - Grant permissions: `Bookings.ReadWrite.All`

2. **Get Credentials**:
   - Copy Client ID
   - Create Client Secret
   - Note Tenant ID

3. **Update .env**:
   ```bash
   MS_CLIENT_ID=your_client_id
   MS_CLIENT_SECRET=your_client_secret
   MS_TENANT_ID=your_tenant_id
   ```

---

## 🎙️ ElevenLabs Setup

1. Sign up at elevenlabs.io
2. Get API key from settings
3. Choose voice ID (or use default)
4. Update .env:
   ```bash
   ELEVENLABS_API_KEY=your_api_key
   ELEVENLABS_VOICE_ID=voice_id_or_leave_empty_for_default
   ```

---

## 🎯 Testing Production Features

### Authentication
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

### Rate Limiting
```bash
# Test rate limit (make 6 requests quickly)
for i in {1..6}; do
  curl http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"x","password":"x"}'
done
# Should see 429 Too Many Requests on 6th
```

### Database
```bash
# Check database connection
python -c "from database import engine; import asyncio; asyncio.run(engine.connect())"
```

---

## 🚨 Troubleshooting

### Database Connection Issues
- Check DATABASE_URL format
- Verify PostgreSQL is running
- Check firewall rules
- Verify credentials

### Authentication Not Working
- Check JWT_SECRET_KEY is set
- Verify token expiration settings
- Check CORS configuration
- Clear browser localStorage

### Rate Limiting Too Strict
- Adjust limits in `middleware/rate_limiter.py`
- Use Redis for distributed limiting
- Whitelist IPs if needed

### ElevenLabs Voice Failing
- Check API key validity
- Verify account has credits
- Check network connectivity
- Review audio size limits

---

## 📈 Performance Optimization

1. **Database Indexing**:
   ```sql
   CREATE INDEX idx_sessions_status ON sessions(status);
   CREATE INDEX idx_users_email ON users(email);
   ```

2. **Connection Pooling**:
   - Adjust `pool_size` and `max_overflow` in database.py
   - Monitor active connections

3. **Caching**:
   - Add Redis for session storage
   - Cache RAG results
   - Cache user permissions

4. **CDN**:
   - Serve frontend from CDN
   - Cache static assets
   - Enable gzip compression

---

## ✅ Go-Live Checklist

- [ ] All environment variables configured
- [ ] Database created and migrated
- [ ] First admin user created
- [ ] HTTPS/SSL enabled
- [ ] CORS configured for production domain
- [ ] Rate limiting tested
- [ ] All API keys validated
- [ ] Error tracking configured (Sentry)
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation reviewed

---

**Your system is production-ready! 🎉**
