import os

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "liquid/lfm-2.5-2.6b:free"


class LLMError(Exception):
    def __init__(self, message: str, hint: str | None = None):
        super().__init__(message)
        self.hint = hint


async def complete(prompt: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise LLMError(
            "OPENROUTER_API_KEY is not set.",
            hint="Copy backend/.env.example to backend/.env and add your OpenRouter API key.",
        )
    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        except httpx.RequestError as exc:
            raise LLMError(f"Could not reach OpenRouter: {exc}") from exc

    if response.status_code == 429:
        raise LLMError(
            "OpenRouter rate limit hit.",
            hint="Free-tier models have low rate limits — wait a bit and try again.",
        )
    if response.status_code >= 400:
        raise LLMError(f"OpenRouter returned an error ({response.status_code}): {response.text}")

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise LLMError(f"Unexpected response shape from OpenRouter: {data}") from exc
