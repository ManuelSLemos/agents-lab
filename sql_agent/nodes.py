"""Plain-Python workflow nodes. Whatever they return flows to the next node."""

import sqlite3

from google.adk.events.event import Event

from .config import MAX_RETRIES, RESULT_STATE_KEY
from .database import run_query

ROUTE_OK = "ok"
ROUTE_REJECTED = "rejected"
ROUTE_RETRY = "retry"
ROUTE_FAILED = "failed"


def _clean_sql(raw: str) -> str:
    """Strip the markdown fences that models like to add around SQL."""
    text = str(raw).strip().strip("`").strip()
    return text[3:].strip() if text[:3].lower() == "sql" else text


def validate(node_input: str) -> Event:
    """Allow read-only queries only; the route decides the next node."""
    sql = _clean_sql(node_input)
    if sql.lower().startswith("select"):
        return Event(output=sql, route=ROUTE_OK)
    return Event(output=f"Only SELECT queries are allowed, got: {sql}", route=ROUTE_REJECTED)


def execute(node_input: str, attempts: int = 0) -> Event:
    """Run the validated query. On a SQL error, send it back to the writer."""
    try:
        result = str(run_query(node_input))
    except sqlite3.Error as error:
        if attempts >= MAX_RETRIES:
            return Event(output=f"The query failed after {attempts} retries: {error}", route=ROUTE_FAILED)
        feedback = f"This query failed:\n{node_input}\nError: {error}\nWrite a corrected SELECT."
        return Event(output=feedback, state={"attempts": attempts + 1}, route=ROUTE_RETRY)
    return Event(output=result, state={RESULT_STATE_KEY: result}, route=ROUTE_OK)


def reject(node_input: str) -> str:
    """Return the reason why the request could not be answered."""
    return node_input
