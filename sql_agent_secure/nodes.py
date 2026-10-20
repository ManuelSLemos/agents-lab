"""Workflow nodes. validate is only a cheap first filter; the real defense lives in database.py."""

import re
import sqlite3

from google.adk.events.event import Event
from sql_agent.config import MAX_RETRIES, RESULT_STATE_KEY
from sql_agent.nodes import ROUTE_FAILED, ROUTE_OK, ROUTE_REJECTED, ROUTE_RETRY, reject  # noqa: F401

from security import wrap_untrusted

from .database import run_query

_COMMENTS = re.compile(r"/\*.*?\*/|--[^\n]*", re.DOTALL)
_ALLOWED_FIRST_WORDS = {"select", "with"}


def _clean_sql(raw: str) -> str:
    """Strip the markdown fences that models like to add around SQL."""
    text = str(raw).strip().strip("`").strip()
    return text[3:].strip() if text[:3].lower() == "sql" else text


def validate(node_input: str) -> Event:
    """Cheap first filter on the first word. The engine rejects multiple statements and comments are its job."""
    sql = _clean_sql(node_input)
    first_word = _COMMENTS.sub(" ", sql).split(maxsplit=1)[:1]  # comments are removed only for this check
    if first_word and first_word[0].lower() in _ALLOWED_FIRST_WORDS:
        return Event(output=sql, route=ROUTE_OK)
    return Event(output=f"Only a single SELECT query is allowed, got: {sql}", route=ROUTE_REJECTED)


def execute(node_input: str, attempts: int = 0) -> Event:
    """Run the query. The result is marked as DATA before it reaches the LLM."""
    try:
        result = wrap_untrusted("db_result", str(run_query(node_input)))
    except sqlite3.Error as error:
        if attempts >= MAX_RETRIES:
            return Event(output=f"The query failed after {attempts} retries: {error}", route=ROUTE_FAILED)
        feedback = f"This query failed:\n{node_input}\nError: {error}\nWrite a corrected SELECT."
        return Event(output=feedback, state={"attempts": attempts + 1}, route=ROUTE_RETRY)
    return Event(output=result, state={RESULT_STATE_KEY: result}, route=ROUTE_OK)
