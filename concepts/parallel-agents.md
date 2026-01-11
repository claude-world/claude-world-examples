# Parallel Agents

> Why do one thing at a time when you can do five?

## The Problem with Sequential Work

Traditional AI assistant workflow:

```
Step 1: Search for files (5 seconds)
Step 2: Read file A (3 seconds)
Step 3: Read file B (3 seconds)
Step 4: Search for patterns (5 seconds)
Step 5: Analyze results (5 seconds)

Total: 21 seconds (sequential)
```

## The Parallel Agents Solution

Claude Code can launch multiple agents simultaneously:

```
Agent 1: Search for files     ─┐
Agent 2: Read file A          ─┼─ All run in parallel
Agent 3: Read file B          ─┤
Agent 4: Search for patterns  ─┤
Agent 5: Analyze codebase     ─┘

Total: 5 seconds (parallel) = max(individual times)
```

**Result**: 4x faster for the same work.

## When to Use Parallel Agents

### Good Use Cases

1. **Exploring a codebase**
   - Agent 1: Find all TypeScript files
   - Agent 2: Search for API routes
   - Agent 3: Look for test files
   - Agent 4: Check configuration files

2. **Bug hunting**
   - Agent 1: Search for error message
   - Agent 2: Check recent git commits
   - Agent 3: Look for related tests
   - Agent 4: Find similar code patterns

3. **Code review**
   - Agent 1: Check for security issues
   - Agent 2: Analyze test coverage
   - Agent 3: Review code style
   - Agent 4: Check documentation

4. **Feature planning**
   - Agent 1: Analyze existing architecture
   - Agent 2: Find similar features
   - Agent 3: Check dependencies
   - Agent 4: Review API conventions

### When NOT to Use

- Tasks that depend on previous results
- Simple, single-file operations
- When you need to maintain strict order

## How It Works in Practice

### Example: Finding a Bug

You say:
```
"There's a bug in user authentication - users are getting logged out randomly"
```

Claude launches 5 parallel agents:

```
Agent 1 (Explore): Analyze auth module structure
Agent 2 (Grep): Search for "logout" and "session"
Agent 3 (Grep): Search for token expiration logic
Agent 4 (Read): Check auth middleware
Agent 5 (Grep): Look at recent auth-related commits
```

All agents complete in ~5 seconds.

Claude then synthesizes:
```
"Found the issue: In auth/middleware.ts:47, the token
expiration check uses < instead of <=, causing tokens
to expire 1 second early. Here's the fix..."
```

### Example: Adding a Feature

You say:
```
"Add a password reset feature"
```

Claude launches parallel research:

```
Agent 1: Check existing email service
Agent 2: Review user model and auth patterns
Agent 3: Look for similar flows (signup, verification)
Agent 4: Check API route conventions
Agent 5: Review test patterns
```

Then implements with full context of your codebase patterns.

## Best Practices

### 1. Give Clear, Complete Tasks

**Bad**: "Help me understand the code"

**Good**: "Analyze how user authentication works, including the login flow, session management, and token refresh logic"

### 2. Trust the Process

Don't interrupt Claude while agents are running. Let them complete and synthesize.

### 3. Provide Context in CLAUDE.md

The better your CLAUDE.md, the smarter the parallel agents:

```markdown
## Key Areas

### Authentication (/lib/auth)
- JWT-based with refresh tokens
- Middleware in /middleware/auth.ts
- User model in /prisma/schema.prisma

### API Routes (/app/api)
- RESTful conventions
- Error handling in /lib/errors.ts
- Validation with Zod
```

## The Efficiency Math

| Approach | 5 Tasks × 5 sec each |
|----------|---------------------|
| Sequential | 25 seconds |
| Parallel | 5 seconds |
| **Speedup** | **5x** |

For complex tasks with 10+ subtasks, parallel agents can provide **10x or more** speedup.

## Summary

1. Claude Code can run multiple agents in parallel
2. Use for exploration, bug hunting, code review, and feature planning
3. Provide clear context so agents work smarter
4. Trust the process - don't micromanage

---

Back to [README](../README.md)
