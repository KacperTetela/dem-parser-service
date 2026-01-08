FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any are needed (awpy might need some, but usually wheels cover it)
# RUN apt-get update && apt-get install -y ...

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create temp directory
RUN mkdir temp

# Expose port
EXPOSE 5001

# Run with Gunicorn-style workers via Uvicorn for concurrency
# --workers 4 allows handling multiple requests in parallel (via multiprocessing)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7355", "--workers", "4"]
