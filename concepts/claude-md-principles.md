# CLAUDE.md Principles

> Your CLAUDE.md is your team's onboarding document. Make it count.

## What is CLAUDE.md?

CLAUDE.md is a special file that Claude Code reads at the start of every session. It's your chance to give Claude context about your project.

Think of it as the document you'd give a new developer on their first day.

## The 5 Principles

### 1. Be Specific, Not Generic

**Bad**:
```markdown
# My Project
This is a web application.
```

**Good**:
```markdown
# E-commerce Platform

## Tech Stack
- Next.js 14 (App Router)
- PostgreSQL + Prisma
- Stripe for payments
- Cloudflare R2 for images

## Key Directories
- /app - Next.js pages and API routes
- /lib - Shared utilities
- /components - React components
- /prisma - Database schema and migrations
```

### 2. Document Decisions, Not Just Facts

**Bad**:
```markdown
We use JWT tokens.
```

**Good**:
```markdown
## Authentication
We use JWT tokens stored in httpOnly cookies (not localStorage).

Why: Prevents XSS attacks from stealing tokens.

Implementation:
- Access token: 15 min expiry
- Refresh token: 7 day expiry
- Refresh endpoint: POST /api/auth/refresh
```

### 3. Include Common Commands

```markdown
## Development Commands

```bash
pnpm dev          # Start dev server
pnpm test         # Run tests
pnpm db:migrate   # Run migrations
pnpm db:seed      # Seed test data
```

## Before Committing
1. Run `pnpm typecheck`
2. Run `pnpm test`
3. Run `pnpm lint`
```

### 4. Set Boundaries and Preferences

```markdown
## Coding Preferences

DO:
- Use TypeScript strict mode
- Write tests for new features
- Use existing UI components from /components/ui
- Follow existing patterns in the codebase

DON'T:
- Add new dependencies without asking
- Modify the authentication flow
- Change database schema without migration
- Use any over proper types
```

### 5. Keep It Updated

Your CLAUDE.md should evolve with your project:

- Add patterns as they emerge
- Remove outdated information
- Document new architectural decisions
- Include learnings from bugs

## Template

```markdown
# [Project Name]

> One-line description

## Tech Stack
- [Framework]
- [Database]
- [Key libraries]

## Directory Structure
```
/src
  /components  - React components
  /lib         - Utilities
  /api         - API routes
```

## Development

### Setup
```bash
pnpm install
cp .env.example .env
pnpm db:migrate
```

### Commands
```bash
pnpm dev      # Development
pnpm test     # Tests
pnpm build    # Production build
```

## Architecture Decisions

### [Decision 1]
What: [Description]
Why: [Reasoning]

### [Decision 2]
What: [Description]
Why: [Reasoning]

## Coding Guidelines

### Do
- [Guideline 1]
- [Guideline 2]

### Don't
- [Anti-pattern 1]
- [Anti-pattern 2]

## Common Tasks

### Adding a new API endpoint
1. Create file in /api
2. Add types in /types
3. Write tests in /__tests__

### Adding a new component
1. Create in /components
2. Use existing design tokens
3. Add Storybook story
```

## Pro Tips

1. **Start small** - A 20-line CLAUDE.md is better than no CLAUDE.md
2. **Be prescriptive** - "Use X" is better than "You might want to use X"
3. **Include examples** - Show don't tell
4. **Version control it** - Your CLAUDE.md should be in git

---

Next: [Parallel Agents](./parallel-agents.md)
