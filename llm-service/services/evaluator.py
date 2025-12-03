import json
from typing import Dict, List, Any
from services.claude_client import ClaudeClient


class Evaluator:
    """Evaluates candidate answers and decides next action"""

    def __init__(self, claude_client: ClaudeClient):
        self.client = claude_client

    async def evaluate_and_decide(
        self,
        question: Dict,
        answer: str,
        history: List[Dict]
    ) -> Dict:
        """Evaluate answer and decide next action"""

        system_prompt = f"""You are an AI technical interviewer conducting a {question.get('difficulty')} level interview.

## Your Persona
- Professional but warm
- Patient with pauses and hesitation
- Ask clarifying questions when answers are ambiguous
- Never give away answers directly

## Current Question
{question.get('stem')}

## Evaluation Hints
{', '.join(question.get('evaluationHints', []))}

## Your Task
Based on the candidate's answer, you must:
1. Evaluate their response on a 1-5 scale
2. Decide the next action (follow_up, next_question, or end_interview)
3. Provide a natural, conversational response

## Evaluation Criteria
- Correctness: Did they get the right answer?
- Communication: Did they explain clearly?
- Approach: Was their problem-solving systematic?
- Edge Cases: Did they consider boundary conditions?

Return your response as valid JSON:
{{
  "evaluation": {{
    "correctness": 1-5,
    "communication": 1-5,
    "approach": 1-5,
    "edgeCases": 1-5,
    "notes": "Brief observation"
  }},
  "nextAction": "follow_up" | "next_question" | "end_interview",
  "aiResponse": "Your natural, conversational response to the candidate"
}}

Decision rules:
- If clarity < 3: Ask for clarification (follow_up)
- If correctness < 3: Offer a hint (follow_up)
- If correctness > 4: Ask challenging follow-up or move to next question
- Limit follow-ups to 2 per question
"""

        user_message = f"Candidate's answer: {answer}"

        response = await self.client.generate_text(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.7
        )

        try:
            result = json.loads(response)
            return {
                "evaluation": result.get("evaluation"),
                "nextAction": result.get("nextAction", "next_question"),
                "aiResponse": result.get("aiResponse", "Thank you for your answer.")
            }
        except json.JSONDecodeError:
            # Fallback response
            return {
                "evaluation": {
                    "correctness": 3,
                    "communication": 3,
                    "approach": 3,
                    "edgeCases": 3,
                    "notes": "Unable to parse evaluation"
                },
                "nextAction": "next_question",
                "aiResponse": "Thank you for your answer. Let's move on to the next question."
            }
