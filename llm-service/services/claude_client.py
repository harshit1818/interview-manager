from groq import AsyncGroq
from typing import List, Dict
import os


class ClaudeClient:
    """Client for interacting with Groq API (drop-in replacement for Claude)"""

    def __init__(self, api_key: str = None):
        self.client = AsyncGroq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    async def generate_text(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 1.0
    ) -> str:
        """Generate text using Groq."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
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
        """Generate text with conversation history."""
        try:
            groq_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                groq_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating with history: {e}")
            raise
