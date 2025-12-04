from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import deque
import time
import asyncio


@dataclass
class Exchange:
    speaker: str
    text: str
    timestamp: float
    evaluation: Optional[Dict[str, Any]] = None
    type: str = "message"


@dataclass 
class CompressedSummary:
    question_index: int
    summary: str
    avg_score: float
    key_points: List[str]


class ContextManager:
    """Manages conversation context with sliding window and compression."""
    
    MAX_RECENT_EXCHANGES = 6  # Keep last 6 exchanges in full
    MAX_COMPRESSED_SUMMARIES = 10  # Keep up to 10 compressed summaries
    MAX_KEY_POINTS = 20  # Keep up to 20 key technical points
    
    # Keywords that indicate important technical content
    TECHNICAL_KEYWORDS = [
        "hash map", "hashmap", "dictionary", "array", "linked list",
        "binary search", "binary tree", "bst", "heap", "stack", "queue",
        "dynamic programming", "dp", "memoization", "recursion",
        "o(n)", "o(1)", "o(log n)", "o(n^2)", "time complexity", "space complexity",
        "sorting", "quicksort", "mergesort", "graph", "dfs", "bfs",
        "two pointer", "sliding window", "greedy", "backtracking"
    ]
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.recent_exchanges: deque = deque(maxlen=self.MAX_RECENT_EXCHANGES)
        self.compressed_summaries: List[CompressedSummary] = []
        self.key_points: deque = deque(maxlen=self.MAX_KEY_POINTS)
        self.evaluation_scores: List[Dict[str, int]] = []
        self.current_question_index: int = 0
        self.created_at: float = time.time()
        self._lock = asyncio.Lock()
    
    async def add_exchange(
        self, 
        speaker: str, 
        text: str, 
        evaluation: Optional[Dict[str, Any]] = None,
        exchange_type: str = "message"
    ) -> None:
        """Add a new exchange to the context."""
        async with self._lock:
            exchange = Exchange(
                speaker=speaker,
                text=text,
                timestamp=time.time(),
                evaluation=evaluation,
                type=exchange_type
            )
            
            # Extract key technical points before potentially compressing
            self._extract_key_points(text)
            
            # Store evaluation scores separately
            if evaluation:
                self.evaluation_scores.append(evaluation)
            
            # Check if we need to compress before adding
            if len(self.recent_exchanges) >= self.MAX_RECENT_EXCHANGES:
                await self._compress_oldest()
            
            self.recent_exchanges.append(exchange)
    
    def _extract_key_points(self, text: str) -> None:
        """Extract and store key technical points from text."""
        text_lower = text.lower()
        for keyword in self.TECHNICAL_KEYWORDS:
            if keyword in text_lower:
                # Find surrounding context (up to 100 chars)
                idx = text_lower.find(keyword)
                start = max(0, idx - 30)
                end = min(len(text), idx + len(keyword) + 70)
                context = text[start:end].strip()
                if context and context not in self.key_points:
                    self.key_points.append(f"...{context}...")
                    break  # One key point per exchange
    
    async def _compress_oldest(self) -> None:
        """Compress oldest exchanges into a summary."""
        if len(self.recent_exchanges) < 2:
            return
        
        # Take oldest 2 exchanges to compress
        exchanges_to_compress = []
        for _ in range(2):
            if self.recent_exchanges:
                exchanges_to_compress.append(self.recent_exchanges.popleft())
        
        if not exchanges_to_compress:
            return
        
        # Create compressed summary
        texts = [e.text for e in exchanges_to_compress]
        evaluations = [e.evaluation for e in exchanges_to_compress if e.evaluation]
        
        avg_score = 0.0
        if evaluations:
            scores = []
            for ev in evaluations:
                if isinstance(ev, dict):
                    scores.append(sum(ev.get(k, 3) for k in ["correctness", "communication", "approach", "edgeCases"]) / 4)
            if scores:
                avg_score = sum(scores) / len(scores)
        
        # Simple heuristic summary (in production, use LLM)
        summary_text = self._create_heuristic_summary(texts, evaluations)
        
        summary = CompressedSummary(
            question_index=self.current_question_index,
            summary=summary_text,
            avg_score=avg_score,
            key_points=[kp for kp in self.key_points][-3:]  # Last 3 key points
        )
        
        self.compressed_summaries.append(summary)
        
        # Keep summaries bounded
        if len(self.compressed_summaries) > self.MAX_COMPRESSED_SUMMARIES:
            self.compressed_summaries.pop(0)
    
    def _create_heuristic_summary(
        self, 
        texts: List[str], 
        evaluations: List[Optional[Dict[str, Any]]]
    ) -> str:
        """Create a simple heuristic summary without LLM call."""
        # Extract speaker pattern
        summary_parts = []
        
        for text in texts:
            # Truncate long texts
            truncated = text[:150] + "..." if len(text) > 150 else text
            summary_parts.append(truncated)
        
        # Add evaluation note if available
        if evaluations:
            valid_evals = [e for e in evaluations if e]
            if valid_evals:
                avg_correctness = sum(e.get("correctness", 3) for e in valid_evals) / len(valid_evals)
                summary_parts.append(f"[Score: {avg_correctness:.1f}/5]")
        
        return " | ".join(summary_parts)
    
    def get_context_for_llm(self) -> str:
        """Get formatted context string for LLM consumption."""
        context_parts = []
        
        # Add compressed history summary
        if self.compressed_summaries:
            context_parts.append("=== Previous Discussion Summary ===")
            for summary in self.compressed_summaries[-3:]:  # Last 3 summaries
                context_parts.append(f"Q{summary.question_index + 1}: {summary.summary}")
            context_parts.append("")
        
        # Add key technical points mentioned
        if self.key_points:
            context_parts.append("=== Key Technical Points Mentioned ===")
            context_parts.append(", ".join(list(self.key_points)[-5:]))
            context_parts.append("")
        
        # Add performance summary
        if self.evaluation_scores:
            avg_scores = self._calculate_average_scores()
            context_parts.append("=== Candidate Performance So Far ===")
            context_parts.append(f"Correctness: {avg_scores.get('correctness', 3):.1f}/5, "
                               f"Communication: {avg_scores.get('communication', 3):.1f}/5, "
                               f"Approach: {avg_scores.get('approach', 3):.1f}/5")
            context_parts.append("")
        
        # Add recent conversation (full text)
        context_parts.append("=== Recent Conversation ===")
        for exchange in self.recent_exchanges:
            speaker = "Interviewer" if exchange.speaker == "ai" else "Candidate"
            context_parts.append(f"{speaker}: {exchange.text}")
        
        return "\n".join(context_parts)
    
    def _calculate_average_scores(self) -> Dict[str, float]:
        """Calculate average scores from all evaluations."""
        if not self.evaluation_scores:
            return {}
        
        totals = {"correctness": 0, "communication": 0, "approach": 0, "edgeCases": 0}
        count = 0
        
        for ev in self.evaluation_scores:
            if isinstance(ev, dict):
                for key in totals:
                    totals[key] += ev.get(key, 3)
                count += 1
        
        if count == 0:
            return {}
        
        return {k: v / count for k, v in totals.items()}
    
    def get_full_transcript(self) -> List[Dict[str, Any]]:
        """Get full transcript for final report (combines compressed + recent)."""
        transcript = []
        
        # Add compressed summaries as context markers
        for summary in self.compressed_summaries:
            transcript.append({
                "type": "summary",
                "question_index": summary.question_index,
                "summary": summary.summary,
                "avg_score": summary.avg_score
            })
        
        # Add recent exchanges
        for exchange in self.recent_exchanges:
            transcript.append({
                "speaker": exchange.speaker,
                "text": exchange.text,
                "timestamp": exchange.timestamp,
                "type": exchange.type,
                "evaluation": exchange.evaluation
            })
        
        return transcript
    
    def advance_question(self) -> None:
        """Called when moving to next question."""
        self.current_question_index += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics."""
        return {
            "session_id": self.session_id,
            "recent_exchanges": len(self.recent_exchanges),
            "compressed_summaries": len(self.compressed_summaries),
            "key_points": len(self.key_points),
            "evaluations": len(self.evaluation_scores),
            "current_question": self.current_question_index,
            "age_seconds": time.time() - self.created_at
        }


class ContextManagerRegistry:
    """Registry to manage context managers for multiple sessions."""
    
    def __init__(self):
        self._managers: Dict[str, ContextManager] = {}
        self._lock = asyncio.Lock()
    
    async def get_or_create(self, session_id: str) -> ContextManager:
        """Get existing context manager or create new one."""
        async with self._lock:
            if session_id not in self._managers:
                self._managers[session_id] = ContextManager(session_id)
            return self._managers[session_id]
    
    async def remove(self, session_id: str) -> None:
        """Remove context manager for completed session."""
        async with self._lock:
            if session_id in self._managers:
                del self._managers[session_id]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get stats for all active sessions."""
        return {
            "active_sessions": len(self._managers),
            "sessions": {sid: mgr.get_stats() for sid, mgr in self._managers.items()}
        }


# Global registry instance
context_registry = ContextManagerRegistry()
