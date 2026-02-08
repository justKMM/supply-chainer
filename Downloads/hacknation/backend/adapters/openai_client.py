from __future__ import annotations

from openai import AsyncOpenAI

from backend.config import OPENAI_API_KEY

async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def get_async_client() -> AsyncOpenAI:
    return async_client
