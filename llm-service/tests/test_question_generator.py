import pytest
import json
from unittest.mock import AsyncMock, MagicMock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.question_generator import QuestionGenerator


@pytest.mark.asyncio
async def test_generate_question_success(mock_claude_client):
    mock_claude_client.generate_text = AsyncMock(return_value=json.dumps({
        "stem": "Find the kth largest element in an array.",
        "followUps": ["What data structure would you use?", "Can you improve the time complexity?"],
        "evaluationHints": ["Heap-based approach", "QuickSelect algorithm"],
        "redFlags": ["Sorting the entire array"]
    }))

    generator = QuestionGenerator(mock_claude_client)
    result = await generator.generate(topic="DSA", difficulty="Junior", position=1)

    assert result["stem"] == "Find the kth largest element in an array."
    assert result["difficulty"] == "medium"
    assert len(result["followUps"]) == 2
    assert "id" in result


@pytest.mark.asyncio
async def test_generate_question_fallback_on_invalid_json(mock_claude_client):
    mock_claude_client.generate_text = AsyncMock(return_value="This is not valid JSON")

    generator = QuestionGenerator(mock_claude_client)
    result = await generator.generate(topic="DSA", difficulty="Junior", position=0)

    assert "stem" in result
    assert result["difficulty"] == "easy"


@pytest.mark.asyncio
async def test_difficulty_progression():
    mock_client = MagicMock()
    mock_client.generate_text = AsyncMock(return_value=json.dumps({
        "stem": "Test question",
        "followUps": [],
        "evaluationHints": [],
        "redFlags": []
    }))

    generator = QuestionGenerator(mock_client)

    q0 = await generator.generate("DSA", "Junior", 0)
    assert q0["difficulty"] == "easy"

    q1 = await generator.generate("DSA", "Junior", 1)
    assert q1["difficulty"] == "medium"

    q2 = await generator.generate("DSA", "Junior", 2)
    assert q2["difficulty"] == "hard"
