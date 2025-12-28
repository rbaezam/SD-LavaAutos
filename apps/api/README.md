# WashFlow API

FastAPI backend for WashFlow car wash SaaS.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- PostgreSQL 15+
- [just](https://github.com/casey/just) (optional, for task running)

## Setup

1. **Install dependencies:**
   ```bash
   uv sync --all-extras
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run migrations:**
   ```bash
   just migrate
   # or: uv run alembic upgrade head
   ```

4. **Start development server:**
   ```bash
   just dev
   # or: uv run uvicorn washflow_api.main:app --reload
   ```

## Available Commands

Using `just` (recommended):

| Command | Description |
|---------|-------------|
| `just install` | Install dependencies |
| `just dev` | Run dev server with hot reload |
| `just run` | Run production server |
| `just migrate` | Apply database migrations |
| `just migration "message"` | Create new migration |
| `just test` | Run tests |
| `just lint` | Run linter |
| `just format` | Format code |
| `just typecheck` | Run type checker |

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

## Project Structure

```
apps/api/
├── src/washflow_api/
│   ├── api/           # API routes
│   │   └── v1/        # Version 1 endpoints
│   ├── core/          # Config, security, logging
│   ├── db/            # Database setup
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # App entry point
├── migrations/        # Alembic migrations
├── tests/             # Test files
└── pyproject.toml     # Dependencies & config
```
