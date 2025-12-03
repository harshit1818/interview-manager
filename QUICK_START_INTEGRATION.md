# Quick Start: Integration Guide

**Goal:** Get all 3 services running together in 30 minutes

---

## ⚡ Super Quick Start (Copy-Paste Commands)

### **Terminal 1: LLM Service** (Person B's work)
```bash
cd llm-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# IMPORTANT: Edit .env and add ANTHROPIC_API_KEY=your_key_here
python main.py
```
**Expected:** `Uvicorn running on http://0.0.0.0:8000`

### **Terminal 2: Backend** (Your work)
```bash
cd backend
go mod download
cp .env.example .env
go run cmd/server/main.go
```
**Expected:** `Server starting on port 8080`

### **Terminal 3: Frontend** (Your work - already running)
```bash
cd frontend
npm run dev
```
**Expected:** `Local: http://localhost:3000`

---

## ✅ **Verification Steps**

### **1. Check All Services Running:**
```bash
# In a new terminal:
curl http://localhost:8000/health  # LLM Service
curl http://localhost:8080/health  # Backend
curl http://localhost:3000         # Frontend (open in browser)
```

All should return 200 OK ✓

### **2. Test the Chain:**
```bash
# Test LLM Service directly:
curl -X POST http://localhost:8000/api/question/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"DSA","difficulty":"Junior","position":0}'

# Should return a question JSON ✓

# Test Backend calling LLM Service:
curl -X POST http://localhost:8080/api/interview/start \
  -H "Content-Type: application/json" \
  -d '{"candidateName":"Test","topic":"DSA","difficulty":"Junior","duration":30}'

# Should return sessionId and firstQuestion ✓
```

### **3. Test in Browser:**
1. Open http://localhost:3000
2. Fill form: Name, Topic (DSA), Difficulty (Junior), Duration (30 min)
3. Click "Start Interview"
4. Should navigate to interview page ✓
5. Should show a question ✓
6. AI should speak the question ✓

---

## 🎯 **What Each Service Does**

```
┌──────────────────────────────────────────┐
│  Browser (http://localhost:3000)        │
│  - Shows UI                              │
│  - Captures voice/video                  │
│  - Sends to Backend                      │
└─────────────┬────────────────────────────┘
              │ POST /api/interview/start
              ↓
┌──────────────────────────────────────────┐
│  Backend (http://localhost:8080)         │
│  - Manages sessions                      │
│  - Routes requests                       │
│  - Stores state                          │
└─────────────┬────────────────────────────┘
              │ POST /api/question/generate
              ↓
┌──────────────────────────────────────────┐
│  LLM Service (http://localhost:8000)     │
│  - Generates questions                   │
│  - Evaluates answers                     │
│  - Creates reports                       │
└─────────────┬────────────────────────────┘
              │ API Call
              ↓
┌──────────────────────────────────────────┐
│  Claude API (Anthropic)                  │
│  - LLM reasoning                         │
│  - Natural language processing           │
└──────────────────────────────────────────┘
```

---

## 🐛 **Quick Troubleshooting**

### **Problem: LLM Service won't start**
```bash
# Check Python version (need 3.9+)
python --version

# Check if venv activated (should see (venv) in prompt)
source venv/bin/activate

# Check dependencies
pip list | grep anthropic

# Check API key
cat .env | grep ANTHROPIC_API_KEY
```

### **Problem: Backend won't start**
```bash
# Check Go installed
go version

# Check Go dependencies
go mod download

# Check port 8080 not in use
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows
```

### **Problem: Frontend can't connect**
```bash
# Check .env.local
cat .env.local
# Should have: NEXT_PUBLIC_API_URL=http://localhost:8080

# Check backend is running
curl http://localhost:8080/health

# Check browser console for errors
```

---

## 📝 **Environment Files Setup**

### **1. llm-service/.env**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

### **2. backend/.env**
```bash
PORT=8080
LLM_SERVICE_URL=http://localhost:8000
```

### **3. frontend/.env.local**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

---

## 🎬 **First Test (Manual)**

Once all 3 services are running:

**1. Open browser:** http://localhost:3000

**2. Start interview:**
- Name: "Test Candidate"
- Topic: "DSA"
- Difficulty: "Junior"
- Duration: "30 minutes"
- Click "Start Interview"

**3. You should see:**
- Interview page loads ✓
- Question displays ✓
- AI speaks the question ✓
- Can click "Start Recording" ✓
- Can speak and see transcript ✓
- Can submit answer ✓

**4. After submit:**
- AI evaluates your answer ✓
- AI asks follow-up or next question ✓
- Conversation continues ✓

**5. End interview:**
- Click "End Interview" ✓
- Report generates ✓
- Scores display ✓

---

## 📊 **Expected Terminal Outputs**

### **Terminal 1 (LLM Service):**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     127.0.0.1:54321 - "POST /api/question/generate HTTP/1.1" 200 OK
```

### **Terminal 2 (Backend):**
```
Server starting on port 8080
[POST] /api/interview/start - 200 (1.2s)
[POST] /api/interview/respond - 200 (1.5s)
```

### **Terminal 3 (Frontend):**
```
✓ Ready in 3s
✓ Compiled / in 1.2s
GET / 200 in 24ms
GET /interview/abc123 200 in 45ms
```

---

## ⏱️ **Timeline**

### **Phase 1: Setup** (30 min)
- Install dependencies (all 3 services)
- Configure environment variables
- Start all services

### **Phase 2: First Test** (1 hour)
- Test services independently
- Test service connections
- Fix configuration issues

### **Phase 3: Integration** (2 hours)
- Test full flow
- Debug issues
- Verify all features work

### **Phase 4: Polish** (1 hour)
- Fix UI issues
- Improve error messages
- Test edge cases

**Total:** ~5 hours to full working system

---

## 🎉 **Success Criteria**

You'll know it's working when:
- ✅ All 3 terminals show "running" status
- ✅ Can complete a full interview
- ✅ Questions make sense
- ✅ AI evaluates answers
- ✅ Report generates
- ✅ Integrity warnings appear
- ✅ No errors in any terminal
- ✅ No errors in browser console

---

## 🚀 **Ready to Integrate!**

**Current Status:**
- ✅ Frontend: Working perfectly
- ⏳ Backend: Ready to start
- ⏳ LLM Service: Waiting for Person B

**Next Step:** Wait for Person B to say "LLM service is ready!" then follow this guide.

**Estimated Time to Full Integration:** ~5-7 days
- Days 1-2: Person B completes LLM service
- Days 3-4: You start and test backend
- Day 5-7: Integration and polish

---

## 📞 **Need Help?**

**Check these files:**
- `shared/api-contract.md` - API specifications
- `shared/SETUP_GUIDE.md` - Detailed setup
- `PERSON_B_BRIEFING.md` - For Person B
- `VIDEO_INTERVIEW_FEATURES.md` - Frontend features

**Your frontend is ready! Just waiting for backend + LLM integration.** 🎯
