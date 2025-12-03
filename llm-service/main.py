from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv

from services.claude_client import ClaudeClient
from services.question_generator import QuestionGenerator
from services.evaluator import Evaluator
from services.report_generator import ReportGenerator

# Load environment variables
load_dotenv()

app = FastAPI(title="Interview LLM Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
claude_client = ClaudeClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
question_generator = QuestionGenerator(claude_client)
evaluator = Evaluator(claude_client)
report_generator = ReportGenerator(claude_client)


# Models
class Question(BaseModel):
    id: str
    stem: str
    difficulty: str
    followUps: List[str]
    evaluationHints: List[str]
    redFlags: List[str]
    asked: bool = False
    askedAt: Optional[str] = None


class Evaluation(BaseModel):
    correctness: int
    communication: int
    approach: int
    edgeCases: int
    notes: str


class ConversationTurn(BaseModel):
    timestamp: str
    speaker: str
    text: str
    type: str
    evaluation: Optional[Evaluation] = None


class GenerateQuestionRequest(BaseModel):
    topic: str
    difficulty: str
    position: int


class EvaluateRequest(BaseModel):
    question: Question
    answer: str
    history: List[ConversationTurn]


class EvaluateResponse(BaseModel):
    evaluation: Optional[Evaluation]
    nextAction: str
    aiResponse: str


class GenerateReportRequest(BaseModel):
    session: Dict[str, Any]


class Report(BaseModel):
    sessionId: str
    candidateName: str
    topic: str
    difficulty: str
    duration: int
    questionsAsked: int
    overallScore: float
    scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    integrityScore: float
    integrityIssues: int
    recommendation: str
    generatedAt: str


# Routes
@app.get("/")
async def root():
    return {"message": "Interview LLM Service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/question/generate", response_model=Question)
async def generate_question(request: GenerateQuestionRequest):
    """Generate an interview question based on topic and difficulty"""
    try:
        question = await question_generator.generate(
            topic=request.topic,
            difficulty=request.difficulty,
            position=request.position
        )
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate", response_model=EvaluateResponse)
async def evaluate_answer(request: EvaluateRequest):
    """Evaluate candidate's answer and decide next action"""
    try:
        result = await evaluator.evaluate_and_decide(
            question=request.question,
            answer=request.answer,
            history=request.history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report/generate", response_model=Report)
async def generate_report(request: GenerateReportRequest):
    """Generate final interview report"""
    try:
        report = await report_generator.generate(session=request.session)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
