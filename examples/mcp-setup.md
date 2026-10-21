# MCP Setup Examples

> Copy-paste MCP configurations for common project types and services.

## Quick Setup: Essential MCP Stack

```bash
# 1. GitHub: issues, PRs, Actions (GitHub's official remote server)
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"

# 2. Context7: up-to-date library documentation
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"

# 3. Optional: a project knowledge graph (CRITICAL: use MEMORY_FILE_PATH)
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

Claude Code's built-in tools already read and edit project files and run `git`, and its built-in memory (CLAUDE.md plus auto memory) persists across sessions. Add filesystem, Git, or memory servers only when you need more: directories outside the project, structured Git tools, or an explicit knowledge graph.

Verify with `claude mcp list`, or run `/mcp` inside a session to see status and finish OAuth sign-in.

---

## Setup by Project Type

### Web Application (Full Stack)

```bash
# Database (choose one)
# Supabase / PostgreSQL (official remote server, read-only)
claude mcp add --scope project --transport http supabase \
  "https://mcp.supabase.com/mcp?project_ref=<project-ref>&read_only=true"

# Self-hosted PostgreSQL (Postgres MCP Pro, read-only mode)
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://user:pass@localhost:5432/myapp" \
  -- uvx postgres-mcp --access-mode=restricted

# Browser automation for UI testing
claude mcp add --scope project playwright -- npx -y @playwright/mcp@latest

# GitHub for issue/PR management
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"

# Context7 for up-to-date docs
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"
```

### API-Only Backend

```bash
# Database
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://user:pass@localhost:5432/api" \
  -- uvx postgres-mcp --access-mode=restricted

# Error monitoring
claude mcp add --scope user --transport http sentry https://mcp.sentry.dev/mcp

# Sequential thinking for complex API design
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

### Static Site / Documentation

```bash
# Minimal setup: built-in tools cover the files; add docs lookup
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"

# Optional: structured Git history tools
claude mcp add --scope project git -- uvx mcp-server-git --repository .
```

### Data Science / ML

```bash
# Databases
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://user:pass@localhost:5432/analytics" \
  -- uvx postgres-mcp --access-mode=restricted

claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017/analytics" \
  -- npx -y mongodb-mcp-server --readOnly

# Sequential thinking for analysis workflows
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## Complete Configuration Examples

MCP servers live in `.mcp.json` (project scope) or `~/.claude.json` (local and user scope), never in `settings.json`. Settings files control approvals and permissions for those servers.

### Project Servers (.mcp.json)

`claude mcp add --scope project` writes this file; commit it so the team shares the servers:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/memory.jsonl"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=${SUPABASE_PROJECT_REF}&read_only=true"
    }
  }
}
```

### Project Settings (.claude/settings.json)

Pre-approve the project's servers and set tool permissions. `mcp__<server>__*` matches every tool from a server:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "enabledMcpjsonServers": ["memory", "playwright", "supabase"],
  "permissions": {
    "allow": ["mcp__memory__*", "mcp__context7__*"],
    "ask": ["mcp__supabase__*"]
  }
}
```

### User Servers (~/.claude.json)

`~/.claude.json` also holds other Claude Code state, so add user servers with the CLI instead of editing the file:

```bash
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## Database Setup Patterns

The original reference servers for PostgreSQL and SQLite (`@modelcontextprotocol/server-postgres` and `server-sqlite`) are archived. Use a maintained server instead.

### PostgreSQL with Supabase

```bash
# Official Supabase server; sign in through /mcp after adding it
claude mcp add --scope project --transport http supabase \
  "https://mcp.supabase.com/mcp?project_ref=<project-ref>&read_only=true"
```

**Or in `.mcp.json`:**

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=${SUPABASE_PROJECT_REF}&read_only=true"
    }
  }
}
```

### PostgreSQL Local Development

```bash
# Postgres MCP Pro; restricted mode runs read-only transactions
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://postgres:postgres@localhost:5432/myapp_dev" \
  -- uvx postgres-mcp --access-mode=restricted
```

### SQLite for Prototyping

There is no maintained official SQLite server. For prototypes, let Claude use the `sqlite3` CLI through Bash, and allow it with a permission rule such as `Bash(sqlite3 ./data/app.db *)`.

### MongoDB

```bash
# Local (MongoDB's official server)
claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017/myapp" \
  -- npx -y mongodb-mcp-server --readOnly

# MongoDB Atlas
claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb+srv://user:pass@cluster.mongodb.net/myapp" \
  -- npx -y mongodb-mcp-server --readOnly
```

---

## Cloud Service Integrations

These are the providers' official remote servers. After adding one, run `/mcp` to sign in with OAuth.

### Vercel

```bash
claude mcp add --scope user --transport http vercel https://mcp.vercel.com
```

**Capabilities:** Deployments, projects, logs, documentation search

### Cloudflare

```bash
# Workers, KV, R2, and D1 bindings
claude mcp add --scope user --transport http cloudflare-bindings https://bindings.mcp.cloudflare.com/mcp

