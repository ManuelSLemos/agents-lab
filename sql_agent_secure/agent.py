"""Same graph as sql_agent, with validate, execute and answerer hardened.

    START -> sql_writer -> validate --ok-------> execute --ok-------> answerer
                 ^                  \\-rejected-> reject  \\-failed---> reject
                 |                                       |
                 +------------------retry----------------+
"""

from google.adk.workflow import Workflow

from .answerer import answerer
from .nodes import ROUTE_FAILED, ROUTE_OK, ROUTE_REJECTED, ROUTE_RETRY, execute, reject, validate
from .writer import sql_writer

root_agent = Workflow(
    name="sql_agent_secure",
    edges=[
        ("START", sql_writer, validate),
        (validate, {ROUTE_OK: execute, ROUTE_REJECTED: reject}),
        (execute, {ROUTE_OK: answerer, ROUTE_RETRY: sql_writer, ROUTE_FAILED: reject}),
    ],
)
