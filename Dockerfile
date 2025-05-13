# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

ENV SLEEP_HOURS=24

ENTRYPOINT ["/app/docker-entrypoint.sh"]
