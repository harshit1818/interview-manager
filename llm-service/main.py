from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import logging
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv

from services.claude_client import ClaudeClient
from services.question_generator import QuestionGenerator
from services.evaluator import Evaluator
from services.report_generator import ReportGenerator
from services.context_manager import context_registry, ContextManager
from services.jd_processor import JDProcessor, INTERVIEW_TOPICS, get_topic_list, get_topics_by_domain

# Load environment variables
load_dotenv()

# Warn if Anthropic key missing
if not os.getenv("ANTHROPIC_API_KEY"):
    logging.warning("ANTHROPIC_API_KEY not set. Set it in environment or llm-service/.env before running.")

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
jd_processor = JDProcessor(claude_client)

# In-memory storage for JD contexts (session_id -> jd_context)
jd_contexts: Dict[str, str] = {}


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
    sessionId: Optional[str] = None  # For JD-based questions


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


class AddContextRequest(BaseModel):
    sessionId: str
    speaker: str
    text: str
    exchangeType: str = "message"
    evaluation: Optional[Dict[str, Any]] = None


class ContextStatsResponse(BaseModel):
    session_id: str
    recent_exchanges: int
    compressed_summaries: int
    key_points: int
    evaluations: int
    current_question: int
    age_seconds: float


# Routes
@app.get("/")
async def root():
    return {"message": "Interview LLM Service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/context/add")
async def add_to_context(request: AddContextRequest):
    """Add an exchange to the session context."""
    try:
        ctx_manager = await context_registry.get_or_create(request.sessionId)
        await ctx_manager.add_exchange(
            speaker=request.speaker,
            text=request.text,
            evaluation=request.evaluation,
            exchange_type=request.exchangeType
        )
        return {"success": True, "stats": ctx_manager.get_stats()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/context/{session_id}")
async def get_context(session_id: str):
    """Get the current context for LLM consumption."""
    try:
        ctx_manager = await context_registry.get_or_create(session_id)
        return {
            "context": ctx_manager.get_context_for_llm(),
            "stats": ctx_manager.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/context/{session_id}/advance")
async def advance_question(session_id: str):
    """Mark that interview moved to next question."""
    try:
        ctx_manager = await context_registry.get_or_create(session_id)
        ctx_manager.advance_question()
        return {"success": True, "current_question": ctx_manager.current_question_index}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/context/{session_id}")
async def clear_context(session_id: str):
    """Clear context for a completed session."""
    try:
        await context_registry.remove(session_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/context/stats/all")
async def get_all_context_stats():
    """Get stats for all active session contexts."""
    return context_registry.get_all_stats()


# ============== Topics & Job Description Endpoints ==============

@app.get("/api/topics")
async def list_topics():
    """Get list of all available interview topics."""
    return {
        "topics": get_topic_list(),
        "count": len(INTERVIEW_TOPICS)
    }


@app.get("/api/topics/domain/{domain}")
async def list_topics_by_domain(domain: str):
    """Get topics filtered by domain."""
    topics = get_topics_by_domain(domain)
    return {
        "domain": domain,
        "topics": topics,
        "count": len(topics)
    }


@app.get("/api/topics/domains")
async def list_domains():
    """Get list of all available domains."""
    domains = list(set(t["domain"] for t in INTERVIEW_TOPICS.values()))
    return {"domains": sorted(domains)}


@app.post("/api/jd/upload")
async def upload_job_description(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """Upload and process a job description PDF."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
        
        # Process PDF
        jd = await jd_processor.process_pdf(content)
        
        # Generate interview context and store it
        jd_context = jd_processor.generate_interview_context(jd)
        jd_contexts[session_id] = jd_context
        
        return {
            "success": True,
            "sessionId": session_id,
            "extracted": {
                "title": jd.title,
                "domain": jd.domain,
                "experienceLevel": jd.experience_level,
                "keyTechnologies": jd.key_technologies[:10],
                "requiredSkills": jd.required_skills[:10],
                "responsibilities": jd.responsibilities[:5]
            },
            "suggestedTopic": "dynamic",
            "interviewContext": jd_context
        }
    except ImportError as e:
        raise HTTPException(
            status_code=500, 
            detail="PDF processing libraries not installed. Run: pip install pypdf pdfplumber"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jd/text")
async def process_jd_text(request: Dict[str, Any]):
    """Process job description from raw text (alternative to PDF upload)."""
    try:
        text = request.get("text", "")
        session_id = request.get("sessionId", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="Job description text is required")
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # Process text
        jd = await jd_processor.process_text(text)
        
        # Generate interview context and store it
        jd_context = jd_processor.generate_interview_context(jd)
        jd_contexts[session_id] = jd_context
        
        return {
            "success": True,
            "sessionId": session_id,
            "extracted": {
                "title": jd.title,
                "domain": jd.domain,
                "experienceLevel": jd.experience_level,
                "keyTechnologies": jd.key_technologies[:10],
                "requiredSkills": jd.required_skills[:10],
                "responsibilities": jd.responsibilities[:5]
            },
            "suggestedTopic": "dynamic",
            "interviewContext": jd_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jd/{session_id}")
async def get_jd_context(session_id: str):
    """Get stored JD context for a session."""
    if session_id not in jd_contexts:
        raise HTTPException(status_code=404, detail="No JD context found for this session")
    return {
        "sessionId": session_id,
        "context": jd_contexts[session_id]
    }


@app.delete("/api/jd/{session_id}")
async def clear_jd_context(session_id: str):
    """Clear JD context for a session."""
    if session_id in jd_contexts:
        del jd_contexts[session_id]
    return {"success": True}


@app.post("/api/question/generate", response_model=Question)
async def generate_question(request: GenerateQuestionRequest):
    """Generate an interview question based on topic and difficulty"""
    try:
        # Get JD context if topic is dynamic and session has JD
        jd_context = None
        if request.topic == "dynamic" and request.sessionId:
            jd_context = jd_contexts.get(request.sessionId)
            if not jd_context:
                raise HTTPException(
                    status_code=400, 
                    detail="Dynamic topic requires a job description. Upload JD first."
                )
        
        question = await question_generator.generate(
            topic=request.topic,
            difficulty=request.difficulty,
            position=request.position,
            jd_context=jd_context
        )
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate", response_model=EvaluateResponse)
async def evaluate_answer(request: EvaluateRequest):
    """Evaluate candidate's answer and decide next action"""
    try:
        result = await evaluator.evaluate_and_decide(
            question=request.question.model_dump(),
            answer=request.answer,
            history=[h.model_dump() for h in request.history]
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
