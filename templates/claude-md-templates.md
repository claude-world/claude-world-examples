# CLAUDE.md Templates by Framework

> Ready-to-use CLAUDE.md templates for popular frameworks and tech stacks.

## How to Use These Templates

1. Copy the template for your tech stack
2. Paste into `CLAUDE.md` at your project root
3. Customize the bracketed `[placeholders]`
4. Remove sections that don't apply
5. Add project-specific rules

## Templates

### React + TypeScript

```markdown
# [Project Name]

## Tech Stack
- React 18+ with TypeScript
- [State Management: Redux Toolkit / Zustand / Context]
- [Styling: Tailwind CSS / styled-components / CSS Modules]
- [Testing: Vitest / Jest + React Testing Library]

## Project Structure
```
src/
├── components/     # Reusable UI components
├── pages/          # Route components
├── hooks/          # Custom React hooks
├── store/          # State management
├── services/       # API calls
├── types/          # TypeScript types
└── utils/          # Helper functions
```

## Code Standards

### Components
- Functional components only (no class components)
- Props interface defined above component
- Use `const Component: React.FC<Props>` pattern
- Co-locate component, styles, and tests

### Naming
- Components: PascalCase (`UserProfile.tsx`)
- Hooks: camelCase with `use` prefix (`useAuth.ts`)
- Utils: camelCase (`formatDate.ts`)
- Types: PascalCase with descriptive suffix (`UserResponse`)

### State Management
- Local state for UI-only state
- Global state for shared data
- Server state with [React Query / SWR]

## Testing
- Run tests: `npm test`
- Coverage target: 80%
- Test user behavior, not implementation

## Commands
```bash
npm run dev      # Development server
npm run build    # Production build
npm run test     # Run tests
npm run lint     # Lint check
```
```

---

### Next.js 14+ (App Router)

```markdown
# [Project Name]

## Tech Stack
- Next.js 14+ with App Router
- TypeScript strict mode
- [Database: Prisma / Drizzle + PostgreSQL]
- [Auth: NextAuth.js / Clerk]
- Tailwind CSS

## Project Structure
```
app/
├── (auth)/         # Auth route group
├── (dashboard)/    # Dashboard route group
├── api/            # API routes
└── layout.tsx      # Root layout

components/
├── ui/             # Shadcn/ui components
└── features/       # Feature components

lib/
├── db.ts           # Database client
├── auth.ts         # Auth utilities
└── utils.ts        # Helper functions
```

## Code Standards

### Server vs Client Components
- Default to Server Components
- Add 'use client' only when needed (hooks, browser APIs)
- Keep client components small and leaf-level

### Data Fetching
- Server Components: Direct database/API calls
- Client Components: Server Actions or API routes
- Always handle loading and error states

### Route Handlers
- Use `route.ts` for API endpoints
- Return `NextResponse.json()` for JSON
- Handle errors with proper status codes

## Database
- Migrations: `npx prisma migrate dev`
- Generate: `npx prisma generate`
- Studio: `npx prisma studio`

## Commands
```bash
npm run dev      # Development (turbopack)
npm run build    # Production build
npm run start    # Production server
npm run lint     # ESLint check
```

## Environment Variables
Required in `.env.local`:
- `DATABASE_URL`
- `NEXTAUTH_SECRET`
- `NEXTAUTH_URL`
```

---

### Python + FastAPI

```markdown
# [Project Name]

## Tech Stack
- Python 3.11+
- FastAPI with Pydantic v2
- SQLAlchemy 2.0 + PostgreSQL
- Alembic for migrations
- pytest for testing

## Project Structure
```
app/
├── api/
│   ├── routes/      # API endpoints
│   └── deps.py      # Dependencies
├── core/
│   ├── config.py    # Settings
│   └── security.py  # Auth utilities
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
└── main.py          # App entry point

tests/
├── api/             # API tests
├── services/        # Service tests
└── conftest.py      # Fixtures
```

## Code Standards

### Type Hints
- All functions must have type hints
- Use Pydantic models for request/response
- Avoid `Any` type

### API Design
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return appropriate status codes
- Use dependency injection for auth, db

### Database
- Use async SQLAlchemy
- One model per file
- Alembic for all schema changes

## Commands
```bash
# Development
uvicorn app.main:app --reload

# Testing
pytest -v
pytest --cov=app

# Database
alembic upgrade head
alembic revision --autogenerate -m "description"

# Linting
ruff check .
mypy app/
```

## Environment Variables
Required in `.env`:
- `DATABASE_URL`
- `SECRET_KEY`
- `ENVIRONMENT` (development/production)
```

---

### Node.js + Express + TypeScript

```markdown
# [Project Name]

## Tech Stack
- Node.js 20+ with TypeScript
- Express.js
- [Database: Prisma / TypeORM + PostgreSQL]
- Jest for testing
- Zod for validation

## Project Structure
```
src/
├── controllers/     # Request handlers
├── services/        # Business logic
├── models/          # Database models
├── middleware/      # Express middleware
├── routes/          # Route definitions
├── utils/           # Helper functions
├── types/           # TypeScript types
└── app.ts           # Express app setup

tests/
├── integration/     # API tests
└── unit/            # Unit tests
```

## Code Standards

### Error Handling
- Use custom error classes
- Centralized error middleware
- Never expose internal errors to client

### Validation
- Validate all input with Zod
- Sanitize user input
- Return 400 for validation errors

### Authentication
- JWT in httpOnly cookies
- Refresh token rotation
- Rate limiting on auth endpoints

## API Response Format
```typescript
// Success
{ "data": {...}, "meta": {...} }

// Error
{ "error": { "code": "...", "message": "..." } }
```

## Commands
```bash
npm run dev      # Development with nodemon
npm run build    # Compile TypeScript
npm run start    # Production server
npm run test     # Run tests
npm run lint     # ESLint check
```

## Environment Variables
Required in `.env`:
- `PORT`
- `DATABASE_URL`
- `JWT_SECRET`
- `NODE_ENV`
```

---

### Go + Gin/Echo

```markdown
# [Project Name]

## Tech Stack
- Go 1.21+
- [Framework: Gin / Echo]
- PostgreSQL with pgx
- golang-migrate for migrations
- testify for testing

## Project Structure
```
cmd/
└── api/
    └── main.go      # Entry point

internal/
├── handler/         # HTTP handlers
├── service/         # Business logic
├── repository/      # Database access
├── model/           # Domain models
├── middleware/      # HTTP middleware
└── config/          # Configuration

pkg/
└── utils/           # Shared utilities

migrations/          # SQL migrations
```

## Code Standards

### Error Handling
- Return errors, don't panic
- Wrap errors with context
- Use custom error types for domain errors

### Naming
- Packages: lowercase, single word
- Interfaces: verb-er pattern (`Reader`, `Handler`)
- Avoid stuttering (`user.User` → `user.Model`)

### Database
- Use prepared statements
- Connection pooling configured
- Transactions for multi-step operations

## Commands
```bash
# Development
go run cmd/api/main.go

# Build
go build -o bin/api cmd/api/main.go

# Test
go test ./...
go test -cover ./...

# Migrations
migrate -path migrations -database $DATABASE_URL up
migrate -path migrations -database $DATABASE_URL down 1
```

## Environment Variables
Required:
- `PORT`
- `DATABASE_URL`
- `JWT_SECRET`
- `ENVIRONMENT`
```

---

### Vue 3 + TypeScript

```markdown
# [Project Name]

## Tech Stack
- Vue 3 with Composition API
- TypeScript
- [State: Pinia]
- [Router: Vue Router 4]
- [UI: Vuetify / PrimeVue / Naive UI]
- Vite

## Project Structure
```
src/
├── components/      # Reusable components
├── views/           # Route views
├── composables/     # Composition functions
├── stores/          # Pinia stores
├── services/        # API services
├── types/           # TypeScript types
├── utils/           # Helper functions
└── router/          # Route definitions
```

## Code Standards

### Components
- Use `<script setup lang="ts">`
- Props with TypeScript interfaces
- Emit with typed events
- Single-file components (.vue)

### Composition API
- Use `ref` for primitives, `reactive` for objects
- Extract logic into composables
- Name composables with `use` prefix

### State Management
- Pinia for global state
- Define stores with `defineStore`
- Use getters for computed state

## Commands
```bash
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production
npm run test     # Run tests
npm run lint     # Lint check
```
```

---

### Astro + React/Vue

