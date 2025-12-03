# AI-Powered Video Interview System

A prototype system for conducting AI-powered technical interviews with integrity detection.

## Project Structure

```
interview-manager/
├── backend/           # Go backend server
├── frontend/          # TypeScript/React frontend
├── llm-service/       # Python LLM integration
├── shared/            # Shared types and documentation
└── README.md
```

## Tech Stack

- **Backend**: Go (REST API, session management)
- **Frontend**: TypeScript + React + Next.js
- **LLM Service**: Python + Claude API
- **Video**: WebRTC (peer.js)
- **Code Editor**: Monaco Editor
- **Voice**: Browser Web Speech API (STT/TTS)

## Quick Start

**See detailed guide:** `shared/SETUP_GUIDE.md`

### 1. Start LLM Service (Terminal 1)
```bash
cd llm-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
python main.py
```

### 2. Start Backend (Terminal 2)
```bash
cd backend
go mod download
cp .env.example .env
go run cmd/server/main.go
```

### 3. Start Frontend (Terminal 3)
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Then open http://localhost:3000

## Free Tools Used

- ✅ Claude API (Free tier)
- ✅ Browser Web Speech API (Free)
- ✅ MediaPipe Face Detection (Free)
- ✅ WebRTC P2P (Free)
- ✅ Monaco Editor (Free)

## Architecture

```
Frontend (TypeScript) → Go Backend → Python LLM Service → Claude API
     ↓                       ↓                ↓
  Browser APIs        REST API + WS      Evaluation Logic
```

## API Endpoints

See `shared/api-contract.md` for full API documentation.

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

## Development

Person A: Frontend + Backend
Person B: LLM Service + Intelligence Layer

## Demo Flow

1. Admin creates interview session
2. Candidate joins → Consent screen
3. AI greets candidate (TTS)
4. Interview loop: Question → Answer → Evaluate → Follow-up
5. Integrity detection (tab switch, multiple faces)
6. Generate final report

## License

MIT
