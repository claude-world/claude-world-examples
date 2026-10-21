# Changelog

All notable changes to claude-world-examples will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-10-21

Every page brought up to current Claude Code (2.1.x, checked against 2.1.305), the Claude 5.5 models, and `anthropics/claude-code-action@v1`.

### Added
- `templates/github-actions-suite/claude.yml` (Claude Code answers `@claude` in issues and PRs) and `claude-code-review.yml` (automated PR review with the official code-review plugin), both on `anthropics/claude-code-action@v1`
- Claude Code GitHub Action section in the GitHub Actions automation example (EN and zh-TW)
- Validate workflow: yamllint and actionlint (with shellcheck) for the workflow templates, a checker that parses every `json`/`yaml` code block and lints complete workflows embedded in Markdown, and a lychee link check (also weekly)
- `SECURITY.md` with private reporting instructions, and a Dependabot config for this repository's own actions
- Built-in memory (CLAUDE.md, `.claude/rules/`, auto memory), plugins, skills, `AGENTS.md`, and permission rules where the pages discuss them

### Changed
- Model references: Opus/Sonnet 4.6 and Haiku 4.5 → Opus 5.5, Sonnet 5.5, Haiku 5.5 (Fable 5.1 noted where relevant); API examples pick `claude-haiku-5-5` for short, high-volume tasks and `claude-sonnet-5-5` for long-form writing
- API examples read the `text` blocks of a response instead of `content[0]` (current models return a thinking block first), drop sampling parameters, and leave `max_tokens` headroom for thinking
- Hooks docs rewritten to the current schema: the full event list, parallel execution, the `if` field, `onFailure: "continue" | "block"`, stdin JSON, exit-code and JSON decisions, correct environment variables
- MCP docs: correct scopes (`local`, `project` in `.mcp.json`, `user` in `~/.claude.json`), current server packages and official remote servers, `"type": "http"` entries, MCP tool search
- Subagent docs use the `Agent` tool (formerly `Task`), separate built-in agents (Explore, Plan, general-purpose) from custom ones, and note that Explore uses the main model
- Extended thinking guide rewritten around effort levels (`/effort`, `--effort`, frontmatter `effort`) and `ultrathink`
- Install instructions use the native installer (`curl -fsSL https://claude.ai/install.sh | bash`); npm install is deprecated upstream
- Workflow templates and examples: `actions/checkout@v7`, `actions/setup-node@v7`, and other current action majors; Node 24; least-privilege `permissions:`; untrusted values passed through `env:`
- The social-post template now posts to X only (the owner's change); the suite README matches
- Both READMEs refreshed (version, targets, install, model table, quality checks)

### Fixed
- Every API example and template used `claude-sonnet-4-20250514`, which was retired on 2026-06-15 and now fails
- `onFailure: "warn"`/`"ignore"`, `$CLAUDE_FILE_PATH`, and other hook fields and variables that never existed
- MCP scopes documented as `settings.json` files, nonexistent packages (`@modelcontextprotocol/server-git`, `server-sqlite`, `server-mongodb`, `context7-mcp`), deprecated ones (`server-github`, `server-postgres`), and the nonexistent `claude mcp status`
- Workflow bugs: an invalid `if:` expression and an invalid `toBase64()` call, release text interpolated into shell scripts, generated text spliced into a `python3 -c` string, an access token in a URL, ignored `workflow_dispatch` inputs, Resend batch errors that were never detected, and batches over Resend's 100-email limit
- Invalid JSON in code blocks (comments, duplicate keys) and broken relative links in the zh-TW pages
- Dead external links (OWASP API Security, GDPR email marketing, feed validators)

---

## [1.2.0] - 2026-03-14

Documentation maintenance and version updates.

### Changed
- Bumped version badge and timestamps to v1.2.0

---

## [1.1.0] - 2026-03-13

### Added
- Trend Pulse MCP integration examples (`examples/trend-pulse/`)
  - Basic trending queries with `get_trending` and `search_trends`
  - Content brief generation from trending signals
- CF Browser integration examples (`examples/cf-browser/`)
  - Screenshot capture and page inspection
  - JavaScript-rendered page scraping
- 5 new documentation examples + 2 new guides (designing agents, designing skills)
- GitHub Actions automation suite template

### Changed
- Updated model references: Opus/Sonnet 4.5 → 4.6

### Fixed
- Light mode text visibility in React component examples

---

## [1.0.0] - 2026-01-13

First official release, synced with [claude-world.com v1.0.0](https://claude-world.com).

**🚀 從零到上線：48 小時內完成**

This examples repository accompanies the Claude World website, providing practical code examples and templates for Claude Code users.

### Content

**Concepts** (8 files)
- Director Mode Basics
- CLAUDE.md Principles
- CLAUDE.md Anti-Patterns
- Hooks Basics
- MCP Basics
- Memory System
- Parallel Agents
- Multi-AI Workflow

**Examples** (6 files)
- Simple CLAUDE.md
- Bug Hunting Pattern
- Feature Development
- Refactoring Patterns
- Hooks Patterns
- MCP Setup

**Guides** (6 files)
- Agents Guide
- Extended Thinking
- Quick Reference Cards
- Production Readiness
- Security Best Practices
- Specification-Driven Development

**Templates** (1 file)
- CLAUDE.md by Framework (React, Next.js, Python, Go, etc.)

### Links

- Website: https://claude-world.com
- Discord: https://discord.gg/rBtHzSD288

---

## Versioning

This repo follows the main website versioning:
- When claude-world.com releases a new version, this repo syncs with matching content
- Tag format: `vX.Y.Z` matching website version
