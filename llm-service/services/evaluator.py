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

        # Check if answer contains code
        has_code = '```' in answer

        # Check if this is an introduction question
        is_introduction = question.get('difficulty') == 'introduction' or 'introduce yourself' in question.get('stem', '').lower()

        system_prompt = f"""You are an AI technical interviewer conducting a {question.get('difficulty')} level interview.

## Your Persona
- Professional but warm
- Patient with pauses and hesitation
- Ask clarifying questions when answers are ambiguous
- Never give away answers directly
- Review both verbal explanations AND code implementations
{"- For introduction questions: keep it brief, acknowledge, then move to technical questions" if is_introduction else ""}

## Current Question
{question.get('stem')}

## Evaluation Hints
{', '.join(question.get('evaluationHints', []))}

## Your Task
The candidate may provide:
1. Verbal explanation of their approach
2. Code implementation (in markdown code blocks)
3. Both verbal + code

You must:
1. Evaluate BOTH the explanation AND the code (if provided)
2. Check code for correctness, efficiency, edge cases
3. Analyze code quality, readability, and best practices
4. Decide the next action (follow_up, next_question, or end_interview)
5. Provide a natural, conversational response

## Evaluation Criteria
- Correctness: Did they get the right answer? Does the code work?
- Communication: Did they explain clearly? Is code readable?
- Approach: Was their problem-solving systematic? Is algorithm correct?
- Edge Cases: Did they consider boundary conditions in code?

{"## Code Review Focus (code was provided)" if has_code else ""}
{"- Check syntax and logic errors" if has_code else ""}
{"- Verify time/space complexity" if has_code else ""}
{"- Look for edge case handling" if has_code else ""}
{"- Assess code readability and style" if has_code else ""}

IMPORTANT: Return ONLY valid JSON with no extra text before or after. No explanations, no markdown, just pure JSON.

Response format:
{{
  "evaluation": {{
    "correctness": 1-5,
    "communication": 1-5,
    "approach": 1-5,
    "edgeCases": 1-5,
    "notes": "Brief observation about explanation and/or code"
  }},
  "nextAction": "follow_up" | "next_question" | "end_interview",
  "aiResponse": "Your natural, conversational response to the candidate (mention code if they wrote it)"
}}

Decision rules:
{"- For introduction: Acknowledge briefly and use nextAction=next_question to move to technical questions" if is_introduction else ""}
{"- For technical questions:" if not is_introduction else ""}
- If clarity < 3: Ask for clarification (follow_up)
- If correctness < 3: Offer a hint (follow_up)
- If code has bugs: Point them out gently and ask them to fix
- If correctness > 4: Ask about optimization or move to next question
- Limit follow-ups to 2 per question
"""

        user_message = f"Candidate's answer: {answer}"

        response = await self.client.generate_text(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.7
        )

        try:
            # Try direct JSON parse first
            result = json.loads(response)
            return {
                "evaluation": result.get("evaluation"),
                "nextAction": result.get("nextAction", "next_question"),
                "aiResponse": result.get("aiResponse", "Thank you for your answer.")
            }
        except json.JSONDecodeError:
            # Try to extract JSON from response (Claude sometimes adds extra text)
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return {
                        "evaluation": result.get("evaluation"),
                        "nextAction": result.get("nextAction", "next_question"),
                        "aiResponse": result.get("aiResponse", "Thank you for your answer.")
                    }
                except json.JSONDecodeError:
                    pass

            # Log the response for debugging
            print(f"Failed to parse LLM response. Raw response: {response[:500]}")

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
