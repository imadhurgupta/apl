# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Cloud Run injects PORT env var; default to 8080
ENV PORT=8080

# Run with gunicorn — 1 worker to preserve in-memory state across requests
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 60 app:app
