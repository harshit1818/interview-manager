# Frontend + Backend Integration Plan

**Goal:** Connect all 3 services to create a working end-to-end AI video interview system

**Team:** 2 people working together
- **Person A (You):** Frontend + Backend (Go)
- **Person B:** LLM Service (Python)

---

## 🎯 Overview

```
┌─────────────────┐
│   Frontend      │  You built ✓ (Port 3000)
│  (TypeScript)   │  - Video + Voice working
│                 │  - UI complete
└────────┬────────┘
         │ HTTP REST API
         ↓
┌─────────────────┐
│   Backend       │  To build (Port 8080)
│     (Go)        │  - API endpoints
│                 │  - Session management
└────────┬────────┘
         │ HTTP REST API
         ↓
┌─────────────────┐
│  LLM Service    │  Person B builds (Port 8000)
│   (Python)      │  - Question generation
│                 │  - Answer evaluation
└────────┬────────┘
         │
         ↓
   Claude API (Anthropic)
```

---

## 📋 Integration Phases

### **Phase 1: Independent Development** ✅ DONE
**Status:** Both teams build independently

**Person A (You):**
- ✅ Frontend UI complete
- ✅ Voice integration working
- ✅ Video analysis working
- ✅ Mock data ready

**Person B:**
- ⏳ LLM service skeleton created
- ⏳ Needs to implement 3 endpoints
- ⏳ Needs Claude API key

**Timeline:** Complete

---

### **Phase 2: Person B Builds LLM Service** ⏳ IN PROGRESS
**Goal:** Get Python service running with Claude API

**Person B Tasks:**
1. ✅ Setup Python environment
2. ⏳ Get Claude API key from https://console.anthropic.com/
3. ⏳ Implement question generation endpoint
4. ⏳ Implement evaluation endpoint
5. ⏳ Implement report generation endpoint
6. ⏳ Test with curl/Postman

**Person B Deliverables:**
```bash
# These should work:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/question/generate -d '{"topic":"DSA","difficulty":"Junior","position":0}'
```

**Timeline:** 2-3 days
**Files:** `llm-service/*` (Person B works here)

---

### **Phase 3: Person A Builds Go Backend** ⏳ NEXT
**Goal:** Create REST API that connects frontend to LLM service

**Your Tasks:**
1. ⏳ Setup Go environment
2. ⏳ Install Go dependencies
3. ⏳ Test backend starts successfully
4. ⏳ Test backend can call Person B's Python service
5. ⏳ Implement session management
6. ⏳ Test all endpoints

**Your Deliverables:**
```bash
# These should work:
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/interview/start -d '{"candidateName":"Test","topic":"DSA","difficulty":"Junior","duration":30}'
```

**Timeline:** 1-2 days
**Files:** `backend/*` (You work here)

---

### **Phase 4: Connect Frontend to Backend** ⏳ AFTER PHASE 3
**Goal:** Make your frontend call your backend

**Your Tasks:**
1. ⏳ Update `.env.local` with backend URL
2. ⏳ Test API calls from browser
3. ⏳ Handle loading states
4. ⏳ Handle errors gracefully
5. ⏳ Test full flow

**Changes Needed:**
- Minimal! API client already built in `src/lib/api.ts`
- Just need backend running

**Timeline:** 1-2 hours

---

### **Phase 5: End-to-End Integration** ⏳ FINAL
**Goal:** All 3 services working together

**Full Stack Running:**
```bash
# Terminal 1: LLM Service (Person B)
cd llm-service && python main.py

# Terminal 2: Backend (You)
cd backend && go run cmd/server/main.go

# Terminal 3: Frontend (You)
cd frontend && npm run dev
```

**Test Complete Flow:**
1. Open http://localhost:3000
2. Fill form → Start interview
3. Interview page loads
4. AI speaks first question (TTS)
5. Click "Start Recording" → Answer question
6. Submit answer → AI evaluates
7. AI asks follow-up or next question
8. Complete interview → See report

**Timeline:** 1 day of testing & bug fixing

---

## 🔄 **Detailed Integration Steps**

### **Step 1: Person B Completes LLM Service** (Days 1-2)

**Person B checklist:**
- [ ] Python venv setup
- [ ] Dependencies installed
- [ ] Claude API key configured
- [ ] `/api/question/generate` working
- [ ] `/api/evaluate` working
- [ ] `/api/report/generate` working
- [ ] Can test with curl
- [ ] Returns valid JSON

**How to verify:**
```bash
# Person B tests:
curl -X POST http://localhost:8000/api/question/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"DSA","difficulty":"Junior","position":0}'

# Should return a question JSON
```

---

### **Step 2: Person A Builds Go Backend** (Days 2-3)

**Your checklist:**
- [ ] Go installed
- [ ] Dependencies downloaded: `go mod download`
- [ ] Environment configured
- [ ] Backend starts: `go run cmd/server/main.go`
- [ ] Health check works: `curl http://localhost:8080/health`
- [ ] Can call Person B's service
- [ ] All endpoints implemented

**How to verify:**
```bash
# You test:
curl -X POST http://localhost:8080/api/interview/start \
  -H "Content-Type: application/json" \
  -d '{"candidateName":"Test","topic":"DSA","difficulty":"Junior","duration":30}'

# Should return sessionId and firstQuestion
```

**Key Files You'll Work On:**
- `backend/cmd/server/main.go` - Already created ✓
- `backend/internal/handlers/*` - Already created ✓
- `backend/internal/services/*` - Already created ✓

**Just need to:**
1. Install Go
2. Run `go mod download`
3. Test it works!

---

### **Step 3: Connect Frontend to Backend** (Day 3)

**Your tasks:**
1. Make sure backend is running on port 8080
2. Frontend is already configured to call it!
3. Test the flow

**Test:**
```bash
# Backend running in Terminal 1
cd backend && go run cmd/server/main.go

# Frontend running in Terminal 2
cd frontend && npm run dev

# Open browser
http://localhost:3000
```

**What should happen:**
- Fill form → Submit
- Should navigate to `/interview/[sessionId]`
- Should show first question
- AI should speak the question
- You can answer and submit

**If errors occur:**
- Check browser console
- Check backend terminal logs
- Check Person B's Python service logs
- Verify all 3 services running

---

### **Step 4: Full Integration Testing** (Day 4)

**End-to-End Test:**

1. **Start all services:**
```bash
# Terminal 1: Person B's LLM Service
cd llm-service
source venv/bin/activate
python main.py
# Should see: Uvicorn running on http://0.0.0.0:8000

# Terminal 2: Your Backend
cd backend
go run cmd/server/main.go
# Should see: Server starting on port 8080

# Terminal 3: Your Frontend
cd frontend
npm run dev
# Should see: Local: http://localhost:3000
```

2. **Test Flow:**
   - [ ] Home page loads
   - [ ] Can start interview
   - [ ] Interview page loads
   - [ ] Question displays
   - [ ] AI speaks question (TTS)
   - [ ] Can record answer (STT)
   - [ ] Can submit answer
   - [ ] AI evaluates and responds
   - [ ] Follow-up or next question
   - [ ] Can end interview
   - [ ] Report generates

3. **Test Integrity:**
   - [ ] Tab switch → Warning shows
   - [ ] Look away → Warning shows
   - [ ] Multiple faces → Warning shows
   - [ ] Events logged in backend

---

## 🔗 **Integration Points (Where Services Connect)**

### **1. Frontend → Backend**
**File:** `src/lib/api.ts` (Already built ✓)

**Endpoints used:**
```typescript
POST /api/interview/start
POST /api/interview/respond
POST /api/interview/end
GET /api/interview/status/:sessionId
POST /api/integrity/event
```

**What happens:**
1. User clicks "Start Interview"
2. Frontend calls `interviewAPI.start(formData)`
3. Backend receives request
4. Backend calls LLM service
5. Backend returns response
6. Frontend shows question

---

### **2. Backend → LLM Service**
**File:** `backend/internal/services/llm_client.go` (Already built ✓)

