FROM python:3.12-slim
# Subproject: Notion Dockerfile

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps separately for better layer caching
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Code is mounted at runtime via docker compose
