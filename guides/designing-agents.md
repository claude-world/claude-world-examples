# Designing Project-Specific Claude Code Agents

> Custom agents transform repetitive tasks into one-command operations. This guide covers everything from basics to advanced patterns.

## Quick Reference

| Section | Content |
|---------|---------|
| [What are Agents?](#what-are-agents) | Understanding subagents and Task tool |
| [When to Create](#when-to-create-custom-agents) | Built-in vs custom agents |
| [File Structure](#agent-file-structure) | YAML frontmatter + markdown format |
| [Best Practices](#best-practices-for-agent-prompts) | Writing effective agent prompts |
| [Examples](#agent-examples) | Real-world specialized agents |
| [Configuration](#configuring-agents) | Setting up `.claude/agents/` |
| [Delegation Tips](#effective-agent-delegation) | Getting the most from agents |

## What are Agents?

Agents (also called subagents) are specialized Claude instances spawned via the **Task tool**. Each agent has:

- **Focused expertise** - Defined role and responsibilities
- **Specific tools** - Only the tools it needs
- **Clear output** - Structured response format
- **Activation triggers** - When to automatically engage

```
Main Claude Instance
       │
       ├── Task(code-reviewer) ─► Reviews code quality
       ├── Task(debugger) ─► Investigates bugs
       ├── Task(doc-writer) ─► Creates documentation
       └── Task(security-auditor) ─► Checks vulnerabilities
```

### How Agents Work

When you invoke an agent, Claude Code:

1. Reads the agent definition from `.claude/agents/`
2. Creates a new context with the agent's system prompt
3. Grants only the specified tools
4. Executes the task with focused expertise
5. Returns results to the main conversation

**Conceptual Task tool syntax:**

```javascript
Task({
  subagent_type: "agent-name",    // Agent to invoke
  model: "sonnet",                 // Optional: haiku, sonnet, opus
  prompt: "Your specific task",    // What to do
  run_in_background: false         // Optional: async execution
})
```

### Built-in vs Custom Agents

| Built-in Agents | Purpose |
|-----------------|---------|
| `Explore` | Fast codebase navigation (Haiku) |
| `general-purpose` | Complex multi-step tasks |
| `code-reviewer` | Code quality analysis |
| `security-auditor` | Vulnerability detection |
| `test-runner` | Test execution |
| `debugger` | Root cause analysis |
| `doc-writer` | Documentation |

**Custom agents** extend these with project-specific expertise.

## When to Create Custom Agents

### Create Custom Agents When:

1. **Repetitive specialized tasks** - Same process run frequently
2. **Project-specific knowledge** - Domain expertise needed
3. **Consistent output format** - Standardized results required
4. **Team workflow** - Shared processes across developers
5. **Complex multi-step procedures** - Documented process to follow

### Use Built-in Agents When:

1. **General coding tasks** - Standard development work
2. **One-off operations** - Not repeated often
3. **Simple searches** - Basic file/pattern matching
4. **Standard reviews** - Generic code quality checks

### Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| "Review this PR for our coding standards" | Custom: `project-reviewer` |
| "Find all TypeScript files" | Built-in: `Explore` |
| "Check for security issues" | Built-in: `security-auditor` |
| "Generate API docs in our format" | Custom: `api-doc-generator` |
| "Debug this error" | Built-in: `debugger` |
| "Migrate data using our process" | Custom: `data-migrator` |

## Agent File Structure

Agents are markdown files with YAML frontmatter, stored in `.claude/agents/`.

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

```markdown
---
name: agent-name
description: Brief description shown in agent list. Keep under 100 chars.
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

# Agent Name

You are a [role description]. You help users with [specific tasks].

## Activation

Automatically activate when:
- [Trigger condition 1]
- [Trigger condition 2]
- [Trigger condition 3]

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
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (kebab-case) |
| `description` | Yes | Brief description (<100 chars) |
| `tools` | Yes | Comma-separated tool list |
| `model` | No | `haiku`, `sonnet` (default), or `opus` |

### Available Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| `Read` | Read files | Always include |
| `Write` | Create new files | Generators |
| `Edit` | Modify existing files | Fixers, updaters |
| `Bash` | Execute shell commands | Test runners, builders |
| `Grep` | Search file contents | Analyzers |
| `Glob` | Find files by pattern | Explorers |
| `Task` | Spawn sub-agents | Orchestrators |
| `WebFetch` | Fetch web content | Documentation agents |
| `WebSearch` | Search the web | Research agents |
| `TodoWrite` | Manage task lists | Project managers |

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

# Orchestrator agents
tools: Read, Grep, Glob, Task
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
tools: All tools
---
```

### 2. Clear Activation Triggers

Define when the agent should activate.

```markdown
## Activation

Automatically activate when:
- User runs tests and they fail
- User mentions "test", "coverage", "failing"
- User asks to verify changes work
- After significant code changes
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

```markdown
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
```

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
```

## Agent Examples

### Example 1: Code Reviewer (Read-Only)

```markdown
---
name: code-reviewer
description: Reviews code for quality, patterns, and best practices
tools: Read, Grep, Glob
model: sonnet
---

# Code Reviewer Agent

You are a senior developer conducting code review. Focus on maintainability, patterns, and potential issues.

## Activation

Automatically activate when:
- User mentions "review", "PR", "pull request"
- User asks for feedback on code
- Before merging to main branch

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
```

### Example 2: Debugger (Investigation)

```markdown
---
name: debugger
description: Systematic root cause analysis for errors and unexpected behavior
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Debugger Agent

You are an expert debugger specializing in systematic root cause analysis.

## Activation

Automatically activate when:
- Error messages or stack traces appear
- Tests fail unexpectedly
- User mentions "bug", "error", "not working", "debug"
- Unexpected behavior observed

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
```

### Example 3: API Doc Generator (Write)

```markdown
---
name: api-doc-generator
description: Generates API documentation from code in OpenAPI format
tools: Read, Write, Grep, Glob
model: sonnet
---

# API Documentation Generator

You generate comprehensive API documentation by analyzing code.

## Activation

Automatically activate when:
- User mentions "API docs", "OpenAPI", "Swagger"
- New endpoints are added
- API changes are made

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

```markdown
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
```

## Guidelines

- Keep descriptions concise
- Include all possible error codes
- Provide working curl examples
- Follow existing documentation style
```

### Example 4: Database Migration Agent (Full Access)

```markdown
---
name: db-migrator
description: Manages database schema migrations safely
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

# Database Migration Agent

You manage database schema changes through migrations.

## Activation

Automatically activate when:
- User mentions "migration", "schema change", "alter table"
- Database structure needs modification
- New models are added

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

```markdown
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
```

## Guidelines

- One logical change per migration
- Descriptive migration names
- Always test rollback
- Document breaking changes
```

### Example 5: Orchestrator Agent (Delegates to Others)

```markdown
---
name: pr-reviewer
description: Orchestrates comprehensive PR review using multiple agents
tools: Read, Grep, Glob, Task
model: sonnet
---

# PR Review Orchestrator

You coordinate comprehensive pull request reviews by delegating to specialized agents.

## Activation

Automatically activate when:
- User mentions "full review", "comprehensive PR review"
- Before merging significant changes

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
Task({
  subagent_type: "code-reviewer",
  model: "sonnet",
  prompt: "Review code quality for changes in: [file list]"
})

Task({
  subagent_type: "security-auditor",
  model: "sonnet",
  prompt: "Check security for: [file list]"
})

Task({
  subagent_type: "test-runner",
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
```

## Configuring Agents

### Directory Setup

```bash
# Create agents directory
mkdir -p .claude/agents

# Create your first agent
touch .claude/agents/my-agent.md
```

### Project Settings

`.claude/settings.json`:
```json
{
  "agents": {
    "enabled": true
  }
}
```

### Sharing Agents

Agents in `.claude/agents/` are project-specific and can be:
- **Committed to git** - Shared with team
- **Copied between projects** - Reusable templates
- **Stored in user directory** - Personal agents at `~/.claude/agents/`

### Agent Organization

For large projects with many agents:

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
Task({
  subagent_type: "code-reviewer",
  model: "sonnet",
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
Task({ subagent_type: "code-reviewer", prompt: "Review code quality" })
Task({ subagent_type: "security-auditor", prompt: "Check security" })
Task({ subagent_type: "test-runner", prompt: "Analyze coverage" })

// Time = max(individual times), not sum
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
| File search | Haiku | Explore |
| Pattern matching | Haiku | Custom scanner |
| Standard implementation | Sonnet | general-purpose |
| Code review | Sonnet | code-reviewer |
| Security audit | Sonnet/Opus | security-auditor |
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
Task({ subagent_type: "Explore", prompt: "Map auth file structure" })
Task({ subagent_type: "Explore", prompt: "Find JWT patterns" })
Task({ subagent_type: "Explore", prompt: "Analyze middleware" })
Task({ subagent_type: "Explore", prompt: "Check auth tests" })
```

### Pattern 2: Implementation + Review

Build, then verify:

```javascript
// Phase 1: Build
Task({ subagent_type: "general-purpose", prompt: "Implement feature X" })

// Phase 2: Verify (parallel)
Task({ subagent_type: "code-reviewer", prompt: "Review implementation" })
Task({ subagent_type: "test-runner", prompt: "Run tests" })
```

### Pattern 3: Bug Investigation

Parallel hypothesis testing:

```javascript
Task({ subagent_type: "Explore", prompt: "Check session handling" })
Task({ subagent_type: "Explore", prompt: "Look for race conditions" })
Task({ subagent_type: "Explore", prompt: "Review error logs" })
Task({ subagent_type: "debugger", prompt: "Synthesize and find root cause" })
```

### Pattern 4: Documentation Suite

Generate multiple docs:

```javascript
Task({ subagent_type: "doc-writer", prompt: "Update README" })
Task({ subagent_type: "api-doc-generator", prompt: "Generate API docs" })
Task({ subagent_type: "doc-writer", prompt: "Add inline comments" })
```

## Troubleshooting

### Agent Not Found

```
Error: Agent 'my-agent' not found
```

**Solution:** Verify file exists at `.claude/agents/my-agent.md` with correct frontmatter.

### Agent Not Using Specified Tools

**Solution:** Check `tools` field in frontmatter. Must be comma-separated, valid tool names.

### Agent Producing Inconsistent Output

**Solution:** Define explicit `## Output Format` section with template.

### Agent Taking Too Long

**Solution:**
- Use `model: haiku` for simpler tasks
- Break complex tasks into smaller agents
- Use `run_in_background: true` for long operations

### Agent Ignoring Instructions

**Solution:**
- Make activation triggers more specific
- Add explicit constraints in Guidelines section
- Use numbered steps in Process section

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
- [Agents Guide](./agents-guide.md) - Using built-in agents
- [Extended Thinking](./extended-thinking.md) - When to use thinking mode
- [Quick Reference](./quick-reference.md) - Claude Code essentials

Back to [README](../README.md)
