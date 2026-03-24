import google.generativeai as genai
from typing import List, Dict
import os


class ClaudeClient:
    """Client for interacting with Gemini API (drop-in replacement for Claude)"""

    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def generate_text(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 1.0
    ) -> str:
        """Generate text using Gemini."""
        try:
            response = await self.model.generate_content_async(
                contents=f"{system_prompt}\n\n{user_message}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text
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
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [msg["content"]]})

            # Prepend system prompt to first user message
            if contents and system_prompt:
                first_part = contents[0]["parts"][0]
                contents[0]["parts"][0] = f"{system_prompt}\n\n{first_part}"

            response = await self.model.generate_content_async(
                contents=contents,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text
        except Exception as e:
            print(f"Error generating with history: {e}")
            raise
