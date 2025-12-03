from anthropic import Anthropic
from typing import List, Dict
import asyncio


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Correct model version

    async def _call_messages_create(self, **kwargs):
        """Run the blocking Anthropic call in a thread to avoid blocking event loop."""
        return await asyncio.to_thread(self.client.messages.create, **kwargs)

    def _extract_text(self, message) -> str:
        """Robustly extract text from Anthropic response objects."""
        try:
            content = getattr(message, "content", None)
            if content and isinstance(content, list) and len(content) > 0:
                first = content[0]
                if isinstance(first, dict):
                    return first.get("text", "")
                # object with attribute `text`
                return getattr(first, "text", "")

            # Fallback to string representation
            return str(message)
        except Exception:
            return str(message)

    async def generate_text(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 1.0
    ) -> str:
        """Generate text using Claude (non-blocking)."""
        try:
            message = await self._call_messages_create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return self._extract_text(message)
        except Exception as e:
            print(f"Error generating text: {e}")
            raise

    async def generate_with_history(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 1.0
    ) -> str:
        """Generate text with conversation history (non-blocking)."""
        try:
            message = await self._call_messages_create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages,
            )
            return self._extract_text(message)
        except Exception as e:
            print(f"Error generating with history: {e}")
            raise
