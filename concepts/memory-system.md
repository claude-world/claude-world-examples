# Memory System Basics

> Build persistent project intelligence with Claude Code's built-in memory, and add the Memory MCP when you want an explicit knowledge graph - never lose context between sessions again.

## The Problem: Session Amnesia

Every Claude Code session starts fresh. Previous decisions, bug fixes, and architectural choices are forgotten:

```
Session 1: "We decided to use Redis for caching because..."
Session 2: "Why are we using Redis?"
Session 3: [Repeats same discussion]
```

This is **institutional memory failure**.

## Built-in Memory: CLAUDE.md and Auto Memory

Claude Code ships two memory layers, and both load at the start of every session:

| | CLAUDE.md files | Auto memory |
|---|---|---|
| **Who writes it** | You (or Claude, when you ask) | Claude, on its own |
| **What it holds** | Instructions: commands, conventions, architecture | Learnings: your preferences, corrections, project context |
| **Where** | `./CLAUDE.md`, `~/.claude/CLAUDE.md`, `.claude/rules/` | `~/.claude/projects/<project>/memory/` |
| **Loaded** | In full, every session | The first 200 lines (or 25KB) of the `MEMORY.md` index, then topic files on demand |

- Run `/memory` to open these files and to turn auto memory on or off.
- Say "remember that we use Zod for all API validation" and Claude can save it to auto memory. For a rule the whole team should follow, ask Claude to add it to CLAUDE.md instead.
- Subagents can keep their own memory with the `memory:` frontmatter field (`user`, `project`, or `local`).

For most projects this is enough. See [CLAUDE.md Principles](./claude-md-principles.md) for writing good instructions.

## Optional: The Memory MCP Knowledge Graph

Add the Memory MCP server when you want knowledge that is structured and queryable rather than prose: entities linked by relations, a graph the whole team shares through the repository, or more facts than a 200-line index can hold.

The Memory MCP creates a **persistent knowledge graph** that stores:

| Component | Description | Example |
|-----------|-------------|---------|
| **Entities** | Named concepts with type | `authentication_system` |
| **Observations** | Facts about entities | "Uses JWT tokens" |
| **Relations** | Connections between entities | `auth` → uses → `redis` |

```
┌──────────────────────────────────────────────────┐
│              Knowledge Graph                      │
│                                                  │
│  ┌─────────────────┐       ┌──────────────────┐  │
│  │ authentication  │──uses─▶│ redis_cache     │  │
│  │                 │       │                  │  │
│  │ Observations:   │       │ Observations:    │  │
│  │ • Uses JWT      │       │ • v7.2           │  │
│  │ • 24h TTL       │       │ • <1ms latency   │  │
│  └─────────────────┘       └──────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Quick Setup

### Step 1: Add Memory MCP

```bash
# CRITICAL: Use MEMORY_FILE_PATH for project isolation
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

**Why project isolation matters:**
- Without `MEMORY_FILE_PATH`, all projects share the same memory
- Each project should have its own knowledge graph
- Committed to repo = shared team knowledge

### Step 2: Verify

```bash
claude mcp list

# Should show:
# memory: npx -y @modelcontextprotocol/server-memory - ✓ Connected
```

### Step 3: Initialize

In Claude Code:

```
"Save initial project context to memory"
```

Claude creates entities for project, tech stack, and key decisions.

## Core Tools

The server gives Claude these tools. You don't call them yourself: ask in plain language and Claude picks the right one.

| Tool | Description |
|------|-------------|
| `create_entities` / `create_relations` | Save new knowledge to the graph |
| `add_observations` | Add facts to an existing entity |
| `search_nodes` | Search names, types, and observations |
| `open_nodes` / `read_graph` | Read specific entities or the whole graph |
| `delete_entities` / `delete_observations` / `delete_relations` | Remove stale knowledge |

The built-in `/memory` command manages CLAUDE.md and auto memory files, not this graph. Commands such as `/memory-save` or `/memory-audit` exist only if a plugin or your own skills add them.

### Ask in Natural Language

```
"Save this decision to memory: We chose PostgreSQL for JSONB support"

"What do we know about our caching strategy?"

"Update memory: Token TTL changed from 24h to 7 days"
```

## What to Store

### 1. Architecture Decisions (Most Important)

```
Entity: database_choice
Type: decision
Observations:
- "Selected PostgreSQL for JSONB support"
- "Considered MySQL but needed JSON queries"
- "Decision date: 2026-01-05"
```

**Why?** Prevents revisiting decided topics.

### 2. Bug Fixes

```
Entity: auth_timeout_bug
Type: bug_fix
Observations:
- "Issue: Users logged out after 5 minutes"
- "Root cause: Token refresh race condition"
- "Solution: Mutex around refresh"
- "PR: #234"
```

**Why?** Prevents reintroducing fixed bugs.

### 3. Design Patterns

```
Entity: error_handling_pattern
Type: pattern
Observations:
- "Use Result type for async operations"
- "Never throw in domain layer"
- "Log errors at boundary only"
```

**Why?** Ensures consistent implementation.

### 4. External Integrations

```
Entity: stripe_integration
Type: integration
Observations:
- "API version: 2024-11-20"
- "Webhook: /api/webhooks/stripe"
- "Using Stripe Checkout"
```

