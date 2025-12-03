import pytest
import json
from unittest.mock import AsyncMock, MagicMock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.evaluator import Evaluator


@pytest.mark.asyncio
async def test_evaluate_and_decide_success(mock_claude_client, sample_question):
    mock_claude_client.generate_text = AsyncMock(return_value=json.dumps({
        "evaluation": {
            "correctness": 4,
            "communication": 5,
            "approach": 4,
            "edgeCases": 3,
            "notes": "Good explanation of the approach"
        },
        "nextAction": "follow_up",
        "aiResponse": "Great! Can you explain the time complexity?"
    }))

    evaluator = Evaluator(mock_claude_client)
    result = await evaluator.evaluate_and_decide(
        question=sample_question,
        answer="I would use three pointers to reverse the list iteratively.",
        history=[]
    )

    assert result["evaluation"]["correctness"] == 4
    assert result["nextAction"] == "follow_up"
    assert "time complexity" in result["aiResponse"]


@pytest.mark.asyncio
async def test_evaluate_fallback_on_invalid_json(mock_claude_client, sample_question):
    mock_claude_client.generate_text = AsyncMock(return_value="Invalid response from LLM")

    evaluator = Evaluator(mock_claude_client)
    result = await evaluator.evaluate_and_decide(
        question=sample_question,
        answer="I don't know",
        history=[]
    )

    assert result["evaluation"]["correctness"] == 3
    assert result["nextAction"] == "next_question"
    assert "aiResponse" in result


@pytest.mark.asyncio
async def test_evaluate_next_question_action(mock_claude_client, sample_question):
    mock_claude_client.generate_text = AsyncMock(return_value=json.dumps({
        "evaluation": {
            "correctness": 5,
            "communication": 5,
            "approach": 5,
            "edgeCases": 4,
            "notes": "Excellent answer"
        },
        "nextAction": "next_question",
        "aiResponse": "Perfect! Let's move to the next question."
    }))

    evaluator = Evaluator(mock_claude_client)
    result = await evaluator.evaluate_and_decide(
        question=sample_question,
        answer="Use three pointers, O(n) time, O(1) space.",
        history=[]
    )

    assert result["nextAction"] == "next_question"
