# Multi-AI Workflow Pattern

> When one AI isn't enough: coordinating Claude, Codex, and Gemini CLI.

## Why Multiple AI CLIs?

Each AI CLI has different strengths:

| CLI | Best For | Tradeoffs |
|-----|----------|-----------|
| **Claude Code** | Complex reasoning, architecture, code review | Slower for bulk operations |
| **Codex CLI** | Fast edits, batch refactoring, simple fixes | Less context awareness |
| **Gemini CLI** | Long-running tasks, large codebases | Different interaction style |

Using them together can be more efficient than using one for everything.

## The Handoff Pattern

### When to Stay with Claude

```
✓ Complex architecture decisions
✓ Multi-step reasoning
✓ Code review with context
✓ Debugging with investigation
✓ Feature implementation with tests
✓ Security-sensitive code
```

### When to Handoff to Codex

```
✓ Bulk find-and-replace
✓ Simple refactoring (rename variable across files)
✓ Mechanical transformations
✓ Template generation
✓ Formatting/style fixes
```

### When to Handoff to Gemini

```
✓ Very long tasks (>30 minutes)
✓ Large codebase exploration
✓ Background processing
✓ Tasks that can run while you do other work
```

## Practical Examples

### Example 1: Large Refactoring

**Scenario**: Rename a module from `UserAuth` to `Authentication` across 50 files.

**Approach**:

```
Step 1: Claude analyzes impact
"Analyze what needs to change to rename UserAuth to Authentication"

Claude: [Launches parallel agents]
→ Lists all files with UserAuth
→ Identifies import patterns
→ Flags potential breaking changes
→ Creates change plan

Step 2: Handoff to Codex for bulk changes
"Using the plan above, rename UserAuth to Authentication in all files"

Codex: [Fast batch replacement]
→ Updates 50 files in seconds
→ Fixes imports
→ Mechanical work done quickly

Step 3: Claude validates
"Verify the refactoring is complete and correct"

Claude: [Reviews the changes]
→ Checks for missed references
→ Runs tests
→ Identifies any issues
```

### Example 2: Test Generation

**Scenario**: Generate tests for 20 utility functions.

**Approach**:

```
Step 1: Claude establishes patterns
"Analyze our test patterns and create a template for utility tests"

Claude: [Analyzes existing tests]
→ Identifies test structure
→ Creates template
→ Documents edge cases to cover

Step 2: Codex generates bulk tests
"Generate tests for these 20 functions following the template"

Codex: [Generates all 20 test files]
→ Fast mechanical generation
→ Follows template exactly

Step 3: Claude reviews and enhances
"Review generated tests and add missing edge cases"

Claude: [Reviews intelligently]
→ Adds edge cases Codex missed
→ Improves assertions
→ Ensures coverage
```

### Example 3: Long-Running Analysis

**Scenario**: Analyze a legacy codebase for modernization opportunities.

**Approach**:

```
Step 1: Gemini for initial scan (background)
"Scan the entire codebase and create an inventory of:
- Deprecated patterns
- Dead code
- Missing tests
- Security issues"

Gemini: [Runs in background for 30+ minutes]
→ You continue other work
→ Comprehensive report when done

Step 2: Claude prioritizes findings
"Review Gemini's report and prioritize by impact"

Claude: [Applies judgment]
→ Ranks issues by severity
→ Creates action plan
→ Estimates effort

Step 3: Execute with appropriate tool
→ Security fixes: Claude (needs context)
→ Dead code removal: Codex (mechanical)
→ Pattern updates: Mixed approach
```

## Context Passing Strategies

### Strategy 1: File-Based Handoff

