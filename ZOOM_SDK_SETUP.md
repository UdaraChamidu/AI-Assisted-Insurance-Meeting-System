# Zoom Meeting SDK Setup Guide

## The Problem
You're currently using **OAuth Client credentials** for the Meeting SDK, which causes "Invalid signature" errors.

You need **two separate sets** of Zoom credentials:

1. **Server-to-Server OAuth** (for creating meetings via API)
   - Used: ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
   - ✅ You already have these configured correctly

2. **Meeting SDK** (for joining meetings in the browser)
   - Used: ZOOM_SDK_KEY, ZOOM_SDK_SECRET
   - ❌ Currently using OAuth credentials (wrong!)

---

## How to Get Meeting SDK Credentials

### Step 1: Go to Zoom Marketplace
1. Visit: https://marketplace.zoom.us/
2. Sign in with your Zoom account
3. Click "Develop" → "Build App"

### Step 2: Create a Meeting SDK App
1. Click "Create" under **"Meeting SDK"** (NOT Server-to-Server OAuth)
2. Give your app a name (e.g., "Insurance Agent Meeting SDK")
3. Choose "User-managed app" or "Account-level app"
4. Click "Create"

### Step 3: Get Your SDK Credentials
1. After creating the app, go to the "App Credentials" tab
2. You'll see:
   - **SDK Key** (looks like: `KgNwpTllS-ahh0098ImRNg`)
   - **SDK Secret** (looks like: `abc123xyz456...`)
3. Copy these values

### Step 4: Update Your .env File
Open `backend/.env` and replace:

```env
# WRONG - Currently using Client ID/Secret
ZOOM_SDK_KEY=_8J7Z4ntQeKo5iM7dYIi8Q
ZOOM_SDK_SECRET=7pNa498xgo6l2LtfRgF51Q5voHBVxnsu

# CORRECT - Use your new Meeting SDK credentials
ZOOM_SDK_KEY=<your-actual-sdk-key>
ZOOM_SDK_SECRET=<your-actual-sdk-secret>
```

Also update `frontend/.env`:
```env
VITE_ZOOM_SDK_KEY=<your-actual-sdk-key>
```

### Step 5: Activate the App
1. In the Zoom Marketplace, go to "Activation" tab
2. Toggle "Activated" to ON
3. Accept any terms if prompted

### Step 6: Restart Your Servers
```bash
# Backend
cd backend
# Restart the server (Ctrl+C then rerun)

# Frontend
cd frontend
# Restart the server (Ctrl+C then rerun)
```

---

## Summary of All Zoom Credentials

You need **BOTH** of these apps in Zoom Marketplace:

| Purpose | App Type | Credentials Needed |
|---------|----------|-------------------|
| Create meetings via API | Server-to-Server OAuth | ZOOM_ACCOUNT_ID<br>ZOOM_CLIENT_ID<br>ZOOM_CLIENT_SECRET |
| Join meetings in browser | Meeting SDK | ZOOM_SDK_KEY<br>ZOOM_SDK_SECRET |

---

## Testing
After updating credentials and restarting:
1. Try joining a Zoom meeting
2. Check browser console - should see "Successfully joined meeting"
3. No more "Invalid signature" errors

---

## Still Having Issues?

Check the Zoom Meeting SDK documentation:
https://developers.zoom.us/docs/meeting-sdk/web/
