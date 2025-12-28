# WashFlow Web

Vue 3 frontend for WashFlow car wash SaaS.

## Prerequisites

- Node.js 18+
- pnpm

## Setup

1. **Install dependencies:**
   ```bash
   pnpm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start development server:**
   ```bash
   pnpm dev
   ```

## Available Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start dev server on port 5173 |
| `pnpm build` | Build for production |
| `pnpm preview` | Preview production build |
| `pnpm lint` | Run ESLint |
| `pnpm lint:fix` | Fix ESLint issues |
| `pnpm typecheck` | Run TypeScript type checking |

## Tech Stack

- Vue 3 + Composition API
- TypeScript
- Vite
- TailwindCSS
- Pinia (state management)
- Vue Router
- Axios
- Zod (validation)
- Lucide icons

## Project Structure

```
apps/web/src/
├── assets/          # CSS and static assets
├── components/
│   ├── layout/      # App layout components
│   └── ui/          # Reusable UI components (shadcn-vue style)
├── composables/     # Vue composables (future)
├── lib/             # Utilities and API client
├── router/          # Vue Router configuration
├── stores/          # Pinia stores
└── views/           # Page components
    ├── app/         # Protected app pages
    └── auth/        # Auth pages
```

## Routes

- `/login` - Login page
- `/register` - Registration page
- `/app/dashboard` - Main dashboard (protected)
- `/app/settings` - User settings (protected)
