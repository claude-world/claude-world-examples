# Quick Reference Cards

> One-page visual guides for fast lookup.

## CLAUDE.md Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE.md CHECKLIST                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ TECH STACK                                                   │
│    ├── Framework + version                                      │
│    ├── Database + ORM                                           │
│    ├── Key libraries                                            │
│    └── Runtime (Node version, etc.)                             │
│                                                                 │
│  □ PROJECT STRUCTURE                                            │
│    ├── /src layout                                              │
│    ├── Where to put new files                                   │
│    └── Naming conventions                                       │
│                                                                 │
│  □ COMMANDS                                                     │
│    ├── Dev server: _______________                              │
│    ├── Run tests: _______________                               │
│    ├── Build: _______________                                   │
│    └── Migrations: _______________                              │
│                                                                 │
│  □ CODE STYLE                                                   │
│    ├── TypeScript strict? □ Yes □ No                            │
│    ├── Linter config                                            │
│    └── Formatting (Prettier?)                                   │
│                                                                 │
│  □ PERMISSIONS                                                  │
│    ├── Can do freely: _______________                           │
│    ├── Needs mention: _______________                           │
│    └── Prohibited: _______________                              │
│                                                                 │
│  □ PATTERNS                                                     │
│    ├── API response format                                      │
│    ├── Error handling                                           │
│    └── Component structure                                      │
│                                                                 │
│  □ HEALTH CHECK                                                 │
│    ├── Last updated: _______________                            │
│    └── Under 500 lines? □ Yes □ No                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Director Mode Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                DIRECTOR MODE DECISION TREE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  START: You have a task for Claude                              │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────┐                                        │
│  │ Is the outcome      │                                        │
│  │ clearly defined?    │                                        │
│  └─────────┬───────────┘                                        │
│       YES  │  NO → Define the goal first                        │
│            ▼                                                    │
│  ┌─────────────────────┐                                        │
│  │ Is context in       │                                        │
│  │ CLAUDE.md?          │                                        │
│  └─────────┬───────────┘                                        │
│       YES  │  NO → Add to CLAUDE.md                             │
│            ▼                                                    │
│  ┌─────────────────────┐                                        │
│  │ Can it run in       │                                        │
│  │ parallel?           │                                        │
│  └─────────┬───────────┘                                        │
│       YES  │  NO → Single agent is fine                         │
│            ▼                                                    │
│  ╔═════════════════════╗                                        │
│  ║ USE DIRECTOR MODE:  ║                                        │
│  ║                     ║                                        │
│  ║ 1. Give clear goal  ║                                        │
│  ║ 2. Let Claude plan  ║                                        │
│  ║ 3. Review results   ║                                        │
│  ╚═════════════════════╝                                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ANTI-PATTERNS TO AVOID:                                 │    │
│  │ ✗ "Can you help me..."  → "Implement X"                 │    │
│  │ ✗ Step-by-step micro    → Outcome-focused               │    │
│  │ ✗ Watching every step   → Review at completion          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Parallel Agents Cheat Sheet

