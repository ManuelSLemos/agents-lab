"""Hardened text-to-SQL: the SQLite engine decides what can be read."""

from observability import setup

setup()

from .agent import root_agent  # noqa: E402

__all__ = ["root_agent"]
