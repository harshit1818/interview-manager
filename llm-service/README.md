# LLM Service (Python)

Claude API integration for question generation, evaluation, and report generation.

## Structure

```
llm-service/
├── services/
│   ├── __init__.py
│   ├── claude_client.py        # Claude API wrapper
│   ├── question_generator.py   # Question generation
│   ├── evaluator.py            # Answer evaluation
│   └── report_generator.py     # Report generation
├── main.py                     # FastAPI application
├── requirements.txt
└── .env.example
```

## Setup

1. Install Python 3.9+

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your Claude API key to `.env`:
```
ANTHROPIC_API_KEY=your_actual_api_key
```

6. Run service:
```bash
python main.py
```

Service will start on `http://localhost:8000`

## Get Claude API Key (Free)

1. Visit https://console.anthropic.com/
2. Sign up for an account
3. Get $5 free credits to start
4. Create an API key in the dashboard

## API Endpoints

### Generate Question
```
POST /api/question/generate
{
  "topic": "DSA",
  "difficulty": "Junior",
  "position": 0
}
```

### Evaluate Answer
```
POST /api/evaluate
{
  "question": {...},
  "answer": "candidate's response",
  "history": [...]
}
```

### Generate Report
```
POST /api/report/generate
{
  "session": {...}
}
```

## Services

### ClaudeClient
Wrapper for Anthropic's Claude API with retry logic and error handling.

### QuestionGenerator
- Generates questions based on topic and difficulty
- Uses structured prompts for consistency
- Fallback questions if generation fails

### Evaluator
- Evaluates candidate responses
- Scores on multiple dimensions
- Decides next action (follow-up, next question, end)

### ReportGenerator
- Analyzes full interview session
- Calculates aggregate scores
- Generates strengths/weaknesses
- Provides hiring recommendation

## Cost Estimation

Using Claude 3.5 Sonnet:
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

For a 30-minute interview (~10 questions):
- Estimated cost: $0.10 - $0.50
- Free tier covers ~10-50 interviews

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Test question generation
curl -X POST http://localhost:8000/api/question/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"DSA","difficulty":"Junior","position":0}'
```
