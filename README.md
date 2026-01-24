# AI-Assisted Insurance Meeting System

A complete end-to-end system enabling insurance companies to run AI-assisted Zoom meetings where staff receive real-time AI support invisible to customers.

## 🎯 Overview

This system provides:
- **SMS Booking Flow**: Send SMS → Customer books via Microsoft Bookings → Receives custom join link
- **Embedded Zoom**: Meetings run inside your website, not zoom.us
- **Real-time Transcription**: Customer speech converted to text via Deepgram
- **AI-Powered RAG**: Gemini AI provides answers based on your insurance knowledge base
- **Staff-Only AI**: Customers never see AI responses - only staff do
- **Voice Responses**: AI answers converted to voice for natural customer interaction

---

## 🏗️ Architecture

### Backend (Python/FastAPI)
- REST API for session/lead management
- WebSocket server for real-time events
- Twilio SMS integration
- Microsoft Bookings webhook handling
- Zoom Meeting API & SDK signature generation
- Deepgram live transcription
- Pinecone vector database (RAG)
- Google Gemini LLM
- ElevenLabs TTS (optional)

### Frontend (React/TypeScript)
- **Admin Page**: Send SMS, view sessions
- **Agent Assist Page**: Zoom meeting + AI suggestions + live transcription
- **Customer Join Page**: Simple Zoom meeting interface

---

## 📋 Prerequisites

### Required Services & API Keys
1. **Twilio** - SMS sending
2. **Microsoft Graph API** - Outlook Bookings integration
3. **Zoom** - Meetings API & Web SDK
4. **Deepgram** - Speech-to-text
5. **Google Gemini** - LLM responses
6. **Pinecone** - Vector database
7. **ElevenLabs** (Optional) - Text-to-speech

### System Requirements
- Python 3.9+
- Node.js 18+
- npm or yarn

---

## 🚀 Installation

### 1. Clone and Setup

```bash
cd "d:\Insurance Agent"
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### 4. Environment Configuration

Create `.env` file in the root directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Backend
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

MS_CLIENT_ID=your_microsoft_client_id
MS_CLIENT_SECRET=your_microsoft_client_secret
MS_TENANT_ID=your_microsoft_tenant_id

ZOOM_API_KEY=your_zoom_api_key
ZOOM_API_SECRET=your_zoom_api_secret
ZOOM_SDK_KEY=your_zoom_sdk_key
ZOOM_SDK_SECRET=your_zoom_sdk_secret

DEEPGRAM_API_KEY=your_deepgram_api_key

GOOGLE_API_KEY=your_google_api_key

PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=insurance-knowledge

ELEVENLABS_API_KEY=your_elevenlabs_api_key (optional)

DOMAIN=https://yourdomain.com

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ZOOM_SDK_KEY=your_zoom_sdk_key
```

---

## 📚 RAG Knowledge Base Setup

### Ingest Sample Insurance Documents

```bash
cd backend
python scripts/ingest_documents.py --sample
```

This creates sample insurance policies (life, auto, home) and uploads them to Pinecone.

### Ingest Your Own Documents

```bash
# Place your PDF, DOCX, or TXT files in a directory
python scripts/ingest_documents.py --directory /path/to/your/documents
```

Supported formats:
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)

---

## 🏃 Running the Application

### Start Backend

```bash
cd backend
python main.py
```

Backend runs on `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:5173`

---

## 📱 Usage Guide

### 1. Send SMS to Customer (Admin)

1. Navigate to `http://localhost:5173/admin`
2. Enter customer phone number and name
3. Click "Send SMS"
4. Customer receives SMS with Microsoft Bookings link

### 2. Customer Books Meeting

1. Customer clicks Bookings link from SMS
2. Selects meeting time in Microsoft Bookings
3. Receives email with join link: `https://yourdomain.com/join/{sessionId}`

### 3. Customer Joins Meeting

1. Customer clicks join link at meeting time
2. Zoom loads in browser
3. System marks customer as joined

### 4. Staff Joins Meeting

1. Staff opens Admin panel
2. Clicks "Open Session" for active session
3. Agent Assist page loads with:
   - Zoom meeting (left panel)
   - Live transcription (right top)
   - AI suggestions (right middle)
   - RAG context (right bottom)

