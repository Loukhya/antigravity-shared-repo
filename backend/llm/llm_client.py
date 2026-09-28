"""
JobShield AI - Unified LLM Client Interface
Supports Groq (Llama 3.3 70B) and Google Gemini (gemini-2.5-flash) with graceful heuristic fallback.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def call_llm(
    prompt: str,
    system_instruction: str = "You are JobShield AI, an objective recruitment security auditor.",
    temperature: float = 0.1
) -> str:
    """
    Calls configured LLM provider (Groq or Gemini) with fallback.
    """
    # 1. Try Groq (Llama 3.3 70B)
    if GROQ_API_KEY:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=GROQ_API_KEY)
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=temperature
            )
            return chat_completion.choices[0].message.content or ""
        except Exception as e:
            print(f"[LLM] Groq call failed: {e}, attempting fallback.")

    # 2. Try Google Gemini (gemini-2.5-flash)
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=dict(
                    system_instruction=system_instruction,
                    temperature=temperature
                )
            )
            return response.text or ""
        except Exception as e:
            print(f"[LLM] Gemini call failed: {e}")

    # 3. Default graceful offline response
    return ""