**Endpoints used:**
```go
POST /api/question/generate
POST /api/evaluate
POST /api/report/generate
```

**What happens:**
1. Backend receives request from frontend
2. Backend calls `llmClient.GetFirstQuestion(topic, difficulty)`
3. LLM service calls Claude API
4. LLM service returns question JSON
5. Backend returns to frontend

---

## 🧪 **Testing Strategy**

### **Test Independently First**

**Person A (You):**
```bash
# Test frontend with mock data
cd frontend
npm run dev
# Open http://localhost:3000/test-voice
# Open http://localhost:3000/test-video
```

**Person B:**
```bash
# Test LLM service with curl
cd llm-service
python main.py

# In another terminal:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/question/generate ...
```

**Together:**
Test backend calling LLM service:
```bash
# Terminal 1: Person B starts LLM service
python main.py

# Terminal 2: Person A starts backend
go run cmd/server/main.go

# Terminal 3: Person A tests
curl -X POST http://localhost:8080/api/interview/start ...
```

---

### **Test Together (Integration)**

**Scenario 1: Happy Path**
1. Start interview
2. Answer 3 questions
3. End interview
4. View report

**Scenario 2: Integrity Events**
1. Start interview
2. Switch tab → Warning
3. Look away → Warning
4. Have someone join → Warning
5. Check events in report

**Scenario 3: Error Handling**
1. Kill LLM service
2. Try to start interview
3. Should show error message
4. Restart LLM service
5. Should work again

---

## 📊 **Integration Checklist**

### **Before Integration:**
- [x] Frontend works independently
- [x] Voice test page works
- [x] Video test page works
- [ ] Person B's LLM service works
- [ ] Person A's Go backend works

### **During Integration:**
- [ ] All 3 services start without errors
- [ ] Health checks pass for all services
- [ ] Backend can reach LLM service
- [ ] Frontend can reach backend
- [ ] CORS configured correctly
- [ ] Environment variables set

### **After Integration:**
- [ ] Can complete full interview
- [ ] Questions generate correctly
- [ ] Answers evaluated correctly
- [ ] Report generated correctly
- [ ] Integrity events logged
- [ ] No console errors
- [ ] No crashes

---

## 🐛 **Common Integration Issues & Solutions**

### **Issue 1: CORS Errors**
**Symptom:** Browser console shows "CORS policy" error

**Solution:**
```go
// backend/internal/middleware/middleware.go
// Already configured to allow all origins for development ✓
```

### **Issue 2: Backend Can't Reach LLM Service**
**Symptom:** "Failed to connect to LLM service"

**Solution:**
```bash
# Check Person B's service is running:
curl http://localhost:8000/health

# Check backend .env has correct URL:
LLM_SERVICE_URL=http://localhost:8000
```

### **Issue 3: Frontend Can't Reach Backend**
**Symptom:** Network error in browser console

