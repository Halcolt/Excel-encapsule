FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

EXPOSE 8000
ENV PORT=8000
CMD ["/bin/sh", "-lc", "gunicorn -w 2 -b 0.0.0.0:${PORT} main:app"]
