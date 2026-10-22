"""Shared configuration."""

import os
from pathlib import Path

from google.adk.models.lite_llm import LiteLlm

# LiteLLM reads OLLAMA_API_BASE from the environment (defaults to localhost:11434).
MODEL = LiteLlm(model="ollama_chat/qwen3:4b")

# How many times the writer may correct a failing query.
MAX_RETRIES = 2

# Key under which the query result is stored in the session state.
RESULT_STATE_KEY = "query_result"

# Chinook sample database (music store). Override with CHINOOK_DB_PATH.
DB_PATH = Path(os.environ.get("CHINOOK_DB_PATH", Path(__file__).resolve().parent.parent / "Chinook.db"))
