# Designing Project-Specific Claude Code Skills

> From repetitive workflows to reusable slash commands - mastering skills unlocks consistent, efficient development

## Quick Reference

| Skill Type | Purpose | Example |
|------------|---------|---------|
| Workflow | Multi-step processes | `/workflow`, `/test-first` |
| Generator | Create files from templates | `/generate-component` |
| Checker | Validate against standards | `/project-health-check` |
| Runner | Execute command sequences | `/deploy-staging` |
| Utility | Single-purpose actions | `/smart-commit` |

---

## What Are Claude Code Skills?

Skills are **slash commands** (`/command-name`) that expand into prompts. When you type `/workflow` in Claude Code, the content of `workflow.md` becomes your prompt, giving Claude detailed instructions on how to proceed.

Think of skills as **reusable workflow templates**:

```
You type:     /test-first user authentication
Claude sees:  [Full TDD workflow instructions] + "user authentication"
Result:       Structured test-driven development process
```

### Key Characteristics

- **User-facing**: Skills appear in the `/` autocomplete menu
- **Prompt expansion**: The skill file content becomes your prompt
- **Argument passing**: Use `$ARGUMENTS` to capture user input
- **Declarative**: Define the "what", let Claude figure out the "how"

---

## Skills vs Agents vs Hooks

Understanding when to use each:

| Aspect | Skills | Agents | Hooks |
|--------|--------|--------|-------|
| **Invocation** | `/command args` | Task tool or mention | Automatic triggers |
| **User-facing** | Yes (in `/` menu) | No (internal use) | No (background) |
| **Use case** | User workflows | Subtask delegation | Event reactions |
| **Location** | `.claude/commands/` | `.claude/agents/` | `.claude/settings.json` |
| **Example** | `/smart-commit` | `code-reviewer` agent | Pre-commit validation |

### When to Use Each

**Use Skills when:**
- You want a reusable workflow users invoke directly
- The process has clear steps to follow
- You need consistent execution of common tasks

**Use Agents when:**
- You need specialized expertise for subtasks
- You want to delegate work within a skill
- You need parallel processing capabilities

**Use Hooks when:**
- You want automatic reactions to events
- Pre/post processing is needed for certain actions
- You need validation before commits or file saves

### How They Work Together

```
User invokes: /workflow "add user login"
                  │
                  ▼
           ┌─────────────────┐
           │  Workflow Skill │  (defines the process)
           └────────┬────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Explore │ │  Code   │ │  Test   │
   │  Agent  │ │ Reviewer│ │ Runner  │
   └─────────┘ └─────────┘ └─────────┘
                    │
                    ▼
           ┌─────────────────┐
           │   Pre-Commit    │  (hook validates)
           │      Hook       │
           └─────────────────┘
```

---

## Skill File Structure

### File Location

Skills live in `.claude/commands/`:

```
project-root/
└── .claude/
    └── commands/
        ├── workflow.md
        ├── test-first.md
        ├── smart-commit.md
        └── deploy-staging.md
```

### Basic Structure

Every skill file has two parts: **frontmatter** and **content**.

```markdown
---
description: Brief description shown in / menu
---

# Skill Name

[Instructions that execute when the skill is invoked]

## Steps

1. First, do this
2. Then, do that
3. Finally, verify
```

### Frontmatter Options

```yaml
---
# Required
description: What this skill does (shown in / menu)

# Optional
user-invocable: true           # Show in / menu (default: true)
allowed-tools: [Read, Write]   # Restrict available tools
context: fork                  # Isolated context
agent: my-agent                # Run as specific agent
---
```

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `description` | string | required | Shown in `/` autocomplete |
| `user-invocable` | boolean | true | Whether to show in menu |
| `allowed-tools` | array | all | Restrict tool access |
| `context` | string | - | "fork" for isolated execution |
| `agent` | string | - | Run as specified agent |

### Handling Arguments

Use `$ARGUMENTS` to capture user input:

