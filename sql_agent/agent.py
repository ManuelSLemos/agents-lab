"""Workflow definition: the graph is the only place where the flow is described.

    START -> sql_writer -> validate --ok-------> execute --ok-------> answerer
                 ^                  \\-rejected-> reject  \\-failed---> reject
                 |                                       |
                 +------------------retry----------------+
"""

from google.adk.workflow import Workflow

from .agents import answerer, sql_writer
from .nodes import ROUTE_FAILED, ROUTE_OK, ROUTE_REJECTED, ROUTE_RETRY, execute, reject, validate

root_agent = Workflow(
    name="sql_agent",
    edges=[
        ("START", sql_writer, validate),
        (validate, {ROUTE_OK: execute, ROUTE_REJECTED: reject}),
        (execute, {ROUTE_OK: answerer, ROUTE_RETRY: sql_writer, ROUTE_FAILED: reject}),
    ],
)
