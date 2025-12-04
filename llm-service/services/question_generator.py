import json
import uuid
import logging
import re
from typing import Dict, Optional
from services.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates interview questions using Claude"""

    def __init__(self, claude_client: ClaudeClient):
        self.client = claude_client

    async def generate(
        self, 
        topic: str, 
        difficulty: str, 
        position: int,
        jd_context: Optional[str] = None
    ) -> Dict:
        """Generate an interview question based on topic or job description."""

        # Determine difficulty level for the question
        if position == 0:
            target_difficulty = "easy"
        elif position == 1:
            target_difficulty = "medium"
        else:
            target_difficulty = "hard"

        # Build system prompt based on whether JD context is provided
        if topic == "dynamic" and jd_context:
            logger.info(f"Using JD-based prompt with context: {jd_context[:100]}...")
            system_prompt = self._build_jd_based_prompt(jd_context, difficulty, target_difficulty)
        else:
            logger.info(f"Using topic-based prompt for: {topic}")
            system_prompt = self._build_topic_based_prompt(topic, difficulty, target_difficulty)

        user_message = f"Generate a {target_difficulty} question for position {position} in the interview."

        response = await self.client.generate_text(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.8
        )
        
        logger.info(f"Claude response (first 500 chars): {response[:500] if response else 'None'}")

        # Try to extract JSON from response
        question_data = self._extract_json(response)
        
        if question_data:
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
        else:
            logger.warning(f"Failed to parse JSON, using fallback. Response was: {response[:300]}")
            return self._get_fallback_question(topic, target_difficulty)
    
    def _extract_json(self, response: str) -> Optional[Dict]:
        """Extract JSON from response, handling markdown code blocks."""
        if not response:
            return None
            
        # First try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find raw JSON object
        json_match = re.search(r'\{[^{}]*"stem"[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Try finding JSON with nested objects (for followUps arrays)
        json_match = re.search(r'\{.*"stem".*"followUps".*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None

    def _build_topic_based_prompt(self, topic: str, difficulty: str, target_difficulty: str) -> str:
        """Build prompt for standard topic-based interviews."""
        return f"""You are an expert technical interviewer creating questions for {topic} interviews.
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

    def _build_jd_based_prompt(self, jd_context: str, difficulty: str, target_difficulty: str) -> str:
        """Build prompt for job description-based interviews."""
        return f"""You are an expert interviewer creating questions based on a specific job description.

JOB CONTEXT:
{jd_context}

Generate ONE highly relevant interview question that:
1. Tests skills specifically mentioned in the job description
2. Is appropriate for a {difficulty} level candidate
3. Reflects real scenarios they would face in this role
4. Has {target_difficulty} difficulty level

Return your response as valid JSON with this structure:
{{
  "stem": "The main question text - make it specific to the job requirements",
  "followUps": ["Follow-up question 1", "Follow-up question 2"],
  "evaluationHints": ["What a good answer should include based on job requirements"],
  "redFlags": ["Signs the candidate may not be suitable for this specific role"]
}}

Focus on the most critical skills and responsibilities from the job description."""

    def _get_fallback_question(self, topic: str, difficulty: str) -> Dict:
        """Fallback question if generation fails"""
        fallback_questions = {
            "algorithms": {
                "easy": {
                    "stem": "Given an array of integers, find two numbers that add up to a specific target.",
                    "followUps": ["What's the time complexity?", "Can you optimize space usage?"],
                    "evaluationHints": ["Hash map approach", "Two-pointer technique"],
                    "redFlags": ["Nested loops without optimization discussion"]
                },
                "medium": {
                    "stem": "Design an algorithm to detect a cycle in a linked list.",
                    "followUps": ["Can you find the start of the cycle?", "What's the space complexity?"],
                    "evaluationHints": ["Floyd's cycle detection", "Two-pointer approach"],
                    "redFlags": ["Using extra data structure when O(1) space is possible"]
                },
                "hard": {
                    "stem": "Implement an LRU cache with O(1) get and put operations.",
                    "followUps": ["How would you handle concurrent access?"],
                    "evaluationHints": ["Hash map + doubly linked list", "OrderedDict usage"],
                    "redFlags": ["O(n) operations", "Missing edge cases"]
                }
            },
            "system_design": {
                "easy": {
                    "stem": "Design a URL shortening service like bit.ly.",
                    "followUps": ["How would you handle high traffic?", "How do you generate unique IDs?"],
                    "evaluationHints": ["Base62 encoding", "Database sharding"],
                    "redFlags": ["No consideration for scalability"]
                }
            },
            "behavioral": {
                "easy": {
                    "stem": "Tell me about a time you had to work with a difficult team member.",
                    "followUps": ["What would you do differently?", "What did you learn?"],
                    "evaluationHints": ["STAR method", "Shows empathy and problem-solving"],
                    "redFlags": ["Blaming others", "No concrete examples"]
                }
            },
            "product_management": {
                "medium": {
                    "stem": "How would you prioritize features for a new mobile app launch?",
                    "followUps": ["How do you balance user needs vs business goals?"],
                    "evaluationHints": ["Framework usage (RICE, MoSCoW)", "Data-driven approach"],
                    "redFlags": ["No structured approach", "Ignoring stakeholder input"]
                }
            }
        }

        # Get fallback for topic/difficulty, or use easy question as default
        topic_questions = fallback_questions.get(topic, fallback_questions.get("algorithms", {}))
        question = topic_questions.get(difficulty, topic_questions.get("easy", {
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
