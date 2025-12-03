# Person B - LLM Service Developer Briefing

**Your Role:** Build the intelligence layer that powers the AI interviewer using Claude API.

---

## 🎯 Your Responsibilities

You own the **entire LLM service** - the "brain" of the interview system. Your service will:

1. **Generate interview questions** based on topic and difficulty
2. **Evaluate candidate answers** and score them
3. **Decide next actions** (follow-up questions, move to next, or end)
4. **Generate final reports** with recommendations

**Think of it as:** You're building an expert interviewer that can think, evaluate, and make decisions autonomously.

---

## 🛠️ Your Tech Stack

### Core Technologies
- **Python 3.9+** - Main language
- **FastAPI** - Web framework (fast, modern, async)
- **Anthropic Claude API** - LLM for intelligence
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Why These Choices?
- **Python**: Best ecosystem for AI/ML work
- **FastAPI**: Fast, easy to build APIs, automatic docs
- **Claude**: Best reasoning capabilities, good at following instructions
- **Free tier**: $5 credits = 25-30 complete interviews

---

## 📁 Your Files (llm-service/)

```
llm-service/
├── main.py                          # FastAPI app with 3 endpoints
├── services/
│   ├── claude_client.py             # Wrapper for Claude API
│   ├── question_generator.py        # Generate questions
│   ├── evaluator.py                 # Evaluate + decide next action
│   └── report_generator.py          # Final report generation
├── requirements.txt                 # Python dependencies
├── .env                             # Your Claude API key (create this)
└── README.md                        # Your documentation
```

**Total: ~500 lines of code** - Very manageable!

---

## 🏗️ Architecture & Design

### Your Service Architecture

```
┌─────────────────────────────────────────────────┐
│           FastAPI (main.py)                     │
│  ┌─────────────────────────────────────────┐   │
│  │  POST /api/question/generate            │   │
│  │  POST /api/evaluate                     │   │
│  │  POST /api/report/generate              │   │
│  └─────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┼──────────┬─────────────┐
        ↓          ↓          ↓             ↓
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Question │ │Evaluator │ │ Report   │ │  Claude  │
│Generator │ │          │ │Generator │ │  Client  │
└──────────┘ └──────────┘ └──────────┘ └────┬─────┘
                                             │
                                             ↓
                                    ┌────────────────┐
                                    │  Claude API    │
                                    │  (Anthropic)   │
                                    └────────────────┘
```

### Design Principles

1. **Stateless**: Your service doesn't store sessions - Go backend handles that
2. **Pure Functions**: Each endpoint does one thing well
3. **Error Handling**: Graceful fallbacks if Claude API fails
4. **Structured Prompts**: Use consistent prompt templates
5. **JSON Responses**: Always return valid JSON for easy parsing

---

## 🔌 Your 3 Main Endpoints

### 1. Generate Question
**Purpose:** Create interview questions dynamically

**Input:**
```json
{
  "topic": "DSA",
  "difficulty": "Junior",
  "position": 0
}
```

**Your Job:**
- Use Claude to generate a relevant question
- Ensure it matches difficulty (easy → medium → hard progression)
- Include follow-up questions
- Provide evaluation hints
- Return structured JSON

**Output:**
```json
{
  "id": "uuid",
  "stem": "Find two numbers that sum to target",
  "difficulty": "easy",
  "followUps": ["What's the time complexity?", "Can you optimize space?"],
  "evaluationHints": ["Hash map approach", "O(n) optimal"],
  "redFlags": ["Nested loops without optimization"]
}
```

---

### 2. Evaluate Answer & Decide Next
**Purpose:** Score candidate's answer and decide what to do next

**Input:**
```json
{
  "question": { ... },
  "answer": "I would use a hash map to store...",
  "history": [ ... ]
}
```

**Your Job:**
- Use Claude to evaluate the answer
- Score on 4 dimensions (correctness, communication, approach, edge cases)
- Decide: follow-up, next question, or end interview
- Generate natural AI response

**Output:**
```json
{
  "evaluation": {
    "correctness": 4,
    "communication": 5,
    "approach": 4,
    "edgeCases": 3,
    "notes": "Good solution, clear explanation"
  },
  "nextAction": "follow_up",
  "aiResponse": "Great! Can you analyze the time complexity?"
}
```

