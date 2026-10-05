FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY . .

RUN uv sync

CMD ["uv", "run", "adk", "web", "--host", "0.0.0.0", "--port", "8000", "--reload_agents"]
