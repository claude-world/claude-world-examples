# Complete Guide to Claude Code Agents

> From single prompts to parallel orchestration - mastering agents unlocks 5-10x efficiency

## Quick Reference

| Agent | Purpose | Default Model | Use For |
|-------|---------|---------------|---------|
| `Explore` | Fast codebase navigation | Haiku 4.5 | File search, pattern matching |
| `general-purpose` | Complex multi-step tasks | Sonnet 4.5 | Implementation, analysis |
| `code-reviewer` | Code quality analysis | Sonnet 4.5 | PR reviews, patterns |
| `security-auditor` | Vulnerability detection | Sonnet 4.5 | Auth, payments, data |
| `test-runner` | Test execution | Haiku 4.5 | Running, analyzing tests |
| `debugger` | Root cause analysis | Sonnet 4.5 | Bug investigation |
| `refactor-assistant` | Code improvement | Sonnet 4.5 | Cleanup, restructuring |
| `doc-writer` | Documentation | Haiku/Sonnet | README, API docs |

## The Task Tool

All agents are spawned via the `Task` tool. The examples below use a conceptual JavaScript-like syntax to illustrate the parameters—Claude Code internally handles the actual invocation.

**Conceptual syntax (for illustration):**

```javascript
Task({
  subagent_type: "Explore",           // Required: Agent type
  model: "haiku",                      // Optional: haiku, sonnet, opus
  prompt: "Your task description",     // Required: What to do
  run_in_background: false             // Optional: Async execution
})
```

> **Note:** When using Claude Code, you don't write this syntax directly. Instead, you describe what you want and Claude Code spawns the appropriate agents. The syntax above shows the underlying parameters for documentation purposes.

## Agent Types

### Explore Agent (Fastest)

The **Explore agent** is Claude Code's efficiency powerhouse. Powered by Haiku 4.5, it replaces 5 manual search operations with one intelligent query.

#### Thoroughness Levels

| Level | Time | Use Case |
|-------|------|----------|
| `quick` | 10-30s | Find specific file/function |
| `medium` | 30-60s | Map module structure |
| `very thorough` | 60-120s | Complete flow analysis |

#### Examples

**Quick search:**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: "Explore auth (thoroughness: quick). Find login handler."
})
```

**Medium exploration:**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: `
    Explore payment module (thoroughness: medium).
    Find Stripe integration points and webhook handlers.
  `
})
```

**Thorough analysis:**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: `
    Explore authentication (thoroughness: very thorough).
    Map complete auth flow: login → session → token refresh → logout.
  `
})
```

#### Why Explore is Faster

**Old approach (5 manual steps):**
```
Glob *auth*.ts          → 15s
Grep "JWT"              → 15s
Read auth/index.ts      → 10s
Grep middleware         → 15s
Read test files         → 10s
Total: 65 seconds
```

**New approach (1 Explore agent):**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: "Explore auth (thoroughness: medium). Map JWT, middleware, tests."
})
// Total: 30-45 seconds
```

### general-purpose Agent

For complex, multi-step tasks requiring deeper reasoning.

```javascript
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Implement user profile editing feature.
    - Add API endpoint for profile updates
    - Create form component with validation
    - Include image upload support
    - Follow existing patterns in src/api/
  `
})
```

### code-reviewer Agent

Specializes in code quality and best practices.

```javascript
Task({
  subagent_type: "code-reviewer",
  model: "sonnet",
  prompt: `
    Review changes in the authentication module.
    Check for:
    - Code quality and patterns
    - Error handling
    - Test coverage
    - Documentation

    Provide findings with severity levels.
  `
})
```

### security-auditor Agent

Critical for auth, payments, and data handling code.

```javascript
Task({
  subagent_type: "security-auditor",
  model: "sonnet",  // Use "opus" for critical code
  prompt: `
    Audit the authentication module.
    Check for OWASP Top 10:
    - Injection vulnerabilities
    - Broken authentication
    - Sensitive data exposure
    - Broken access control

    Report findings with severity.
  `
})
```

**When to use:**
| Scenario | Priority |
|----------|----------|
| Auth/login changes | High |
| Payment code | Critical |
| User data handling | High |
| API endpoints | Medium |
| File uploads | High |

### test-runner Agent

Handles test execution and coverage analysis.

```javascript
Task({
  subagent_type: "test-runner",
  model: "haiku",
  prompt: `
    Run all tests related to user authentication.
    Report:
    - Pass/fail status
    - Coverage percentage
    - Failed test details
  `
})
```

### debugger Agent

Systematic root cause analysis.

```javascript
Task({
  subagent_type: "debugger",
  model: "sonnet",
  prompt: `
    Investigate: TypeError: Cannot read 'id' of undefined
    at CheckoutForm.handleSubmit (checkout.tsx:45)

    Context: Error occurs when submitting with empty cart.

    Find root cause and suggest fix.
  `
})
```

### refactor-assistant Agent

Code improvement without changing functionality.

```javascript
Task({
  subagent_type: "refactor-assistant",
  model: "sonnet",
  prompt: `
    Refactor utils/helpers.ts:
    - Split into focused modules
    - Remove dead code
    - Improve naming
    - Add TypeScript types
  `
})
```

### doc-writer Agent

Creates and updates documentation.

```javascript
Task({
  subagent_type: "doc-writer",
  model: "sonnet",
  prompt: `
    Document the user API endpoints.
    Include:
    - Endpoint descriptions
    - Request/response formats
    - Authentication requirements
    - Error codes
    - Examples
  `
})
```

## Parallel Agent Patterns

### Pattern 1: Analysis Swarm

Launch 5 Explore agents for comprehensive analysis:

```javascript
// All run in parallel
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Map auth file structure (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Find JWT patterns (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Analyze middleware (thoroughness: medium)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Check auth tests (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Review recent changes (thoroughness: quick)" })
```

### Pattern 2: Implementation + Review

Build and verify simultaneously:

```javascript
// Phase 1: Implementation
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "Implement user profile feature"
})

// Phase 2: Parallel review (after Phase 1)
Task({ subagent_type: "code-reviewer", model: "sonnet",
  prompt: "Review code quality" })
Task({ subagent_type: "security-auditor", model: "sonnet",
  prompt: "Security review" })
Task({ subagent_type: "test-runner", model: "haiku",
  prompt: "Run and analyze tests" })
```

### Pattern 3: Multi-File Refactoring

Divide work across agents:

```javascript
// Each agent handles one file
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Refactor payment/checkout.ts to new pattern" })
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Refactor payment/subscription.ts to new pattern" })
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Refactor payment/refund.ts to new pattern" })
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Update payment/types.ts for new pattern" })
```

### Pattern 4: Bug Investigation

Parallel hypothesis testing:

```javascript
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Search for session handling changes (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Check for race conditions (thoroughness: medium)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Review error logs (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Find timeout configurations (thoroughness: quick)" })
Task({ subagent_type: "debugger", model: "sonnet",
  prompt: "Analyze most likely root cause from exploration" })
```

## Model Selection

| Task Type | Model | Cost | Speed |
|-----------|-------|------|-------|
| Quick search | Haiku 4.5 | $ | Fast |
| Pattern matching | Haiku 4.5 | $ | Fast |
| Test running | Haiku 4.5 | $ | Fast |
| Simple docs | Haiku 4.5 | $ | Fast |
| Code review | Sonnet 4.5 | $$ | Balanced |
| Implementation | Sonnet 4.5 | $$ | Balanced |
| Debugging | Sonnet 4.5 | $$ | Balanced |
| Security audit | Sonnet/Opus | $$-$$$ | Balanced-Thorough |
| Architecture | Opus 4.5 | $$$ | Thorough |

**Key trade-offs:**
- Haiku 4.5: 2x faster, 1/3 cost vs Sonnet
- Sonnet 4.5: Best coding performance
- Opus 4.5: Highest intelligence, default Thinking Mode

## Background Agents

For long-running tasks:

```javascript
Task({
  subagent_type: "security-auditor",
  model: "opus",
  prompt: "Comprehensive security audit of entire codebase",
  run_in_background: true
})
```

Check on background tasks:
```javascript
TaskOutput({ task_id: "...", block: false })
```

## Best Practices

### 1. Choose the Right Agent

```
File search       → Explore (haiku)
Implementation    → general-purpose (sonnet)
Code quality      → code-reviewer (sonnet)
Security          → security-auditor (sonnet/opus)
Testing           → test-runner (haiku)
Bugs              → debugger (sonnet)
Cleanup           → refactor-assistant (sonnet)
Docs              → doc-writer (haiku/sonnet)
```

### 2. Keep Prompts Focused

**Too broad:**
```
"Analyze everything about the codebase"
```

**Focused:**
```
"Explore auth module (thoroughness: medium). Find JWT handling and session management."
```

### 3. Provide Context

```javascript
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Context: Migrating from REST to GraphQL.
    Pattern: Use new ApiClient from src/lib/api.ts

    Task: Refactor user service to use GraphQL.
  `
})
```

### 4. Use Parallel When Possible

Independent tasks should run simultaneously:

```javascript
// These are independent - run in parallel
Task({ ..., prompt: "Analyze file A" })
Task({ ..., prompt: "Analyze file B" })
Task({ ..., prompt: "Analyze file C" })
```

### 5. Chain Dependent Tasks

Sequential tasks should be phased:

```
Phase 1: Explore (gather context)
Phase 2: Implement (with context from Phase 1)
Phase 3: Review (verify Phase 2)
```

## Common Workflows

### New Feature Development

```
1. Explore (quick): Understand existing patterns
2. general-purpose: Implement feature
3. test-runner: Run tests
4. code-reviewer + security-auditor: Review (parallel)
5. doc-writer: Update documentation
```

### Bug Fix

```
1. 4x Explore (parallel): Investigate from multiple angles
2. debugger: Synthesize findings, identify root cause
3. general-purpose: Implement fix
4. test-runner: Verify fix, add regression test
```

### Code Review

```
1. Explore: Understand changes
2. code-reviewer: Quality check
3. security-auditor: Security check
4. test-runner: Coverage analysis
```

## Summary

| Principle | Action |
|-----------|--------|
| Start with Explore | Use `thoroughness: medium` for most tasks |
| Parallelize everything | Independent tasks = parallel agents |
| Match model to task | Haiku for search, Sonnet for implementation |
| Keep prompts focused | One clear goal per agent |
| Chain dependent work | Phase 1 → Phase 2 → Phase 3 |

---

**Related:**
- [Parallel Agents](../concepts/parallel-agents.md) - Deeper dive into parallel patterns
- [Multi-Agent Patterns](https://claude-world.com/articles/multi-agent-patterns) - Advanced orchestration

Back to [README](../README.md)
