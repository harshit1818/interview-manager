# Frontend Implementation Plan

Step-by-step plan to build the interview frontend from scratch.

---

## 🎯 Goal
Build a working interview interface where candidates can:
1. Start an interview
2. See questions and answer via voice
3. Use a code editor
4. See real-time transcript
5. View final report

---

## 📋 Phase-by-Phase Implementation

### **Phase 1: Foundation (30 min)** ✅ DONE
- [x] Project structure
- [x] Dependencies configured
- [x] TypeScript types defined
- [x] API client setup

**Next: Start building UI**

---

### **Phase 2: Basic UI Setup (20 min)** 🔄 CURRENT
**Goal:** Get Tailwind working and create base layout

**Tasks:**
1. Configure Tailwind CSS
2. Add global styles
3. Create basic layout component
4. Add `_app.tsx` and `_document.tsx`

**Files to create/modify:**
- `tailwind.config.js`
- `postcss.config.js`
- `src/styles/globals.css`
- `src/pages/_app.tsx`
- `src/pages/_document.tsx`

**Test:**
```bash
npm run dev
# Should see styled page at localhost:3000
```

---

### **Phase 3: Home/Start Page (30 min)** 📝 NEXT
**Goal:** Candidate can enter details and start interview

**Features:**
- Form with name, topic, difficulty, duration
- Validation
- Nice gradient background
- "Start Interview" button
- Navigate to interview page on submit

**Files:**
- `src/pages/index.tsx` (already created, needs polish)

**Test:**
- Fill form → Click start → Should navigate to interview page

---

### **Phase 4: Interview Page Layout (45 min)** 📝 TODO
**Goal:** Create the main interview interface layout

**Components to build:**
1. **VideoCall component** - Show camera + AI avatar
2. **QuestionDisplay** - Show current question
3. **CodeEditor** - Monaco editor
4. **TranscriptPanel** - Conversation history
5. **ControlPanel** - Record/Submit buttons

**Layout:**
```
┌─────────────────────────────────────────┐
│  Video (Candidate + AI)                 │
├─────────────────────┬───────────────────┤
│  Current Question   │  Transcript       │
├─────────────────────┤                   │
│  Code Editor        │                   │
├─────────────────────┤                   │
│  Controls           │                   │
└─────────────────────┴───────────────────┘
```

**Test:**
- Page loads without errors
- All sections visible
- Responsive on mobile

---

### **Phase 5: Voice Integration (1 hour)** 📝 TODO
**Goal:** Get voice input/output working

**Features:**
1. **Speech Recognition (STT)**
   - Start/stop recording button
   - Show live transcript
   - Visual feedback when listening

2. **Text-to-Speech (TTS)**
   - Speak AI questions
   - Speak AI responses
   - Pause/resume controls

**Files:**
- `src/hooks/useVoice.ts` (already created)
- Wire up to interview page

**Test:**
- Click "Start Recording" → Browser asks for mic permission
- Speak → Text appears
- AI speaks questions through speakers

---

### **Phase 6: API Integration (1 hour)** 📝 TODO
**Goal:** Connect to backend API

**Flow:**
1. Start interview → Call `POST /api/interview/start`
2. Submit answer → Call `POST /api/interview/respond`
3. Get AI response → Display and speak
4. End interview → Call `POST /api/interview/end`

**Files:**
- `src/lib/api.ts` (already created)
- Wire up in interview page

**Test:**
- With backend running, complete full interview flow
- Check network tab for API calls
- Verify data flows correctly

---

### **Phase 7: Code Editor (30 min)** 📝 TODO
**Goal:** Working code editor with syntax highlighting

**Features:**
- Monaco editor embedded
- Language selection (JS, Python, etc.)
- Paste detection
- Auto-complete

**Files:**
- `src/components/CodeEditor.tsx` (already created)
- Polish and test

**Test:**
- Type code → Syntax highlighting works
- Paste large code → Integrity event logged

---

### **Phase 8: Integrity Detection (30 min)** 📝 TODO
**Goal:** Detect and log cheating attempts

**Features:**
1. Tab switch detection
2. Window blur detection
3. Large paste detection
4. Visual warnings to user

**Files:**
- `src/hooks/useIntegrityDetection.ts` (already created)
- Add warning UI

**Test:**
- Switch tab → Warning appears
- Click outside → Event logged
- Paste code → Event logged

---

### **Phase 9: Report Page (45 min)** 📝 TODO
**Goal:** Show final interview report

**Features:**
- Overall score (big number)
- Score breakdown (chart/bars)
- Strengths & weaknesses
- Recommendation badge
- Transcript viewer
- Integrity score

**Files to create:**
- `src/pages/report/[sessionId].tsx`
- `src/components/ReportCard.tsx`

**Test:**
- Complete interview → See report
- Scores display correctly
- Can review transcript

---

### **Phase 10: Polish & UX (1 hour)** 📝 TODO
**Goal:** Make it look professional

**Improvements:**
1. Loading states
2. Error messages
3. Animations/transitions
4. Mobile responsive
5. Accessibility
6. Better visual design

**Test:**
- Works on mobile
- Graceful error handling
- Smooth user experience

---

## 🏗️ Implementation Order

**Today (Session 1): Basic Flow**
1. ✅ Setup Tailwind - 20 min
2. ✅ Polish home page - 30 min
3. ✅ Build interview layout - 45 min
4. ✅ Test navigation flow - 15 min

**Session 2: Core Functionality**
5. Voice integration - 1 hour
6. API integration - 1 hour
7. Test full flow - 30 min

**Session 3: Complete Features**
8. Code editor polish - 30 min
9. Integrity detection - 30 min
10. Report page - 45 min

**Session 4: Polish**
11. UX improvements - 1 hour
12. Testing & bug fixes - 1 hour

**Total Time: ~8-10 hours**

---

## 🎨 Design System

### Colors
```javascript
primary: blue-500 (#3B82F6)
secondary: purple-600 (#9333EA)
success: green-500 (#10B981)
danger: red-500 (#EF4444)
warning: yellow-500 (#F59E0B)
```

### Components Style
- Rounded corners: `rounded-lg`
- Shadows: `shadow-lg`
- Spacing: Consistent padding/margins
- Transitions: `transition duration-200`

---

## 📱 Responsive Breakpoints

```
sm: 640px   (mobile)
md: 768px   (tablet)
lg: 1024px  (laptop)
xl: 1280px  (desktop)
```

**Strategy:** Mobile-first design

---

## ✅ Testing Checklist

After each phase:
- [ ] Component renders without errors
- [ ] No console errors
- [ ] Works on Chrome
- [ ] Works on Firefox
- [ ] Responsive on mobile
- [ ] Accessibility (keyboard navigation)

---

## 🚀 Quick Start (Right Now)

**Let's start with Phase 2:**

```bash
cd frontend
npm run dev
```

**Files to create next:**
1. `tailwind.config.js`
2. `postcss.config.js`
3. `src/styles/globals.css`
4. `src/pages/_app.tsx`

Let's build! 🎉
