"""Agent that turns a natural-language question into SQL."""

from google.adk.agents.llm_agent import Agent

from ..config import MODEL
from ..database import get_schema

sql_writer = Agent(
    name="sql_writer",
    model=MODEL,
    description="Translates a natural-language question into a SQLite SELECT.",
    # Needs the original question when it is asked to correct a failed query.
    include_contents="default",
    instruction=(
        "Translate the user's question into ONE SQLite SELECT statement. "
        "Reply with the SQL only: no explanations, no markdown.\n\n"
        f"Schema:\n{get_schema()}"
    ),
)
