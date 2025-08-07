FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY main.py ./
COPY services/ ./services/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Expose port
EXPOSE 8080

# Run the HTTP server (accessible from outside)
CMD ["poetry", "run", "start"]