**Decision Logic:**
- Low clarity (< 3) → Ask for clarification
- Low correctness (< 3) → Offer hint
- High correctness (> 4) → Challenge with harder follow-up
- After 2 follow-ups → Move to next question

---

### 3. Generate Report
**Purpose:** Create comprehensive final evaluation

**Input:**
```json
{
  "session": {
    "id": "...",
    "candidateName": "John",
    "topic": "DSA",
    "transcript": [ ... ],
    "integrityEvents": [ ... ]
  }
}
```

**Your Job:**
- Analyze entire interview session
- Calculate aggregate scores
- Identify strengths and weaknesses
- Provide hiring recommendation
- Consider integrity issues

**Output:**
```json
{
  "sessionId": "...",
  "overallScore": 4.2,
  "scores": {
    "correctness": 4.0,
    "communication": 4.5,
    "approach": 4.0,
    "edgeCases": 3.5
  },
  "strengths": ["Clear communication", "Systematic approach"],
  "weaknesses": ["Edge case handling needs work"],
  "recommendation": "hire",
  "integrityScore": 85.0
}
```

---

## 🎨 Prompt Engineering (Your Secret Sauce)

### Question Generation Prompt Template

```python
system_prompt = f"""You are an expert technical interviewer creating questions
for {topic} interviews.

Generate ONE high-quality interview question suitable for a {difficulty} level candidate.
The question should be {target_difficulty} difficulty level.

Return as JSON:
{{
  "stem": "The main question text",
  "followUps": ["Follow-up 1", "Follow-up 2"],
  "evaluationHints": ["Expected approach 1", "Expected approach 2"],
  "redFlags": ["Common mistake 1", "Common mistake 2"]
}}

Make it practical and relevant to real-world scenarios."""
```

### Evaluation Prompt Template

```python
system_prompt = f"""You are an AI technical interviewer conducting
a {difficulty} level interview.

## Current Question
{question_stem}

## Evaluation Hints
{evaluation_hints}

## Your Task
Evaluate the candidate's answer on a 1-5 scale:
- Correctness: Did they get the right answer?
- Communication: Did they explain clearly?
- Approach: Was their problem-solving systematic?
- Edge Cases: Did they consider boundary conditions?

Return as JSON:
{{
  "evaluation": {{"correctness": 1-5, ...}},
  "nextAction": "follow_up" | "next_question" | "end_interview",
  "aiResponse": "Your natural, conversational response"
}}

Decision rules:
- If clarity < 3: Ask for clarification
- If correctness < 3: Offer a hint
- If correctness > 4: Ask challenging follow-up
- Limit: 2 follow-ups per question"""
```

---

## 🚀 Getting Started (Step-by-Step)

### Step 1: Setup Environment (5 min)
```bash
cd llm-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get Claude API Key (5 min)
1. Go to https://console.anthropic.com/
2. Sign up (takes 2 minutes)
3. Get $5 free credits
4. Go to "API Keys" → "Create Key"
5. Copy the key (starts with `sk-ant-...`)

### Step 3: Configure (1 min)
```bash
cp .env.example .env
```

Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
```

### Step 4: Test (2 min)
```bash
python main.py
```

Visit http://localhost:8000/docs - You'll see auto-generated API docs!

### Step 5: Test Endpoint (3 min)
```bash
curl -X POST http://localhost:8000/api/question/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "DSA",
    "difficulty": "Junior",
    "position": 0
  }'
```

You should get a question back!

---

## 🔧 Development Workflow

### Phase 1: Build Independently (Day 1-2)
1. **Start with `claude_client.py`**
   - Test basic Claude API calls
   - Handle errors gracefully

2. **Build `question_generator.py`**
   - Start with hardcoded questions as fallback
   - Test with different topics/difficulties
   - Refine prompts for better questions

3. **Build `evaluator.py`**
   - Test with sample answers
   - Tune the scoring logic
   - Make sure decision logic works

4. **Build `report_generator.py`**
   - Test with mock session data
   - Calculate scores correctly
   - Generate meaningful insights

### Phase 2: Integration (Day 3)
1. **Coordinate with Person A**
   - Share your API endpoint
   - Agree on exact JSON formats
   - Test with Postman/curl together

2. **Test End-to-End**
   - Person A calls your endpoints from Go backend
   - Debug any JSON parsing issues
   - Verify data flows correctly

### Phase 3: Polish (Day 4-5)
1. **Improve prompts** for better quality
2. **Add error handling** for edge cases
3. **Optimize** Claude API calls (reduce tokens)
4. **Add logging** for debugging

