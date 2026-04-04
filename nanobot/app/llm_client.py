from openai import AsyncOpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
        )

    async def get_response(
        self,
        message: str,
        conversation_history: list[dict],
        system_prompt: str,
    ) -> str:
        """Get response from LLM"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": message}
            ]

            response = await self.client.chat.completions.create(
                model=settings.QWEN_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return f"I'm sorry, I encountered an error processing your request: {str(e)}"
