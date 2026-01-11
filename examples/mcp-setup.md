# MCP Setup Examples

> Complete setup recipes for common MCP configurations - copy, paste, and adapt for your projects.

## Quick Setup: Essential MCP Stack

The minimal MCP setup that works for most projects:

```bash
# 1. Filesystem access (project-scoped)
claude mcp add --scope project filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem .

# 2. Memory with project isolation (CRITICAL: use MEMORY_FILE_PATH)
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.json \
  -- npx -y @modelcontextprotocol/server-memory

# 3. Git operations
claude mcp add --scope project git \
  -- npx -y @modelcontextprotocol/server-git
```

**Result:** Claude can now read/write files, remember decisions across sessions, and manage Git operations.

---

## Setup by Project Type

### Web Application (Full Stack)

```bash
# Core stack
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory
claude mcp add --scope project git -- npx -y @modelcontextprotocol/server-git

# Database (choose one)
# PostgreSQL
claude mcp add --scope project postgres \
  -e DATABASE_URL="${DATABASE_URL}" \
  -- npx -y @modelcontextprotocol/server-postgres

# SQLite (for local development)
claude mcp add --scope project sqlite \
  -e DATABASE_PATH="./data/dev.db" \
  -- npx -y @modelcontextprotocol/server-sqlite

# GitHub for issue/PR management
claude mcp add --scope user github \
  -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-github

# Context7 for up-to-date docs
claude mcp add --scope user context7 \
  -- npx -y context7-mcp
```

### API-Only Backend

```bash
# Core
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory

# Database
claude mcp add --scope project postgres \
  -e DATABASE_URL="${DATABASE_URL}" \
  -- npx -y @modelcontextprotocol/server-postgres

# Sequential thinking for complex API design
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

### Static Site / Documentation

```bash
# Minimal setup
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory
claude mcp add --scope project git -- npx -y @modelcontextprotocol/server-git

# Context7 for referencing libraries
claude mcp add --scope user context7 \
  -- npx -y context7-mcp
```

### Data Science / ML

```bash
# Core
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory

# Databases
claude mcp add --scope project postgres \
  -e DATABASE_URL="${DATABASE_URL}" \
  -- npx -y @modelcontextprotocol/server-postgres

# Sequential thinking for analysis workflows
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## Complete Settings File Examples

### Project Settings (.claude/settings.json)

**Minimal Configuration:**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/memory.json"
      }
    }
  },
  "enableAllProjectMcpServers": true
}
```

**Full-Stack Application:**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/memory.json"
      }
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  },
  "enableAllProjectMcpServers": true
}
```

### User Settings (~/.claude/settings.json)

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "context7-mcp"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## Database Setup Patterns

### PostgreSQL with Supabase

```bash
# Using connection string from Supabase dashboard
claude mcp add --scope project postgres \
  -e DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  -- npx -y @modelcontextprotocol/server-postgres
```

**Or via settings.json:**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${SUPABASE_DATABASE_URL}"
      }
    }
  }
}
```

### PostgreSQL Local Development

```bash
claude mcp add --scope project postgres \
  -e DATABASE_URL="postgresql://localhost:5432/myapp_dev" \
  -- npx -y @modelcontextprotocol/server-postgres
```

### SQLite for Prototyping

```bash
# Auto-creates the database file if it doesn't exist
claude mcp add --scope project sqlite \
  -e DATABASE_PATH="./data/app.db" \
  -- npx -y @modelcontextprotocol/server-sqlite
```

### MongoDB

```bash
# Local
claude mcp add --scope project mongodb \
  -e MONGODB_URI="mongodb://localhost:27017/myapp" \
  -- npx -y @modelcontextprotocol/server-mongodb

# MongoDB Atlas
claude mcp add --scope project mongodb \
  -e MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/myapp" \
  -- npx -y @modelcontextprotocol/server-mongodb
```

---

## Cloud Service Integrations

### Vercel

```bash
claude mcp add --scope user vercel \
  -e VERCEL_TOKEN="${VERCEL_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-vercel
```

**Capabilities:** Deploy projects, manage domains, view deployments

### Cloudflare

```bash
claude mcp add --scope user cloudflare \
  -e CLOUDFLARE_API_TOKEN="${CF_API_TOKEN}" \
  -- npx -y @anthropic-ai/mcp-server-cloudflare
