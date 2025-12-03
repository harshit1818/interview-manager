# Complete Setup Guide

Step-by-step guide to get the entire system running.

## Prerequisites

- **Go** 1.21+ ([Download](https://go.dev/dl/))
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.9+ ([Download](https://python.org/downloads/))
- **Claude API Key** ([Get free credits](https://console.anthropic.com/))

---

## Quick Start (5 minutes)

### 1. Clone/Navigate to Project
```bash
cd interview-manager
```

### 2. Start LLM Service (Terminal 1)
```bash
cd llm-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
python main.py
```

**Verify:** Open http://localhost:8000/health

### 3. Start Backend (Terminal 2)
```bash
cd backend
cp .env.example .env
go mod download
go run cmd/server/main.go
```

**Verify:** Open http://localhost:8080/health

### 4. Start Frontend (Terminal 3)
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

**Verify:** Open http://localhost:3000

---

## Detailed Setup

### LLM Service (Python)

1. **Create virtual environment:**
   ```bash
   cd llm-service
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get Claude API key:**
   - Visit https://console.anthropic.com/
   - Sign up (get $5 free credits)
   - Go to API Keys section
   - Create a new API key
   - Copy the key

5. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   ```

6. **Run service:**
   ```bash
   python main.py
   ```

   **Expected output:**
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

7. **Test:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

---

### Backend (Go)

1. **Install dependencies:**
   ```bash
   cd backend
   go mod download
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

   `.env` contents:
   ```
   PORT=8080
   LLM_SERVICE_URL=http://localhost:8000
   ```

3. **Run server:**
   ```bash
   go run cmd/server/main.go
   ```

   **Expected output:**
   ```
   Server starting on port 8080
   ```

4. **Test:**
   ```bash
   curl http://localhost:8080/health
   # Should return: {"status":"healthy"}
   ```

---

### Frontend (TypeScript/React)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   ```

   `.env.local` contents:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8080
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

   **Expected output:**
   ```
   - ready started server on 0.0.0.0:3000
   - Local:   http://localhost:3000
   ```

4. **Test:**
   - Open http://localhost:3000 in browser
   - You should see the interview start page

---

## Testing the Full Flow

### 1. Start an Interview

1. Go to http://localhost:3000
2. Fill in:
   - Name: "Test Candidate"
   - Topic: "DSA"
   - Level: "Junior"
   - Duration: "30 minutes"
3. Click "Start Interview"

### 2. Conduct Interview

1. Allow camera/microphone access
2. You'll see:
   - Your video feed
   - AI interviewer avatar
   - Current question
   - Code editor
   - Transcript panel

3. Click "Start Recording" and answer the question
4. Click "Stop Recording" and "Submit Answer"
5. AI will evaluate and ask follow-up or next question

### 3. Test Integrity Detection

1. Switch to another browser tab → Event logged
2. Click outside the window → Event logged
3. Paste large code → Event logged
4. Check backend logs to see integrity events

### 4. End Interview

1. Click "End Interview"
2. View generated report with scores and recommendations

---

## Troubleshooting

### LLM Service Issues

**Error: "ANTHROPIC_API_KEY not found"**
- Check `.env` file exists in `llm-service/`
- Verify API key is correct
- Make sure to restart Python service after adding key

**Error: "API request failed"**
- Check you have Claude API credits
- Visit https://console.anthropic.com/ to check usage
- Free tier gives $5 (~10-50 interviews)

### Backend Issues

**Error: "Failed to connect to LLM service"**
- Make sure LLM service is running on port 8000
- Check `LLM_SERVICE_URL` in backend `.env`
- Test: `curl http://localhost:8000/health`

**Port already in use:**
```bash
# Change PORT in .env to something else like 8081
PORT=8081
```

### Frontend Issues

**Error: "Failed to fetch"**
- Make sure backend is running on port 8080
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for CORS errors

**Browser microphone not working:**
- Must use HTTPS or localhost
- Check browser permissions
- Some browsers require user gesture to start recording

---

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │  Port 3000 (TypeScript/React)
│  - UI/UX        │  - Video call interface
│  - Voice I/O    │  - Browser Speech API
│  - Integrity    │  - Tab switch detection
└────────┬────────┘
         │ HTTP/WS
         ↓
┌─────────────────┐
│   Backend       │  Port 8080 (Go)
│  - REST API     │  - Session management
│  - WebSocket    │  - State machine
│  - Storage      │  - In-memory DB
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│  LLM Service    │  Port 8000 (Python/FastAPI)
│  - Question Gen │  - Claude API wrapper
│  - Evaluation   │  - Scoring logic
│  - Reports      │  - Analysis
└────────┬────────┘
         │ API
         ↓
┌─────────────────┐
│  Claude API     │  Anthropic
│  - GPT-4 class  │
│  - Reasoning    │
└─────────────────┘
```

---

## Development Workflow

### Person A (Frontend + Backend)
```bash
# Terminal 1: Backend
cd backend && go run cmd/server/main.go

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Person B (LLM Service)
```bash
# Terminal 1: LLM Service
cd llm-service && python main.py
```

### Both: Testing Integration
- Person B implements LLM logic
- Person A calls endpoints from backend
- Test with curl or Postman
- Verify in frontend UI

---

## Next Steps

1. **Add Question Bank:** Create `llm-service/data/questions.json`
2. **Improve UI:** Add Tailwind CSS styling
3. **Add MediaPipe:** Implement face detection
4. **WebRTC:** Add peer-to-peer video
5. **Persistence:** Replace in-memory storage with SQLite
6. **Deploy:** Docker compose for easy deployment

---

## Cost Tracking

**Claude API Usage (per interview):**
- Question generation: ~500 tokens = $0.02
- Evaluation (3-5 rounds): ~2000 tokens = $0.10
- Report generation: ~1000 tokens = $0.05
- **Total per interview: ~$0.15-0.20**

**Free tier covers:**
- $5 free credits = ~25-30 complete interviews

---

## Getting Help

- Check individual README files in each directory
- Review `shared/api-contract.md` for API details
- Check browser console for frontend errors
- Check terminal output for backend/LLM errors
- Test each service independently first
