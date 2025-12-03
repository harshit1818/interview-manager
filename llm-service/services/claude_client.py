from anthropic import Anthropic
from typing import List, Dict


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Correct model version

    async def generate_text(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 1.0
    ) -> str:
        """Generate text using Claude"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return message.content[0].text
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
        """Generate text with conversation history"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error generating with history: {e}")
            raise
