# WashFlow

A SaaS platform for car wash businesses in Mexico. This monorepo contains the backend API, web frontend, and mobile app.

## Repository Structure

```
washflow/
├── apps/
│   ├── api/          # FastAPI backend (Python)
│   ├── web/          # Vue 3 frontend (TypeScript)
│   └── mobile/       # Flutter mobile app (Dart)
├── packages/
│   └── shared/       # Shared types and documentation
├── infra/            # Infrastructure (Docker, etc.)
└── README.md
```

## Prerequisites

- **Docker** & Docker Compose
- **Python 3.12+** with [uv](https://docs.astral.sh/uv/)
- **Node.js 18+** with [pnpm](https://pnpm.io/)
- **Flutter 3.16+** (stable channel)
- **just** (optional, for task running) - `brew install just`

## Quick Start

### 1. Start Database

```bash
cd infra
docker compose up -d
```

This starts:
- PostgreSQL on port `5432`
- pgAdmin on port `5050` (http://localhost:5050)

### 2. Start API

```bash
cd apps/api

# Copy and configure environment
cp .env.example .env

# Install dependencies
uv sync --all-extras

# Run migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn washflow_api.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

### 3. Start Web App

```bash
cd apps/web

# Copy and configure environment
cp .env.example .env

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

Web app will be available at http://localhost:5173

### 4. Run Mobile App

```bash
cd apps/mobile

# Install dependencies
flutter pub get

# Run on connected device/emulator
flutter run

# For Android emulator, the API is accessible at 10.0.2.2:8000
# For iOS simulator, use localhost:8000
# For physical device, use your machine's IP address
flutter run --dart-define=API_BASE_URL=http://YOUR_IP:8000
```

## Development

### API Commands

Using `just` (in `apps/api`):

| Command | Description |
|---------|-------------|
| `just dev` | Run dev server with hot reload |
| `just migrate` | Apply database migrations |
| `just migration "message"` | Create new migration |
| `just test` | Run tests |
| `just lint` | Run linter |
| `just format` | Format code |

### Web Commands

Using `pnpm` (in `apps/web`):

| Command | Description |
|---------|-------------|
| `pnpm dev` | Run dev server |
| `pnpm build` | Build for production |
| `pnpm lint` | Run linter |
| `pnpm typecheck` | Type check |

### Mobile Commands

Using `flutter` (in `apps/mobile`):

| Command | Description |
|---------|-------------|
| `flutter run` | Run on device/emulator |
| `flutter build apk` | Build Android APK |
| `flutter build ios` | Build iOS app |

## Database

### Connection Details

- **Host:** localhost
- **Port:** 5432
- **Database:** washflow
- **User:** washflow
- **Password:** washflow

### pgAdmin Access

- **URL:** http://localhost:5050
- **Email:** admin@washflow.local
- **Password:** admin

## Environment Variables

### API (apps/api/.env)

```bash
DATABASE_URL=postgresql+asyncpg://washflow:washflow@localhost:5432/washflow
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ACCESS_TTL_MIN=30
JWT_REFRESH_TTL_DAYS=7
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DEBUG=true
LOG_LEVEL=DEBUG
```

### Web (apps/web/.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Architecture

### API

- **Framework:** FastAPI
- **Database:** PostgreSQL with async SQLAlchemy 2.0
- **Migrations:** Alembic
- **Auth:** JWT (access + refresh tokens)

### Web

- **Framework:** Vue 3 + TypeScript
- **Styling:** TailwindCSS + shadcn-vue style components
- **State:** Pinia
- **Routing:** Vue Router
- **HTTP:** Axios with interceptors

### Mobile

- **Framework:** Flutter
- **State:** Riverpod
- **Routing:** GoRouter
- **HTTP:** Dio
- **Storage:** Flutter Secure Storage

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh tokens |
| GET | `/api/v1/auth/me` | Get current user |

## Future Modules (Not Implemented)

- Multi-tenant organizations
- Multiple locations (sucursales)
- Ticket/service management
- Kanban board for workflow
- Staff scheduling
- Customer tracking
- Public tracking page
- Waiting room display

## License

Proprietary - All rights reserved