```markdown
# [Project Name]

## Tech Stack
- Astro 4+
- [UI Framework: React / Vue / Svelte]
- Tailwind CSS
- [CMS: Contentful / Sanity / MDX]

## Project Structure
```
src/
├── components/      # UI components
├── layouts/         # Page layouts
├── pages/           # File-based routing
├── content/         # Content collections
├── styles/          # Global styles
└── utils/           # Helper functions

public/              # Static assets
```

## Code Standards

### Islands Architecture
- Default to static (no JS)
- Add `client:*` only when needed
- Prefer `client:visible` for below-fold

### Content Collections
- Define schemas in `src/content/config.ts`
- Use type-safe queries
- Validate frontmatter

### Performance
- Minimize client-side JS
- Use image optimization
- Preload critical assets

## Commands
```bash
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production
astro add [pkg]  # Add integration
```
```

---

### Django + DRF

```markdown
# [Project Name]

## Tech Stack
- Python 3.11+ / Django 5+
- Django REST Framework
- PostgreSQL
- Celery + Redis (background tasks)
- pytest-django

## Project Structure
```
project/
├── config/          # Django settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/       # User app
│   ├── core/        # Shared utilities
│   └── [feature]/   # Feature apps
├── tests/           # Test files
└── manage.py

```

## Code Standards

### Apps
- One app per domain concept
- Keep apps small and focused
- Use apps/ directory for all apps

### Models
- Use UUIDs for primary keys
- Add `created_at`, `updated_at` timestamps
- Define `__str__` for all models

### API
- Use ViewSets for CRUD
- Custom actions with `@action` decorator
- Pagination on all list endpoints

### Serializers
- Separate read/write serializers if needed
- Validate in serializer, not view
- Use `SerializerMethodField` sparingly

## Commands
```bash
# Development
python manage.py runserver

# Database
python manage.py makemigrations
python manage.py migrate

# Testing
pytest
pytest --cov=apps

# Shell
python manage.py shell_plus
```

## Environment Variables
Required:
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `DJANGO_SETTINGS_MODULE`
```

---

### Ruby on Rails

```markdown
# [Project Name]

## Tech Stack
- Ruby 3.2+ / Rails 7+
- PostgreSQL
- [Frontend: Hotwire / React]
- RSpec + FactoryBot
- Sidekiq for background jobs

## Project Structure
```
app/
├── controllers/
├── models/
├── views/
├── services/        # Service objects
├── queries/         # Query objects
└── jobs/            # Background jobs

spec/
├── models/
├── requests/
├── services/
└── factories/
```

## Code Standards

### Controllers
- Thin controllers, fat models
- Use `before_action` for auth
- Respond with appropriate status codes

### Models
- Validations in model
- Scopes for common queries
- Callbacks sparingly (prefer service objects)

### Service Objects
- One public method (`call`)
- Return Result object or raise
- Keep side-effect free when possible

## Commands
```bash
# Development
bin/rails server

# Database
bin/rails db:migrate
bin/rails db:seed

# Testing
bundle exec rspec
bundle exec rspec --format documentation

# Console
bin/rails console

# Generate
bin/rails generate model User name:string email:string
```

## Environment Variables
Required in `.env`:
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY_BASE`
- `RAILS_ENV`
```

---

## Customization Tips

### Add Project-Specific Sections

```markdown
## Business Logic

### [Domain Concept]
- Rule 1
- Rule 2

### Workflow
1. Step 1
2. Step 2
```

### Add Team Conventions

```markdown
## Team Conventions

### Code Review
- All PRs require 1 approval
- Use conventional commits
- Squash merge to main

### Branch Naming
- feature/[ticket]-description
- fix/[ticket]-description
- chore/description
```

### Add External Services

```markdown
## External Services

### [Service Name]
- Purpose: [why we use it]
- Dashboard: [URL]
- Docs: [URL]
```

## Summary

1. **Start with a template** - Don't write from scratch
2. **Customize for your project** - Remove what doesn't apply
3. **Keep it updated** - CLAUDE.md is a living document
4. **Be specific** - Vague instructions = inconsistent results
5. **Include commands** - Claude needs to know how to run things

---

See also: [CLAUDE.md Principles](../concepts/claude-md-principles.md) | [CLAUDE.md Anti-Patterns](../concepts/claude-md-anti-patterns.md)