**Why?** Quick reference for integration details.

## Memory Patterns

### Pattern 1: Session Start Load

Begin each session by loading context:

```
"What do we know about the feature I'm working on?"
```

### Pattern 2: Immediate Recording

After decisions, save immediately:

```
"Save this decision to memory: We're using Redis for
session caching because it provides sub-millisecond
latency for 10K+ concurrent sessions."
```

### Pattern 3: Bug Context

When fixing bugs:

```
"Save this bug fix to memory: Login timeout was caused
by token refresh race condition. Fixed with mutex.
Files: auth/refresh.ts"
```

### Pattern 4: Monthly Audit

```
"Audit the memory graph: list stale, duplicate, or contradictory entries"
```

Then clean up:
```
"Clean up outdated observations about the old auth system"
```

## Knowledge Graph Structure

The server stores the graph as JSON Lines in `MEMORY_FILE_PATH`; `read_graph` returns it in this shape:

```json
{
  "entities": [
    {
      "name": "authentication_system",
      "entityType": "component",
      "observations": [
        "Uses JWT tokens for stateless auth",
        "Tokens expire after 24 hours",
        "Implemented in auth/ directory"
      ]
    }
  ],
  "relations": [
    {
      "from": "authentication_system",
      "to": "redis_cache",
      "relationType": "uses"
    }
  ]
}
```

## Storage Options

| Option | Path | Use Case |
|--------|------|----------|
| **Built-in auto memory** | `~/.claude/projects/<project>/memory/` | Personal learnings per repository (on by default, not shared) |
| **Project graph** (Recommended for teams) | `./.claude/memory.jsonl` | Team-shared, committed to repo |
| **User graph** | `~/.claude/memory.jsonl` | Personal patterns, cross-project |
| **Hybrid** | Both graphs | Project decisions + personal prefs |

## Memory vs CLAUDE.md

| Use CLAUDE.md For | Use Auto Memory For | Use the Memory MCP For |
|-------------------|---------------------|------------------------|
| Static policies and rules | Your preferences and corrections | Decisions & rationale as linked entities |
| Build and test commands | Context Claude learns as it works | Bug fixes & resolutions to query later |
| Project structure | Facts that change over time | Team knowledge shared through the repo |
| Workflow definitions | Personal, per-machine notes | Relations between components |

**Key difference:** CLAUDE.md is always loaded in full, so keep it under about 200 lines. Auto memory loads a short index and reads topic files when needed. The Memory MCP graph is queried on demand. None of them enforce anything; use permissions or hooks for rules that must hold.

## Best Practices

### 1. Save Immediately

```
"Save this decision to memory now before we forget the context."
```

### 2. Be Specific

❌ Bad: "Using PostgreSQL"

✅ Good: "Selected PostgreSQL for JSONB support needed for user preferences storage"

### 3. Include Context

Add the "why" not just the "what":

```
"Chose Redis over Memcached because we need data
structures (lists, sets) for session management"
```

### 4. Use Temporal Markers

```
Observations:
- "[2026-01-05] Initial choice: MySQL"
- "[2026-01-08] Migrated to PostgreSQL for JSONB"
```

### 5. Mark Confidence

```
Observations:
- "[CONFIRMED] Uses JWT for auth"
- "[ASSUMPTION] Token TTL is 24 hours (verify)"
- "[OUTDATED] Previous used session cookies"
```

## Troubleshooting

### Memory Not Persisting

1. Check `MEMORY_FILE_PATH` is set correctly
2. Verify file write permissions
3. Run `claude mcp list` to confirm MCP is active

### Search Not Finding Results

1. Search is a case-insensitive substring match on names, types, and observations, so try a shorter term
2. Use broader search terms
3. Check observations contain search terms

### Duplicate Entities

1. Ask Claude to audit the graph for duplicates
2. Merge duplicates: "Merge entity A and B"
3. Update relations to merged entity

## Integration with Workflows

### With /workflow

`/workflow` comes from the community [director-mode-lite](https://github.com/claude-world/director-mode-lite) plugin; any implementation request works the same way:

```
"Implement user profile editing based on our
existing patterns and decisions."

Claude:
→ Searches memory for patterns, conventions
→ Finds error handling pattern, API conventions
→ Implements following established patterns
```

### With Multi-Session Projects

```
Day 1: "We're building a payment system. Save the architecture."
Day 2: "Continue payment work. What did we decide yesterday?"
Day 3: "Finish payment integration. What's left?"
```

Memory provides continuity across all sessions.

## Getting Started Checklist

**Today:**
- [ ] Run `/memory` and check that auto memory is on
- [ ] Save one architecture decision (CLAUDE.md or the graph)
- [ ] Add the Memory MCP if you want a shared knowledge graph

**This week:**
- [ ] Build initial knowledge graph
- [ ] Save all major decisions
- [ ] Integrate with daily workflow

**This month:**
- [ ] Complete knowledge graph coverage
- [ ] Establish team conventions
- [ ] Schedule a regular memory audit

---

*Memory transforms Claude Code from a stateless tool to a knowledgeable partner. Build your knowledge graph, and every session starts with full context.*

*Related: [Memory System Guide](https://claude-world.com/articles/memory-system-guide) | [MCP Basics](./mcp-basics.md)*