```markdown
---
description: Search codebase for pattern
---

# Code Search

Search the codebase for: $ARGUMENTS

If no arguments provided, ask what to search for.
```

**Usage examples:**
```
/search loginHandler           → $ARGUMENTS = "loginHandler"
/search "user authentication"  → $ARGUMENTS = "user authentication"
/search                        → $ARGUMENTS = ""
```

---

## Creating Reusable Workflows as Skills

### Step 1: Identify the Pattern

Look for tasks you repeat often:
- Running through a development process
- Creating new files following a template
- Performing quality checks
- Deploying to environments

### Step 2: Document the Steps

Write out the manual steps:
```
1. Understand the requirement
2. Check existing patterns
3. Write tests first
4. Implement minimally
5. Verify tests pass
6. Commit with conventional format
```

### Step 3: Create the Skill File

Transform steps into a structured skill:

```markdown
---
description: Complete 5-step development workflow
---

# Development Workflow

Execute the development workflow for: $ARGUMENTS

## Step 1: Focus Problem

Use Explore agent to understand the context:
- What files are affected?
- What patterns exist?
- What tests are relevant?

## Step 2: Prevent Over-development

Check for YAGNI violations:
- Is this the minimal solution?
- Are we building for "just in case"?
- Can this be simpler?

## Step 3: Test First (TDD)

Follow Red-Green-Refactor:
1. Write failing test
2. Minimal implementation
3. Refactor while green

## Step 4: Document

Update relevant documentation:
- Code comments for "why"
- README if needed
- API docs if applicable

## Step 5: Smart Commit

Create conventional commit:
- One logical change per commit
- Clear, descriptive message
- No debug code or temp files
```

### Step 4: Test and Iterate

Run the skill several times:
1. Does it work for different inputs?
2. Are the steps clear enough?
3. Is anything missing?

---

## Skill Design Patterns

### Pattern 1: Workflow Skill

For multi-step processes with clear phases.

```markdown
---
description: Complete test-driven development cycle
---

# Test-Driven Development

Implement TDD for: $ARGUMENTS

## Red Phase - Write Failing Test

- Test one specific behavior
- Test name describes expected result
- Confirm test fails (feature doesn't exist)

## Green Phase - Minimal Implementation

- Write ONLY enough code to pass
- Don't optimize yet
- Just make it work

## Refactor Phase - Clean Up

- Remove duplication
- Improve naming
- Simplify logic
- Keep tests passing

## Checklist

- [ ] Tests cover edge cases
- [ ] Tests run fast (< 100ms for unit tests)
- [ ] Code is clean and readable
```

### Pattern 2: Generator Skill

For creating files from templates.

```markdown
---
description: Generate new API endpoint with tests
---

# API Endpoint Generator

Generate endpoint for: $ARGUMENTS

## Process

1. **Check** if endpoint already exists
2. **Analyze** existing endpoint patterns in `/src/api/`
3. **Generate** route handler following project conventions
4. **Create** test file with standard test cases
5. **Update** API index to export new endpoint

## Output Location

- Route: `src/api/[name].ts`
- Tests: `src/api/__tests__/[name].test.ts`
- Types: `src/types/api.ts` (if needed)

## Template

Follow the pattern in existing endpoints:
- Error handling with try/catch
- Input validation with zod
- Consistent response format
- TypeScript types for request/response
```

### Pattern 3: Checker Skill

For validation against standards.

```markdown
---
description: Run comprehensive quality checks
---

# Quality Check

Validate project against quality standards.

## Checks to Run

### Required (Must Pass)
- [ ] `npm run lint` - No linting errors
- [ ] `npm run typecheck` - No type errors
- [ ] `npm test` - All tests pass
- [ ] `npm run build` - Build succeeds

### Recommended (Should Pass)
- [ ] Test coverage > 80%
- [ ] No files over 500 lines
- [ ] No console.log statements in production code

## Output Format

| Check | Status | Notes |
|-------|--------|-------|
| Lint | PASS/FAIL | Details |
| Types | PASS/FAIL | Details |
| Tests | PASS/FAIL | Details |
| Build | PASS/FAIL | Details |

## Auto-Fix

If issues found, offer to fix:
- Lint errors: `npm run lint:fix`
- Formatting: `npm run format`
```