**Solution:**
```bash
# Check backend is running:
curl http://localhost:8080/health

# Check frontend .env.local has correct URL:
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### **Issue 4: JSON Parsing Errors**
**Symptom:** "Failed to parse response"

**Solution:**
- Check API contract matches (`shared/api-contract.md`)
- Verify field names are identical
- Check capitalization (Go vs TypeScript)
- Use browser DevTools → Network tab to inspect

---

## 🔧 **Development Workflow**

### **Daily Workflow:**

**Morning:**
1. Pull latest code
2. Start all 3 services
3. Run quick smoke test
4. Plan the day's tasks

**During Development:**
1. Make changes in your area
2. Test locally
3. Commit working code
4. Coordinate on Slack/Discord

**Evening:**
1. Integration test
2. Fix any issues found
3. Document what's working
4. Plan next day

---

## 📞 **Communication Between Person A & B**

### **What to Share:**

**Person B shares with Person A:**
- "LLM service running on port 8000 ✓"
- "Question generation endpoint ready ✓"
- "Here's a sample API response..."
- "Changed response format, updated docs"

**Person A shares with Person B:**
- "Frontend calling your API now"
- "Getting this error from your service..."
- "Can you add this field to the response?"
- "Backend is sending requests, check logs"

### **When to Sync:**
- 🔴 **Immediately:** Breaking changes to API
- 🟡 **Daily:** Progress updates
- 🟢 **Weekly:** Overall status

---

## 🎯 **Integration Milestones**

### **Milestone 1: Services Start** (Week 1, Day 1)
- [ ] LLM service starts on port 8000
- [ ] Backend starts on port 8080
- [ ] Frontend starts on port 3000
- [ ] All health checks pass

### **Milestone 2: API Connection** (Week 1, Day 2-3)
- [ ] Backend can call LLM service
- [ ] Frontend can call backend
- [ ] Basic request/response works
- [ ] No CORS errors

### **Milestone 3: Question Flow** (Week 1, Day 4)
- [ ] Can start an interview
- [ ] Question displays in UI
- [ ] AI speaks question
- [ ] Can submit answer
- [ ] Backend receives answer

### **Milestone 4: Evaluation Flow** (Week 1, Day 5)
- [ ] LLM evaluates answer
- [ ] AI responds with feedback
- [ ] Next question or follow-up
- [ ] Conversation flows naturally

### **Milestone 5: Complete Interview** (Week 2, Day 1)
- [ ] Can complete 3-5 questions
- [ ] Can end interview
- [ ] Report generates
- [ ] Report displays in UI

### **Milestone 6: Integrity Detection** (Week 2, Day 2)
- [ ] Video analysis events logged
- [ ] Tab switch events logged
- [ ] Events sent to backend
- [ ] Events included in report

### **Milestone 7: Polish & Demo** (Week 2, Day 3-5)
- [ ] UI polished
- [ ] Error handling improved
- [ ] Demo script prepared
- [ ] No known bugs
- [ ] Ready to present

---

## 🚀 **Your Next Steps (Person A)**

### **Today (After Person B Completes LLM Service):**

**1. Test Person B's Service** (30 min)
```bash
# Make sure Person B's service is running
curl http://localhost:8000/health

# Test question generation
curl -X POST http://localhost:8000/api/question/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"DSA","difficulty":"Junior","position":0}'
```

**2. Start Go Backend** (1 hour)
```bash
cd backend

# Install Go if not installed
# Mac: brew install go
# Windows: Download from golang.org

# Download dependencies
go mod download

# Create .env file
cp .env.example .env

# Edit .env - make sure LLM_SERVICE_URL points to Person B
# LLM_SERVICE_URL=http://localhost:8000

# Run backend
go run cmd/server/main.go

# Should see: "Server starting on port 8080"
```

**3. Test Backend** (30 min)
```bash
# Health check
curl http://localhost:8080/health

# Try starting an interview
curl -X POST http://localhost:8080/api/interview/start \
  -H "Content-Type: application/json" \
  -d '{
    "candidateName": "Test User",
    "topic": "DSA",
    "difficulty": "Junior",
    "duration": 30
  }'

# Should return sessionId and firstQuestion
```

**4. Test Frontend → Backend** (30 min)
```bash
# Make sure backend is running
# Frontend already running

