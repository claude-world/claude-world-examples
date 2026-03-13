# Changelog

All notable changes to claude-world-examples will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
