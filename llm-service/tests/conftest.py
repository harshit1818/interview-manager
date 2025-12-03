import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.claude_client import ClaudeClient


@pytest.fixture
def mock_claude_client():
    client = MagicMock(spec=ClaudeClient)
    client.generate_text = AsyncMock()
    client.generate_with_history = AsyncMock()
    return client


@pytest.fixture
def sample_question():
    return {
        "id": "test-q-001",
        "stem": "Implement a function to reverse a linked list.",
        "difficulty": "medium",
        "followUps": ["What is the time complexity?", "Can you do it recursively?"],
        "evaluationHints": ["Iterative with three pointers", "O(n) time, O(1) space"],
        "redFlags": ["Modifying node values instead of pointers"],
        "asked": False,
        "askedAt": None
    }


@pytest.fixture
def sample_history():
    return [
        {"timestamp": "2025-12-04T10:00:00", "speaker": "ai", "text": "Welcome!", "type": "greeting"},
    ]


@pytest.fixture
def sample_session():
    return {
        "id": "session-001",
        "candidateName": "Test User",
        "topic": "DSA",
        "difficulty": "Junior",
        "duration": 30,
        "questions": [{"id": "q1", "stem": "Two sum problem"}],
        "transcript": [
            {"timestamp": "2025-12-04T10:00:00", "speaker": "ai", "text": "Hello", "type": "greeting"},
            {
                "timestamp": "2025-12-04T10:01:00",
                "speaker": "candidate",
                "text": "I would use a hash map",
                "type": "answer",
                "evaluation": {"correctness": 4, "communication": 4, "approach": 4, "edgeCases": 3, "notes": "Good"}
            }
        ],
        "integrityEvents": []
    }
