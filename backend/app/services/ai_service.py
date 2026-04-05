from openai import AsyncOpenAI
from app.config import settings
from app.schemas import AIExcursionExtraction, ExcursionBatch
import json
import re


CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to save an excursion


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.MISTRAL_API_KEY,
            base_url=settings.MISTRAL_BASE_URL,
        )

    async def extract_excursion_data(self, message: str) -> ExcursionBatch:
        """Extract excursion statistics from natural language message.
        Returns a batch of excursions (can be 0 if message is not about excursions).
        """
        
        prompt = f"""You are an assistant that extracts excursion statistics from natural language messages from tour guides.

CRITICAL RULES:
1. If the message does NOT contain information about a completed excursion/tour (e.g., greetings, general chat, questions), return an empty list with confidence 0.0
2. If the message describes ONE excursion, return a list with one object
3. If the message describes MULTIPLE separate excursions (e.g., "Monday I had X, Tuesday I had Y"), return a list with multiple objects
4. Only extract data if the message is clearly about a tour/excursion that was completed
5. For each excursion, extract:
   - number_of_tourists: integer
   - average_age: float
   - age_distribution: float (0-20, standard deviation of ages)
   - vivacity_before: float (0-1, energy level before tour)
   - vivacity_after: float (0-1, energy level after tour)
   - interest_in_it: float (0-1, interest in IT topics)
   - interests_list: space-separated keywords of what tourists were interested in
   - confidence: float (0-1, how confident you are about the extraction). Set to 0.0 if the message is not about excursions.

Return ONLY a valid JSON array of excursion objects. Use null for unknown fields.

Message: "{message}"

JSON response (array of objects, can be empty if not about excursions):"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": "You extract structured excursion data from text. Return ONLY a valid JSON array of excursion objects, or an empty array [] if the message is not about excursions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500,
            )

            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            raw_data = json.loads(content)
            
            # Ensure it's a list
            if not isinstance(raw_data, list):
                raw_data = [raw_data]
            
            # Parse each excursion and filter by confidence
            excursions = []
            for item in raw_data:
                extraction = AIExcursionExtraction(
                    number_of_tourists=item.get("number_of_tourists"),
                    average_age=item.get("average_age"),
                    age_distribution=item.get("age_distribution"),
                    vivacity_before=item.get("vivacity_before"),
                    vivacity_after=item.get("vivacity_after"),
                    interest_in_it=item.get("interest_in_it"),
                    interests_list=item.get("interests_list"),
                    confidence=item.get("confidence", 0.0),
                    raw_message=message,
                )
                # Only keep excursions with sufficient confidence
                if extraction.confidence >= CONFIDENCE_THRESHOLD:
                    excursions.append(extraction)
            
            return ExcursionBatch(excursions=excursions, raw_message=message)

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                return ExcursionBatch(excursions=[], raw_message=message)
            # Return empty on error
            return ExcursionBatch(excursions=[], raw_message=message)

    async def analyze_statistics(self, query: str, context: str) -> str:
        """Answer natural language questions about excursion statistics"""
        
        prompt = f"""You are a helpful analyst for Innopolis tour guides.
Answer the following question based on the excursion data context provided.

Context (excursion data summary):
{context}

Question: {query}

Provide a clear, helpful answer with specific numbers and insights."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": "You analyze excursion statistics and provide insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Sorry, I encountered an error analyzing the statistics: {str(e)}"


# Singleton instance
ai_service = AIService()
