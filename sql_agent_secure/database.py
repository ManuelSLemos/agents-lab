"""Read-only SQLite guarded by the engine itself: allowed tables and functions, capped rows and time."""

import sqlite3
import time

from sql_agent.database import QueryResult

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


TABLES = {"courses", "students"}
FUNCTIONS = {"count", "sum", "avg", "min", "max", "round", "lower", "upper", "length", "abs", "coalesce"}
MAX_ROWS = 50
MAX_SECONDS = 1.0

_deadline = 0.0


def _authorize(action: int, arg1: str | None, arg2: str | None, db: str | None, source: str | None) -> int:
    """SQLite asks here before doing anything. Whatever is not explicitly allowed is denied."""
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ and arg1 in TABLES:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION and arg2 in FUNCTIONS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def _timed_out() -> int:
    """Return 1 (abort the query) once it has run for too long."""
    return 1 if time.monotonic() > _deadline else 0


_connection = sqlite3.connect(":memory:", check_same_thread=False)
_connection.executescript(_SEED)
_connection.execute("PRAGMA query_only = ON")
_connection.set_authorizer(_authorize)  # set last: after seeding and PRAGMAs, which are no longer allowed
_connection.set_progress_handler(_timed_out, 10_000)


def run_query(sql: str) -> QueryResult:
    """Execute a single statement under the limits above; return at most MAX_ROWS rows."""
    global _deadline
    _deadline = time.monotonic() + MAX_SECONDS
    cursor = _connection.execute(sql)
    columns = [column[0] for column in cursor.description]
    return QueryResult(sql=sql, columns=columns, rows=cursor.fetchmany(MAX_ROWS))
