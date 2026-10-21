# Quick Reference Cards

> One-page visual guides for fast lookup.

## CLAUDE.md Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE.md CHECKLIST                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Start with /init; edit with /memory or ask Claude              │
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
│  □ BOUNDARIES (enforced in .claude/settings.json, not here)     │
│    ├── allow (no prompt): _______________                       │
│    ├── ask (always confirm): _______________                    │
│    └── deny (never): _______________                            │
│                                                                 │
│  □ PATTERNS                                                     │
│    ├── API response format                                      │
│    ├── Error handling                                           │
│    └── Component structure                                      │
│                                                                 │
│  □ HEALTH CHECK                                                 │
│    ├── Last updated: _______________                            │
│    ├── Under ~200 lines? □ Yes □ No                             │
│    ├── Procedures → skills; path-specific → .claude/rules/      │
│    └── Audit: /doctor prompt-audit; loaded? /context            │
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
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ TOOLING (community plugin, not built in):               │    │
│  │ /plugin marketplace add claude-world/director-mode-lite │    │
│  │ /plugin install director-mode-lite@director-mode-lite   │    │
│  │ → adds /workflow, /focus-problem, /smart-commit         │    │
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
│  │ ✓ Exploring codebase    │ ✓ Bug investigation          │     │
│  │ ✓ Code review           │ ✓ Feature research           │     │
│  │ ✓ Multiple file search  │ ✓ Architecture analysis      │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  WHEN NOT TO USE:                                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ ✗ Sequential dependencies (A must finish before B)     │     │
│  │ ✗ Single file edits                                    │     │
│  │ ✗ Simple lookups                                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  SUBAGENT TYPES (Agent tool, formerly Task):                    │
│  ┌─────────────────┬────────────────────────────────────┐       │
│  │ Explore         │ Read-only search (main model);     │       │
│  │                 │ quick / medium / very thorough     │       │
│  │ Plan            │ Research during plan mode          │       │
│  │ general-purpose │ Multi-step work, all tools         │       │
│  │ Your own        │ .claude/agents/<name>.md           │       │
│  └─────────────────┴────────────────────────────────────┘       │
│  (Grep, Read and Bash are tools these agents use)               │
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
│  │  → Run concurrently, each in its own context           │     │
│  │  → Results synthesized automatically                   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  CONTROLS: Ctrl+B backgrounds work; /tasks lists it;            │
│            Esc interrupts                                       │
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
│  │  Wrong turn? Esc Esc or /rewind restores a checkpoint  │     │
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
│  STEP 3: REVIEW PLAN (plan mode: Shift+Tab or /plan)            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Claude proposes:                                      │     │
│  │  - Database changes                                    │     │
│  │  - New files                                           │     │
│  │  - Modified files                                      │     │
│  │  - Tests                                               │     │
│  │                                                        │     │
│  │  You: "Proceed" or "Adjust X"                          │     │
│  │  Ctrl+G opens the plan in your editor                  │     │
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
│  ✗ DON'T: Implement incrementally (button → handler → API)      │
│  ✓ DO: Implement completely in one go                           │
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
│  │  "ultrathink" (deeper reasoning for one turn)          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Claude Code Essentials

```
┌─────────────────────────────────────────────────────────────────┐
│               CLAUDE CODE ESSENTIALS (2.1.x)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BUILT-IN COMMANDS:                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  /init     starter CLAUDE.md  │ /memory   memory files │     │
│  │  /model    switch model       │ /effort   depth        │     │
│  │  /plan     plan mode          │ /rewind   checkpoints  │     │
│  │  /context  context usage      │ /compact  summarize    │     │
│  │  /clear    fresh context      │ /resume   past session │     │
│  │  /review   review diff or PR  │ /tasks    background   │     │
│  │  /permissions  allow/ask/deny │ /hooks    view hooks   │     │
│  │  /mcp      MCP servers        │ /plugin   plugins      │     │
│  │  /skills   list skills        │ /usage    cost, limits │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  SHORTCUTS:                                                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Shift+Tab  cycle permission modes (incl. plan, auto)  │     │
│  │  Esc        interrupt     │ Esc Esc   rewind menu      │     │
│  │  Ctrl+B     background    │ Ctrl+O    transcript       │     │
│  │  Ctrl+R     history search│ Ctrl+G    external editor  │     │
│  │  Option+P / Alt+P  switch model;  ! shell;  @ file     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  FILES:                                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  CLAUDE.md or .claude/CLAUDE.md project, shared        │     │
│  │  CLAUDE.local.md                personal, gitignore it │     │
│  │  ~/.claude/CLAUDE.md            all your projects      │     │
│  │  .claude/rules/*.md             modular, path rules    │     │
│  │  .claude/settings.json          permissions, hooks, env│     │
│  │  .claude/settings.local.json    personal overrides     │     │
│  │  ~/.claude/settings.json        user settings          │     │
│  │  .claude/skills/<name>/SKILL.md skills → /<name>       │     │
│  │  .claude/agents/<name>.md       subagents              │     │
│  │  .mcp.json                      project MCP servers    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  MCP SCOPES (claude mcp add --scope ...):                       │
│    local (default) → ~/.claude.json, this project, private      │
│    project         → .mcp.json, shared via git                  │
│    user            → ~/.claude.json, all your projects          │
│                                                                 │
│  HOOKS ("hooks" key in settings.json; view with /hooks):        │
│    PreToolUse (exit 2 = block), PostToolUse, Stop,              │
│    UserPromptSubmit, SessionStart; input = JSON on stdin        │
│                                                                 │
│  THINKING: "ultrathink" in one prompt; /effort low to max       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

Back to [README](../README.md)