```
┌─────────────────────────────────────────────────────────────────┐
│                  PARALLEL AGENTS CHEAT SHEET                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WHEN TO USE PARALLEL AGENTS:                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ ✓ Exploring codebase    │ ✓ Bug investigation         │     │
│  │ ✓ Code review           │ ✓ Feature research          │     │
│  │ ✓ Multiple file search  │ ✓ Architecture analysis     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  WHEN NOT TO USE:                                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ ✗ Sequential dependencies (A must finish before B)     │     │
│  │ ✗ Single file edits                                    │     │
│  │ ✗ Simple lookups                                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  AGENT TYPES:                                                   │
│  ┌──────────────┬───────────────────────────────────────┐       │
│  │ Explore      │ Codebase structure, find files        │       │
│  │ Grep         │ Search for patterns/text              │       │
│  │ Read         │ Examine specific files                │       │
│  │ Bash         │ Run commands, check git               │       │
│  └──────────────┴───────────────────────────────────────┘       │
│                                                                 │
│  EFFICIENCY MATH:                                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Sequential: 5 tasks × 5 sec = 25 seconds              │     │
│  │  Parallel:   5 tasks at once = 5 seconds               │     │
│  │                                                        │     │
│  │  SPEEDUP: 5x for independent tasks                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  EXAMPLE PARALLEL PATTERN:                                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  "Investigate the authentication bug"                  │     │
│  │                                                        │     │
│  │  Agent 1: Explore auth module structure                │     │
│  │  Agent 2: Grep for "login" and "session"               │     │
│  │  Agent 3: Read auth middleware                         │     │
│  │  Agent 4: Check recent auth commits                    │     │
│  │  Agent 5: Search for error handling                    │     │
│  │                                                        │     │
│  │  → All complete in ~5 seconds                          │     │
│  │  → Results synthesized automatically                   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Bug Hunting Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                   BUG HUNTING WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. DESCRIBE CLEARLY                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  ✗ Bad:  "Login is broken"                             │     │
│  │  ✓ Good: "Users logged out after 15 min, expected:     │     │
│  │          session refresh while active"                 │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  2. INCLUDE CONTEXT                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  □ Error message (exact text)                          │     │
│  │  □ Steps to reproduce                                  │     │
│  │  □ Expected vs Actual behavior                         │     │
│  │  □ When it started (commit? deploy?)                   │     │
│  │  □ What you've tried                                   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  3. LET CLAUDE INVESTIGATE                                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Claude launches parallel agents:                      │     │
│  │  → Search for error/related code                       │     │
│  │  → Check recent changes                                │     │
│  │  → Review tests                                        │     │
│  │  → Analyze patterns                                    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  4. REVIEW & APPROVE                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Claude: "Found issue in /lib/auth.ts:42..."           │     │
│  │  You: "Fix it"                                         │     │
│  │  Claude: [implements fix + tests + commit]             │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  TYPICAL TIME: 2-5 minutes                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Feature Development Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                FEATURE DEVELOPMENT WORKFLOW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 1: DEFINE COMPLETELY                                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Include:                                              │     │
│  │  □ What it does (user story)                           │     │
│  │  □ UI requirements                                     │     │
│  │  □ API requirements                                    │     │
│  │  □ Edge cases                                          │     │
│  │  □ Out of scope                                        │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  STEP 2: LET CLAUDE ANALYZE                                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Claude researches (parallel):                         │     │
│  │  → Existing patterns                                   │     │
│  │  → Related code                                        │     │
│  │  → API conventions                                     │     │
│  │  → Test patterns                                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  STEP 3: REVIEW PLAN                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Claude proposes:                                      │     │
│  │  - Database changes                                    │     │
│  │  - New files                                           │     │
│  │  - Modified files                                      │     │
│  │  - Tests                                               │     │
│  │                                                        │     │
│  │  You: "Proceed" or "Adjust X"                          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  STEP 4: IMPLEMENT & REVIEW                                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Claude implements everything at once:                 │     │
│  │  ✓ All files created/modified                          │     │
│  │  ✓ Tests written                                       │     │
│  │  ✓ Tests passing                                       │     │
│  │  → Ready for your review                               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  ✗ DON'T: Implement incrementally (button → handler → API)     │
│  ✓ DO: Implement completely in one go                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Command Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                   COMMAND QUICK REFERENCE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  EFFECTIVE COMMANDS:                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  "Implement X with Y constraints"                      │     │
│  │  "Fix the bug in [location]"                           │     │
│  │  "Refactor X to use Y pattern"                         │     │
│  │  "Add tests for X with edge cases"                     │     │
│  │  "Investigate why X is happening"                      │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  INEFFECTIVE COMMANDS:                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  "Can you help me with..."        → Be direct          │     │
│  │  "I was thinking maybe..."        → State clearly      │     │
│  │  "First read X, then read Y..."   → Let Claude decide  │     │
│  │  "What do you think about..."     → Give direction     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  POWER PHRASES:                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  "following our existing patterns"                     │     │
│  │  "with full test coverage"                             │     │
│  │  "matching the project style"                          │     │
│  │  "including error handling"                            │     │
│  │  "using parallel agents"                               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

Back to [README](../README.md)
