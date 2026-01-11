# MCP Basics

> Model Context Protocol (MCP) extends Claude Code's capabilities by connecting to external tools, databases, and services.

## What is MCP?

MCP is Claude Code's plugin system. Think of MCP servers as plugins that give Claude new abilities beyond its base capabilities:

- **Access external data sources** (databases, APIs, file systems)
- **Execute specialized tools** (Git, package managers, cloud services)
- **Maintain persistent context** (memory, knowledge graphs)
- **Integrate with development tools** (IDEs, CI/CD, project management)

## MCP Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code CLI                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │                 MCP Client                       │    │
│  │  Manages connections to MCP servers             │    │
│  └─────────────────────────────────────────────────┘    │
│            │              │              │               │
│            ▼              ▼              ▼               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ MCP Server 1 │ │ MCP Server 2 │ │ MCP Server 3 │     │
│  │ (filesystem) │ │   (memory)   │ │    (git)     │     │
│  └──────────────┘ └──────────────┘ └──────────────┘     │
│            │              │              │               │
│            ▼              ▼              ▼               │
│      Local Files    Knowledge     Git Repository        │
│                      Graph                               │
└─────────────────────────────────────────────────────────┘
```

## Adding MCP Servers

Always use the official CLI method:

```bash
# Basic syntax
claude mcp add --scope <scope> <name> [options] -- <command>

# Scopes:
# --scope user     → ~/.claude/settings.json (all projects)
# --scope project  → .claude/settings.json (this project)

# Environment variables use -e flag:
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory
```

> **Note:** The `-e` flag sets environment variables for the MCP server. Multiple `-e` flags can be used for multiple variables.

## Essential MCP Servers

### 1. Filesystem Access

```bash
claude mcp add --scope project filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem .
```

**Capabilities:** Read/write files, create directories, list contents, file search

### 2. Memory (Knowledge Graph)

```bash
# IMPORTANT: Always use MEMORY_FILE_PATH for project isolation
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.json \
  -- npx -y @modelcontextprotocol/server-memory
```

**Capabilities:** Persistent knowledge storage, cross-session memory, semantic search

**Warning:** Without `MEMORY_FILE_PATH`, all projects share the same memory!

### 3. Git Operations

```bash
claude mcp add --scope project git \
  -- npx -y @modelcontextprotocol/server-git
```

**Capabilities:** Git status, log, diff, branch operations, file blame

### 4. GitHub Integration

```bash
claude mcp add --scope user github \
  -e GITHUB_TOKEN=<your-token> \
  -- npx -y @modelcontextprotocol/server-github
```

**Capabilities:** Issues, PRs, repository management, code search

### 5. Sequential Thinking

```bash
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

**Capabilities:** Structured reasoning, multi-step analysis, complex problem decomposition

### 6. Context7 (Live Documentation)

```bash
claude mcp add --scope user context7 \
  -- npx -y context7-mcp
```

**Capabilities:** Real-time official documentation, up-to-date library references

## Database MCP Servers

### PostgreSQL

```bash
claude mcp add --scope project postgres \
  -e DATABASE_URL="postgresql://user:pass@localhost:5432/db" \
  -- npx -y @modelcontextprotocol/server-postgres
```

### SQLite

```bash
claude mcp add --scope project sqlite \
  -e DATABASE_PATH="./data/app.db" \
  -- npx -y @modelcontextprotocol/server-sqlite
```

### MongoDB

```bash
claude mcp add --scope project mongodb \
  -e MONGODB_URI="mongodb://localhost:27017/db" \
  -- npx -y @modelcontextprotocol/server-mongodb
```

## MCP Scope Hierarchy

MCP servers follow Claude Code's four-layer hierarchy:

```
┌─────────────────────────────────────────────┐
│  Layer 1: Enterprise                         │
│  Location: /etc/claude-code/settings.json    │
│  Control: IT department (allowlist)          │
├─────────────────────────────────────────────┤
│  Layer 2: User Global                        │
│  Location: ~/.claude/settings.json           │
│  Use: Personal MCP servers (github, etc.)    │
├─────────────────────────────────────────────┤
│  Layer 3: Project                            │
│  Location: .claude/settings.json             │
│  Use: Project-specific (db, memory)          │
├─────────────────────────────────────────────┤
│  Layer 4: Project Local                      │
│  Location: .claude/settings.local.json       │
│  Use: Personal overrides (gitignored)        │
└─────────────────────────────────────────────┘
```

**Priority:** Local > Project > User > Enterprise

## MCP Context Cost

Each MCP server consumes context tokens. Be mindful:

| MCP Server | Approx. Tokens | Recommendation |
|------------|----------------|----------------|
| hubspot | ~1,800 | Small |
| netlify | ~2,000 | Small |
| figma | ~2,500 | Acceptable |
| notion | Optimized | Official |
| vercel | ~3,000 | Acceptable |
| stripe | ~4,000 | Medium |
| linear | ~6,200 | Large |
| atlassian | ~7,100 | Large |
| asana | ~12,800 | Too large |
| sentry | ~14,000 | Use sparingly |

**Best Practice:** Only enable MCP servers you actively use.

## Configuration Files

### Project Settings (.claude/settings.json)

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

## MCP Management Commands

```bash
# List all MCP servers
claude mcp list

# Add a new server
claude mcp add --scope project <name> -- <command>

# Remove a server
claude mcp remove --scope project <name>

# Check server status
claude mcp status

# Reset project MCP choices (troubleshooting)
claude mcp reset-project-choices
```

## Practical Examples

### Database Query

With postgres MCP enabled:

```
User: "Show me users who signed up in the last 7 days"

Claude: [Uses postgres MCP]
  → Queries: SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'
  → Returns formatted results
```

### Knowledge Persistence

With memory MCP enabled:

```
User: "Remember that we use Zod for all API validation"

Claude: [Uses memory MCP]
  → Creates entity: "API Validation"
  → Adds observation: "Use Zod for all API validation"
  → Available in future sessions
```

### GitHub Integration

With github MCP enabled:

```
User: "Create an issue for the login bug"

Claude: [Uses github MCP]
  → Creates issue with title, body, labels
  → Links to relevant code
```

## Troubleshooting

### Server Not Loading

```bash
# Check if server is registered
claude mcp list

# Reset and re-add
claude mcp reset-project-choices
claude mcp add --scope project <name> -- <command>
```

### Permission Issues

Ensure `enableAllProjectMcpServers: true` in project settings.

### Environment Variable Issues

Use `${VAR_NAME}` syntax for environment variables in config files:

```json
{
  "env": {
    "DATABASE_URL": "${DATABASE_URL}"
  }
}
```

## MCP vs Other Tools

| Feature | MCP | Built-in Tools | Hooks |
|---------|-----|----------------|-------|
| External data access | Primary | Limited | No |
| Persistent storage | Memory MCP | Session only | No |
| Custom integrations | Extensible | Fixed | Via commands |
| Context cost | Variable | Included | Minimal |

## Getting Started

**Today:**
1. Add filesystem and memory MCP to your project
2. Use `MEMORY_FILE_PATH` for project isolation
3. Save one important decision to memory

**This week:**
1. Add database MCP if applicable
2. Configure GitHub MCP for issue tracking
3. Explore memory commands (/memory-*)

---

*MCP transforms Claude Code from a standalone assistant into an integrated development platform.*

*Reference: [Model Context Protocol](https://modelcontextprotocol.io/) | [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code)*