---

## 🧪 Testing Strategy

### Unit Testing Each Service

**Test Question Generator:**
```python
# Test different topics
topics = ["DSA", "React", "System Design", "Backend APIs"]
for topic in topics:
    question = await generator.generate(topic, "Junior", 0)
    assert question["stem"] != ""
    assert len(question["followUps"]) > 0
```

**Test Evaluator:**
```python
# Test with good answer
response = await evaluator.evaluate_and_decide(
    question=sample_question,
    answer="I would use a hash map for O(n) time complexity",
    history=[]
)
assert response["evaluation"]["correctness"] >= 4

# Test with poor answer
response = await evaluator.evaluate_and_decide(
    question=sample_question,
    answer="I don't know",
    history=[]
)
assert response["nextAction"] == "follow_up"
```

**Test with curl:**
```bash
# Test question generation
curl -X POST http://localhost:8000/api/question/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"DSA","difficulty":"Junior","position":0}'

# Test evaluation
curl -X POST http://localhost:8000/api/evaluate \
  -H "Content-Type: application/json" \
  -d @test_evaluate.json
```

---

## 💡 Pro Tips & Best Practices

### 1. Prompt Engineering
- **Be specific**: Tell Claude exactly what format you want
- **Use examples**: Show Claude an example of good output
- **Set constraints**: "Keep response under 50 words"
- **Test variations**: Try different phrasings

### 2. Error Handling
```python
try:
    response = await claude_client.generate_text(...)
    result = json.loads(response)
except json.JSONDecodeError:
    # Fallback to predetermined response
    result = get_fallback_question()
except Exception as e:
    # Log error and return graceful failure
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail="LLM service error")
```

### 3. Cost Optimization
- Use lower `max_tokens` when possible (1024 is plenty)
- Cache common questions (optional enhancement)
- Use `temperature=0.7` for consistent output
- Monitor usage at https://console.anthropic.com/

### 4. JSON Parsing
Always wrap JSON parsing:
```python
try:
    data = json.loads(llm_response)
except json.JSONDecodeError:
    # Sometimes LLM adds extra text, try to extract JSON
    import re
    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group())
    else:
        # Use fallback
        data = default_response
```

### 5. Logging
Add logging for debugging:
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Generating question for {topic} - {difficulty}")
logger.debug(f"LLM Response: {response}")
logger.error(f"Failed to parse: {error}")
```

---

## 📊 Expected Performance

### Response Times (approximate)
- Question generation: 1-2 seconds
- Evaluation: 1-2 seconds
- Report generation: 2-3 seconds

### Quality Targets
- Questions should be relevant 90%+ of the time
- Evaluation scores should align with human judgment 80%+
- No crashes/errors during normal operation

### Cost Per Interview
- Question generation (3-5 questions): $0.05
- Evaluations (3-5 rounds): $0.10
- Report generation: $0.05
- **Total: ~$0.20 per interview**
- **Your $5 free credits = ~25 interviews**

---

## 🔗 Integration with Person A

### What Person A Needs from You

1. **Your service running on port 8000**
   ```bash
   python main.py
   # Should see: Uvicorn running on http://0.0.0.0:8000
   ```

2. **Health check working**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

3. **Consistent JSON format**
   - Follow the structures in `shared/api-contract.md`
   - Don't change field names without coordinating
   - Always return valid JSON

4. **Error handling**
   - Return proper HTTP status codes
   - 200 for success
   - 500 for errors
   - Include error messages in response

### Communication Points

**Daily sync with Person A:**
- "Question generation endpoint is ready"
- "Evaluation is working, but tuning the prompts"
- "Getting JSON parsing errors, let's debug together"

**Share your progress:**
- Push code regularly
- Update if API contract changes
- Test your endpoints before integration

---

## 🐛 Common Issues & Solutions

### Issue 1: "ANTHROPIC_API_KEY not found"
**Solution:**
```bash
# Make sure .env exists
ls -la .env

# Check contents
cat .env

# Should see: ANTHROPIC_API_KEY=sk-ant-...

# Restart Python service after adding key
```

### Issue 2: "Rate limit exceeded"
**Solution:**
- Check usage at https://console.anthropic.com/
- You might have used all credits
- Wait a bit between requests during testing

### Issue 3: JSON parsing fails
**Solution:**
```python
# Add better prompts
system_prompt += "\nIMPORTANT: Return ONLY valid JSON, no extra text."