```markdown
## Handoff File: handoff-context.md

### Task
Rename all instances of `oldFunction` to `newFunction`

### Context
- Files to modify: /src/utils/*.ts, /src/components/*.tsx
- Pattern: `oldFunction(` → `newFunction(`
- Also update: imports, exports, type definitions

### Completed by Claude
- [x] Impact analysis
- [x] Identified 47 files

### For Codex
- [ ] Perform replacements
- [ ] Update imports
```

### Strategy 2: Checkpoint Pattern

```
1. Claude creates checkpoint after analysis
   → Saves state to .claude-checkpoint.json

2. Other CLI reads checkpoint
   → Understands what's been done
   → Knows what to do next

3. Claude validates final state
   → Compares to expected outcome
   → Handles edge cases
```

### Strategy 3: Git Branch Isolation

```bash
# Claude works on analysis branch
git checkout -b feature/auth-refactor-analysis
# Claude does analysis work

# Codex works on implementation branch
git checkout -b feature/auth-refactor-impl
# Codex does mechanical changes

# Merge and Claude validates
git checkout feature/auth-refactor-analysis
git merge feature/auth-refactor-impl
# Claude reviews merged result
```

## Decision Framework

```
┌─────────────────────────────────────────┐
│         WHICH CLI SHOULD I USE?         │
└─────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Is it complex/nuanced?│
        └───────────┬───────────┘
               YES  │  NO
                    │    │
    ┌───────────────┘    └──────────────┐
    ▼                                   ▼
┌─────────┐                    ┌───────────────────┐
│ CLAUDE  │                    │ Is it bulk/batch? │
└─────────┘                    └─────────┬─────────┘
                                    YES  │  NO
                               ┌─────────┘  │
                               ▼            ▼
                          ┌───────┐   ┌───────────────┐
                          │ CODEX │   │ Is it long-   │
                          └───────┘   │ running?      │
                                      └───────┬───────┘
                                         YES  │  NO
                                    ┌─────────┘  │
                                    ▼            ▼
                               ┌────────┐   ┌────────┐
                               │ GEMINI │   │ CLAUDE │
                               └────────┘   └────────┘
```

## Best Practices

### 1. Start with Claude

Claude excels at understanding the task and creating a plan:

```
"I need to update all API endpoints to use the new auth pattern.
Create a plan for this migration."
```

### 2. Document Handoff Points

When switching CLIs, be explicit:

```markdown
## Handoff to Codex

### What's done
- Analysis complete
- Pattern identified
- 34 files listed

### What to do
- Replace pattern A with pattern B in listed files
- Do NOT modify: /src/auth/core.ts (needs manual review)
```

### 3. Validate After Bulk Operations

Always return to Claude for validation:

```
"Codex has completed the bulk rename. Verify:
1. All references updated
2. Tests still pass
3. No missed edge cases"
```

### 4. Keep Humans in the Loop

For critical operations:

```
Claude → Codex → Human Review → Claude Validation
            ↓
    Bulk changes need human approval
    before Claude validates
```

## Anti-Patterns to Avoid

### Don't: Use Codex for Complex Logic

```
✗ "Codex, refactor this authentication flow to use JWT"
  → Lacks context, may break security

✓ "Claude, refactor authentication to use JWT"
  → Understands implications, handles edge cases
```

### Don't: Use Claude for Mechanical Work

```
✗ "Claude, rename 'foo' to 'bar' in all 200 files"
  → Wastes Claude's capabilities, slow

✓ "Codex, rename 'foo' to 'bar' in all 200 files"
  → Fast, perfect for mechanical tasks
```

### Don't: Lose Context Between Handoffs

```
✗ "Codex, finish what Claude started"
  → Codex doesn't know what Claude did

✓ "Codex, based on handoff-context.md, complete the rename operation"
  → Clear context passed
```

## Summary

| Step | CLI | Purpose |
|------|-----|---------|
| 1. Analyze | Claude | Understand task, create plan |
| 2. Bulk Execute | Codex | Fast mechanical changes |
| 3. Long Tasks | Gemini | Background processing |
| 4. Validate | Claude | Review, test, finalize |

The key insight: **Use the right tool for each phase of work**.

---

See also: [Director Mode Basics](./director-mode-basics.md) | [Parallel Agents](./parallel-agents.md)
