"""SQLite access: sample data, schema introspection and read-only execution."""

import sqlite3
from dataclasses import dataclass

_SEED = """
CREATE TABLE courses (id INTEGER PRIMARY KEY, name TEXT, level TEXT, price REAL);
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, course_id INTEGER REFERENCES courses(id));

INSERT INTO courses VALUES
    (1, 'Python from scratch', 'beginner', 49),
    (2, 'React for beginners', 'beginner', 59),
    (3, 'Introduction to AI', 'intermediate', 89);

INSERT INTO students VALUES
    (1, 'Ana', 1), (2, 'Luis', 1), (3, 'Marta', 2), (4, 'Pablo', 3), (5, 'Sofia', 3);
"""


@dataclass(frozen=True)
class QueryResult:
    sql: str
    columns: list[str]
    rows: list[tuple]

    def __str__(self) -> str:
        return f"SQL: {self.sql}\nColumns: {self.columns}\nRows: {self.rows}"


_connection = sqlite3.connect(":memory:", check_same_thread=False)
_connection.executescript(_SEED)
_connection.execute("PRAGMA query_only = ON")  # defense in depth: no writes after seeding


def get_schema() -> str:
    """Return the CREATE TABLE statements so the LLM knows what it can query."""
    rows = _connection.execute("SELECT sql FROM sqlite_master WHERE type = 'table'")
    return "\n".join(sql for (sql,) in rows)


def run_query(sql: str) -> QueryResult:
    """Execute a single SQL statement and return its columns and rows."""
    cursor = _connection.execute(sql)
    columns = [column[0] for column in cursor.description]
    return QueryResult(sql=sql, columns=columns, rows=cursor.fetchall())
