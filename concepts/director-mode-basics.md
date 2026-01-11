# Director Mode Basics

> Stop being a hands-on developer. Start being a team director.

## The Problem

Most developers use Claude Code like this:

```
Developer: "Hey Claude, can you help me add a login feature?"
Claude: "Sure! What authentication method would you like?"
Developer: "JWT"
Claude: "Great! Where should I store the tokens?"
Developer: "LocalStorage"
Claude: "Should I add refresh token logic?"
Developer: "Yes"
... [10 more questions later] ...
```

This is **inefficient**. You're spending more time answering questions than getting work done.

## The Director Mode Solution

Think of yourself as a team director, and Claude as your development team.

A good director doesn't:
- Answer every small question
- Approve every minor decision
- Micromanage implementation details

A good director does:
- Set clear objectives
- Provide context and constraints
- Trust the team to execute
- Review completed work

## Practical Implementation

### 1. Give Clear Objectives

**Bad**: "Can you help me with authentication?"

**Good**: "Implement JWT authentication with refresh tokens. Store tokens in httpOnly cookies. Use the existing User model."

### 2. Provide Context in CLAUDE.md

```markdown
# Project Context

## Architecture Decisions
- We use JWT for authentication (not sessions)
- All API routes are in /api folder
- We follow REST conventions

## Preferences
- TypeScript strict mode
- Prefer composition over inheritance
- Write tests for all new features
```

### 3. Let Claude Execute Autonomously

With proper context, Claude can:
- Make reasonable decisions without asking
- Use parallel agents to work faster
- Complete entire features in one go

### 4. Review, Don't Supervise

Instead of watching every step:
1. Give the task
2. Let Claude work
3. Review the completed PR
4. Provide feedback if needed

## The Mindset Shift

| Micromanager | Director Mode |
|--------------|---------------|
| Answers every question | Provides context upfront |
| Approves each step | Reviews completed work |
| Single-threaded work | Parallel agents |
| Watches Claude work | Does other tasks while Claude works |
| 1x productivity | 5-10x productivity |

## Getting Started

1. **Write a comprehensive CLAUDE.md** - Include your tech stack, preferences, and common patterns
2. **Use imperative commands** - "Implement X" instead of "Can you help with X?"
3. **Trust the process** - Let Claude make decisions within your constraints
4. **Iterate** - Improve your CLAUDE.md based on what questions Claude asks

## Example Session

```
You: "Implement user profile editing with avatar upload"

Claude: [Launches 4 parallel agents]
- Agent 1: Analyzes existing user model
- Agent 2: Checks file upload patterns in codebase
- Agent 3: Reviews UI component library
- Agent 4: Examines API route conventions

[10 seconds later]

Claude: "I've implemented the profile editing feature:
- Added /api/users/profile endpoint
- Created ProfileEditForm component
- Integrated with existing S3 upload service
- Added tests for all new code
- Created migration for avatar_url column

Ready for review."
```

Total time: 2 minutes instead of 30 minutes of back-and-forth.

---

Next: [CLAUDE.md Principles](./claude-md-principles.md)