### Pattern 4: Runner Skill

For executing command sequences.

```markdown
---
description: Deploy to staging environment
---

# Deploy Staging

Deploy current branch to staging.

## Pre-flight Checks

1. Verify on correct branch
2. Run quality checks
3. Ensure no uncommitted changes

## Deployment Steps

```bash
# Build
npm run build

# Run tests
npm test

# Deploy
npm run deploy:staging
```

## Post-deployment

1. Verify deployment succeeded
2. Run smoke tests
3. Report deployment status

## Error Handling

If deployment fails:
1. Show error output
2. Check common issues
3. Suggest rollback if needed
```

### Pattern 5: Utility Skill

For single-purpose actions.

```markdown
---
description: Create conventional commit with quality checks
---

# Smart Commit

Create a high-quality commit for current changes.

## Pre-Commit Checklist

- [ ] One logical change only
- [ ] No debug code
- [ ] Tests pass
- [ ] No linting errors

## Commit Format

```
<type>(<scope>): <description>

<body>

<footer>
```

### Types
| Type | Use When |
|------|----------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Code restructure |
| `chore` | Maintenance |

## Execution

1. Run `git diff --staged` to see changes
2. Determine appropriate type and scope
3. Write clear description (50 chars or less)
4. Execute commit
```

---

## Advanced Skill Features

### Context Fork (Isolated Execution)

Run skills in isolated context to prevent side effects:

```yaml
---
description: Experimental feature exploration
context: fork
---

# Explore Feature

Try out a feature implementation without affecting main context.
Changes made here won't persist unless explicitly saved.
```

### Agent Mode

Run skill as a specific agent:

```yaml
---
description: Security audit with specialized expertise
agent: security-auditor
---

# Security Audit

Perform comprehensive security review of: $ARGUMENTS
```

### Tool Restrictions

Limit available tools for safety:

```yaml
---
description: Read-only codebase analysis
allowed-tools: [Read, Grep, Glob]
---

# Code Analysis

Analyze the codebase without making changes.
This skill cannot modify any files.
```

---

## Best Practices

### 1. Clear, Descriptive Names

```
Good: /deploy-staging, /generate-component, /run-tests
Bad:  /ds, /gc, /rt
```

### 2. Helpful Descriptions

```markdown
# Good
description: Run tests and automatically fix failures

# Bad
description: test stuff
```

### 3. Handle Missing Arguments

```markdown
Implement feature: $ARGUMENTS

If no arguments provided:
1. Ask what feature to implement
2. Wait for user input before proceeding
```

### 4. Structured Steps

Break complex workflows into clear phases:

```markdown
## Phase 1: Analyze
[What to analyze and why]

## Phase 2: Plan
[How to approach the solution]

## Phase 3: Execute
[The actual implementation]

## Phase 4: Verify
[How to confirm success]
```

### 5. Include Checklists

Checklists help ensure completeness:

```markdown
## Pre-deployment Checklist
- [ ] All tests pass
- [ ] No linting errors
- [ ] Documentation updated
- [ ] No sensitive data exposed
```

### 6. Define Expected Output

Show what success looks like:

```markdown
## Expected Output

When complete, show:
```
## Deployment Complete

- Environment: staging
- Version: 1.2.3
- URL: https://staging.example.com

### Next Steps
1. Verify functionality at URL
2. Run smoke tests
3. Notify team
```
```

### 7. Reference Other Skills/Agents

Build on existing capabilities:

```markdown
## Process

1. First, run `/focus-problem` to understand the requirement
2. Use the **code-reviewer** agent to check existing patterns
3. After implementation, run `/smart-commit` to commit changes
```

---

## Example Skills

### /commit (Utility)

