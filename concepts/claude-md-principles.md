# CLAUDE.md Principles

> Your CLAUDE.md is your team's onboarding document. Make it count.

## What is CLAUDE.md?

CLAUDE.md is a markdown file that Claude Code loads into context at the start of every session. It's your chance to give Claude the project context it can't infer from the code alone.

Think of it as the document you'd give a new developer on their first day.

### Where CLAUDE.md Files Live

Claude Code reads CLAUDE.md from several locations. They load in this order, from broadest to most specific:

| Scope | Location | Shared with |
|-------|----------|-------------|
| Managed policy | Deployed by IT, e.g. `/etc/claude-code/CLAUDE.md` on Linux | Everyone on the machine |
| User | `~/.claude/CLAUDE.md` | Only you, all projects |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Your team, via git |
| Local | `./CLAUDE.local.md` (add it to `.gitignore`) | Only you, this project |

Files in the directory where you start Claude, and in the directories above it, load at launch. They add up rather than override each other, and the most specific file is read last. CLAUDE.md files in subdirectories load on demand, once Claude reads or edits a file there. If a repository has an `AGENTS.md` for other coding agents and no CLAUDE.md, Claude Code reads the `AGENTS.md` instead; if you keep both, put `@AGENTS.md` at the top of your CLAUDE.md to import it.

Run `/init` to have Claude draft a CLAUDE.md from your codebase, `/memory` to open your memory files, and `/context` to confirm which ones loaded.

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
- Next.js 16 (App Router)
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

````markdown
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
````

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

> **Guidance, not enforcement.** Claude treats CLAUDE.md as context: it tries to follow these rules, but nothing here is enforced. For anything that must hold every time, add a `deny` (or `ask`) rule under `permissions` in `.claude/settings.json`, or a [hook](./hooks-basics.md). [CLAUDE.md Anti-Patterns](./claude-md-anti-patterns.md) shows an example.

### 5. Keep It Updated

Your CLAUDE.md should evolve with your project:

- Add patterns as they emerge (a good trigger: Claude makes the same mistake twice)
- Remove outdated information
- Document new architectural decisions
- Include learnings from bugs

Edit the file directly (`/memory` opens it), or ask Claude to "add this to CLAUDE.md". The old `#` quick-add shortcut is gone. Every so often, run `/doctor prompt-audit`: Claude flags instructions written for older models, references to files or commands that no longer exist, and contradictions, then proposes edits and changes nothing until you approve.

## When CLAUDE.md Grows

Aim for under ~200 lines per CLAUDE.md. The whole file loads every session, and long files reduce adherence: important rules get lost in the noise. For each line, ask: "Would removing this cause Claude to make mistakes?" If not, cut it.

| Content | Where it belongs |
|---------|------------------|
| Facts every session needs: commands, conventions, layout | `CLAUDE.md` |
| Guidance for one part of the codebase | `.claude/rules/*.md` with `paths:` frontmatter |
| Multi-step procedures: deploy, release, migrations | A skill in `.claude/skills/<name>/SKILL.md` |
| Rules that must never be broken | `permissions` in `.claude/settings.json`, or hooks |

A rule with `paths:` frontmatter loads only when Claude works with matching files:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Rules
- Validate request bodies with Zod
- Return errors in the format defined in `src/lib/errors.ts`
```

`@path` imports (`See @docs/architecture.md`) help organize a long file, but imported files still load at launch, so they don't save context. A plain path without `@` isn't imported; Claude can open the file when a task needs it.

Claude also keeps **auto memory**, on by default: notes it writes for itself about your preferences and corrections, stored in `~/.claude/projects/<project>/memory/`. CLAUDE.md holds what you want Claude to know; auto memory holds what Claude has learned. `/memory` manages both.

## Template

````markdown
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

<!-- Keep these short. Longer procedures (deploy, release) belong in a skill. -->

### Adding a new API endpoint
1. Create file in /api
2. Add types in /types
3. Write tests in /__tests__

### Adding a new component
1. Create in /components
2. Use existing design tokens
3. Add Storybook story
````

## Pro Tips

1. **Start small** - Run `/init` for a first draft, then trim. A 20-line CLAUDE.md is better than no CLAUDE.md
2. **Be prescriptive** - "Use X" is better than "You might want to use X"
3. **Include examples** - Show don't tell
4. **Version control it** - Commit `CLAUDE.md`; keep personal notes in a gitignored `CLAUDE.local.md`
5. **Check what loaded** - `/context` lists the memory files in your current session
6. **Leave notes for humans in comments** - Block-level `<!-- HTML comments -->` are stripped before Claude sees the file

---

Next: [Parallel Agents](./parallel-agents.md)
