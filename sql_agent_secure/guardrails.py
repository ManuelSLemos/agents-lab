"""ADK callbacks used as guardrails: before_model checks the input, after_model checks the output."""

import re

from google.adk.models.llm_response import LlmResponse
from google.genai import types

# One layer among several: easy to bypass (other languages, encodings), so nothing depends on it alone.
_INJECTION = re.compile(
    r"ignor\w*\s+(all\s+|your\s+|the\s+|tus\s+|las\s+)?(previous|prior|above|anteriores|instructions|instrucciones)"
    r"|olvida\s+(todo|tus|las)"
    r"|\bsystem\s*:"
    r"|you\s+are\s+now|ahora\s+eres"
    r"|act\s+as\b|act[uú]a\s+como"
    r"|(repeat|repite)\b.*\b(instructions|prompt|instrucciones)",
    re.IGNORECASE,
)
_LEAK_MARKERS = ("CREATE TABLE", "<db_result>", "&lt;/db_result&gt;")

BLOCKED_PROMPT = "BLOCKED: the request looks like a prompt injection."
SAFE_ANSWER = "I can only answer questions about the courses and students data."


def _text(content: types.Content | None) -> str:
    return " ".join(part.text for part in (content.parts or []) if part.text) if content else ""


def _reply(text: str) -> LlmResponse:
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))


def block_injection(callback_context, llm_request) -> LlmResponse | None:
    """before_model: if any user message looks like an injection, skip the model call entirely."""
    for content in llm_request.contents:
        if content.role == "user" and _INJECTION.search(_text(content)):
            return _reply(BLOCKED_PROMPT)
    return None


def filter_answer(callback_context, llm_response) -> LlmResponse | None:
    """after_model: the answer must not echo the schema or our own data markers."""
    text = _text(llm_response.content)
    if any(marker.lower() in text.lower() for marker in _LEAK_MARKERS):
        return _reply(SAFE_ANSWER)
    return None
