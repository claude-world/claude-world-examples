# Memory System Basics

> Build persistent project intelligence with the Memory MCP - never lose context between sessions again.

## The Problem: Session Amnesia

Every Claude Code session starts fresh. Previous decisions, bug fixes, and architectural choices are forgotten:

```
Session 1: "We decided to use Redis for caching because..."
Session 2: "Why are we using Redis?"
Session 3: [Repeats same discussion]
```

This is **institutional memory failure**.

## The Solution: Memory MCP

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
  -e MEMORY_FILE_PATH=./.claude/memory.json \
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
# memory (project) - @modelcontextprotocol/server-memory
```

### Step 3: Initialize

In Claude Code:

```
"Save initial project context to memory"
```

Claude creates entities for project, tech stack, and key decisions.

## Core Commands

| Command | Description |
|---------|-------------|
| `/memory-save` | Save knowledge to graph |
| `/memory-search` | Search stored knowledge |
| `/memory-list` | List all entities |
| `/memory-audit` | Find stale/duplicate entries |

### Natural Language Works Too

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
/memory-audit
```

Then clean up:
```
"Clean up outdated observations about the old auth system"
```

## Memory JSON Structure

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
| **Project** (Recommended) | `./.claude/memory.json` | Team-shared, committed to repo |
| **User** | `~/.claude/memory.json` | Personal patterns, cross-project |
| **Hybrid** | Both | Project decisions + personal prefs |

## Memory vs CLAUDE.md

| Use Memory For | Use CLAUDE.md For |
|----------------|-------------------|
| Decisions & rationale | Static policies |
| Bug fixes & resolutions | Tool configurations |
| Evolving patterns | Project structure |
| Session-to-session context | Workflow definitions |

**Key difference:** Memory is queryable and on-demand (low context cost). CLAUDE.md is always loaded (high context cost).

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

1. Entity names are case-sensitive
2. Use broader search terms
3. Check observations contain search terms

### Duplicate Entities

1. Run `/memory-audit`
2. Merge duplicates: "Merge entity A and B"
3. Update relations to merged entity

## Integration with Workflows

### With /workflow

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
- [ ] Add Memory MCP to your project
- [ ] Save one architecture decision
- [ ] Try `/memory-search`

**This week:**
- [ ] Build initial knowledge graph
- [ ] Save all major decisions
- [ ] Integrate with daily workflow

**This month:**
- [ ] Complete knowledge graph coverage
- [ ] Establish team conventions
- [ ] Schedule regular `/memory-audit`

---

*Memory transforms Claude Code from a stateless tool to a knowledgeable partner. Build your knowledge graph, and every session starts with full context.*

*Related: [Memory System Guide](https://claude-world.com/articles/memory-system-guide) | [MCP Basics](./mcp-basics.md)*
