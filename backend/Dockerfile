FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY . .

# Run db seeding and start server
EXPOSE 8000

# We run database migrations/seeding before starting
CMD python seed.py && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
