import pytest
import json
from unittest.mock import AsyncMock, MagicMock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.report_generator import ReportGenerator


@pytest.mark.asyncio
async def test_generate_report_success(mock_claude_client, sample_session):
    mock_claude_client.generate_text = AsyncMock(return_value=json.dumps({
        "strengths": ["Clear communication", "Good problem-solving approach"],
        "weaknesses": ["Could improve edge case handling"],
        "recommendation": "hire"
    }))

    generator = ReportGenerator(mock_claude_client)
    report = await generator.generate(session=sample_session)

    assert report["sessionId"] == "session-001"
    assert report["candidateName"] == "Test User"
    assert report["recommendation"] == "hire"
    assert len(report["strengths"]) == 2
    assert report["integrityScore"] == 100.0


@pytest.mark.asyncio
async def test_generate_report_with_integrity_issues(mock_claude_client, sample_session):
    sample_session["integrityEvents"] = [
        {"type": "TAB_SWITCH", "severity": "medium"},
        {"type": "GAZE_AWAY", "severity": "low"}
    ]

    mock_claude_client.generate_text = AsyncMock(return_value=json.dumps({
        "strengths": ["Technical knowledge"],
        "weaknesses": ["Integrity concerns"],
        "recommendation": "maybe"
    }))

    generator = ReportGenerator(mock_claude_client)
    report = await generator.generate(session=sample_session)

    assert report["integrityScore"] == 85.0
    assert report["integrityIssues"] == 2


@pytest.mark.asyncio
async def test_generate_report_fallback_on_invalid_json(mock_claude_client, sample_session):
    mock_claude_client.generate_text = AsyncMock(return_value="Not valid JSON")

    generator = ReportGenerator(mock_claude_client)
    report = await generator.generate(session=sample_session)

    assert report["recommendation"] == "maybe"
    assert "strengths" in report
    assert "weaknesses" in report


@pytest.mark.asyncio
async def test_score_calculation(mock_claude_client):
    session_with_evals = {
        "id": "s1",
        "candidateName": "Candidate",
        "topic": "DSA",
        "difficulty": "Junior",
        "duration": 30,
        "questions": [],
        "transcript": [
            {"evaluation": {"correctness": 4, "communication": 5, "approach": 4, "edgeCases": 3}},
            {"evaluation": {"correctness": 5, "communication": 4, "approach": 5, "edgeCases": 4}},
        ],
        "integrityEvents": []
    }

    mock_claude_client.generate_text = AsyncMock(return_value=json.dumps({
        "strengths": ["Good"],
        "weaknesses": ["None"],
        "recommendation": "hire"
    }))

    generator = ReportGenerator(mock_claude_client)
    report = await generator.generate(session=session_with_evals)

    assert report["scores"]["correctness"] == 4.5
    assert report["scores"]["communication"] == 4.5
