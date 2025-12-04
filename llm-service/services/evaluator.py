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
        has_code = '```' in answer or self._looks_like_code(answer)

        # Check if this is an introduction question
        is_introduction = question.get('difficulty') == 'introduction' or 'introduce yourself' in question.get('stem', '').lower()
        
        # Check conversation stage from history
        conversation_stage = self._determine_stage(history, answer)

        system_prompt = f"""You are a senior technical interviewer at a top tech company conducting a live interview.

## YOUR PERSONALITY
- Warm, encouraging, but professionally rigorous
- Patient - give candidates time to think
- Interactive - this is a CONVERSATION, not an exam
- Never give away answers, but guide with hints
- Celebrate good insights: "That's a great observation!"
- Normalize struggle: "This is a tricky part, take your time"

## CURRENT QUESTION
{question.get('stem')}

## EVALUATION CRITERIA
{', '.join(question.get('evaluationHints', []))}

## CONVERSATION STAGE: {conversation_stage}
{self._get_stage_guidance(conversation_stage, has_code)}

## CANDIDATE'S RESPONSE TYPE
{"They provided CODE. Review it carefully for:" if has_code else "They provided a VERBAL response."}
{self._get_code_review_guidance() if has_code else ""}

## HOW TO RESPOND LIKE A HUMAN INTERVIEWER:

1. **If candidate asks clarifying questions**: Answer them! This shows good problem-solving.
   - "Great question! Yes, the array can contain negative numbers."
   - "Good thinking to clarify that. The input will always be valid."

2. **If candidate explains their approach (no code yet)**:
   - Acknowledge: "I see what you're thinking..."
   - Probe deeper: "What data structure would you use for that?"
   - Check understanding: "And what would be the time complexity of that approach?"
   - If approach is good: "That sounds like a solid approach. Go ahead and code it up."
   - If approach has issues: "Interesting. What happens if [edge case]?"

3. **If candidate seems stuck**:
   - "Take your time, there's no rush."
   - "What's the first thing that comes to mind?"
   - "Let's break it down - what's the simplest case?"
   - Give a gentle hint without revealing the answer

4. **If candidate writes code**:
   - "Let me take a look at your code..."
   - Point out bugs gently: "I see a small issue on line X. Can you spot it?"
   - If correct: "Nice! This looks good. Can you walk me through it?"
   - Ask about complexity: "What's the time and space complexity here?"

5. **If candidate is done and correct**:
   - "Excellent work! Before we move on, can you think of any edge cases?"
   - "Great solution. How would you optimize this if the input size was 10x larger?"

{"## INTRODUCTION HANDLING" if is_introduction else ""}
{"Keep it brief and warm. Acknowledge their background, then smoothly transition: 'Thanks for sharing! Let's dive into a technical problem...'" if is_introduction else ""}

IMPORTANT: Return ONLY valid JSON. No markdown, no extra text.

{{
  "evaluation": {{
    "correctness": 1-5,
    "communication": 1-5,
    "approach": 1-5,
    "edgeCases": 1-5,
    "notes": "Brief internal note about their performance"
  }},
  "nextAction": "follow_up" | "next_question" | "end_interview",
  "aiResponse": "Your natural, conversational response (1-3 sentences, like a real interviewer would say)"
}}

## DECISION RULES:
- Candidate asking clarifying questions → follow_up (answer their question!)
- Candidate explaining approach → follow_up (discuss, then ask to code)
- Candidate's approach is flawed → follow_up (hint at the issue)
- Candidate wrote buggy code → follow_up (point out bug)
- Candidate solved it correctly → next_question (after brief discussion)
- Introduction done → next_question"""

        user_message = f"Candidate's response: {answer}"

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
                "nextAction": "follow_up",
                "aiResponse": "I see. Could you elaborate a bit more on your approach?"
            }
    
    def _looks_like_code(self, text: str) -> bool:
        """Detect if text looks like code even without markdown blocks."""
        code_indicators = [
            'def ', 'function ', 'class ', 'return ', 'if ', 'for ', 'while ',
            '= []', '= {}', '= new ', '=> {', '()', ');', '};'
        ]
        return any(indicator in text for indicator in code_indicators)
    
    def _determine_stage(self, history: List[Dict], current_answer: str) -> str:
        """Determine conversation stage based on history."""
        if not history:
            return "initial_response"
        
        # Count exchanges for current question
        exchanges = len([h for h in history if h.get('type') in ['answer', 'follow_up']])
        
        if '?' in current_answer and len(current_answer) < 200:
            return "clarifying_question"
        elif self._looks_like_code(current_answer) or '```' in current_answer:
            return "code_submission"
        elif exchanges == 0:
            return "initial_response"
        elif exchanges < 3:
            return "approach_discussion"
        else:
            return "wrapping_up"
    
    def _get_stage_guidance(self, stage: str, has_code: bool) -> str:
        """Get guidance for the current conversation stage."""
        guidance = {
            "clarifying_question": "The candidate is asking a clarifying question. ANSWER IT helpfully! This is a good sign.",
            "initial_response": "This is their first response. Listen carefully, acknowledge their thinking, and guide them.",
            "approach_discussion": "We're discussing approach. Ask probing questions, check their understanding.",
            "code_submission": "They've written code. Review it carefully, provide feedback.",
            "wrapping_up": "We've discussed enough. Wrap up this question or move to the next."
        }
        return guidance.get(stage, "Continue the conversation naturally.")
    
    def _get_code_review_guidance(self) -> str:
        """Guidance for code review."""
        return """
- Correctness: Does the logic work? Any bugs?
- Edge cases: Empty input, single element, duplicates?
- Complexity: Is it optimal? Can it be improved?
- Style: Is it readable? Good variable names?
- Walk through: Can they trace through an example?"""
