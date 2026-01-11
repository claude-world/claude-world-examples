# Claude World Examples

> Practical examples and best practices for mastering Claude Code

[![Website](https://img.shields.io/badge/Website-claudeworld.dev-blue)](https://claudeworld.dev)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da)](https://discord.gg/claude-code-builders)

## What is Claude World?

Claude World is a community dedicated to helping developers master **Claude Code** - Anthropic's official CLI for AI-assisted software development.

We focus on:
- **CEO Mode** - A mindset shift from "AI assistant" to "AI team member"
- **Efficient Workflows** - Parallel agents, minimal interruption
- **Best Practices** - Battle-tested patterns from real projects

## Examples

### Concepts

| Example | Description |
|---------|-------------|
| [CEO Mode Basics](./concepts/ceo-mode-basics.md) | The mindset shift that 10x your productivity |
| [CLAUDE.md Principles](./concepts/claude-md-principles.md) | How to write effective project instructions |
| [Parallel Agents](./concepts/parallel-agents.md) | Run 5 agents simultaneously for faster results |

### Practical Examples

| Example | Description |
|---------|-------------|
| [Simple CLAUDE.md](./examples/simple-claude-md.md) | A minimal but effective CLAUDE.md template |
| [Bug Hunting Pattern](./examples/bug-hunting.md) | Use parallel agents to find bugs fast |
| [Feature Development](./examples/feature-development.md) | Structured approach to building features |

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

## The CEO Mode Mindset

Traditional approach:
```
You: "Can you help me fix this bug?"
Claude: "Sure, I can help. First, let me ask..."
You: [waits for questions]
Claude: [asks 5 questions]
You: [answers questions]
Claude: [finally starts working]
```

CEO Mode approach:
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

**Key principle**: You're the CEO. Claude is your autonomous team. Give clear direction, let them execute.

## Community

- **Website**: [claudeworld.dev](https://claudeworld.dev)
- **Discord**: [Claude Code Builders Taiwan](https://discord.gg/claude-code-builders)
- **Twitter**: [@anthropic](https://twitter.com/anthropic)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

For discussions and questions, join our [Discord community](https://discord.gg/claude-code-builders).

## License

MIT License - see [LICENSE](./LICENSE)

---

Built with Claude Code by the Claude World community.