```

**Capabilities:** Workers, Pages, D1 database, R2 storage, DNS

### Netlify

```bash
claude mcp add --scope user netlify \
  -e NETLIFY_AUTH_TOKEN="${NETLIFY_AUTH_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-netlify
```

**Capabilities:** Deploy, forms, functions, environment variables

---

## Team/Collaboration MCP

### Linear (Project Management)

```bash
claude mcp add --scope user linear \
  -e LINEAR_API_KEY="${LINEAR_API_KEY}" \
  -- npx -y @modelcontextprotocol/server-linear
```

**Warning:** ~6,200 tokens - use sparingly

### Notion

```bash
claude mcp add --scope user notion \
  -e NOTION_TOKEN="${NOTION_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-notion
```

**Note:** Official Notion MCP is optimized for lower token usage

### Slack

```bash
claude mcp add --scope user slack \
  -e SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-slack
```

---

## Memory Isolation Patterns

### Per-Project Memory (Recommended)

```bash
# Each project has its own memory file
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.json \
  -- npx -y @modelcontextprotocol/server-memory
```

**Result:** Memory is committed with project, shared among team

### User-Global Memory

```bash
# Single memory across all projects (personal knowledge)
claude mcp add --scope user memory \
  -e MEMORY_FILE_PATH=~/.claude/global-memory.json \
  -- npx -y @modelcontextprotocol/server-memory
```

**Result:** Personal knowledge persists across all projects

### Hybrid Approach

```json
{
  "mcpServers": {
    "project-memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/project-memory.json"
      }
    }
  }
}
```

In user settings:
```json
{
  "mcpServers": {
    "personal-memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "~/.claude/personal-memory.json"
      }
    }
  }
}
```

---

## Environment Variable Management

### Using .env Files

Create `.env` in project root:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
SUPABASE_DATABASE_URL=postgresql://postgres:[pass]@db.xxx.supabase.co:5432/postgres
```

Reference in settings.json:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### Using Shell Environment

```bash
# Export first
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Then add MCP (picks up from environment)
claude mcp add --scope user github \
  -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-github
```

---

## Verification & Troubleshooting

### Verify Setup

```bash
# List all configured MCP servers
claude mcp list

# Check status
claude mcp status

# In Claude Code session
# Type: "What MCP servers are available?"
```

### Common Issues & Fixes

**MCP Not Loading:**

```bash
# Reset and re-add
claude mcp reset-project-choices
claude mcp add --scope project <name> -- <command>
```

**Permission Denied:**

Ensure in `.claude/settings.json`:
```json
{
  "enableAllProjectMcpServers": true
}
```

**Environment Variables Not Working:**

1. Check `.env` file exists and has correct values
2. Ensure `${VAR}` syntax (not `$VAR`)
3. Restart Claude Code after changes

**Database Connection Failed:**

```bash
# Test connection outside Claude first
psql $DATABASE_URL

# Check if port is accessible
nc -zv localhost 5432
```

---

## Setup Checklist

### New Project Setup

- [ ] Add filesystem MCP
- [ ] Add memory MCP with `MEMORY_FILE_PATH`
- [ ] Add git MCP
- [ ] Add database MCP if applicable
- [ ] Run `claude mcp list` to verify
- [ ] Test with "What MCP servers are active?"

### Team Onboarding

- [ ] Document required MCP servers in README
- [ ] Create `.claude/settings.json` template
- [ ] Add `.env.example` with required variables
- [ ] Add `.claude/memory.json` to `.gitignore` OR commit (team preference)

---

## Quick Reference

| MCP | Scope | Use Case |
|-----|-------|----------|
| filesystem | project | File operations |
| memory | project | Project knowledge |
| git | project | Version control |
| postgres/sqlite/mongodb | project | Database access |
| github | user | Issues, PRs |
| context7 | user | Live documentation |
| sequential-thinking | user | Complex reasoning |
| vercel/cloudflare/netlify | user | Deployments |

---

*For MCP concepts and architecture, see [MCP Basics](../concepts/mcp-basics.md)*

*Reference: [MCP Official Registry](https://modelcontextprotocol.io/) | [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code)*
