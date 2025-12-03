import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        with patch("main.claude_client") as mock_client:
            mock_client.generate_text = AsyncMock(return_value=json.dumps({
                "stem": "Test question",
                "followUps": ["Follow up 1"],
                "evaluationHints": ["Hint 1"],
                "redFlags": ["Red flag 1"]
            }))
            from main import app
            yield TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Interview LLM Service" in response.json()["message"]


def test_generate_question_endpoint(client):
    with patch("main.question_generator.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {
            "id": "q-123",
            "stem": "What is a binary tree?",
            "difficulty": "easy",
            "followUps": ["How do you traverse it?"],
            "evaluationHints": ["DFS or BFS"],
            "redFlags": ["Confusing with BST"],
            "asked": False,
            "askedAt": None
        }

        response = client.post("/api/question/generate", json={
            "topic": "DSA",
            "difficulty": "Junior",
            "position": 0
        })

        assert response.status_code == 200
        data = response.json()
        assert data["stem"] == "What is a binary tree?"
        assert data["difficulty"] == "easy"


def test_evaluate_endpoint(client):
    with patch("main.evaluator.evaluate_and_decide", new_callable=AsyncMock) as mock_eval:
        mock_eval.return_value = {
            "evaluation": {
                "correctness": 4,
                "communication": 4,
                "approach": 4,
                "edgeCases": 3,
                "notes": "Good answer"
            },
            "nextAction": "next_question",
            "aiResponse": "Great job!"
        }

        response = client.post("/api/evaluate", json={
            "question": {
                "id": "q-1",
                "stem": "Question text",
                "difficulty": "easy",
                "followUps": [],
                "evaluationHints": [],
                "redFlags": [],
                "asked": True,
                "askedAt": "2025-12-04T10:00:00"
            },
            "answer": "My answer",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert data["nextAction"] == "next_question"


def test_generate_report_endpoint(client):
    with patch("main.report_generator.generate", new_callable=AsyncMock) as mock_report:
        mock_report.return_value = {
            "sessionId": "s-001",
            "candidateName": "Test",
            "topic": "DSA",
            "difficulty": "Junior",
            "duration": 30,
            "questionsAsked": 3,
            "overallScore": 4.0,
            "scores": {"correctness": 4.0, "communication": 4.0, "approach": 4.0, "edgeCases": 4.0},
            "strengths": ["Good"],
            "weaknesses": ["None"],
            "integrityScore": 100.0,
            "integrityIssues": 0,
            "recommendation": "hire",
            "generatedAt": "2025-12-04T10:00:00"
        }

        response = client.post("/api/report/generate", json={
            "session": {
                "id": "s-001",
                "candidateName": "Test",
                "topic": "DSA",
                "difficulty": "Junior",
                "duration": 30,
                "questions": [],
                "transcript": [],
                "integrityEvents": []
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert data["recommendation"] == "hire"
