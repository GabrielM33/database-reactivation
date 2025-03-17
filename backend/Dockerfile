FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.5.1

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-dev

# Copy application code
COPY . .

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"] 
