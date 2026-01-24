# 🚀 Quick Start Guide

## ✅ Step 1: Start Backend

```powershell
cd backend
python main.py
```

**Expected:** Backend should start on `http://localhost:8000`

---

## 👤 Step 2: Create Login Credentials

You have **3 options**:

### Option A: Create Test Users (FASTEST)
```powershell
cd backend
python create_user.py --test
```

This creates:
- **Email:** `admin@insurance.com` | **Password:** `admin123` (admin)
- **Email:** `agent@insurance.com` | **Password:** `agent123` (agent)

### Option B: Create Custom User (Interactive)
```powershell
cd backend
python create_user.py
```

Follow the prompts to enter your email, password, name, and role.

### Option C: Use Registration API
1. Go to `http://localhost:5173`
2. Click "Register" or navigate to `/register` (if route exists)
3. Create account through UI

---

## 🌐 Step 3: Login

1. Open `http://localhost:5173/login`
2. Enter your credentials
3. Start using the app!

---

## 📝 Notes

- **Backend:** Must be running for frontend to work
- **Database:** Make sure PostgreSQL is running and `insurance_agent` database exists
- **Ngrok:** Only needed for Twilio webhooks (can skip for local testing)

---

## 🆘 Common Issues

### Database Connection Error
```
Make sure PostgreSQL is running:
- Check if service is started
- Verify DATABASE_URL in backend/.env
- Ensure database 'insurance_agent' exists
```

### "Field required" errors
```
Check backend/.env file exists and has all required fields
(Use .env.example as reference)
```
