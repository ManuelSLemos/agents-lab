# sql_agent

Multi-agent text-to-SQL built with the ADK graph API (`Workflow`). Ask a question in natural
language, get an answer computed from a SQLite database.

```
START -> sql_writer -> validate --ok-------> execute --ok-------> answerer
             ^                  \-rejected-> reject  \-failed---> reject
             |                                       |
             +------------------retry----------------+
```

| Node | Type | Job |
|---|---|---|
| `sql_writer` | LLM agent | Question -> one SQLite `SELECT` (also fixes a failed query) |
| `validate` | Python | Only `SELECT` passes; routes `ok` / `rejected` |
| `execute` | Python | Runs the query; on SQL error routes `retry` (max `MAX_RETRIES`) or `failed` |
| `reject` | Python | Returns why the request could not be answered |
| `answerer` | LLM agent | Explains the result in the user's language |

## Layout

```
sql_agent/
├── agent.py      # the graph (the only place where the flow is described)
├── agents/       # one module per LLM agent
├── nodes.py      # plain-Python nodes and route names
├── database.py   # sample SQLite data, schema, read-only query execution
└── config.py     # model, MAX_RETRIES, state key
```

## Run

```bash
docker compose up -d ollama      # needs qwen3:4b pulled
adk web                          # pick "sql_agent"
```

Example questions: "¿Cuántos alumnos tiene cada curso?", "¿Cuál es el curso más caro?"

## Safety

Two layers: `validate` rejects anything that is not a `SELECT`, and the connection runs with
`PRAGMA query_only = ON`, so even a query that slipped through cannot write.
