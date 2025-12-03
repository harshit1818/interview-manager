# API Contract

Communication between Frontend, Backend, and LLM Service.

## Architecture Flow

```
Frontend (Port 3000)
    ↓
Backend API (Port 8080)
    ↓
LLM Service (Port 8000)
    ↓
Claude API
```

## Backend API (Go) → Frontend (TypeScript)

### Start Interview
**Endpoint:** `POST /api/interview/start`

**Request:**
```json
{
  "candidateName": "John Doe",
  "topic": "DSA",
  "difficulty": "Junior",
  "duration": 30
}
```

**Response:**
```json
{
  "sessionId": "abc123...",
  "firstQuestion": {
    "id": "q1",
    "stem": "Find two numbers that sum to target",
    "difficulty": "easy",
    "followUps": ["What's the time complexity?"],
    "evaluationHints": ["Hash map approach"],
    "redFlags": ["Nested loops"],
    "asked": false
  }
}
```

---

### Submit Answer
**Endpoint:** `POST /api/interview/respond`

**Request:**
```json
{
  "sessionId": "abc123...",
  "transcript": "I would use a hash map...",
  "timestamp": 1234567890
}
```

**Response:**
```json
{
  "evaluation": {
    "correctness": 4,
    "communication": 5,
    "approach": 4,
    "edgeCases": 3,
    "notes": "Good solution"
  },
  "nextAction": "follow_up",
  "nextQuestion": null,
  "aiResponse": "Great! Can you explain the time complexity?"
}
```

---

### End Interview
**Endpoint:** `POST /api/interview/end`

**Request:**
```json
{
  "sessionId": "abc123..."
}
```

**Response:**
```json
{
  "report": {
    "sessionId": "abc123...",
    "candidateName": "John Doe",
    "overallScore": 4.2,
    "scores": {
      "correctness": 4.0,
      "communication": 4.5,
      "approach": 4.0,
      "edgeCases": 3.5
    },
    "strengths": ["Clear communication", "Systematic approach"],
    "weaknesses": ["Edge case handling"],
    "recommendation": "hire"
  }
}
```

---

### Get Status
**Endpoint:** `GET /api/interview/status/:sessionId`

**Response:**
```json
{
  "currentState": "in_progress",
  "timeRemaining": 25,
  "questionsAsked": 2,
  "currentQuestion": {...}
}
```

---

### Log Integrity Event
**Endpoint:** `POST /api/integrity/event`

**Request:**
```json
{
  "sessionId": "abc123...",
  "eventType": "TAB_SWITCH",
  "timestamp": 1234567890,
  "metadata": {}
}
```

**Response:**
```json
{
  "acknowledged": true,
  "severity": "medium"
}
```

---

## Backend (Go) → LLM Service (Python)

### Generate Question
**Endpoint:** `POST /api/question/generate`

**Request:**
```json
{
  "topic": "DSA",
  "difficulty": "Junior",
  "position": 0
}
```

**Response:**
```json
{
  "id": "q1",
  "stem": "Find two numbers that sum to target",
  "difficulty": "easy",
  "followUps": ["What's the time complexity?"],
  "evaluationHints": ["Hash map approach"],
  "redFlags": ["Nested loops"],
  "asked": false
}
```

---

### Evaluate Answer
**Endpoint:** `POST /api/evaluate`

**Request:**
```json
{
  "question": {...},
  "answer": "I would use a hash map...",
  "history": [...]
}
```

**Response:**
```json
{
  "evaluation": {
    "correctness": 4,
    "communication": 5,
    "approach": 4,
    "edgeCases": 3,
    "notes": "Good solution"
  },
  "nextAction": "follow_up",
  "aiResponse": "Great! Can you explain the time complexity?"
}
```

---

### Generate Report
**Endpoint:** `POST /api/report/generate`

**Request:**
```json
{
  "session": {
    "id": "abc123...",
    "candidateName": "John Doe",
    "topic": "DSA",
    "difficulty": "Junior",
    "duration": 30,
    "transcript": [...],
    "integrityEvents": [...]
  }
}
```

**Response:**
```json
{
  "sessionId": "abc123...",
  "overallScore": 4.2,
  "scores": {...},
  "strengths": [...],
  "weaknesses": [...],
  "recommendation": "hire"
}
```

---

## Data Types

### Question
```typescript
{
  id: string
  stem: string
  difficulty: 'easy' | 'medium' | 'hard'
  followUps: string[]
  evaluationHints: string[]
  redFlags: string[]
  asked: boolean
  askedAt?: string
}
```

### Evaluation
```typescript
{
  correctness: number  // 1-5
  communication: number  // 1-5
  approach: number  // 1-5
  edgeCases: number  // 1-5
  notes: string
}
```

### IntegrityEvent
```typescript
{
  timestamp: string
  type: 'TAB_SWITCH' | 'WINDOW_BLUR' | 'MULTIPLE_FACES' | 'GAZE_AWAY' | 'LARGE_PASTE'
  severity: 'low' | 'medium' | 'high'
  metadata: Record<string, any>
}
```