# Open browser: http://localhost:3000
# Fill form
# Click "Start Interview"
# Should navigate to interview page
# Should show question from LLM
```

---

### **Tomorrow (After Backend Works):**

**5. Full Integration Test** (2 hours)
- [ ] Complete a full interview
- [ ] Test all 3 question types (easy/medium/hard)
- [ ] Test follow-up questions
- [ ] Test report generation
- [ ] Test integrity detection

**6. Bug Fixing** (2-4 hours)
- Fix any errors found
- Improve error messages
- Add loading states
- Polish UI

**7. Demo Preparation** (1 hour)
- Practice the demo flow
- Prepare talking points
- Have backup plan if something fails
- Test on different browsers

---

## 📁 **Files You'll Work On (Person A)**

### **Already Done ✅:**
- `frontend/*` - All UI code
- `backend/*` - All skeleton code

### **Need to Verify:**
- `backend/cmd/server/main.go` - Entry point
- `backend/internal/handlers/*` - HTTP handlers
- `backend/internal/services/llm_client.go` - Calls Person B's service
- `backend/.env` - Configuration

### **Just Need to Run:**
```bash
cd backend
go mod download
cp .env.example .env
go run cmd/server/main.go
```

---

## 🤝 **Coordination Points**

### **What You Need from Person B:**

**1. Service Status:**
- Is the LLM service running?
- On which port?
- Is Claude API key working?

**2. API Responses:**
- What does the question response look like exactly?
- What does the evaluation response look like?
- Any differences from `shared/api-contract.md`?

**3. Error Handling:**
- What errors might the service return?
- How to handle Claude API rate limits?
- What's the fallback if API fails?

### **What Person B Needs from You:**

**1. Request Format:**
- Are you sending requests in the right format?
- Check `shared/api-contract.md`
- Show them example requests

**2. Testing:**
- Can you test their endpoints?
- Share any errors you get
- Help debug integration issues

**3. Timing:**
- When will backend be ready?
- When can you start integration testing?

---

## 🎬 **Demo Flow (After Integration)**

### **Golden Path (5 minutes):**

**Setup (30 sec):**
- Show all 3 services running
- Show health checks passing

**Start Interview (1 min):**
1. Fill form: "John Doe", DSA, Junior, 30 min
2. Click "Start Interview"
3. Page loads → AI avatar appears
4. Recording starts

**Interview Loop (3 min):**
1. AI speaks: "Hello John! Let's start with a question..."
2. Question displays: "Find two numbers that sum to target"
3. Click "Start Recording"
4. Answer: "I would use a hash map..."
5. Click "Submit"
6. AI evaluates: "Excellent! What's the time complexity?"
7. Answer follow-up
8. Next question appears
9. Show integrity detection (switch tab → warning)

**End (30 sec):**
1. Click "End Interview"
2. Report displays
3. Show scores, strengths, weaknesses
4. Show integrity events logged

---

## 📊 **Integration Success Metrics**

### **Technical Metrics:**
- Response time < 3 seconds
- No crashes during 30-minute interview
- All 3 services stay running
- No memory leaks

### **Functional Metrics:**
- Questions relevant to topic/difficulty
- Evaluation scores make sense
- Follow-ups are intelligent
- Report is comprehensive

### **User Experience:**
- Natural conversation flow
- Clear visual feedback
- Smooth transitions
- Professional appearance

---

## 🔮 **After Integration Works**

### **Enhancements (Optional):**
1. Add more question topics
2. Improve LLM prompts
3. Add data persistence (SQLite)
4. Deploy to cloud (Vercel + Railway)
5. Add authentication
6. Create admin dashboard
7. Export reports as PDF
8. Email notifications

---

## ✅ **Ready for Integration!**

### **Current Status:**
```
Frontend (Person A):  ✅ 100% Complete
Backend (Person A):   ✅ Skeleton Ready (needs Go installation)
LLM Service (Person B): ⏳ Waiting for completion
```

### **Next Immediate Steps:**

**1. Person B:** Complete LLM service (2-3 days)
**2. Person A:** Install Go and test backend (1 day)
**3. Together:** Integration testing (1-2 days)

**Total Time to Full Integration:** ~5-7 days

---

## 📞 **Questions to Ask Person B:**

1. "When will your LLM service be ready?"
2. "Can you share a working curl command for your endpoints?"
3. "Any issues getting the Claude API key?"
4. "Should we do a test call together?"

---

## 🎉 **Summary**

**What's Ready:**
- ✅ Frontend with video + voice (YOU)
- ✅ Backend skeleton (YOU)
- ⏳ LLM service (PERSON B)

**What's Next:**
1. Wait for Person B to complete LLM service
2. You start the Go backend
3. Connect frontend → backend → LLM
4. Test end-to-end
5. Demo!

**Your frontend is READY and WAITING for backend integration!** 🚀

Need help with anything specific? Ready to start the backend when Person B is done? 🎯