# Or extract JSON from response
import re
json_match = re.search(r'\{.*\}', response, re.DOTALL)
```

### Issue 4: Questions are too hard/easy
**Solution:**
- Refine your difficulty mapping
- Add more examples in prompts
- Test with different `temperature` values (0.5-1.0)

---

## 📈 Enhancement Ideas (After MVP)

Once basic functionality works, you can improve:

1. **Question Bank**
   - Create `data/questions.json` with curated questions
   - Use LLM to vary phrasing
   - Fallback to bank if generation fails

2. **Context Awareness**
   - Use conversation history for better follow-ups
   - Avoid repeating questions
   - Adapt difficulty based on performance

3. **Better Scoring**
   - Multi-factor evaluation
   - Weighted scoring by importance
   - Confidence scores

4. **Streaming Responses**
   - Stream Claude responses for faster UX
   - Use Server-Sent Events (SSE)

5. **Caching**
   - Cache common questions
   - Reduce API calls
   - Save costs

---

## ✅ Definition of Done

Your service is "done" when:

- [ ] All 3 endpoints work correctly
- [ ] Health check returns 200
- [ ] Person A can call your API from Go backend
- [ ] Questions are relevant to topic/difficulty
- [ ] Evaluation scores make sense
- [ ] Reports are generated successfully
- [ ] Error handling works (no crashes)
- [ ] You can run 5 complete interviews without issues

---

## 🎯 Success Metrics

**Technical:**
- Response time < 3 seconds per endpoint
- Uptime > 95% during demo
- Zero JSON parsing errors

**Quality:**
- Questions match expected difficulty
- Evaluation aligns with expected scores
- Reports are actionable

**Integration:**
- Person A can complete full interview flow
- No blocking issues during development
- Clean API contract adherence

---

## 📞 When to Reach Out to Person A

**Immediately reach out if:**
- ❌ API contract needs to change
- ❌ You're blocked on understanding requirements
- ❌ Integration is failing

**Coordinate on:**
- ✅ JSON format changes
- ✅ New fields needed
- ✅ Testing end-to-end flow

**Don't worry about:**
- ❓ Internal implementation details
- ❓ How you structure your code
- ❓ Prompt engineering specifics

---

## 🚀 Final Checklist

Before saying "I'm done":

**Setup:**
- [ ] Python environment working
- [ ] Claude API key configured
- [ ] Service starts without errors
- [ ] Can access http://localhost:8000/docs

**Implementation:**
- [ ] Question generation works
- [ ] Evaluation logic works
- [ ] Report generation works
- [ ] Error handling added
- [ ] JSON validation working

**Testing:**
- [ ] Tested with curl/Postman
- [ ] Different topics work
- [ ] Different difficulties work
- [ ] Error cases handled

**Integration:**
- [ ] Person A can call your endpoints
- [ ] Full interview flow works
- [ ] No blocking bugs

---

## 📚 Resources

**Documentation:**
- Claude API Docs: https://docs.anthropic.com/
- FastAPI Docs: https://fastapi.tiangolo.com/
- Python AsyncIO: https://docs.python.org/3/library/asyncio.html

**In This Project:**
- `shared/api-contract.md` - Your API specification
- `shared/SETUP_GUIDE.md` - Setup instructions
- `llm-service/README.md` - Your service docs

**Get Help:**
- Claude API Console: https://console.anthropic.com/
- FastAPI Discord: https://discord.gg/fastapi
- Person A for integration questions

---

## 💬 Questions to Ask Yourself

As you build, ask:

1. **"Is my JSON format consistent?"** - Check against api-contract.md
2. **"What if Claude returns garbage?"** - Add fallbacks
3. **"What if API is down?"** - Handle gracefully
4. **"Are my prompts clear?"** - Test with different inputs
5. **"Can Person A integrate easily?"** - Think about their experience

---

## 🎉 You've Got This!

**Remember:**
- You own the "intelligence" - the most exciting part!
- ~500 lines of code - very manageable
- Claude does the heavy lifting
- Focus on good prompts and solid error handling
- Person A handles all the UI/session complexity

**Your goal:** Make the AI interviewer feel natural, intelligent, and fair.

Good luck! 🚀

---

**Quick Start Command:**
```bash
cd llm-service && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py
```
