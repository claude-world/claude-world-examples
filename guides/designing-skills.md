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

Skills are reusable instructions packaged as a folder with a `SKILL.md` file. You run one as a **slash command** (`/skill-name`), and Claude can also load it on its own when its description matches what you're doing. When you type `/workflow` in Claude Code, the content of `.claude/skills/workflow/SKILL.md` becomes part of your prompt, giving Claude detailed instructions on how to proceed.

> **Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` still works and creates `/deploy`, but prefer `.claude/skills/deploy/SKILL.md` for new work: skills add supporting files, invocation control, and automatic loading.

Think of skills as **reusable workflow templates**:

```
You type:     /test-first user authentication
Claude sees:  [Full TDD workflow instructions] + "user authentication"
Result:       Structured test-driven development process
```

### Key Characteristics

- **User-facing**: Skills appear in the `/` autocomplete menu (`/skills` lists them all)
- **Model-invocable**: Claude loads a skill automatically when its description matches the task, unless you turn that off
- **Prompt expansion**: Only the description sits in context until the skill runs; then its full content enters the conversation
- **Argument passing**: Use `$ARGUMENTS`, `$0`/`$1`, or named arguments to capture user input
- **Declarative**: Define the "what", let Claude figure out the "how"

---

## Skills vs Agents vs Hooks

Understanding when to use each:

| Aspect | Skills | Agents | Hooks |
|--------|--------|--------|-------|
| **Invocation** | `/skill-name args`, or Claude loads it when the description matches | Claude delegates via the Agent tool, or you name or @-mention the agent | Automatic on lifecycle events |
| **User-facing** | Yes (in `/` menu) | Indirectly (you ask for one; it shows in `/tasks`) | No (background) |
| **Use case** | User workflows, reference knowledge | Subtask delegation in an isolated context | Event reactions, enforcement |
| **Location** | `.claude/skills/<name>/SKILL.md` | `.claude/agents/<name>.md` | `hooks` in `.claude/settings.json` |
| **Example** | `/smart-commit` | `code-reviewer` agent (custom) | Pre-commit validation |

### When to Use Each

**Use Skills when:**
- You want a reusable workflow users invoke directly
- The process has clear steps to follow
- You need consistent execution of common tasks
- Claude needs reference knowledge only some of the time

**Use Agents when:**
- You need specialized expertise for subtasks
- You want to delegate work within a skill
- You need parallel processing or context isolation

**Use Hooks when:**
- You want automatic reactions to events
- Pre/post processing is needed for certain actions
- A rule must hold every time (validation before commits or file edits)

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

Skills live in `.claude/skills/`, one folder per skill:

```
project-root/
└── .claude/
    └── skills/
        ├── workflow/
        │   └── SKILL.md
        ├── test-first/
        │   └── SKILL.md
        ├── smart-commit/
        │   └── SKILL.md
        └── deploy-staging/
            ├── SKILL.md
            └── scripts/
                └── smoke-test.sh
```

| Location | Path | Available in |
|----------|------|--------------|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This repository (commit it to share) |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled, as `/plugin-name:skill-name` |
| Legacy command | `.claude/commands/<name>.md` | Still works; same frontmatter except `name` and `paths` |

### Basic Structure

Every `SKILL.md` has two parts: **frontmatter** and **content**.

```markdown
---
description: What this skill does and when to use it (Claude reads this to decide when to load it)
---

# Skill Name

[Instructions that execute when the skill is invoked]

## Steps

1. First, do this
2. Then, do that
3. Finally, verify
```

### Frontmatter Options

All fields are optional; `description` is the one to always write. A realistic combination:

```yaml
---
# Recommended
description: Deploy the current branch to staging. Use when the user asks to deploy or ship to staging.

