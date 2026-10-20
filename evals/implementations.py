"""The two implementations to compare, with the same interface: sql -> 'allowed' | 'blocked'."""

import asyncio
import inspect
import sqlite3

from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from sql_agent import database as original_db
from sql_agent import nodes as original_nodes
from sql_agent_secure import database as secure_db
from sql_agent import agents as original_agents
from sql_agent_secure import nodes as secure_nodes
from sql_agent_secure.answerer import answerer as secure_answerer
from sql_agent_secure.writer import sql_writer as secure_writer

ALLOWED = "allowed"
BLOCKED = "blocked"


def _run(nodes, db, sql: str) -> str:
    event = nodes.validate(sql)
    if event.actions.route != nodes.ROUTE_OK:
        return BLOCKED
    try:
        db.run_query(event.output)
    except sqlite3.Error:
        return BLOCKED
    return ALLOWED


def original(sql: str) -> str:
    return _run(original_nodes, original_db, sql)


def secure(sql: str) -> str:
    return _run(secure_nodes, secure_db, sql)


def original_result(sql: str) -> str:
    """What the answerer LLM receives from the original execute node."""
    return original_nodes.execute(sql).output


def secure_result(sql: str) -> str:
    """What the answerer LLM receives from the secure execute node."""
    return secure_nodes.execute(sql).output


def is_marked_as_data(result: str) -> bool:
    """True when the whole result is inside one <db_result> tag and nothing in it can close the tag."""
    return result.startswith("<db_result>\n") and result.endswith("\n</db_result>") and result.count("</db_result>") == 1


def _first_response(callbacks, *args) -> LlmResponse | None:
    """Run the callbacks the way ADK does: the first one that returns something short-circuits."""
    for callback in callbacks:
        result = callback(*args)
        if inspect.isawaitable(result):
            result = asyncio.run(result)
        if result is not None:
            return result
    return None


def prompt_blocked(writer, text: str) -> bool:
    """True when the writer's configured before_model callbacks stop this user prompt."""
    request = LlmRequest(contents=[types.Content(role="user", parts=[types.Part(text=text)])])
    return _first_response(writer.canonical_before_model_callbacks, None, request) is not None


def answer_replaced(answerer, text: str) -> bool:
    """True when the answerer's configured after_model callbacks replace this model answer."""
    response = LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))
    return _first_response(answerer.canonical_after_model_callbacks, None, response) is not None


original_writer = original_agents.sql_writer
original_answerer = original_agents.answerer
