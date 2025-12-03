# Project Structure

Complete overview of the codebase organization.

```
interview-manager/
│
├── README.md                           # Main project overview
├── .gitignore                          # Git ignore rules
│
├── shared/                             # Shared documentation
│   ├── api-contract.md                 # API endpoint specifications
│   └── SETUP_GUIDE.md                  # Detailed setup instructions
│
├── backend/                            # Go Backend (Person A)
│   ├── cmd/
│   │   └── server/
│   │       └── main.go                 # Entry point
│   ├── internal/
│   │   ├── handlers/                   # HTTP request handlers
│   │   │   ├── interview.go            # Interview endpoints
│   │   │   ├── integrity.go            # Integrity event handlers
│   │   │   ├── admin.go                # Admin endpoints
│   │   │   └── websocket.go            # WebSocket handler
│   │   ├── models/
│   │   │   └── models.go               # Data structures
│   │   ├── services/
│   │   │   ├── session.go              # Session management
│   │   │   └── llm_client.go           # LLM service client
│   │   └── middleware/
│   │       └── middleware.go           # CORS, logging
│   ├── go.mod                          # Go dependencies
│   ├── .env.example                    # Environment template
│   └── README.md                       # Backend docs
│
├── frontend/                           # TypeScript/React Frontend (Person A)
│   ├── src/
│   │   ├── components/                 # React components
│   │   │   ├── VideoCall.tsx           # Video interface
│   │   │   ├── CodeEditor.tsx          # Monaco editor
│   │   │   └── TranscriptPanel.tsx     # Conversation log
│   │   ├── hooks/                      # Custom React hooks
│   │   │   ├── useVoice.ts             # STT/TTS hooks
│   │   │   └── useIntegrityDetection.ts # Tab detection
│   │   ├── lib/
│   │   │   └── api.ts                  # Backend API client
│   │   ├── pages/                      # Next.js pages
│   │   │   ├── index.tsx               # Home/start page
│   │   │   └── interview/
│   │   │       └── [sessionId].tsx     # Interview page
│   │   └── types/
│   │       └── index.ts                # TypeScript types
│   ├── package.json                    # Node dependencies
│   ├── tsconfig.json                   # TypeScript config
│   ├── next.config.js                  # Next.js config
│   ├── .env.example                    # Environment template
│   └── README.md                       # Frontend docs
│
└── llm-service/                        # Python LLM Service (Person B)
    ├── services/
    │   ├── __init__.py
    │   ├── claude_client.py            # Claude API wrapper
    │   ├── question_generator.py       # Generate questions
    │   ├── evaluator.py                # Evaluate answers
    │   └── report_generator.py         # Generate reports
    ├── main.py                         # FastAPI application
    ├── requirements.txt                # Python dependencies
    ├── .env.example                    # Environment template
    └── README.md                       # LLM service docs
```

## Key Files to Understand

### Backend (Go)
1. **`cmd/server/main.go`** - Server startup, routes definition
2. **`internal/handlers/interview.go`** - Interview flow logic
3. **`internal/services/llm_client.go`** - Communication with Python service
4. **`internal/models/models.go`** - Data structures

### Frontend (TypeScript)
1. **`pages/index.tsx`** - Interview start page
2. **`pages/interview/[sessionId].tsx`** - Main interview UI
3. **`hooks/useVoice.ts`** - Browser speech API integration
4. **`lib/api.ts`** - Backend communication

### LLM Service (Python)
1. **`main.py`** - FastAPI routes
2. **`services/claude_client.py`** - Claude API wrapper
3. **`services/question_generator.py`** - Question generation logic
4. **`services/evaluator.py`** - Answer evaluation logic

## File Responsibilities

### Person A Files (Frontend + Backend)
- All files in `frontend/`
- All files in `backend/`
- Focus: UI/UX, API server, session management

### Person B Files (LLM Service)
- All files in `llm-service/`
- Focus: Claude API, question generation, evaluation

### Shared Files
- `shared/api-contract.md` - Define together
- `shared/SETUP_GUIDE.md` - Reference for both
- `.env` files - Individual configuration

## Integration Points

### 1. API Contract
Both teams agree on:
- Request/response formats
- Endpoint URLs
- Data structures

### 2. Data Flow
```
Frontend → Backend → LLM Service → Claude API
   ↑          ↑           ↑
  User    Sessions    Intelligence
```

### 3. Development Workflow
1. Person B: Build LLM service endpoints
2. Person A: Build backend to call LLM service
3. Person A: Build frontend to call backend
4. Both: Test end-to-end integration

## File Counts

- **Backend (Go)**: 10 files
- **Frontend (TypeScript)**: 15 files
- **LLM Service (Python)**: 6 files
- **Shared/Docs**: 5 files
- **Total**: ~36 files

## Lines of Code (Approximate)

- **Backend**: ~800 lines
- **Frontend**: ~1000 lines
- **LLM Service**: ~500 lines
- **Total**: ~2300 lines

## Technology Split

### Person A (Frontend + Backend)
- **Languages**: Go, TypeScript/JavaScript
- **Frameworks**: Next.js, Gin
- **Tools**: Monaco Editor, Browser APIs

### Person B (LLM Service)
- **Language**: Python
- **Framework**: FastAPI
- **API**: Anthropic Claude

## Next Steps for Each Person

### Person A
1. Start backend server: `cd backend && go run cmd/server/main.go`
2. Start frontend: `cd frontend && npm run dev`
3. Test UI flow without LLM (use mock data)

### Person B
1. Get Claude API key
2. Start LLM service: `cd llm-service && python main.py`
3. Test endpoints with curl/Postman

### Together
1. Test `/api/question/generate` from backend
2. Test full interview flow end-to-end
3. Debug integration issues
4. Polish and add features
