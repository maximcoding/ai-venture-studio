FROM python:3.12-slim

WORKDIR /app

# Postgres client for connection
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY docs/ ./docs/

RUN pip install --no-cache-dir -e ".[dev]"

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.main"]
