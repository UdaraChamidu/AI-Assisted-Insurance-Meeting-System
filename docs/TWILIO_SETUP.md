# Twilio Setup Guide with ngrok

This guide will help you set up Twilio for SMS functionality and configure webhooks using ngrok for local development.

---

## 📱 Part 1: Twilio Account Setup

### Step 1: Create Twilio Account

1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free account
3. Verify your email and phone number
4. You'll receive **$15 trial credit** 🎉

### Step 2: Get Your Twilio Credentials

1. After login, go to the **Twilio Console Dashboard**
2. Find your credentials (you'll see them immediately):
   - **Account SID** (looks like: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Auth Token** (click "Show" to reveal it)

3. Copy these and add to your `.env` file:
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   ```

### Step 3: Get a Phone Number

1. In Twilio Console, go to **Phone Numbers** > **Manage** > **Buy a number**
2. Select your country (e.g., United States)
3. Check **SMS** capability
4. Click **Search**
5. Choose a number and click **Buy**
6. Confirm purchase (uses trial credit)

7. Copy your new phone number and add to `.env`:
   ```env
   TWILIO_PHONE_NUMBER=+15551234567
   ```

### Step 4: Verify Test Phone Numbers (Trial Account)

⚠️ **Important**: Trial accounts can only send SMS to **verified phone numbers**

1. Go to **Phone Numbers** > **Manage** > **Verified Caller IDs**
2. Click **Add a new Caller ID**
3. Enter the phone number you want to test with
4. Verify via SMS or phone call
5. Now you can send SMS to this number!

---

## 🌐 Part 2: ngrok Setup for Local Development

ngrok creates a public URL that tunnels to your local development server. This is essential for Twilio webhooks during development.

### Step 1: Install ngrok

**Windows:**
```powershell
# Download from ngrok.com/download
# Or use Chocolatey:
choco install ngrok

# Or use Scoop:
scoop install ngrok
```

**Mac:**
```bash
brew install ngrok/ngrok/ngrok
```

**Linux:**
```bash
# Download and unzip
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok
```

### Step 2: Create ngrok Account (Free)

1. Go to [ngrok.com](https://ngrok.com/)
2. Sign up for free account
3. Go to **Getting Started** > **Your Authtoken**
4. Copy your auth token

5. Connect your account:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
   ```

### Step 3: Start ngrok Tunnel

1. **First, start your backend server:**
   ```bash
   cd backend
   python main.py
   # Server running on http://localhost:8000
   ```

2. **In a new terminal, start ngrok:**
   ```bash
   ngrok http 8000
   ```

3. **You'll see output like this:**
   ```
   ngrok                                                                    
   
   Session Status                online                                     
   Account                       you@email.com                              
   Version                       3.5.0                                      
   Region                        United States (us)                         
   Latency                       49ms                                       
   Web Interface                 http://127.0.0.1:4040                      
   Forwarding                    https://abc123def456.ngrok-free.app -> http://localhost:8000
   
   Connections                   ttl     opn     rt1     rt5     p50     p90
                                 0       0       0.00    0.00    0.00    0.00
   ```

4. **Copy the HTTPS URL** (e.g., `https://abc123def456.ngrok-free.app`)

   ⚠️ **Important**: Always use the **HTTPS** URL, not HTTP!

### Step 4: ngrok Web Interface (Optional but Useful)

While ngrok is running, open [http://localhost:4040](http://localhost:4040) in your browser.

This shows:
- All HTTP requests to your tunnel
- Request/response details
- Replay requests
- Very helpful for debugging!

---

## 🔗 Part 3: Configure Twilio Webhooks

### SMS Status Callbacks (Optional)

If you want to track SMS delivery status:

1. Go to **Phone Numbers** > **Manage** > **Active Numbers**
2. Click your phone number
3. Scroll to **Messaging Configuration**
4. Under **A MESSAGE COMES IN**:
   - Webhook: `https://YOUR-NGROK-URL.ngrok-free.app/api/twilio/sms-webhook`
   - HTTP Method: `POST`
5. Click **Save**

### Testing the Webhook

Create a webhook endpoint in your backend (optional for now):

```python
# backend/routes/twilio_webhook.py
from fastapi import APIRouter, Form

router = APIRouter(prefix="/api/twilio", tags=["twilio"])

@router.post("/sms-webhook")
async def sms_status_webhook(
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    To: str = Form(...),
    From: str = Form(...)
):
    """Handle SMS status updates from Twilio."""
    logger.info(f"SMS Status: {MessageStatus} for {MessageSid}")
    return {"status": "ok"}
```

---

## ✅ Part 4: Test Your Setup

### Test 1: Send SMS via API

1. **Start your backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Start ngrok** (new terminal):
   ```bash
   ngrok http 8000
   ```

3. **Test SMS sending:**

   **Option A: Using curl**
   ```bash
   curl -X POST http://localhost:8000/api/leads \
     -H "Content-Type: application/json" \
     -d '{
       "phone_number": "+1YOUR_VERIFIED_NUMBER",
       "customer_name": "Test Customer",
       "notes": "Test message"
     }'
   ```

   **Option B: Using your frontend**
   - Open `http://localhost:5173/admin`
   - Fill in the SMS form
   - Use your verified phone number
   - Click "Send SMS"

4. **Check your phone** - you should receive the SMS! 📱

### Test 2: Check SMS in Twilio Dashboard

1. Go to **Monitor** > **Logs** > **Messaging**
2. You'll see your sent messages
3. Check status: `queued` → `sent` → `delivered`

---

## 🚨 Common Issues & Solutions

### Issue 1: "Permission Denied" or "Unauthorized"

**Solution:** Double-check your `.env` file:
```env
TWILIO_ACCOUNT_SID=AC...  # Must start with AC
TWILIO_AUTH_TOKEN=...      # Get from Twilio Console (show token)
```

### Issue 2: "The number +1... is unverified"

**Solution:** 
- Trial accounts can only send to verified numbers
- Verify your test number in Twilio Console
- Or upgrade to paid account ($20 minimum)

### Issue 3: ngrok "Too Many Connections"

**Solution:**
- Free ngrok has connection limits
- Restart ngrok tunnel
- Or sign up for ngrok paid plan

### Issue 4: ngrok URL keeps changing

**Solution:**
- Free ngrok generates new URL each restart
- For persistent URL, upgrade to ngrok paid ($8/month)
- Or use other services: localtunnel, serveo, cloudflare tunnel

### Issue 5: "Webhook timeout"

**Solution:**
- Check your backend is running
- Verify ngrok is forwarding to correct port (8000)
- Check ngrok web interface (localhost:4040) for errors

---

## 💰 Twilio Pricing (Post-Trial)

- **Phone Number**: ~$1/month
- **SMS**: ~$0.0075 per message (US)
- **Minimum balance**: $20
- **Trial credit**: $15 (free)

You can test extensively with trial credit!

---

## 🔄 Alternative to ngrok

If you prefer other tunneling services:

### 1. **localtunnel** (Completely Free)
```bash
npm install -g localtunnel
lt --port 8000
```

### 2. **Cloudflare Tunnel** (Free)
```bash
# Install cloudflared
cloudflared tunnel --url http://localhost:8000
```

### 3. **serveo** (Free, no installation)
```bash
ssh -R 80:localhost:8000 serveo.net
```

---

## 📝 Quick Reference

### Your Setup Checklist

- [ ] Twilio account created
- [ ] Account SID and Auth Token copied to `.env`
- [ ] Phone number purchased
- [ ] Phone number added to `.env`
- [ ] Test phone number verified (for trial)
- [ ] ngrok installed
- [ ] ngrok authtoken configured
- [ ] Backend running (`python main.py`)
- [ ] ngrok tunnel running (`ngrok http 8000`)
- [ ] Test SMS sent successfully ✅

### Important URLs

- **Twilio Console**: https://console.twilio.com
- **ngrok Dashboard**: https://dashboard.ngrok.com
- **ngrok Web Interface**: http://localhost:4040
- **Your Backend**: http://localhost:8000
- **Your Frontend**: http://localhost:5173

---

## 🎯 Next Steps

Once Twilio is working:

1. **Test the full flow:**
   - Send SMS → Customer books meeting → Join link generated

2. **Set up other services:**
   - Microsoft Bookings (similar webhook setup)
   - Zoom integration
   - Deepgram transcription

3. **For production:**
   - Upgrade Twilio account (remove restrictions)
   - Use proper domain (no ngrok)
   - Set up webhook endpoints on production server

---

## 🆘 Need Help?

**Twilio Issues:**
- Check: https://www.twilio.com/docs/sms/quickstart/python
- Support: https://support.twilio.com

**ngrok Issues:**
- Check: https://ngrok.com/docs
- Troubleshooting: https://ngrok.com/docs/errors

**Our Backend Issues:**
- Check backend logs: `python main.py` output
- Check ngrok requests: http://localhost:4040
- Verify `.env` file is loaded

---

**You're all set! 🎉 Try sending your first SMS!**
