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

Claude Code can launch multiple subagents at once through its Agent tool (formerly called Task). Each subagent works in its own context window and reports back a summary:

```
Agent 1: Search for files     ─┐
Agent 2: Read file A          ─┼─ All run in parallel
Agent 3: Read file B          ─┤
Agent 4: Search for patterns  ─┤
Agent 5: Analyze codebase     ─┘

Total: 5 seconds (parallel) = max(individual times)
```

**Result**: roughly 4x faster for the same work, and the main conversation only receives the summaries.

Subagents that Claude spawns from the main conversation run in the background by default, so you can keep working while they run. Press `Ctrl+B` to send a running task to the background and `/tasks` to see each subagent with its model and status. Up to 20 subagents can run at once by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` changes the limit).

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
- Several agents editing the same files at once (give each one `isolation: "worktree"`, or edit sequentially)

## How It Works in Practice

### Example: Finding a Bug

You say:
```
"There's a bug in user authentication - users are getting logged out randomly"
```

Claude launches 5 parallel subagents:

```
Agent 1 (Explore): Analyze auth module structure
Agent 2 (Explore): Search for "logout" and "session"
Agent 3 (Explore): Search for token expiration logic
Agent 4 (Explore): Check auth middleware
Agent 5 (general-purpose): Review recent auth-related commits with git log
```

Grep, Read, and Bash are tools that each subagent uses; Explore and general-purpose are the agent types. The five investigations run at the same time instead of one after another.

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

Let the subagents finish and let Claude synthesize. They run in the background, so you can keep working or check progress with `/tasks` instead of interrupting.

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

For complex tasks with many independent subtasks, the speedup grows with the number of agents, up to the concurrency limit. Each subagent also uses its own tokens, so parallelism trades cost for time. For long-running parallel work where agents need to coordinate, see agent teams (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).

## Summary

1. Claude Code can run multiple subagents in parallel, in the background by default
2. Use for exploration, bug hunting, code review, and feature planning
3. Provide clear context so agents work smarter
4. Trust the process - don't micromanage

---

Back to [README](../README.md)
