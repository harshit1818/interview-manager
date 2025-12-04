import json
import uuid
from typing import Dict
from services.claude_client import ClaudeClient


class QuestionGenerator:
    """Generates interview questions using Claude"""

    def __init__(self, claude_client: ClaudeClient):
        self.client = claude_client

    async def generate(self, topic: str, difficulty: str, position: int) -> Dict:
        """Generate an interview question"""

        # Determine difficulty level for the question
        if position == 0:
            target_difficulty = "easy"
        elif position == 1:
            target_difficulty = "medium"
        else:
            target_difficulty = "hard"

        system_prompt = f"""You are an expert technical interviewer creating questions for {topic} interviews.
Generate ONE high-quality interview question suitable for a {difficulty} level candidate.

The question should be {target_difficulty} difficulty level.

Return your response as valid JSON with this structure:
{{
  "stem": "The main question text",
  "followUps": ["Follow-up question 1", "Follow-up question 2"],
  "evaluationHints": ["Expected approach 1", "Expected approach 2"],
  "redFlags": ["Common mistake 1", "Common mistake 2"]
}}

Make the question practical and relevant to real-world scenarios."""

        user_message = f"Generate a {target_difficulty} {topic} question for position {position} in the interview."

        response = await self.client.generate_text(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.8
        )

        try:
            # Parse JSON response
            question_data = json.loads(response)

            return {
                "id": str(uuid.uuid4()),
                "stem": question_data.get("stem", ""),
                "difficulty": target_difficulty,
                "followUps": question_data.get("followUps", []),
                "evaluationHints": question_data.get("evaluationHints", []),
                "redFlags": question_data.get("redFlags", []),
                "asked": False,
                "askedAt": None
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._get_fallback_question(topic, target_difficulty)

    def _get_fallback_question(self, topic: str, difficulty: str) -> Dict:
        """Fallback question if generation fails"""
        fallback_questions = {
            "DSA": {
                "easy": {
                    "stem": "Given an array of integers, find two numbers that add up to a specific target.",
                    "followUps": ["What's the time complexity?", "Can you optimize space usage?"],
                    "evaluationHints": ["Hash map approach", "Two-pointer technique"],
                    "redFlags": ["Nested loops without optimization discussion"]
                }
            }
        }

        # Get fallback for topic/difficulty, or use easy question as default
        question = fallback_questions.get(topic, {}).get(difficulty,
                   fallback_questions.get(topic, {}).get("easy", {
                       "stem": "Given an array of integers, write a function to find two numbers that add up to a specific target.",
                       "followUps": ["What's the time complexity?"],
                       "evaluationHints": ["Hash map approach"],
                       "redFlags": ["Nested loops without optimization"]
                   }))

        return {
            "id": str(uuid.uuid4()),
            "stem": question["stem"],
            "difficulty": difficulty,
            "followUps": question["followUps"],
            "evaluationHints": question["evaluationHints"],
            "redFlags": question["redFlags"],
            "asked": False,
            "askedAt": None
        }
