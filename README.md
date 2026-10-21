# Claude World Examples

> Practical examples and best practices for mastering Claude Code - the official AI-powered CLI from Anthropic

[![Website](https://img.shields.io/badge/Website-claude--world.com-blue)](https://claude-world.com)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da)](https://discord.gg/rBtHzSD288)
[![Version](https://img.shields.io/badge/version-1.3.0-green)](https://github.com/claude-world/claude-world-examples/releases/tag/v1.3.0)
[![Validate](https://github.com/claude-world/claude-world-examples/actions/workflows/validate.yml/badge.svg)](https://github.com/claude-world/claude-world-examples/actions/workflows/validate.yml)

[繁體中文](./README.zh-TW.md)

---

**v1.3.0 (2026-10-21):** every concept, example, guide, and template is updated for Claude Code 2.1.x, the Claude 5.5 models, and `anthropics/claude-code-action@v1`, and CI now validates the code samples and links. See the [CHANGELOG](./CHANGELOG.md).

---

## What is Claude World?

Claude World is a community dedicated to helping developers master **Claude Code** - Anthropic's official CLI for AI-assisted software development. This repository is the companion to [claude-world.com](https://claude-world.com): the articles explain the ideas, and the files here are the copy-paste examples.

We focus on:
- **Director Mode** - A mindset shift from "hands-on developer" to "team director"
- **Efficient Workflows** - Parallel agents, minimal interruption, autonomous execution
- **Best Practices** - Battle-tested patterns from real production projects
- **Advanced Features** - Hooks, MCP, skills, subagents, memory, effort levels, and more

## What the Examples Target

| Area | Version |
|------|---------|
| Claude Code | 2.1.x (checked against 2.1.305) |
| Models | Claude Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.1 |
| GitHub Action | `anthropics/claude-code-action@v1` |
| Claude API | Messages API, `anthropic-version: 2023-06-01` |
| Workflow templates | Node.js 24, `actions/checkout@v7` |

Retired model IDs such as `claude-sonnet-4-20250514` no longer work; every example uses current IDs.

## Repository Structure

```
claude-world-examples/
├── concepts/           # Core concepts and mental models
├── examples/           # Practical code examples
├── guides/             # In-depth guides and tutorials
├── templates/          # Ready-to-use templates (CLAUDE.md, workflows)
└── case-studies/       # Real-world project case studies
```

Most pages have a Traditional Chinese translation in a `zh-TW/` folder next to them.

## Content Overview

### Core Concepts

| Concept | Description | Difficulty |
|---------|-------------|------------|
| [Director Mode Basics](./concepts/director-mode-basics.md) | The mindset shift that 10x your productivity | Beginner |
| [CLAUDE.md Principles](./concepts/claude-md-principles.md) | How to write effective project instructions | Beginner |
| [Hooks Basics](./concepts/hooks-basics.md) | Automated policies and guardrails | Beginner |
| [MCP Basics](./concepts/mcp-basics.md) | Extend Claude with external tools and databases | Beginner |
| [Memory System](./concepts/memory-system.md) | CLAUDE.md, auto memory, and the Memory MCP | Beginner |
| [CLAUDE.md Anti-Patterns](./concepts/claude-md-anti-patterns.md) | Common mistakes and how to fix them | Intermediate |
| [Parallel Agents](./concepts/parallel-agents.md) | Run subagents in parallel for faster results | Intermediate |
| [AI-Assisted Workflow](./concepts/ai-assisted-workflow.md) | Leverage Claude Code as a force multiplier | Intermediate |
| [Multi-AI Workflow](./concepts/multi-ai-workflow.md) | Coordinate Claude, Codex, and Gemini CLI | Advanced |

### Practical Examples

| Example | Description | Use Case |
|---------|-------------|----------|
| [Simple CLAUDE.md](./examples/simple-claude-md.md) | A minimal but effective CLAUDE.md template | Getting started |
| [Bug Hunting Pattern](./examples/bug-hunting.md) | Use parallel agents to find bugs fast | Debugging |
| [Feature Development](./examples/feature-development.md) | Structured approach to building features | Implementation |
| [Refactoring Patterns](./examples/refactoring-patterns.md) | Systematic code improvement with Claude | Code quality |
| [Hooks Patterns](./examples/hooks-patterns.md) | Production-ready hook configurations | Automation |
| [MCP Setup](./examples/mcp-setup.md) | Complete MCP configuration recipes | Integration |
| [Trend Pulse: Basic Trending](./examples/trend-pulse/basic-trending.md) | Query live topics with `get_trending` and `search_trends` | Research |
| [Trend Pulse: Content Brief](./examples/trend-pulse/content-brief.md) | Turn trending signals into a content brief | Content strategy |
| [CF Browser: Screenshot Capture](./examples/cf-browser/screenshot-capture.md) | Capture and inspect rendered pages with browser MCP tools | QA |
| [CF Browser: Page Scraping](./examples/cf-browser/page-scraping.md) | Scrape JavaScript-rendered pages through a browser session | Web data |
| [GitHub Actions Automation](./examples/github-actions-automation.md) | Claude API workflows and the Claude Code GitHub Action | CI/CD |
| [Multi-Language Astro](./examples/multi-language-astro.md) | Complete multi-language website setup | i18n |
| [Supabase + Cloudflare](./examples/supabase-cloudflare-integration.md) | Full-stack with free hosting and database | Full-stack |
| [Newsletter System](./examples/newsletter-system.md) | Complete multi-language newsletter architecture | Email |
| [Content Pipeline](./examples/content-pipeline.md) | Automated content generation and distribution | Automation |
| [Social Media Automation](./examples/social-media-automation.md) | X/Threads API with Claude-generated posts | Social |
| [RSS Feed Astro](./examples/rss-feed-astro.md) | Multi-language RSS feeds with Astro | Content |
| [React Components](./examples/react-components.md) | Common UI patterns for Claude Code projects | UI |
| [API Endpoint Patterns](./examples/api-endpoint-patterns.md) | Cloudflare Edge API design patterns | Backend |

### Guides

| Guide | Description | Time |
|-------|-------------|------|
| [Agents Guide](./guides/agents-guide.md) | Built-in and custom subagents, from Explore to your own | 25 min |
| [Extended Thinking](./guides/extended-thinking.md) | Effort levels, `ultrathink`, and when to reason deeper | 15 min |
| [Quick Reference Cards](./guides/quick-reference.md) | One-page visual guides for fast lookup | 5 min |
| [Production Readiness](./guides/production-readiness.md) | Checklist before shipping to production | 15 min |
| [Security Best Practices](./guides/security-best-practices.md) | Build secure applications and lock down Claude Code | 20 min |
| [Specification-Driven Development](./guides/specification-driven-development.md) | Write specs first, implement reliably | 30 min |
| [Designing Agents](./guides/designing-agents.md) | Create project-specific custom subagents | 20 min |
| [Designing Skills](./guides/designing-skills.md) | Build reusable skills and slash commands | 20 min |

### Templates

| Template | Description |
|----------|-------------|
| [CLAUDE.md by Framework](./templates/claude-md-templates.md) | Ready-to-use templates for React, Next.js, Python, Go, and more |
| [Release Monitor Workflow](./templates/release-monitor-workflow.yml) | GitHub Actions workflow for automated release monitoring |
| [GitHub Actions Suite](./templates/github-actions-suite/) | Claude Code `@claude` assistant and PR review, plus CI, monitoring, social, and newsletter workflows |

### Case Studies

| Case Study | Description |
|------------|-------------|
| [48-Hour Website](./case-studies/48-hour-website.md) | Building claude-world.com from zero to production in 48 hours |

## Topics Covered on claude-world.com

The website covers these advanced topics in depth:

| Topic | Article |
|-------|---------|
| **Fundamentals** | [From Operator to Director: The Mindset Shift](https://claude-world.com/articles/mindset-shift) |
| **Framework** | [The Director Mode Framework](https://claude-world.com/articles/director-mode) |
| **Configuration** | [CLAUDE.md Design Principles](https://claude-world.com/articles/claude-md-design) |
| **Agents** | [Claude Code Agents: Complete Guide](https://claude-world.com/articles/agents-guide) |
| **Multi-Agent** | [Multi-Agent Architecture Patterns](https://claude-world.com/articles/multi-agent-patterns) |
| **Skills** | [Claude Code Skills: Complete Guide](https://claude-world.com/articles/skills-guide) |
| **Hooks** | [Claude Code Hooks: Automated Policies](https://claude-world.com/articles/hooks-guide) |
| **MCP** | [Model Context Protocol Guide](https://claude-world.com/articles/mcp-guide) |
| **Memory** | [Building Persistent Project Intelligence](https://claude-world.com/articles/memory-system-guide) |
| **Context7** | [Access Up-to-Date Documentation](https://claude-world.com/articles/context7-integration) |
| **Extended Thinking** | [Unlock Deeper Reasoning](https://claude-world.com/articles/extended-thinking-guide) |
| **SpecKit** | [Specification-Driven Development](https://claude-world.com/articles/speckit-guide) |
| **Debugging** | [Advanced Debugging Techniques](https://claude-world.com/articles/debugging-techniques) |
| **Security** | [Security-First Development](https://claude-world.com/articles/security-first) |
| **CI/CD** | [Pipeline Integration](https://claude-world.com/articles/cicd-integration) |

## Quick Start

### 1. Install Claude Code

```bash
# macOS, Linux, WSL
curl -fsSL https://claude.ai/install.sh | bash

# Homebrew
brew install --cask claude-code
```

On Windows, run `irm https://claude.ai/install.ps1 | iex` in PowerShell or `winget install Anthropic.ClaudeCode`. Installing with npm still works but is deprecated. Update later with `claude update`.

### 2. Create a CLAUDE.md in your project

Run `/init` inside Claude Code to generate one from your codebase, or start from this:

```markdown
# Project Instructions

## Tech Stack
- [Your framework]
- [Your database]

## Development Guidelines
- Run tests before committing
- Use TypeScript strict mode

## Autonomous Operations
- Read any file
- Run tests
- Create/modify source files

## Requires Confirmation
- Push to remote
- Delete files
- Modify environment variables
```

CLAUDE.md is guidance. To enforce the "Requires Confirmation" list, add permission rules to `.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "ask": ["Bash(git push *)", "Bash(rm *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

### 3. Start Claude Code

```bash
claude
```

## The Director Mode Mindset

### Traditional approach (Hands-on Developer Mode):
```
You: "Can you help me fix this bug?"
Claude: "Sure, I can help. First, let me ask..."
You: [waits for questions]
Claude: [asks 5 questions]
You: [answers questions]
Claude: [finally starts working]
```

### Director Mode approach:
```
You: "Fix the login bug"
Claude: [immediately launches 3 parallel agents]
       [Agent 1: searches for auth code]
       [Agent 2: checks error logs]
       [Agent 3: reviews recent changes]
       [finds and fixes the bug]
       [commits with clear message]
You: [reviews the completed work]
```

**Key principle**: You're the Director. Claude is your autonomous team. Define goals, let them execute.

### The Three Pillars

1. **Goals over Instructions** - Define outcomes, not steps
2. **Team Delegation** - Trust parallel agents to work concurrently
3. **Outcome Verification** - Review results, not every action

## Model Selection

Choose the right model for each task:

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| **Haiku 5.5** | High-volume, latency-sensitive work: classification, extraction, quick searches | Fastest | Low |
| **Sonnet 5.5** | Implementation, code review, refactoring | Fast | Medium |
| **Opus 5.5** | Architecture decisions, security audits, long-running agentic work | Moderate | High |
| **Fable 5.1** | Demanding reasoning and long-horizon agentic work; select it explicitly | Slower | Highest |

**Quick tips**: Switch with `/model` (or `Option+P` on macOS, `Alt+P` on Windows/Linux) and set reasoning depth with `/effort`. In the Claude API, use the full IDs `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`, and `claude-fable-5-1`.

## Quality Checks

Every pull request runs the [Validate](./.github/workflows/validate.yml) workflow:

- **yamllint** and **actionlint** (with shellcheck) on every workflow template
- **Code blocks:** every `json` code block must be valid JSON, every `yaml` block must parse, and complete workflows inside Markdown are linted with actionlint
- **lychee** checks every link in every Markdown file (also weekly, to catch link rot)

See [CONTRIBUTING.md](./CONTRIBUTING.md) to run the same checks locally.

## Community

- **Website**: [claude-world.com](https://claude-world.com)
- **Discord**: [Claude Code Builders Taiwan](https://discord.gg/rBtHzSD288)
- **Twitter**: [@lukashanren1](https://twitter.com/lukashanren1)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### How to Contribute

1. **Examples**: Add practical examples showing patterns in action
2. **Templates**: Create CLAUDE.md templates for different frameworks
3. **Guides**: Write in-depth guides on specific topics
4. **Translations**: Help translate content to other languages

For discussions and questions, join our [Discord community](https://discord.gg/rBtHzSD288).

## Security

Found a problem in an example or template that could harm someone who copies it? Please report it privately; see [SECURITY.md](./SECURITY.md).

## License

MIT License - see [LICENSE](./LICENSE)

---

Built with Claude Code by the Claude World community.

*Last updated: 2026-10-21*
