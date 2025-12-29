FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for asyncpg and bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and source code (needed for hatch build)
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package (this will build and install washflow_api)
RUN pip install --no-cache-dir .

# Copy migrations and alembic config
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn washflow_api.main:app --host 0.0.0.0 --port 8000"]
