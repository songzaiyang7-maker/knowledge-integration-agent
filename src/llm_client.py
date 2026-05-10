"""LLM client wrapper for MiniMax M2.7 API (Anthropic-compatible)."""

import json
from anthropic import Anthropic
from src.config import MINIMAX_API_KEY, MINIMAX_BASE_URL, MINIMAX_MODEL


def get_client():
    return Anthropic(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 4096, temperature: float = 0.3) -> str:
    """Call MiniMax M2.7 via Anthropic SDK and return text response."""
    client = get_client()
    response = client.messages.create(
        model=MINIMAX_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Extract text from response content blocks
    for block in response.content:
        if hasattr(block, "text"):
            return block.text

    return str(response.content)


def call_llm_json(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> dict | list | None:
    """Call LLM and parse JSON from response. Returns None on parse failure."""
    raw = call_llm(system_prompt, user_prompt, max_tokens=max_tokens)

    # Try to extract JSON from markdown code blocks
    import re
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    if json_match:
        raw = json_match.group(1).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try finding JSON array/object directly
        for start_char, end_char in [("[", "]"), ("{", "}")]:
            start = raw.find(start_char)
            end = raw.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(raw[start:end + 1])
                except json.JSONDecodeError:
                    continue
        return None
