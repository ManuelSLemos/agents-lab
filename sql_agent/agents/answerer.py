"""Agent that explains the query result in the user's language."""

from google.adk.agents.llm_agent import Agent

from ..config import MODEL, RESULT_STATE_KEY

answerer = Agent(
    name="answerer",
    model=MODEL,
    description="Explains the query result to the user.",
    # Workflow nodes run without chat history by default; it needs the original question.
    include_contents="default",
    instruction=(
        "Answer the user's question briefly, in the user's language, "
        "using only this query result:\n"
        f"{{{RESULT_STATE_KEY}}}"
    ),
)
