"""SQLite access to the Chinook database: schema introspection and read-only execution."""

import sqlite3
from dataclasses import dataclass

from .config import DB_PATH


@dataclass(frozen=True)
class QueryResult:
    sql: str
    columns: list[str]
    rows: list[tuple]

    def __str__(self) -> str:
        return f"SQL: {self.sql}\nColumns: {self.columns}\nRows: {self.rows}"


# mode=ro makes SQLite itself refuse writes; query_only is a second layer on top.
_connection = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
_connection.execute("PRAGMA query_only = ON")


def get_schema() -> str:
    """Return the CREATE TABLE statements so the LLM knows what it can query."""
    rows = _connection.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
    return "\n".join(sql for (sql,) in rows)


def run_query(sql: str) -> QueryResult:
    """Execute a single SQL statement and return its columns and rows."""
    cursor = _connection.execute(sql)
    columns = [column[0] for column in cursor.description]
    return QueryResult(sql=sql, columns=columns, rows=cursor.fetchall())
