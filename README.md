# Claude World Examples

> Practical examples and best practices for mastering Claude Code

[![Website](https://img.shields.io/badge/Website-claude--world.com-blue)](https://claude-world.com)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da)](https://discord.gg/claude-code-builders)

## What is Claude World?

Claude World is a community dedicated to helping developers master **Claude Code** - Anthropic's official CLI for AI-assisted software development.

We focus on:
- **Director Mode** - A mindset shift from "hands-on developer" to "team director"
- **Efficient Workflows** - Parallel agents, minimal interruption
- **Best Practices** - Battle-tested patterns from real projects

## Examples

### Concepts

| Example | Description |
|---------|-------------|
| [Director Mode Basics](./concepts/director-mode-basics.md) | The mindset shift that 10x your productivity |
| [CLAUDE.md Principles](./concepts/claude-md-principles.md) | How to write effective project instructions |
| [CLAUDE.md Anti-Patterns](./concepts/claude-md-anti-patterns.md) | Common mistakes and how to fix them |
| [Parallel Agents](./concepts/parallel-agents.md) | Run 5 agents simultaneously for faster results |
| [Multi-AI Workflow](./concepts/multi-ai-workflow.md) | Coordinate Claude, Codex, and Gemini CLI |

### Practical Examples

| Example | Description |
|---------|-------------|
| [Simple CLAUDE.md](./examples/simple-claude-md.md) | A minimal but effective CLAUDE.md template |
| [Bug Hunting Pattern](./examples/bug-hunting.md) | Use parallel agents to find bugs fast |
| [Feature Development](./examples/feature-development.md) | Structured approach to building features |
| [Refactoring Patterns](./examples/refactoring-patterns.md) | Systematic code improvement with Claude |

### Guides

| Guide | Description |
|-------|-------------|
| [Quick Reference Cards](./guides/quick-reference.md) | One-page visual guides for fast lookup |
| [Production Readiness](./guides/production-readiness.md) | Checklist before shipping to production |
| [Security Best Practices](./guides/security-best-practices.md) | Build secure applications from the start |

## Quick Start

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Create a CLAUDE.md in your project

```markdown
# Project Instructions

## Tech Stack
- [Your framework]
- [Your database]

## Development Guidelines
- Run tests before committing
- Use TypeScript strict mode
```

### 3. Start Claude Code

```bash
claude
```

## The Director Mode Mindset

Traditional approach:
```
You: "Can you help me fix this bug?"
Claude: "Sure, I can help. First, let me ask..."
You: [waits for questions]
Claude: [asks 5 questions]
You: [answers questions]
Claude: [finally starts working]
```

Director Mode approach:
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

## Community

- **Website**: [claude-world.com](https://claude-world.com)
- **Discord**: [Claude Code Builders Taiwan](https://discord.gg/claude-code-builders)
- **Twitter**: [@lukashanren1](https://twitter.com/lukashanren1)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

For discussions and questions, join our [Discord community](https://discord.gg/claude-code-builders).

## License

MIT License - see [LICENSE](./LICENSE)

---

Built with Claude Code by the Claude World community.
