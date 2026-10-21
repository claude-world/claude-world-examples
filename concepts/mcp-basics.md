# MCP Basics

> Model Context Protocol (MCP) extends Claude Code's capabilities by connecting to external tools, databases, and services.

## What is MCP?

MCP is an open standard for connecting AI applications to external systems. Each MCP server gives Claude new tools beyond its built-in ones:

- **Access external data sources** (databases, APIs, file systems)
- **Execute specialized tools** (Git, package managers, cloud services)
- **Maintain persistent context** (memory, knowledge graphs)
- **Integrate with development tools** (IDEs, CI/CD, project management)

MCP servers are not Claude Code's plugin system: a [plugin](https://code.claude.com/docs/en/plugins) is a package that can bundle MCP servers together with skills, subagents, and hooks.

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

Use the `claude mcp` CLI (or `/mcp` inside a session):

```bash
# Remote server over HTTP (recommended for hosted services)
claude mcp add --transport http <name> <url>

# Local stdio server: everything after -- is the command that starts it
claude mcp add [--scope <scope>] <name> [-e KEY=value] -- <command> [args...]

# Scopes:
# --scope local    → ~/.claude.json, this project only, private (default)
# --scope project  → .mcp.json in the repo root, shared with your team
# --scope user     → ~/.claude.json, all your projects

# Environment variables use the -e flag:
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.jsonl -- npx -y @modelcontextprotocol/server-memory
```

> **Note:** `-e` (`--env`) sets environment variables for the server and accepts several `KEY=value` pairs. Keep the server name before `-e`, as above: a name placed right after `-e` would be read as another pair. The SSE transport is deprecated; use `--transport http`.

## Essential MCP Servers

### 1. Filesystem Access

```bash
claude mcp add --scope project filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem .
```

**Capabilities:** Read/write files, create directories, list contents, file search. Claude Code's built-in Read, Edit, Glob, and Grep tools already cover the project directory, so add this server only for directories outside it.

### 2. Memory (Knowledge Graph)

```bash
# IMPORTANT: Always use MEMORY_FILE_PATH for project isolation
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

**Capabilities:** An explicit knowledge graph (entities, relations, observations) stored in a JSONL file and searchable across sessions. Claude Code already has built-in memory (CLAUDE.md and auto memory); see [Memory System](./memory-system.md) for when the graph is worth adding.

**Warning:** Without `MEMORY_FILE_PATH`, all projects share the same memory!

### 3. Git Operations

```bash
# The reference Git server is a Python package; uvx runs it without installing
claude mcp add --scope project git \
  -- uvx mcp-server-git --repository .
```

**Capabilities:** Git status, log, diff, branch operations, file blame

### 4. GitHub Integration

```bash
# GitHub's official remote server (the old @modelcontextprotocol/server-github is deprecated)
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"
```

**Capabilities:** Issues, PRs, repository management, code search, Actions

### 5. Sequential Thinking

```bash
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

**Capabilities:** Structured reasoning, multi-step analysis, complex problem decomposition

### 6. Context7 (Live Documentation)

```bash
# Remote server; get an API key at context7.com (or run: npx ctx7 setup --claude)
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"
```

**Capabilities:** Real-time official documentation, up-to-date library references

## Database MCP Servers

The original reference servers for PostgreSQL and SQLite have been archived. Prefer a maintained server from your database vendor:

### Supabase (PostgreSQL)

```bash
# Official remote server; authenticate with /mcp after adding it
claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<project-ref>&read_only=true"
```

### MongoDB

```bash
# Official MongoDB server, read-only
claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017/db" \
  -- npx -y mongodb-mcp-server --readOnly
```

Keep database credentials out of `.mcp.json`: use the local scope, as above, or reference an environment variable such as `${DATABASE_URL}` in a shared config.

## MCP Scope Hierarchy

Where a server is defined decides who gets it:

```
┌─────────────────────────────────────────────┐
│  Managed (organization)                      │
│  Location: managed-mcp.json or managed       │
│            settings (IT controls)            │
├─────────────────────────────────────────────┤
│  Local scope (default)                       │
│  Location: ~/.claude.json, under this        │
│            project's path                    │
│  Use: Personal or credentialed servers       │
├─────────────────────────────────────────────┤
│  Project scope                               │
│  Location: .mcp.json in the repo root        │
│  Use: Shared servers (committed to git)      │
├─────────────────────────────────────────────┤
│  User scope                                  │
│  Location: ~/.claude.json (top level)        │
│  Use: Your servers for every project         │
└─────────────────────────────────────────────┘
```

> **Important:** MCP servers are never configured in `settings.json`. Use `claude mcp add --scope project` to create or update `.mcp.json`; Claude Code asks each user to approve project servers the first time.

**Priority** when the same name is defined twice: Local > Project > User > plugin-provided servers > claude.ai connectors. An organization's managed servers take precedence over all of them.

## MCP Context Cost

MCP tool search is on by default: Claude Code loads a server's tool definitions on demand instead of sending every tool with every request, so a large server no longer costs thousands of tokens up front. Servers still add process overhead and tool names to the context, and every enabled server is another set of actions Claude can take.

**Best Practice:** Only enable MCP servers you actively use, and run `/context` to see what a session is spending its context on.

## Configuration Files

> **Important:** Project MCP servers go in `.mcp.json`, not `.claude/settings.json`. Always use `claude mcp add --scope project` to create correct configuration.

### Project MCP Configuration (.mcp.json)

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
        "MEMORY_FILE_PATH": "./.claude/memory.jsonl"
      }
    }
  }
}
```

A remote server needs `"type": "http"` next to its `url`; an entry with a `url` but no `type` is rejected. `${VAR}` and `${VAR:-default}` are expanded from your environment, so the file can be committed without secrets:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}"
      }
    }
  }
}
```

### User Configuration (~/.claude.json)

`claude mcp add --scope user` writes to the top-level `mcpServers` key of `~/.claude.json`, and `--scope local` writes under the current project's entry in the same file. Let the CLI manage this file rather than editing it by hand.

## MCP Management Commands

```bash
# List all MCP servers and their connection status
claude mcp list

# Show one server's configuration
claude mcp get <name>

# Add a new server
claude mcp add --scope project <name> -- <command>

# Remove a server
claude mcp remove --scope project <name>

# Inside a session: status, OAuth login, reconnect
/mcp

# Reset project MCP approval choices (troubleshooting)
claude mcp reset-project-choices
```

## Practical Examples

### Database Query

With a database MCP server enabled:

```
User: "Show me users who signed up in the last 7 days"

Claude: [Uses the database MCP server]
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

### Project Server Not Approved

Servers from `.mcp.json` wait for approval in interactive sessions. Approve them in the startup prompt or `/mcp`, list trusted ones in `enabledMcpjsonServers` in your settings, or set `enableAllProjectMcpServers: true` in `.claude/settings.local.json` for a repository you trust.

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
| Persistent storage | Memory MCP (knowledge graph) | CLAUDE.md, auto memory | No |
| Custom integrations | Extensible | Fixed | Via commands |
| Context cost | Loaded on demand (tool search) | Included | Minimal |

## Getting Started

**Today:**
1. Add one MCP server you need (GitHub, your database, or Context7)
2. Run `/mcp` to confirm it connected
3. Ask Claude to use it on a real task

**This week:**
1. Share team servers through `.mcp.json` (`--scope project`)
2. Keep credentials in the local scope or in `${VAR}` references
3. Add the memory server only if you want an explicit knowledge graph on top of CLAUDE.md and auto memory

---

*MCP transforms Claude Code from a standalone assistant into an integrated development platform.*

*Reference: [Model Context Protocol](https://modelcontextprotocol.io/) | [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)*
