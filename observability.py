"""Tracing helpers shared by the agents.

ADK exports its own spans (workflow, nodes, call_llm) when the standard OpenTelemetry variables are set:

    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://phoenix:6006/v1/traces
    OTEL_RESOURCE_ATTRIBUTES=openinference.project.name=sql_agent_secure

Any OTLP backend works the same way. This module only adds the LiteLLM spans (model, tokens),
and does nothing when no endpoint is configured, so tests and plain runs stay untouched.
"""

import os

_ENDPOINT_VARS = ("OTEL_EXPORTER_OTLP_ENDPOINT", "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")


def setup() -> None:
    if not any(os.environ.get(var) for var in _ENDPOINT_VARS):
        return
    from openinference.instrumentation.litellm import LiteLLMInstrumentor

    LiteLLMInstrumentor().instrument()