# Cloudflare documentation (no sign-in needed)
claude mcp add --scope user --transport http cloudflare-docs https://docs.mcp.cloudflare.com/mcp
```

**Capabilities:** Workers, Pages, D1 database, R2 storage, documentation

### Netlify

```bash
claude mcp add --scope user netlify -- npx -y @netlify/mcp
```

**Capabilities:** Deploy, forms, functions, environment variables

---

## Team/Collaboration MCP

### Linear (Project Management)

```bash
claude mcp add --scope user --transport http linear https://mcp.linear.app/mcp
```

### Notion

```bash
claude mcp add --scope user --transport http notion https://mcp.notion.com/mcp
```

### Slack

```bash
claude mcp add --scope user --transport http slack https://mcp.slack.com/mcp
```

With MCP tool search on by default, Claude Code loads each server's tool definitions only when needed, so even large servers no longer fill the context up front. Still enable only the servers you use.

---

## Memory Isolation Patterns

Claude Code's built-in auto memory is already per repository (`~/.claude/projects/<project>/memory/`). These patterns apply when you add the memory MCP server.

### Per-Project Memory (Recommended)

```bash
# Each project has its own memory file
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

### User-Global Memory

```bash
# Single memory across all projects (personal knowledge)
claude mcp add --scope user memory \
  -e MEMORY_FILE_PATH="$HOME/.claude/global-memory.jsonl" \
  -- npx -y @modelcontextprotocol/server-memory
```

### Hybrid Approach

Project `.mcp.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/project-memory.jsonl"
      }
    }
  }
}
```

Personal server, added once at user scope:

```bash
claude mcp add --scope user personal-memory \
  -e MEMORY_FILE_PATH="$HOME/.claude/personal-memory.jsonl" \
  -- npx -y @modelcontextprotocol/server-memory
```

---

## Environment Variable Management

### Using .env Files

Create `.env` in project root (and add it to `.gitignore`):

```env
DATABASE_URI=postgresql://user:pass@localhost:5432/myapp
GITHUB_PAT=github_pat_xxxxxxxxxxxx
SUPABASE_PROJECT_REF=abcdefghijklmnop
```

Reference the variables in `.mcp.json`. Claude Code expands `${VAR}` and `${VAR:-default}` from the environment it was started in, so load `.env` into your shell first (for example with `direnv`, or `set -a; source .env; set +a`):

```json
{
  "mcpServers": {
    "postgres": {
      "command": "uvx",
      "args": ["postgres-mcp", "--access-mode=restricted"],
      "env": {
        "DATABASE_URI": "${DATABASE_URI}"
      }
    }
  }
}
```

### Using Shell Environment

```bash
# Export first
export GITHUB_PAT="github_pat_xxxxxxxxxxxx"

# Then add the server; the shell expands $GITHUB_PAT before the CLI saves it
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer $GITHUB_PAT"
```

---

## Verification & Troubleshooting

### Verify Setup

```bash
# List all configured MCP servers with their connection status
claude mcp list

# Show one server's configuration
claude mcp get github

# In Claude Code session
# Run /mcp to check status, sign in, or reconnect
```

### Common Issues & Fixes

**MCP Not Loading:**

```bash
# Reset and re-add
claude mcp reset-project-choices
claude mcp add --scope project <name> -- <command>
```

**Project Server Waiting for Approval:**

Approve it in the startup prompt or `/mcp`, or list it in `.claude/settings.json`:
```json
{
  "enabledMcpjsonServers": ["memory", "supabase"]
}
```

**Environment Variables Not Working:**

1. Check the variable is exported in the shell that starts `claude` (`echo $DATABASE_URI`)
2. Ensure `${VAR}` syntax (not `$VAR`) inside `.mcp.json`
3. Restart Claude Code after changes

**Database Connection Failed:**

```bash
# Test connection outside Claude first
psql "$DATABASE_URI"

# Check if port is accessible
nc -zv localhost 5432
```

---

## Setup Checklist

### New Project Setup

- [ ] Add the GitHub and Context7 servers (user scope)
- [ ] Add a database server if applicable (local scope for credentials)
- [ ] Add the memory server with `MEMORY_FILE_PATH` if you want a knowledge graph
- [ ] Run `claude mcp list` to verify
- [ ] Run `/mcp` in a session to sign in to OAuth servers

### Team Onboarding

- [ ] Document required MCP servers in README
- [ ] Commit `.mcp.json` with `${VAR}` references instead of secrets
- [ ] Add `.env.example` with required variables
- [ ] Add `.claude/memory.jsonl` to `.gitignore` OR commit (team preference)

---

## Quick Reference

| MCP | Scope | Use Case |
|-----|-------|----------|
| github | user | Issues, PRs, Actions |
| context7 | user | Live documentation |
| supabase / postgres / mongodb | project or local | Database access |
| playwright | project | Browser automation and UI testing |
| memory | project | Explicit knowledge graph |
| git | project | Structured Git tools (optional) |
| sequential-thinking | user | Complex reasoning |
| vercel / cloudflare / netlify | user | Deployments |
| linear / notion / slack / sentry | user | Team tools |

---

*For MCP concepts and architecture, see [MCP Basics](../concepts/mcp-basics.md)*

*Reference: [Model Context Protocol](https://modelcontextprotocol.io/) | [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)*
