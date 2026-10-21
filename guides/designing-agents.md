# Designing Project-Specific Claude Code Agents

> Custom agents transform repetitive tasks into one-command operations. This guide covers everything from basics to advanced patterns.

## Quick Reference

| Section | Content |
|---------|---------|
| [What are Agents?](#what-are-agents) | Understanding subagents and the Agent tool |
| [When to Create](#when-to-create-custom-agents) | Built-in vs custom agents |
| [File Structure](#agent-file-structure) | YAML frontmatter + markdown format |
| [Best Practices](#best-practices-for-agent-prompts) | Writing effective agent prompts |
| [Examples](#agent-examples) | Real-world specialized agents |
| [Configuration](#configuring-agents) | Setting up `.claude/agents/` |
| [Delegation Tips](#effective-agent-delegation) | Getting the most from agents |

## What are Agents?

Agents (also called subagents) are specialized Claude instances spawned via the **Agent tool** (named `Task` before Claude Code v2.1.63; `Task` still works as an alias). Each agent has:

- **Focused expertise** - Defined role and responsibilities (its system prompt)
- **Specific tools** - Only the tools it needs
- **Clear output** - Structured response format
- **Delegation triggers** - A `description` that tells Claude when to hand work to it

```
Main Claude Instance
       │
       ├── Agent(code-reviewer) ─► Reviews code quality
       ├── Agent(debugger) ─► Investigates bugs
       ├── Agent(doc-writer) ─► Creates documentation
       └── Agent(security-auditor) ─► Checks vulnerabilities
```

### How Agents Work

When Claude delegates to an agent, Claude Code:

1. Loads the agent definition (from `.claude/agents/`, `~/.claude/agents/`, a plugin, or the `--agents` flag)
2. Starts a fresh context window with the agent's Markdown body as its system prompt (plus your CLAUDE.md files, unless the agent sets `omitClaudeMd: true`)
3. Grants only the tools the definition allows
4. Runs the task from Claude's delegation prompt, on the agent's model and effort level
5. Returns only the agent's final result to the main conversation

The agent never sees your conversation history, only the prompt Claude writes for it.

**Conceptual Agent tool syntax:**

```javascript
Agent({
  subagent_type: "agent-name",     // Agent to invoke (its frontmatter name)
  description: "Short task label", // Shown in the transcript
  prompt: "Your specific task",    // What to do
  model: "sonnet",                 // Optional: overrides the agent's model for this call
  run_in_background: true          // Optional: the default for agents spawned from the main conversation
})
```

### Built-in vs Custom Agents

| Built-in Agents | Purpose |
|-----------------|---------|
| `Explore` | Fast, read-only codebase search (runs on your main model) |
| `Plan` | Read-only research during plan mode |
| `general-purpose` | Complex multi-step tasks (all tools) |

Claude Code also has helper agents it uses automatically: `claude` (catch-all), `statusline-setup`, and `claude-code-guide`.

**Custom agents** extend these with project-specific expertise. Familiar names such as `code-reviewer`, `security-auditor`, `test-runner`, `debugger`, and `doc-writer` are custom agents too: you define them in `.claude/agents/` or install them with a plugin (for example, [Director Mode Lite](https://github.com/claude-world/director-mode-lite) ships `code-reviewer`, `debugger`, and `doc-writer`).

## When to Create Custom Agents

### Create Custom Agents When:

1. **Repetitive specialized tasks** - Same process run frequently
2. **Project-specific knowledge** - Domain expertise needed
3. **Consistent output format** - Standardized results required
4. **Team workflow** - Shared processes across developers
5. **Complex multi-step procedures** - Documented process to follow
6. **Tool limits** - The task should run with restricted tools or permissions

### Use Built-in Agents When:

1. **General coding tasks** - Standard development work
2. **One-off operations** - Not repeated often
3. **Simple searches** - Basic file/pattern matching
4. **Standard reviews** - Generic checks that Claude Code's `/code-review` and `/security-review` commands already cover

### Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| "Review this PR for our coding standards" | Custom: `project-reviewer` |
| "Find all TypeScript files" | Built-in: `Explore` |
| "Check for security issues" | Built-in: `/security-review` (or a custom `security-auditor`) |
| "Generate API docs in our format" | Custom: `api-doc-generator` |
| "Debug this error" | Built-in: `general-purpose` (or a custom `debugger`) |
| "Migrate data using our process" | Custom: `data-migrator` |

## Agent File Structure

Agents are Markdown files with YAML frontmatter. Where a file lives decides who can use it:

| Location | Scope |
|----------|-------|
| `.claude/agents/` | Current project (commit it to share with your team) |
| `~/.claude/agents/` | All your projects |
| Plugin `agents/` directory | Wherever the plugin is enabled, under a scoped name such as `my-plugin:reviewer` |
| `claude --agents '{...}'` | Current session only (JSON definitions) |
| Managed settings | Organization-wide |

When two definitions share a name, managed settings win, then `--agents`, then project, then user, then plugin.

### File Location

```
your-project/
└── .claude/
    └── agents/
        ├── code-reviewer.md
        ├── debugger.md
        ├── doc-writer.md
        ├── api-generator.md
        └── your-custom-agent.md
```

### Complete Format

````markdown
---
name: agent-name
description: What this agent does and when to use it. Use proactively when [trigger 1] or [trigger 2].
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

# Agent Name

You are a [role description]. You help users with [specific tasks].

## Core Knowledge

### [Domain Area 1]
[Relevant expertise and context]

### [Domain Area 2]
[Additional knowledge]

## Process

When invoked:
1. [Step 1 - Understand/Gather]
2. [Step 2 - Analyze/Process]
3. [Step 3 - Execute/Generate]
4. [Step 4 - Verify/Report]

## Output Format

[Define expected output structure]

```markdown
## [Output Section]

### Summary
[Brief overview]

### Details
[Structured findings]

### Actions
[Recommended next steps]
```

## Guidelines

- [Guideline 1]
- [Guideline 2]
- [Guideline 3]
````

### Frontmatter Fields

Only `name` and `description` are required. Field names are camelCase and must match exactly; Claude Code silently ignores fields it doesn't recognize.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, e.g. `code-reviewer` (kebab-case recommended; no `:`) |
| `description` | Yes | When Claude should delegate to this agent. Keep it short and specific |
| `tools` | No | Allowlist, as a comma-separated string or YAML list. Omit it to inherit every tool available to subagents |
| `disallowedTools` | No | Denylist, removed from the inherited or listed tools |
| `model` | No | `sonnet`, `opus`, `haiku`, `fable`, `inherit`, or a full model ID such as `claude-opus-5-5`. Omitted: the main conversation's model (or `CLAUDE_CODE_SUBAGENT_MODEL`) |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan` |
| `maxTurns` | No | Maximum agentic turns before the agent stops |
| `skills` | No | Skills whose full content is preloaded into the agent's context |
| `mcpServers` | No | MCP servers for this agent only (names of configured servers or inline definitions) |
| `hooks` | No | Lifecycle hooks that run only while this agent is active |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | `true` keeps the agent in the background even when Claude would wait for it |
| `effort` | No | `low`, `medium`, `high`, `xhigh`, or `max` while this agent runs |
| `isolation` | No | `worktree` runs the agent in a temporary git worktree |
| `color` | No | Display color in the task list and transcript |
| `initialPrompt` | No | First user turn, auto-submitted when the agent runs as the main session (`claude --agent`) |
| `omitClaudeMd` | No | `true` starts the agent without your user, project, and local CLAUDE.md files |

Plugin agents ignore `hooks`, `mcpServers`, and `permissionMode`; copy the file into `.claude/agents/` if you need them.

### Available Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| `Read` | Read files | Always include |
| `Write` | Create new files | Generators |
| `Edit` | Modify existing files | Fixers, updaters |
| `Bash` | Execute shell commands | Test runners, builders |
| `Grep` | Search file contents | Analyzers |
| `Glob` | Find files by pattern | Explorers |
| `Agent` | Spawn sub-agents (formerly `Task`) | Orchestrators |
| `WebFetch` | Fetch web content | Documentation agents |
| `WebSearch` | Search the web | Research agents |
| `TodoWrite` | Manage task lists | Project managers |

MCP tools work too: `mcp__github__*` grants every tool from the `github` server.

### Tool Selection Guidelines

```markdown
# Read-only agents (safe, fast)
tools: Read, Grep, Glob
Use for: Reviewers, analyzers, auditors

# Read-write agents (careful)
tools: Read, Write, Edit
Use for: Generators, updaters

# Full access agents (trusted)
tools: Read, Write, Edit, Bash, Grep, Glob
Use for: Fixers, builders, migrators

# Everything except file writes
disallowedTools: Write, Edit
Use for: Investigators that still need Bash and MCP tools

# Orchestrator agents
tools: Read, Grep, Glob, Agent
Use for: Coordinators that delegate to other agents
```

## Best Practices for Agent Prompts

### 1. Single Responsibility

Each agent should do ONE thing well.

**Good - Focused:**
```markdown
---
name: test-runner
description: Runs tests and reports failures with coverage
tools: Read, Bash, Grep
---

# Test Runner Agent

You run project tests and provide detailed failure analysis.
```

**Bad - Too broad:**
```markdown
---
name: code-helper
description: Reviews code, writes tests, fixes bugs, generates docs
# no tools field: inherits every tool
---
```

### 2. Clear Activation Triggers

Claude reads only the `description` when deciding whether to delegate. The Markdown body is the agent's system prompt and loads only once the agent runs, so put the triggers in the description. Phrases such as "use proactively" encourage Claude to delegate on its own.

```markdown
---
name: test-runner
description: Runs tests and analyzes failures. Use proactively after significant code changes, when tests fail, or when the user mentions tests, coverage, or failing builds.
tools: Read, Bash, Grep
---
```

### 3. Structured Process

Document step-by-step methodology.

```markdown
## Process

### Phase 1: Understand
1. Read the error message or request
2. Identify relevant files
3. Gather context from related code

### Phase 2: Analyze
1. Form hypotheses
2. Investigate each systematically
3. Gather evidence

### Phase 3: Act
1. Implement solution
2. Verify fix works
3. Check for regressions

### Phase 4: Report
1. Summarize findings
2. Document changes made
3. Suggest preventive measures
```

### 4. Consistent Output Format

Define exactly what output looks like.

````markdown
## Output Format

```markdown
## [Agent Name] Report

### Summary
[One-line description]

### Findings
| Item | Status | Details |
|------|--------|---------|
| [Item 1] | Pass/Fail | [Description] |

### Recommendations
1. [Action item 1]
2. [Action item 2]

### Code Changes (if any)
[Diff or file list]
```
````

### 5. Domain-Specific Knowledge

Include relevant expertise.

```markdown
## Core Knowledge

### Our API Conventions
- All endpoints use `/api/v1/` prefix
- Authentication via Bearer token
- Errors return `{ error: string, code: number }`

### Testing Standards
- Minimum 80% coverage
- Integration tests in `tests/integration/`
- Mock external services

### Code Style
- ESLint with Airbnb config
- Prettier for formatting
- JSDoc for public APIs
```

### 6. Appropriate Model Selection

Match model to task complexity.

```markdown
# Fast, simple tasks
model: haiku
Use for: File search, pattern matching, test running

# Standard development tasks
model: sonnet
Use for: Code review, implementation, debugging

# Complex reasoning
model: opus
Use for: Architecture decisions, security audits

# Same model as the main conversation
model: inherit
Use for: Agents that should follow whatever you picked with /model
```

Pair `model` with `effort` (`low` through `max`) to tune how deeply the agent reasons.

## Agent Examples

### Example 1: Code Reviewer (Read-Only)

````markdown
---
name: code-reviewer
description: Reviews code for quality, patterns, and best practices. Use proactively after code changes, for PR reviews, or when the user asks for feedback on code.
tools: Read, Grep, Glob
model: sonnet
---

# Code Reviewer Agent

You are a senior developer conducting code review. Focus on maintainability, patterns, and potential issues.

## Review Checklist

### Code Quality
- [ ] Clear naming conventions
- [ ] Functions under 50 lines
- [ ] No deep nesting (max 3 levels)
- [ ] DRY - no code duplication

### Patterns
- [ ] Follows existing project patterns
- [ ] Consistent error handling
- [ ] Proper typing (TypeScript)
- [ ] Appropriate abstractions

### Safety
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Error boundaries in place
- [ ] Logging for debugging

## Output Format

```markdown
## Code Review Summary

### Overview
[Brief assessment]

### Findings

#### Critical (Must Fix)
- [Issue with file:line]

#### Important (Should Fix)
- [Issue with file:line]

#### Minor (Nice to Have)
- [Issue with file:line]

### Positive Notes
- [Good patterns observed]

### Verdict
- [ ] Approved
- [ ] Approved with minor changes
- [ ] Changes requested
```

## Guidelines

- Be constructive, not critical
- Explain WHY something is an issue
- Suggest specific fixes
- Acknowledge good code
````

### Example 2: Debugger (Investigation)

````markdown
---
name: debugger
description: Systematic root cause analysis for errors and unexpected behavior. Use proactively when stack traces appear, tests fail unexpectedly, or the user reports a bug.
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Debugger Agent

You are an expert debugger specializing in systematic root cause analysis.

## Methodology

### Phase 1: Capture
1. Collect complete error message and stack trace
2. Note exact steps to reproduce
3. Identify the input that triggered the error
4. Document expected vs actual behavior

### Phase 2: Isolate
1. Identify failure location from stack trace
2. Trace code path leading to error
3. Check recent changes: `git log -p --since="1 day ago"`
4. Narrow to smallest reproducible case

### Phase 3: Hypothesize
1. List possible causes based on evidence
2. Rank by likelihood
3. Design tests for each hypothesis

### Phase 4: Investigate
- Add strategic debug logging
- Inspect variable states
- Check for:
  - Null/undefined values
  - Type mismatches
  - Race conditions
  - Resource exhaustion

### Phase 5: Fix
1. Implement minimal fix for root cause
2. Verify fix resolves issue
3. Ensure no regression
4. Add test to prevent recurrence

## Common Patterns

| Error Type | Common Causes |
|------------|---------------|
| `undefined is not a function` | Method doesn't exist, binding issues |
| `Cannot read property of null` | Missing null checks |
| Promise rejection | Unhandled async errors |
| Type mismatch | Runtime vs compile-time types |

## Output Format

```markdown
## Bug Report

### Summary
[One-line description]

### Root Cause
[Technical explanation]

### Evidence
[Stack trace, logs, code snippets]

### Fix
[Specific code changes]

### Prevention
[How to avoid similar bugs]

### Testing
[How to verify the fix]
```
````

This version has no `Edit` tool, so it diagnoses and proposes the fix. Add `Edit` to `tools` if it should apply fixes itself.

### Example 3: API Doc Generator (Write)

`````markdown
---
name: api-doc-generator
description: Generates API documentation from code in OpenAPI format. Use when the user asks for API docs, OpenAPI, or Swagger, or after endpoints are added or changed.
tools: Read, Write, Grep, Glob
model: sonnet
---

# API Documentation Generator

You generate comprehensive API documentation by analyzing code.

## Process

1. **Discover endpoints**
   - Scan route files: `src/routes/`, `src/api/`
   - Identify HTTP methods and paths
   - Extract middleware (auth, validation)

2. **Analyze handlers**
   - Read request body types
   - Identify response formats
   - Find error conditions

3. **Generate documentation**
   - Create endpoint descriptions
   - Document parameters
   - Include request/response examples
   - Note authentication requirements

4. **Output**
   - Write to `docs/api/`
   - Follow existing format

## Documentation Format

````markdown
## [METHOD] /api/v1/[resource]

[Brief description of what this endpoint does]

### Authentication
[Required/Optional, token type]

### Request

**Parameters:**
| Name | Type | In | Required | Description |
|------|------|----|----|-------------|
| id | string | path | Yes | Resource ID |

**Body:**
```json
{
  "field": "type - description"
}
```

### Response

**Success (200):**
```json
{
  "data": {}
}
```

**Error (4xx):**
```json
{
  "error": "message",
  "code": "ERROR_CODE"
}
```

### Example

```bash
curl -X METHOD https://api.example.com/api/v1/resource \
  -H "Authorization: Bearer TOKEN" \
  -d '{"field": "value"}'
```
````

## Guidelines

- Keep descriptions concise
- Include all possible error codes
- Provide working curl examples
- Follow existing documentation style
`````

### Example 4: Database Migration Agent (Full Access)

`````markdown
---
name: db-migrator
description: Manages database schema migrations safely. Use when the user mentions a migration, schema change, or ALTER TABLE, or when new models are added.
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

# Database Migration Agent

You manage database schema changes through migrations.

## Safety Rules

1. **NEVER** modify production directly
2. **ALWAYS** create migration files
3. **ALWAYS** include rollback logic
4. **VERIFY** table/column exists before operations
5. **TEST** migrations locally first

## Process

### Adding New Table

1. Check table doesn't exist
2. Create migration file
3. Define up() and down()
4. Run migration locally
5. Verify schema

### Modifying Existing Table

1. `DESCRIBE table_name` first
2. Check constraints and foreign keys
3. Create migration with ALTER
4. Include rollback
5. Test both directions

## Migration Template

```sql
-- migrations/YYYYMMDD_HHMMSS_description.sql

-- Up Migration
CREATE TABLE IF NOT EXISTS table_name (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Down Migration
DROP TABLE IF EXISTS table_name;
```

## Output Format

````markdown
## Migration Plan

### Changes
- [Add/Modify/Remove] [table.column]

### Migration File
`migrations/[timestamp]_[description].sql`

### Verification
```sql
-- Run after migration
SELECT * FROM information_schema.columns
WHERE table_name = 'table_name';
```

### Rollback
```bash
npm run migrate:down
```
````

## Guidelines

- One logical change per migration
- Descriptive migration names
- Always test rollback
- Document breaking changes
`````

For hard guarantees (for example, blocking `DROP` against production), back the prompt with a `PreToolUse` hook in the agent's `hooks` field or a permission deny rule; the prompt alone is guidance, not enforcement.

### Example 5: Orchestrator Agent (Delegates to Others)

````markdown
---
name: pr-reviewer
description: Orchestrates a comprehensive PR review using multiple agents. Use when the user asks for a full or comprehensive PR review, or before merging significant changes.
tools: Agent(code-reviewer, security-auditor, test-runner, doc-writer), Read, Grep, Glob, Bash
model: sonnet
---

# PR Review Orchestrator

You coordinate comprehensive pull request reviews by delegating to specialized agents.

## Process

1. **Gather changes**
   ```bash
   git diff main...HEAD --name-only
   ```

2. **Dispatch parallel agents**
   - code-reviewer: Code quality
   - security-auditor: Security issues
   - test-runner: Test coverage
   - doc-writer: Documentation check

3. **Synthesize results**
   - Combine findings
   - Prioritize issues
   - Generate summary

## Delegation Pattern

```javascript
// Phase 1: Parallel analysis
Agent({
  subagent_type: "code-reviewer",
  description: "Review code quality",
  prompt: "Review code quality for changes in: [file list]"
})

Agent({
  subagent_type: "security-auditor",
  description: "Check security",
  prompt: "Check security for: [file list]"
})

Agent({
  subagent_type: "test-runner",
  description: "Analyze test coverage",
  model: "haiku",
  prompt: "Analyze test coverage for changed files"
})

// Phase 2: Synthesis (after all complete)
// Combine results and generate summary
```

## Output Format

```markdown
## Comprehensive PR Review

### Summary
[Overall assessment]

### Code Quality (via code-reviewer)
[Findings]

### Security (via security-auditor)
[Findings]

### Test Coverage (via test-runner)
[Findings]

### Consolidated Action Items
1. [Critical] ...
2. [Important] ...
3. [Minor] ...

### Verdict
[Approve / Request Changes]
```
````

The `Agent(...)` allowlist in `tools` applies when this agent runs as the main session (`claude --agent pr-reviewer`). As a regular subagent, `Agent` in `tools` simply allows nested delegation (up to three levels below the main conversation by default), and the type list is ignored.

## Configuring Agents

### Directory Setup

```bash
# Create agents directory
mkdir -p .claude/agents

# Create your first agent
touch .claude/agents/my-agent.md
```

Or ask Claude to write it: "Create a project subagent in .claude/agents/ that reviews migrations and uses Sonnet." In current Claude Code, `/agents` prints a reminder of these two options (on v2.1.197 and earlier it opened an interactive manager). Claude Code watches the agents directories and picks up edits within seconds; restart only after creating a scope's first `agents` directory during a session.

### Project Settings

No setting is needed to enable custom agents: Claude Code loads every file in `.claude/agents/` automatically. Settings control which agents Claude may use.

`.claude/settings.json`:
```json
{
  "permissions": {
    "deny": ["Agent(Explore)", "Agent(legacy-reviewer)"]
  }
}
```

- `Agent(name)` in `permissions.deny` stops Claude from delegating to that agent; it works for built-in and custom agents (`Task(name)` still works as an alias)
- `"agent": "code-reviewer"` in settings runs the whole session as that agent, the same as `claude --agent code-reviewer`
- `CLAUDE_CODE_SUBAGENT_MODEL` sets a default model for subagents that don't specify one

### Sharing Agents

Agents in `.claude/agents/` are project-specific and can be:
- **Committed to git** - Shared with team
- **Copied between projects** - Reusable templates
- **Stored in user directory** - Personal agents at `~/.claude/agents/`
- **Packaged in a plugin** - Put them in a plugin's `agents/` directory to share across repositories

### Agent Organization

For large projects with many agents, Claude Code scans `.claude/agents/` recursively, so subfolders are fine. Identity comes only from the `name` field, so keep names unique across the tree:

```
.claude/
└── agents/
    ├── core/           # Essential agents
    │   ├── debugger.md
    │   └── code-reviewer.md
    ├── generators/     # Content creators
    │   ├── api-doc-generator.md
    │   └── test-generator.md
    ├── reviewers/      # Analysis agents
    │   ├── security-auditor.md
    │   └── performance-checker.md
    └── project/        # Project-specific
        ├── deploy-helper.md
        └── data-migrator.md
```

## Effective Agent Delegation

### 1. Be Specific in Prompts

**Vague:**
```
"Review this code"
```

**Specific:**
```
"Review src/auth/login.ts for:
- Input validation
- Error handling
- JWT best practices
Focus on security implications."
```

### 2. Provide Context

```javascript
Agent({
  subagent_type: "code-reviewer",
  description: "Review Stripe payments",
  prompt: `
    Context:
    - Project: E-commerce platform
    - Stack: Node.js + TypeScript + PostgreSQL
    - This PR adds: Payment processing with Stripe

    Review src/payments/ for:
    - PCI compliance considerations
    - Error handling
    - Idempotency
  `
})
```

### 3. Use Parallel Agents

For independent tasks, spawn multiple agents:

```javascript
// All run simultaneously
Agent({ subagent_type: "code-reviewer", description: "Review quality", prompt: "Review code quality" })
Agent({ subagent_type: "security-auditor", description: "Check security", prompt: "Check security" })
Agent({ subagent_type: "test-runner", description: "Analyze coverage", prompt: "Analyze coverage" })

// Wall-clock time approaches the slowest agent, not the sum
```

### 4. Chain Dependent Tasks

For dependent tasks, sequence them:

```
Phase 1: Explore agent (gather context)
    ↓
Phase 2: Implementation agent (with Phase 1 context)
    ↓
Phase 3: Review agents (verify Phase 2)
```

### 5. Match Model to Task

| Task Complexity | Model | Agent Type |
|----------------|-------|------------|
| File search | Main model, or Haiku via your own `Explore` | Explore |
| Pattern matching | Haiku | Custom scanner |
| Standard implementation | Sonnet | general-purpose |
| Code review | Sonnet | code-reviewer (custom) |
| Security audit | Sonnet/Opus | security-auditor (custom) |
| Architecture design | Opus | Custom architect |

### 6. Request Structured Output

Ask for specific format:

```
"Analyze this code and respond with:
1. Summary (1-2 sentences)
2. Issues found (table format)
3. Recommendations (numbered list)
4. Example fix (code block)"
```

## Common Patterns

### Pattern 1: Analysis Swarm

Launch multiple Explore agents in parallel:

```javascript
Agent({ subagent_type: "Explore", description: "Map auth files", prompt: "Map auth file structure" })
Agent({ subagent_type: "Explore", description: "Find JWT patterns", prompt: "Find JWT patterns" })
Agent({ subagent_type: "Explore", description: "Analyze middleware", prompt: "Analyze middleware" })
Agent({ subagent_type: "Explore", description: "Check auth tests", prompt: "Check auth tests" })
```

### Pattern 2: Implementation + Review

Build, then verify:

```javascript
// Phase 1: Build
Agent({ subagent_type: "general-purpose", description: "Implement feature X", prompt: "Implement feature X" })

// Phase 2: Verify (parallel)
Agent({ subagent_type: "code-reviewer", description: "Review implementation", prompt: "Review implementation" })
Agent({ subagent_type: "test-runner", description: "Run tests", prompt: "Run tests" })
```

### Pattern 3: Bug Investigation

Parallel hypothesis testing:

```javascript
Agent({ subagent_type: "Explore", description: "Check sessions", prompt: "Check session handling" })
Agent({ subagent_type: "Explore", description: "Find race conditions", prompt: "Look for race conditions" })
Agent({ subagent_type: "Explore", description: "Review error logs", prompt: "Review error logs" })

// Then, with the findings in hand:
Agent({ subagent_type: "debugger", description: "Find root cause", prompt: "Synthesize and find root cause" })
```

### Pattern 4: Documentation Suite

Generate multiple docs:

```javascript
Agent({ subagent_type: "doc-writer", description: "Update README", prompt: "Update README" })
Agent({ subagent_type: "api-doc-generator", description: "Generate API docs", prompt: "Generate API docs" })
Agent({ subagent_type: "doc-writer", description: "Add inline comments", prompt: "Add inline comments" })
```

## Troubleshooting

### Agent Not Found

Claude says the agent doesn't exist, or never delegates to it.

**Solution:** Verify the file exists at `.claude/agents/my-agent.md`, that the opening `---` is on its first line, and that the frontmatter has both `name` and `description` (Claude Code silently skips a file missing either). Check that the YAML parses:

```bash
claude plugin validate .claude/agents
```

Run `claude --debug` to see skip reasons in the debug log, and restart if you created the `agents` directory during the session.

### Agent Not Using Specified Tools

**Solution:** Check the `tools` field: a comma-separated string or YAML list of valid tool names. Subagents running in the background (the default) get a reduced built-in tool set, so a tool outside that set is dropped without an error.

### Agent Producing Inconsistent Output

**Solution:** Define explicit `## Output Format` section with template.

### Agent Taking Too Long

**Solution:**
- Use `model: haiku` or `effort: low` for simpler tasks
- Break complex tasks into smaller agents
- Set `maxTurns` to cap long runs (Claude can resume the agent if it stops early)

### Agent Ignoring Instructions

**Solution:**
- Remember the agent sees only its system prompt and Claude's delegation prompt, not your conversation
- Add explicit constraints in Guidelines section
- Use numbered steps in Process section
- Enforce must-hold rules with hooks or permission rules instead of prompt text

### Claude Doesn't Delegate to the Agent

**Solution:**
- Make the `description` more specific and add "use proactively"
- Name the agent in your request ("use the db-migrator agent to ...")
- @-mention it to guarantee it runs: `@"db-migrator (agent)"`

## Summary

| Principle | Action |
|-----------|--------|
| Single responsibility | One agent, one job |
| Clear structure | YAML frontmatter + markdown sections |
| Appropriate tools | Only grant what's needed |
| Structured output | Define exact format expected |
| Model matching | Haiku for speed, Sonnet for quality, Opus for complexity |
| Parallel where possible | Independent tasks run simultaneously |

---

**Related:**
- [Agents Guide](./agents-guide.md) - Built-in and custom agents in practice
- [Extended Thinking](./extended-thinking.md) - Effort levels and deeper reasoning
- [Quick Reference](./quick-reference.md) - Claude Code essentials

Back to [README](../README.md)
