FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client (with minimal memory usage)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt ./

# Install dependencies with pip (uses less memory than poetry)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"] 
