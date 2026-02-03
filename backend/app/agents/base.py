"""
Base agent class and utilities
"""
from typing import Dict, Any, List
import json
import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize async client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, model: str = settings.OPENAI_MODEL):
        self.model = model
        self.client = client

    async def call_llm(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        json_output: bool = True
    ) -> Any:
        """Call OpenAI and parse response"""
        if not self.client:
            logger.error("OpenAI client not initialized (missing API key)")
            raise ValueError("OpenAI API key is missing")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"} if json_output else None
            )
            
            content = response.choices[0].message.content
            
            if json_output:
                return json.loads(content)
            return content
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise
