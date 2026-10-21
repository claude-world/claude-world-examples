# Complete Guide to Claude Code Agents

> From single prompts to parallel orchestration - mastering agents can multiply your efficiency

## Quick Reference

Built-in agents ship with Claude Code. The others are **custom agents**: Markdown files you define in `.claude/agents/` or install with a plugin. See [Custom Agents](#custom-agents) below.

| Agent | Kind | Purpose | Model | Use For |
|-------|------|---------|-------|---------|
| `Explore` | Built-in | Read-only codebase search | Main conversation's model | File search, pattern matching |
| `Plan` | Built-in | Research during plan mode | Main conversation's model | Context before a plan |
| `general-purpose` | Built-in | Complex multi-step tasks | Main conversation's model | Implementation, analysis |
| `code-reviewer` | Custom | Code quality analysis | `sonnet` (typical) | PR reviews, patterns |
| `security-auditor` | Custom | Vulnerability detection | `sonnet` or `opus` | Auth, payments, data |
| `test-runner` | Custom | Test execution | `haiku` or `sonnet` | Running, analyzing tests |
| `debugger` | Custom | Root cause analysis | `sonnet` (typical) | Bug investigation |
| `refactor-assistant` | Custom | Code improvement | `sonnet` (typical) | Cleanup, restructuring |
| `doc-writer` | Custom | Documentation | `haiku` or `sonnet` | README, API docs |

A custom agent runs on the model in its `model:` field. Without one it follows the main conversation's model (or `CLAUDE_CODE_SUBAGENT_MODEL`, if you set it). Claude Code also has helper agents (`claude`, `statusline-setup`, `claude-code-guide`) that it uses automatically.

## The Agent Tool

All agents are spawned via the `Agent` tool (named `Task` before Claude Code v2.1.63; `Task(...)` still works as an alias in settings and agent definitions). The examples below use a conceptual JavaScript-like syntax to illustrate the parameters—Claude Code internally handles the actual invocation.

**Conceptual syntax (for illustration):**

```javascript
Agent({
  subagent_type: "Explore",            // Agent type: built-in or custom name
  description: "Find login handler",   // Short label shown in the transcript
  prompt: "Your task description",     // Required: What to do
  model: "sonnet",                     // Optional: sonnet, opus, haiku, fable, inherit, or a full model ID
  effort: "high",                      // Optional: low, medium, high, xhigh, max
  isolation: "worktree",               // Optional: work in a temporary git worktree
  run_in_background: true              // Optional: don't block (the default from the main conversation)
})
```

> **Note:** When using Claude Code, you don't write this syntax directly. Instead, you describe what you want ("use the code-reviewer agent on my changes", "explore auth, billing, and the API in parallel") and Claude Code spawns the appropriate agents. To guarantee a specific agent runs, @-mention it: `@"code-reviewer (agent)"`. The syntax above shows the underlying parameters for documentation purposes.

## Agent Types

### Explore Agent (Fast, Read-Only)

The **Explore agent** is Claude Code's built-in search specialist. It replaces a string of manual searches with one delegated query, runs on your main conversation's model, and starts without your CLAUDE.md files or git status to keep research fast and inexpensive. Only its summary comes back to your conversation.

#### Thoroughness Levels

When Claude invokes Explore, it picks a thoroughness level:

| Level | Depth | Use Case |
|-------|-------|----------|
| `quick` | Targeted lookup | Find specific file/function |
| `medium` | Balanced exploration | Map module structure |
| `very thorough` | Comprehensive analysis | Complete flow analysis |

#### Examples

**Quick search:**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Find login handler",
  prompt: "Explore auth (thoroughness: quick). Find login handler."
})
```

**Medium exploration:**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Map Stripe integration",
  prompt: `
    Explore payment module (thoroughness: medium).
    Find Stripe integration points and webhook handlers.
  `
})
```

**Thorough analysis:**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Map complete auth flow",
  prompt: `
    Explore authentication (thoroughness: very thorough).
    Map complete auth flow: login → session → token refresh → logout.
  `
})
```

#### Why Explore Is Efficient

**Old approach (5 manual steps in your main conversation):**
```
Glob *auth*.ts          → file list lands in your context
Grep "JWT"              → every match lands in your context
Read auth/index.ts      → the whole file lands in your context
Grep middleware         → more matches
Read test files         → more files
Result: your context fills with search output you won't reuse
```

**New approach (1 Explore agent):**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Map auth module",
  prompt: "Explore auth (thoroughness: medium). Map JWT, middleware, tests."
})
// The searching happens in Explore's own context window; only the summary comes back
```

#### Run Explore on Haiku

Explore is not Haiku-powered by default. To explore on a lower-cost model, define your own subagent named `Explore` in `.claude/agents/` (project) or `~/.claude/agents/` (user). It overrides the built-in and keeps its own `model`:

```markdown
---
name: Explore
description: Fast read-only codebase search. Use for finding files, symbols, and patterns.
tools: Read, Grep, Glob
model: haiku
---

You are a read-only search agent. Find what was asked, cite file paths and
line numbers, and return a short summary. Never modify files.
```

### Plan Agent

Claude uses the built-in **Plan** agent in plan mode (`Shift+Tab` cycles to it) to research your codebase before presenting a plan. It is read-only, runs on your main conversation's model, and you rarely call it directly.

### general-purpose Agent

For complex, multi-step tasks that need both exploration and action. It has every tool available to subagents and runs on the main conversation's model unless a `model` is passed.

```javascript
Agent({
  subagent_type: "general-purpose",
  description: "Implement profile editing",
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

### Custom Agents

The agents in this section are **not built into Claude Code**. Each is a custom subagent: a Markdown file with YAML frontmatter that Claude can delegate to by name. Get them in one of two ways:

- **Install a plugin.** [Director Mode Lite](https://github.com/claude-world/director-mode-lite) ships `code-reviewer`, `debugger`, and `doc-writer`: run `/plugin marketplace add claude-world/director-mode-lite`, then `/plugin install director-mode-lite@director-mode-lite`. Plugin agents appear under a scoped name such as `director-mode-lite:code-reviewer`.
- **Define them yourself** in `.claude/agents/<name>.md` (this project; commit it to share with your team) or `~/.claude/agents/<name>.md` (all your projects). Or ask Claude: "Create a security-auditor agent in .claude/agents/ that ...".

```markdown
---
name: security-auditor
description: Security specialist for auth, payments, and data handling. Use proactively after changes to security-sensitive code.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a security auditor. Check the changed code against the OWASP Top 10,
report each finding with severity and file:line, and suggest a concrete fix.
```

The examples below use plain names, as if each agent is defined in `.claude/agents/`. A `model` passed on a call overrides the agent's own `model:` for that call. See [Designing Agents](./designing-agents.md) for every frontmatter field.

#### code-reviewer

Specializes in code quality and best practices.

```javascript
Agent({
  subagent_type: "code-reviewer",
  description: "Review auth changes",
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

#### security-auditor

Critical for auth, payments, and data handling code.

```javascript
Agent({
  subagent_type: "security-auditor",
  description: "Audit auth module",
  model: "opus",  // Per-call override for critical code
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

#### test-runner

Handles test execution and coverage analysis.

```javascript
Agent({
  subagent_type: "test-runner",
  description: "Run auth tests",
  prompt: `
    Run all tests related to user authentication.
    Report:
    - Pass/fail status
    - Coverage percentage
    - Failed test details
  `
})
```

#### debugger

Systematic root cause analysis.

```javascript
Agent({
  subagent_type: "debugger",
  description: "Debug checkout TypeError",
  prompt: `
    Investigate: TypeError: Cannot read 'id' of undefined
    at CheckoutForm.handleSubmit (checkout.tsx:45)

    Context: Error occurs when submitting with empty cart.

    Find root cause and suggest fix.
  `
})
```

#### refactor-assistant

Code improvement without changing functionality.

```javascript
Agent({
  subagent_type: "refactor-assistant",
  description: "Refactor helpers module",
  prompt: `
    Refactor utils/helpers.ts:
    - Split into focused modules
    - Remove dead code
    - Improve naming
    - Add TypeScript types
  `
})
```

#### doc-writer

Creates and updates documentation.

```javascript
Agent({
  subagent_type: "doc-writer",
  description: "Document user API",
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

Independent agents run at the same time. Subagents that Claude spawns from the main conversation start in the background, so you can keep working while they run (up to 20 at once by default).

### Pattern 1: Analysis Swarm

Launch 5 Explore agents for comprehensive analysis:

```javascript
// All run in parallel
Agent({ subagent_type: "Explore", description: "Map auth files",
  prompt: "Map auth file structure (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Find JWT patterns",
  prompt: "Find JWT patterns (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Analyze middleware",
  prompt: "Analyze middleware (thoroughness: medium)" })
Agent({ subagent_type: "Explore", description: "Check auth tests",
  prompt: "Check auth tests (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Review recent changes",
  prompt: "Review recent changes (thoroughness: quick)" })
```

### Pattern 2: Implementation + Review

Build, then verify in parallel:

```javascript
// Phase 1: Implementation
Agent({
  subagent_type: "general-purpose",
  description: "Implement profile feature",
  model: "sonnet",
  prompt: "Implement user profile feature"
})

// Phase 2: Parallel review (after Phase 1)
Agent({ subagent_type: "code-reviewer", description: "Review code quality",
  prompt: "Review code quality" })
Agent({ subagent_type: "security-auditor", description: "Security review",
  prompt: "Security review" })
Agent({ subagent_type: "test-runner", description: "Run tests",
  prompt: "Run and analyze tests" })
```

### Pattern 3: Multi-File Refactoring

Divide work across agents:

```javascript
// Each agent handles one file
Agent({ subagent_type: "general-purpose", description: "Refactor checkout.ts",
  model: "sonnet", prompt: "Refactor payment/checkout.ts to new pattern" })
Agent({ subagent_type: "general-purpose", description: "Refactor subscription.ts",
  model: "sonnet", prompt: "Refactor payment/subscription.ts to new pattern" })
Agent({ subagent_type: "general-purpose", description: "Refactor refund.ts",
  model: "sonnet", prompt: "Refactor payment/refund.ts to new pattern" })
Agent({ subagent_type: "general-purpose", description: "Update payment types",
  model: "sonnet", prompt: "Update payment/types.ts for new pattern" })
```

Agents that might touch the same files shouldn't share a checkout. Pass `isolation: "worktree"` so each works in its own temporary git worktree (branched by default from your default branch, not your current `HEAD`), or run the bundled `/batch` skill, which splits a large change into independent units and runs each in its own worktree.

### Pattern 4: Bug Investigation

Parallel hypothesis testing:

```javascript
Agent({ subagent_type: "Explore", description: "Check session changes",
  prompt: "Search for session handling changes (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Look for race conditions",
  prompt: "Check for race conditions (thoroughness: medium)" })
Agent({ subagent_type: "Explore", description: "Review error logs",
  prompt: "Review error logs (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Find timeout configs",
  prompt: "Find timeout configurations (thoroughness: quick)" })

// After the Explore results arrive, Claude passes them on
Agent({ subagent_type: "debugger", description: "Find root cause",
  prompt: "Analyze most likely root cause from exploration" })
```

## Model Selection

| Task Type | Model | Cost | Speed |
|-----------|-------|------|-------|
| Quick search | Haiku 5.5 | $ | Fastest |
| Pattern matching | Haiku 5.5 | $ | Fastest |
| Test running | Haiku 5.5 | $ | Fastest |
| Simple docs | Haiku 5.5 | $ | Fastest |
| Code review | Sonnet 5.5 | $$ | Fast |
| Implementation | Sonnet 5.5 | $$ | Fast |
| Debugging | Sonnet 5.5 | $$ | Fast |
| Security audit | Sonnet 5.5 / Opus 5.5 | $$-$$$ | Fast-Moderate |
| Architecture | Opus 5.5 | $$$ | Moderate |
| Demanding long-horizon work | Fable 5.1 | $$$$ | Slower |

**Key trade-offs** (official descriptions; API prices per million input/output tokens):
- Haiku 5.5: "for high-volume, latency-sensitive tasks such as classification, extraction, and routing" (from $0.10 / $0.50)
- Sonnet 5.5: "the best combination of speed and intelligence" ($2 / $10)
- Opus 5.5: "for long-running agentic coding and knowledge work" ($4 / $20); the default model in Claude Code on Pro, Max, Team, Enterprise, and API accounts, which means subagents inherit it unless you pick another
- Fable 5.1: "for demanding reasoning and long-horizon agentic work"; never the default, select it with `/model fable` (on some plans it bills to usage credits)

## Background Agents

Subagents that Claude spawns from the main conversation already start in the background. For long-running tasks:

```javascript
Agent({
  subagent_type: "security-auditor",
  description: "Full security audit",
  model: "opus",
  prompt: "Comprehensive security audit of entire codebase",
  run_in_background: true
})
```

Check on background work:
- `/tasks` lists background work, including recently finished subagents, with each subagent's model and effort level
- The subagent panel below the prompt input shows running agents; open a row to read its transcript
- `Ctrl+B` moves a running foreground task or agent to the background
- Claude receives each background agent's result as a completion notification, then reports back

## Best Practices

### 1. Choose the Right Agent

```
File search       → Explore (built-in)
Implementation    → general-purpose (built-in, sonnet)
Code quality      → code-reviewer (custom, sonnet)
Security          → security-auditor (custom, sonnet/opus)
Testing           → test-runner (custom, haiku/sonnet)
Bugs              → debugger (custom, sonnet)
Cleanup           → refactor-assistant (custom, sonnet)
Docs              → doc-writer (custom, haiku/sonnet)
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

A subagent starts with a fresh context window: it sees the prompt Claude writes for it (plus your CLAUDE.md, except for Explore and Plan), not your conversation.

```javascript
Agent({
  subagent_type: "general-purpose",
  description: "Migrate user service",
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
Agent({ ..., prompt: "Analyze file A" })
Agent({ ..., prompt: "Analyze file B" })
Agent({ ..., prompt: "Analyze file C" })
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
| Match model to task | Haiku for search, Sonnet for implementation, Opus for the hardest reasoning |
| Keep prompts focused | One clear goal per agent |
| Chain dependent work | Phase 1 → Phase 2 → Phase 3 |

---

**Related:**
- [Parallel Agents](../concepts/parallel-agents.md) - Deeper dive into parallel patterns
- [Designing Agents](./designing-agents.md) - Write your own custom agents
- [Multi-Agent Patterns](https://claude-world.com/articles/multi-agent-patterns) - Advanced orchestration

Back to [README](../README.md)