# Optional
name: deploy-staging            # Command name (defaults to the folder name)
argument-hint: "[service]"      # Shown during autocomplete
disable-model-invocation: true  # Only you can trigger it (it has side effects)
allowed-tools: Bash(npm run *) Bash(git status *)  # Pre-approved while it runs
effort: high                    # Effort level while the skill is active
context: fork                   # Run in an isolated subagent
agent: general-purpose          # Which agent runs it
---
```

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `name` | string | folder name | Command name in the `/` menu |
| `description` | string | first line of content | What it does and when to use it; Claude matches on this, so put the key use case first |
| `when_to_use` | string | - | Extra trigger phrases, appended to the description |
| `argument-hint` | string | - | Autocomplete hint such as `[issue-number]` |
| `arguments` | list | - | Names for positional arguments (`$name` substitution) |
| `disable-model-invocation` | boolean | false | Only you can invoke it; Claude won't load it automatically |
| `user-invocable` | boolean | true | `false` hides it from the `/` menu (Claude-only background knowledge) |
| `allowed-tools` | string/list | - | Tools Claude may use **without asking** during the turn that invokes it; does not restrict other tools |
| `disallowed-tools` | string/list | - | Tools removed while the skill is active |
| `model` | string | session model | Model while the skill is active |
| `effort` | string | session level | `low`, `medium`, `high`, `xhigh`, or `max` while the skill is active |
| `context` | string | - | `fork` runs the skill in a subagent |
| `agent` | string | `general-purpose` | Agent that runs a `context: fork` skill |
| `background` | boolean | true | With `context: fork`, `false` waits for the result |
| `hooks` | object | - | Hooks registered when the skill is invoked |
| `paths` | string/list | - | Globs; Claude auto-loads the skill only when working on matching files |
| `shell` | string | `bash` | Shell for `` !`command` `` injection (`bash` or `powershell`) |

`metadata`, `license`, and `compatibility` come from the open Agent Skills spec; Claude Code accepts them but doesn't act on them.

### Handling Arguments

Use `$ARGUMENTS` to capture everything typed after the command:

```markdown
---
description: Search codebase for pattern
argument-hint: "[pattern]"
---

# Code Search

Search the codebase for: $ARGUMENTS

If no arguments provided, ask what to search for.
```

**Usage examples:**
```
/search loginHandler           → $ARGUMENTS = loginHandler
/search "user authentication"  → $ARGUMENTS = "user authentication" (as typed), $0 = user authentication
/search                        → $ARGUMENTS is empty
```

For individual arguments, use `$0`, `$1` (or `$ARGUMENTS[0]`), or give them names with `arguments`:

```markdown
---
description: Migrate a component from one language to another
arguments: [component, from, to]
argument-hint: "[component] [from] [to]"
---

Migrate the $component component from $from to $to.
Preserve all existing behavior and tests.
```

`/migrate-component SearchBar JavaScript TypeScript` fills `$component`, `$from`, and `$to` in order (the same values as `$0`, `$1`, and `$2`). If no placeholder receives the arguments, Claude Code appends them as `ARGUMENTS: <value>`.

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

Transform steps into a structured skill at `.claude/skills/workflow/SKILL.md`:

```markdown
---
description: Complete 5-step development workflow. Use when starting a new feature or fix.
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
4. Does Claude load it on its own for requests that match the description?

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

For executing command sequences. Deployments have side effects, so keep Claude from starting them on its own:

````markdown
---
description: Deploy to staging environment
disable-model-invocation: true
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
````

### Pattern 5: Utility Skill

For single-purpose actions.

````markdown
---
description: Create conventional commit with quality checks
disable-model-invocation: true
allowed-tools: Bash(git diff *) Bash(git add *) Bash(git commit *) Bash(git status *)
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
````

---

## Advanced Skill Features

### Context Fork (Isolated Execution)

`context: fork` runs the skill in its own subagent, so the work stays out of your main context. The subagent receives the skill content as its prompt but **not** your conversation history, so the instructions must stand on their own. It runs in the background by default (`background: false` waits for the result). File edits still land in your working tree; they're made outside your conversation's checkpoints, so use git to undo them.

```markdown
---
description: Research how a feature works and report back
context: fork
agent: Explore
---

# Explore Feature

Research $ARGUMENTS thoroughly: find the relevant files, read them,
and summarize how the feature works with specific file references.
```

### Agent Mode

`agent` picks which agent runs a `context: fork` skill (it has no effect without `context: fork`). The agent supplies the system prompt, tools, and model; the skill supplies the task:

```markdown
---
description: Security audit with specialized expertise
context: fork
agent: security-auditor
---

# Security Audit

Perform comprehensive security review of: $ARGUMENTS
```

`agent` accepts a built-in agent (`Explore`, `Plan`, `general-purpose`) or a custom agent. `security-auditor` here must exist in `.claude/agents/` (see [Designing Agents](./designing-agents.md)); without `agent`, the skill runs on `general-purpose`.

### Tool Permissions and Restrictions

`allowed-tools` **pre-approves** tools for the turn that invokes the skill; it doesn't limit anything. To take tools away while a skill is active, use `disallowed-tools`:

```markdown
---
description: Read-only codebase analysis
disallowed-tools: Edit Write NotebookEdit Bash
---

# Code Analysis

Analyze the codebase without making changes.
Edit, Write, and Bash are unavailable while this skill runs.
```

And a skill that runs git without a prompt for each command:

```markdown
---
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

Both grants clear when you send your next message. For rules that must hold for the whole session, use permission settings or hooks.

### Dynamic Context Injection

A line of the form `` !`command` `` runs before Claude sees the skill, and the command's output replaces it:

```markdown
---
description: Summarize uncommitted changes and flag anything risky. Use when the user asks what changed.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any
risks such as missing error handling or tests that need updating.
```

A failing command aborts the whole invocation, so append `|| true` to commands that may exit non-zero. For multi-line commands, use a fenced block opened with ` ```! `.

