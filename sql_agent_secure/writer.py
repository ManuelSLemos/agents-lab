"""Same sql_writer as sql_agent, with the input guardrail attached."""

from google.adk.agents.llm_agent import Agent
from sql_agent.config import MODEL
from sql_agent.database import get_schema

from .guardrails import block_injection

sql_writer = Agent(
    name="sql_writer",
    model=MODEL,
    description="Translates a natural-language question into a SQLite SELECT.",
    include_contents="default",
    instruction=(
        "Translate the user's question into ONE SQLite SELECT statement. "
        "Reply with the SQL only: no explanations, no markdown.\n\n"
        f"Schema:\n{get_schema()}"
    ),
    before_model_callback=block_injection,
)
