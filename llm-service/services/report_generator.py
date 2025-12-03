import json
from datetime import datetime, timezone
from typing import Dict, Any
from services.claude_client import ClaudeClient


class ReportGenerator:
    """Generates final interview reports"""

    def __init__(self, claude_client: ClaudeClient):
        self.client = claude_client

    async def generate(self, session: Dict[str, Any]) -> Dict:
        """Generate comprehensive interview report"""

        # Extract evaluation scores from transcript
        evaluations = [
            turn.get("evaluation")
            for turn in session.get("transcript", [])
            if turn.get("evaluation")
        ]

        # Calculate average scores
        scores = self._calculate_scores(evaluations)
        overall_score = sum(scores.values()) / len(scores) if scores else 0

        # Calculate integrity score
        integrity_events = session.get("integrityEvents", [])
        integrity_score = self._calculate_integrity_score(integrity_events)

        system_prompt = """You are an expert HR analyst reviewing a technical interview.

Based on the interview data, provide:
1. Key strengths (2-3 bullet points)
2. Areas for improvement (2-3 bullet points)
3. Hiring recommendation (strong_hire, hire, maybe, no_hire)

Consider both technical performance and integrity issues.

Return as valid JSON:
{
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendation": "hire"
}
"""

        user_message = f"""Interview Summary:
- Topic: {session.get('topic')}
- Difficulty: {session.get('difficulty')}
- Overall Score: {overall_score:.2f}/5
- Questions Asked: {len(session.get('questions', []))}
- Integrity Issues: {len(integrity_events)}
- Scores: {scores}

Transcript length: {len(session.get('transcript', []))} turns
"""

        response = await self.client.generate_text(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.5
        )

        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            analysis = {
                "strengths": ["Completed the interview"],
                "weaknesses": ["Needs more practice"],
                "recommendation": "maybe"
            }

        return {
            "sessionId": session.get("id"),
            "candidateName": session.get("candidateName"),
            "topic": session.get("topic"),
            "difficulty": session.get("difficulty"),
            "duration": session.get("duration"),
            "questionsAsked": len(session.get("questions", [])),
            "overallScore": round(overall_score, 2),
            "scores": scores,
            "strengths": analysis.get("strengths", []),
            "weaknesses": analysis.get("weaknesses", []),
            "integrityScore": integrity_score,
            "integrityIssues": len(integrity_events),
            "recommendation": analysis.get("recommendation", "maybe"),
            "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    def _calculate_scores(self, evaluations: list) -> Dict[str, float]:
        """Calculate average scores from evaluations"""
        if not evaluations:
            return {
                "correctness": 0.0,
                "communication": 0.0,
                "approach": 0.0,
                "edgeCases": 0.0
            }

        scores = {
            "correctness": 0.0,
            "communication": 0.0,
            "approach": 0.0,
            "edgeCases": 0.0
        }

        for evaluation in evaluations:
            if evaluation:
                scores["correctness"] += evaluation.get("correctness", 0)
                scores["communication"] += evaluation.get("communication", 0)
                scores["approach"] += evaluation.get("approach", 0)
                scores["edgeCases"] += evaluation.get("edgeCases", 0)

        count = len(evaluations)
        return {key: round(value / count, 2) for key, value in scores.items()}

    def _calculate_integrity_score(self, events: list) -> float:
        """Calculate integrity score (0-100)"""
        if not events:
            return 100.0

        # Deduct points based on severity
        score = 100.0
        for event in events:
            severity = event.get("severity", "low")
            if severity == "high":
                score -= 20
            elif severity == "medium":
                score -= 10
            else:
                score -= 5

        return max(0.0, score)