### Supporting Files

Keep `SKILL.md` focused (under about 500 lines) and put detail in files next to it. Claude reads them only when needed:

```
deploy-staging/
├── SKILL.md          (required - overview and navigation)
├── reference.md      (detailed docs - loaded when needed)
└── scripts/
    └── smoke-test.sh (executed, not loaded)
```

Reference each file from `SKILL.md` so Claude knows when to open it, and use `${CLAUDE_SKILL_DIR}` to point at bundled scripts regardless of the current directory, for example `` Run `${CLAUDE_SKILL_DIR}/scripts/smoke-test.sh` ``.

### Packaging Skills in a Plugin

To share skills across repositories, put them in a plugin's `skills/` folder. Plugin skills are namespaced by the plugin name:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── review/
        └── SKILL.md      → /my-plugin:review
```

Test locally with `claude --plugin-dir ./my-plugin`, then publish through a marketplace so others can install it with `/plugin`.

---

## Best Practices

### 1. Clear, Descriptive Names

```
Good: /deploy-staging, /generate-component, /run-tests
Bad:  /ds, /gc, /rt
```

### 2. Helpful Descriptions

Claude decides when to load a skill from its description, so lead with what it does and when to use it:

```markdown
# Good
description: Run tests and automatically fix failures. Use when tests fail or the user asks to fix the test suite.

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

````markdown
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
````

### 7. Reference Other Skills/Agents

Build on existing capabilities (they must exist in your setup, for example from a plugin):

```markdown
## Process

1. First, run `/focus-problem` to understand the requirement
2. Use the **code-reviewer** agent to check existing patterns
3. After implementation, run `/smart-commit` to commit changes
```

---

## Example Skills

### /commit (Utility)

````markdown
---
description: Conventional Commits with quality checks
disable-model-invocation: true
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
````

### /review (Checker)

Claude Code already has a `/review` command (an alias of the bundled `/code-review`). A project skill named `review` doesn't replace that alias, so give your own checker a distinct name such as `team-review`:

```markdown
---
name: team-review
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

````markdown
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
````

---

## Configuring Skills in .claude/skills/

### Directory Setup

```bash
# Create a folder for the skill
mkdir -p .claude/skills/my-skill

# Create its SKILL.md
touch .claude/skills/my-skill/SKILL.md
```

### Skill Naming

- Use lowercase with hyphens: `my-skill/`
- The folder name (or the frontmatter `name`) becomes the command: `/my-skill`
- A legacy `.claude/commands/my-skill.md` also becomes `/my-skill`; if a skill and a command share a name, the skill wins
- Be descriptive but concise

### Testing Your Skill

1. Create the skill folder and its `SKILL.md`
2. In Claude Code, type `/` to see it in the menu (or run `/skills`). Edits are picked up live; run `/reload-skills` if you created a new top-level skills directory during the session
3. Invoke with `/skill-name` or `/skill-name arguments`, or ask for something that matches the description to test automatic loading
4. Iterate based on results

### Organizing Multiple Skills

```
.claude/skills/
├── workflow/SKILL.md              # Main development workflow
├── focus-problem/SKILL.md         # Step 1: Analysis
├── test-first/SKILL.md            # Step 3: TDD
├── smart-commit/SKILL.md          # Step 5: Commits
├── project-health-check/SKILL.md  # Quality audit
├── generate-component/SKILL.md    # File generation
└── deploy-staging/SKILL.md        # Deployment
```

### Skill Validation

Check that every `SKILL.md` frontmatter parses:

```bash
claude plugin validate .claude/skills
```

Then:
- Run `/skills` to confirm the skill loaded and see its source
- Run `/skill-doctor` to see each skill's context cost and how often it's used
- If you use [Director Mode Lite](https://github.com/claude-world/director-mode-lite), its `/skill-check` skill also checks descriptions and referenced agents

---

## Summary

| Principle | Action |
|-----------|--------|
| Start simple | One clear purpose per skill |
| Be descriptive | Clear names and descriptions |
| Structure well | Use phases, steps, checklists |
| Handle arguments | Use `$ARGUMENTS`, `$0`/`$1`, or named arguments |
| Define output | Show what success looks like |
| Iterate | Test and improve over time |

---

**Related:**
- [Agents Guide](./agents-guide.md) - Working with agents for subtask delegation
- [Designing Agents](./designing-agents.md) - Custom agents for `context: fork` skills
- [Quick Reference](./quick-reference.md) - Visual cheat sheets

Back to [README](../README.md)