### 5. AI-Assisted Consultation

1. Customer speaks
2. Deepgram transcribes in real-time
3. System sends transcription to RAG
4. Gemini generates answer
5. **Staff sees**: AI answer + follow-up question + context
6. **Customer sees**: Nothing (just Zoom meeting)
7. (Optional) AI answer converted to voice and played to customer

---

## 🔧 API Endpoints

### Sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `POST /api/sessions/{id}/join` - Join session

### Leads
- `POST /api/leads` - Create lead and send SMS
- `GET /api/leads` - List all leads

### Zoom
- `POST /api/zoom/signature` - Generate SDK signature
- `POST /api/zoom/meeting` - Create meeting

### AI/RAG
- `POST /api/ai/query` - Query AI with RAG context
- `GET /api/ai/context/{query}` - Get RAG context only

### WebSocket
- `WS /ws/{session_id}?role=staff` - Real-time events

---

## 🎨 Frontend Routes

- `/` or `/admin` - Admin dashboard
- `/agent/{sessionId}` - Agent assist page (staff)
- `/join/{sessionId}` - Customer join page

---

## 🔐 Security Considerations

- **Staff Authentication**: Implement proper auth before production
- **API Rate Limiting**: Add rate limiting to prevent abuse
- **Session Expiration**: Sessions expire after 24 hours (configurable)
- **HTTPS Required**: Use HTTPS in production for webhooks
- **Environment Variables**: Never commit `.env` file

---

## 🚀 Deployment

### Backend Deployment

Recommended providers:
- **Railway** - Easy Python deployment
- **Render** - Supports WebSockets
- **AWS EC2** - Full control
- **Google Cloud Run** - Serverless option

Requirements:
- Python 3.9+
- Publicly accessible for webhooks
- WebSocket support
- HTTPS/SSL

### Frontend Deployment

Recommended providers:
- **Vercel** - Automatic deployments
- **Netlify** - Simple setup
- **AWS S3 + CloudFront** - Cost-effective

Build command:
```bash
npm run build
```

---

## 🛠️ Troubleshooting

### Backend won't start
- Check all environment variables are set
- Ensure Python 3.9+ is installed
- Verify virtual environment is activated

### Frontend can't connect to backend
- Check `VITE_API_URL` in `.env`
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`

### Zoom not loading
- Verify `ZOOM_SDK_KEY` and `ZOOM_SDK_SECRET`
- Check browser console for errors
- Ensure meeting ID and signature are valid

### Transcription not working
- Check `DEEPGRAM_API_KEY`
- Verify microphone permissions in browser
- Check WebSocket connection

### AI not responding
- Verify `GOOGLE_API_KEY` (Gemini)
- Check `PINECONE_API_KEY` and index exists
- Run document ingestion script
- Check logs for errors

---

## 📊 Project Structure

```
d:\Insurance Agent\
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Configuration
│   ├── models.py                # Pydantic models
│   ├── routes/                  # API routes
│   ├── services/                # External services
│   ├── rag/                     # RAG system
│   ├── websocket/               # WebSocket handlers
│   └── scripts/                 # Utility scripts
├── frontend/
│   ├── src/
│   │   ├── pages/              # React pages
│   │   ├── components/         # React components
│   │   ├── services/           # API & WebSocket clients
│   │   └── hooks/              # Custom React hooks
│   └── package.json
├── .env                        # Environment variables
├── .env.example                # Template
└── README.md                   # This file
```

---

## 🤝 Support

For issues or questions:
1. Check this README
2. Review API docs at `/docs`
3. Check browser console for errors
4. Review backend logs

---

## 📝 License

Proprietary - All rights reserved

---

## ✅ Next Steps

1. ✅ Set up all API keys in `.env`
2. ✅ Run document ingestion script
3. ✅ Test SMS sending
4. ✅ Configure Microsoft Bookings webhook
5. ✅ Test full end-to-end flow
6. ✅ Deploy to production
7. ✅ Set up custom domain
8. ✅ Enable HTTPS/SSL
9. ✅ Implement staff authentication
10. ✅ Monitor and optimize

---

**Built with ❤️ for insurance consultations**
