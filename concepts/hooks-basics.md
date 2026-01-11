# Hooks Basics

> Hooks are Claude Code's automation layer—middleware that sits between Claude's intentions and actual execution.

## What are Hooks?

Hooks let you automatically intercept, validate, and modify Claude's actions. Think of them as policies that enforce themselves.

**Key characteristics:**
- **Event-driven** - Triggered at specific points in Claude's workflow
- **Automatic** - No manual intervention needed once configured
- **Flexible** - Can approve, deny, modify, or audit actions

## Hook Events

| Event | When Triggered | Purpose |
|-------|----------------|---------|
| `SessionStart` | Session begins | Load context, verify environment |
| `UserPromptSubmit` | User sends prompt | Validate input, add context |
| `PreToolUse` | Before tool runs | Approve, deny, or modify actions |
| `PostToolUse` | After tool runs | Audit, react, trigger follow-ups |
| `Stop` | Claude stops | Verify completion criteria |
| `SubagentStop` | Subagent completes | Ensure subagent task completion |

## Hook Flow

```
User Prompt
    │
    ▼
┌─────────────────┐
│ UserPromptSubmit│ ← Validate/modify prompt
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PreToolUse      │ ← Approve/deny/modify action
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Tool Execution  │ ← Actual action (Read, Write, Bash)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PostToolUse     │ ← React to results
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stop            │ ← Verify completion
└────────┬────────┘
         │
         ▼
    Response
```

## Configuration Location

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...],
    "SessionStart": [...],
    "UserPromptSubmit": [...],
    "SubagentStop": [...]
  }
}
```

## Hook Types

### 1. Prompt Hooks

Use Claude to evaluate conditions:

```json
{
  "type": "prompt",
  "prompt": "Check if command is destructive. Return 'approve' or 'block'."
}
```

**Response options:**
- `approve` - Allow the action
- `deny` / `block` - Block the action
- `ask` - Ask user for confirmation

### 2. Command Hooks

Run shell commands:

```json
{
  "type": "command",
  "command": "npm test",
  "onFailure": "block"
}
```

**onFailure options:**
- `block` - Stop if command fails
- `warn` - Show warning but continue
- `ignore` - Silently ignore failure

## Hook Structure

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "prompt | command",
            "prompt": "...",
            "command": "...",
            "onFailure": "block | warn | ignore"
          }
        ]
      }
    ]
  }
}
```

### Matchers

- `"Bash"` - Match specific tool
- `"*"` - Match all tools (wildcard)

## Essential Examples

### Block Dangerous Commands

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "Block if command contains rm -rf, DROP TABLE, or git push --force. Return 'block' or 'approve'."
      }]
    }]
  }
}
```

### Auto-Run Tests After Code Changes

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "npm test --passWithNoTests",
        "onFailure": "warn"
      }]
    }]
  }
}
```

### Verify Tests Before Completion

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "If code was modified, verify tests were run. Block if no tests ran."
      }]
    }]
  }
}
```

## Hooks vs Other Controls

| Feature | Hooks | Permissions | CLAUDE.md |
|---------|-------|-------------|-----------|
| Automatic | Yes | Yes | No |
| Conditional logic | Yes | No | No |
| Shell commands | Yes | No | No |
| Setup complexity | Medium | Easy | Easy |

**Use Hooks when:**
- You need conditional logic
- You want automatic enforcement
- You need external command execution
- You want audit trails

**Use Permissions for:**
- Simple allow/deny rules
- Static file access control

**Use CLAUDE.md for:**
- Guidelines and preferences
- Context and documentation

## Quick Start

1. **Create `.claude/settings.json`** if it doesn't exist

2. **Add a simple security hook:**
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "Block destructive commands (rm -rf, DROP TABLE). Return 'block' or 'approve'."
      }]
    }]
  }
}
```

3. **Test with a safe scenario**

4. **Expand gradually** - Add more hooks as needed

## Best Practices

1. **Start simple** - One hook at a time
2. **Be explicit** - Clear instructions, clear responses
3. **Layer appropriately** - PreToolUse prevents, PostToolUse audits, Stop verifies
4. **Test thoroughly** - Hooks affect every Claude action

## Technical Notes

- **Timeout:** Hooks have a 10-minute timeout (v2.1.3+). Long-running hooks will be terminated.
- **Sequential execution:** Hooks in a chain execute sequentially. If one blocks, subsequent hooks are skipped.
- **Error handling:** Use `onFailure` to control behavior when hooks fail.

## Related Resources

- [Full Hooks Guide](https://claude-world.com/articles/hooks-guide) - Comprehensive documentation
- [Security Best Practices](../guides/security-best-practices.md) - Security patterns
- [CLAUDE.md Principles](./claude-md-principles.md) - Project configuration

---

*Hooks transform Claude from a reactive assistant to a policy-enforcing partner.*