```markdown
---
description: Conventional Commits with quality checks
---

# Smart Commit

Create commit for staged changes.

## Pre-Commit Checks
- [ ] Single logical change
- [ ] No debug code
- [ ] Tests pass

## Format
```
<type>(<scope>): <description>
```

## Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Restructure
- `chore` - Maintenance
```

### /review (Checker)

```markdown
---
description: Code review with multiple perspectives
---

# Code Review

Review recent changes from multiple angles.

## Review Dimensions

### 1. Code Quality
- Naming conventions
- Function length
- Complexity

### 2. Security
- Input validation
- Authentication
- Data exposure

### 3. Testing
- Test coverage
- Edge cases
- Mocking strategy

### 4. Documentation
- Code comments
- API docs
- README updates

## Output

Provide findings with severity levels:
- CRITICAL: Must fix before merge
- WARNING: Should fix soon
- INFO: Consider improving
```

### /test-first (Workflow)

```markdown
---
description: Test-Driven Development cycle
---

# Test-Driven Development

Implement TDD for: $ARGUMENTS

## Red Phase
Write failing test first:
- Test one behavior
- Clear test name
- Confirm failure

## Green Phase
Minimal implementation:
- Just enough to pass
- No optimization
- No extras

## Refactor Phase
Clean up while green:
- Remove duplication
- Improve names
- Simplify logic
```

### /workflow (Complete Workflow)

```markdown
---
description: Complete 5-step development workflow
---

# Development Workflow

## Overview

```
Step 1: Focus Problem    -> Understand before coding
Step 2: Prevent Overdev  -> Only build what's needed
Step 3: Test First       -> Red-Green-Refactor
Step 4: Document         -> Keep it clear
Step 5: Smart Commit     -> Conventional Commits
```

## Step 1: Focus Problem

Use Explore agent:
- What is the user need?
- What defines success?
- What files are affected?

## Step 2: Prevent Over-development

YAGNI check:
- Immediate need only
- No "just in case"
- Simplest solution

## Step 3: Test First

TDD cycle:
1. Write failing test
2. Minimal code to pass
3. Refactor while green

## Step 4: Document

Update docs:
- README if needed
- Code comments for "why"
- API docs if applicable

## Step 5: Smart Commit

Conventional commit:
- One change per commit
- Clear description
- No debug code
```

---

## Configuring Skills in .claude/commands/

### Directory Setup

```bash
# Create commands directory
mkdir -p .claude/commands

# Create your first skill
touch .claude/commands/my-skill.md
```

### Skill Naming

- Use lowercase with hyphens: `my-skill.md`
- The filename (without `.md`) becomes the command: `/my-skill`
- Be descriptive but concise

### Testing Your Skill

1. Create the skill file
2. In Claude Code, type `/` to see it in the menu
3. Invoke with `/skill-name` or `/skill-name arguments`
4. Iterate based on results

### Organizing Multiple Skills

```
.claude/commands/
├── workflow.md           # Main development workflow
├── focus-problem.md      # Step 1: Analysis
├── test-first.md         # Step 3: TDD
├── smart-commit.md       # Step 5: Commits
├── project-health-check.md  # Quality audit
├── generate-component.md # File generation
└── deploy-staging.md     # Deployment
```

### Skill Validation

Use the `/skill-check` command to validate your skills:

```
/skill-check my-skill.md
```

This checks:
- Frontmatter is valid
- Description is present
- Required fields exist
- Referenced agents exist

---

## Summary

| Principle | Action |
|-----------|--------|
| Start simple | One clear purpose per skill |
| Be descriptive | Clear names and descriptions |
| Structure well | Use phases, steps, checklists |
| Handle arguments | Use `$ARGUMENTS` for flexibility |
| Define output | Show what success looks like |
| Iterate | Test and improve over time |

---

**Related:**
- [Agents Guide](./agents-guide.md) - Working with agents for subtask delegation
- [Quick Reference](./quick-reference.md) - Visual cheat sheets

Back to [README](../README.md)
