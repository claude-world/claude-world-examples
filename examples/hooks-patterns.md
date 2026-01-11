# Hooks Patterns

> Battle-tested hook configurations for real-world scenarios - from security guardrails to automated workflows.

## Overview

This guide provides complete, copy-paste-ready hook patterns organized by use case. Each pattern includes the full configuration and explains when and why to use it.

## Pattern Categories

| Category | Purpose | Risk Level |
|----------|---------|------------|
| [Security](#security-patterns) | Prevent destructive actions | Critical |
| [Quality](#quality-patterns) | Enforce code standards | Medium |
| [Workflow](#workflow-patterns) | Automate repetitive tasks | Low |
| [Audit](#audit-patterns) | Track and log actions | Low |

---

## Security Patterns

### 1. Block Destructive Commands

**Use case**: Prevent accidental data loss or irreversible operations

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "Analyze this command for destructive operations. Block if it contains: rm -rf (with root/home paths), DROP TABLE, DROP DATABASE, git push --force, git reset --hard (affecting remote), DELETE FROM without WHERE, TRUNCATE TABLE. Return 'block: [reason]' or 'approve'."
      }]
    }]
  }
}
```

**Why this works**:
- Catches common destructive patterns
- Allows safe versions (e.g., `rm -rf ./node_modules` is usually safe)
- Provides reasoning in block message

### 2. Protect Sensitive Files

**Use case**: Prevent modifications to critical configuration files

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if target file is sensitive. Block writes to: .env, .env.*, **/secrets/*, **/credentials/*, **/private/*, *.pem, *.key, id_rsa*, config/production.*. Return 'block: Protected file' or 'approve'."
      }]
    }, {
      "matcher": "Edit",
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if target file is sensitive. Block edits to: .env, .env.*, **/secrets/*, **/credentials/*, **/private/*, *.pem, *.key, id_rsa*, config/production.*. Return 'block: Protected file' or 'approve'."
      }]
    }]
  }
}
```

### 3. Git Push Protection

**Use case**: Require confirmation before pushing to remote

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "If command contains 'git push': 1) Block if --force or -f flag present (say 'block: Force push requires manual execution'). 2) Block if pushing to main/master without PR (say 'block: Direct push to main requires confirmation'). 3) Otherwise approve. Return 'block: [reason]' or 'approve'."
      }]
    }]
  }
}
```

### 4. API Key Leak Prevention

**Use case**: Block commits containing secrets

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "If command is 'git add' or 'git commit', check staged content for secrets patterns: API keys (sk-*, pk_*, AKIA*), tokens, passwords in plain text, private keys. Block if found with 'block: Potential secret detected - review staged changes'. Otherwise approve."
      }]
    }]
  }
}
```

---

## Quality Patterns

### 5. Test Before Commit

**Use case**: Ensure tests pass before any commit

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'git commit'; then npm test; fi",
        "onFailure": "block"
      }]
    }]
  }
}
```

**Alternative with prompt-based detection**:

> **Note:** The `condition` syntax below is a conceptual example showing the intended behavior. In practice, Claude Code hooks are evaluated sequentially—if a prompt hook returns "approve", subsequent hooks in the chain will run.

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "If this is a git commit command, respond with 'run_tests'. Otherwise respond 'approve'."
      }, {
        "type": "command",
        "command": "npm test --passWithNoTests",
        "onFailure": "block"
      }]
    }]
  }
}
```

> **Important:** The sequential evaluation means all hooks in the chain run unless one blocks. For conditional execution, use shell script logic within the command itself.

### 6. Lint on File Save

**Use case**: Auto-lint files after editing

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "npx eslint --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
        "onFailure": "ignore"
      }]
    }, {
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "npx eslint --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
        "onFailure": "ignore"
      }]
    }]
  }
}
```

### 7. TypeScript Compile Check

**Use case**: Verify TypeScript compiles after changes

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "if [[ \"$CLAUDE_FILE_PATH\" == *.ts ]] || [[ \"$CLAUDE_FILE_PATH\" == *.tsx ]]; then npx tsc --noEmit 2>&1 | head -20; fi",
        "onFailure": "warn"
      }]
    }]
  }
}
```

### 8. Verify Tests Exist

**Use case**: Ensure new features have tests

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "Review the session. If new source files were created in src/, verify corresponding test files exist in tests/ or __tests__/. If tests are missing for new functionality, respond 'block: Missing tests for new code'. Otherwise 'approve'."
      }]
    }]
  }
}
```

---

## Workflow Patterns

### 9. Auto-Format on Edit

**Use case**: Apply Prettier formatting automatically

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
        "onFailure": "ignore"
      }]
    }, {
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
        "onFailure": "ignore"
      }]
    }]
  }
}
```

### 10. Session Context Loading

**Use case**: Load project context at session start

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "echo '[SessionStart] Project: '$(basename $PWD); echo '[SessionStart] Branch: '$(git branch --show-current 2>/dev/null || echo 'not a git repo'); echo '[SessionStart] Uncommitted: '$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')' files'",
        "onFailure": "ignore"
      }]
    }]
  }
}
```

### 11. Prompt Enhancement

**Use case**: Add context to user prompts automatically

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "Enhance this prompt with relevant context if needed. If the user mentions 'the bug' or 'the error', remind to check recent git commits and error logs. If mentioning 'the feature', remind to check the specification in docs/. Return the enhanced context as a system message or 'approve' if no enhancement needed."
      }]
    }]
  }
}
```

### 12. Auto-Commit Message Enhancement

**Use case**: Improve commit messages with conventional commits format

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "If this is a git commit command, verify the message follows Conventional Commits format (feat:, fix:, docs:, style:, refactor:, test:, chore:). If not, suggest the correct format and return 'ask' to confirm with user. If already correct, 'approve'."
      }]
    }]
  }
}
```

---

## Audit Patterns

### 13. Action Logging

**Use case**: Log all file modifications for audit trail

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) WRITE $CLAUDE_FILE_PATH\" >> .claude/audit.log",
        "onFailure": "ignore"
      }]
    }, {
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) EDIT $CLAUDE_FILE_PATH\" >> .claude/audit.log",
        "onFailure": "ignore"
      }]
    }, {
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) BASH\" >> .claude/audit.log",
        "onFailure": "ignore"
      }]
    }]
  }
}
```

### 14. Session Summary

**Use case**: Generate summary when session ends

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "Generate a brief session summary: 1) What was accomplished 2) Files changed 3) Any warnings or concerns. Format as a structured report."
      }]
    }]
  }
}
```

### 15. Subagent Completion Tracking

**Use case**: Track and verify subagent results

```json
{
  "hooks": {
    "SubagentStop": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "Verify subagent completed its task successfully. Check: 1) Did it return expected output format? 2) Did it report any errors? 3) Are results consistent with the request? If issues found, return 'warn: [issue]'. Otherwise 'approve'."
      }]
    }]
  }
}
```

---

## Complete Production Configuration

Here's a comprehensive hooks configuration combining multiple patterns:

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "echo '[Session] '$(basename $PWD)' @ '$(git branch --show-current 2>/dev/null || echo 'no-git')",
        "onFailure": "ignore"
      }]
    }],

    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "Security check: Block rm -rf on important paths, DROP/TRUNCATE TABLE, git push --force. Return 'block: [reason]' or 'approve'."
      }]
    }, {
      "matcher": "Write",
      "hooks": [{
        "type": "prompt",
        "prompt": "Block writes to .env*, **/secrets/*, *.pem, *.key files. Return 'block: Protected file' or 'approve'."
      }]
    }],

    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true",
        "onFailure": "ignore"
      }]
    }],

    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "Verify: 1) No uncommitted sensitive data 2) Tests pass if code changed 3) No TODO comments left unaddressed. Warn if issues found."
      }]
    }]
  }
}
```

---

## Environment Variables

> **Version Note:** Environment variables for hooks were introduced in Claude Code v2.0.60+. The exact variables available may vary by version.

Hooks can access these environment variables:

| Variable | Description | Available In |
|----------|-------------|--------------|
| `CLAUDE_TOOL_INPUT` | The tool's input/arguments | PreToolUse, PostToolUse |
| `CLAUDE_TOOL_OUTPUT` | The tool's output/result | PostToolUse |
| `CLAUDE_FILE_PATH` | Target file path (Edit/Write/Read) | PreToolUse, PostToolUse |
| `CLAUDE_SESSION_ID` | Current session identifier | All hooks |

> **Tip:** Check your Claude Code version with `claude --version`. Environment variable availability may differ between versions.

## Tips for Writing Hooks

### 1. Be Specific with Prompts

```json
// Bad - too vague
{ "prompt": "Check if this is safe" }

// Good - explicit criteria
{ "prompt": "Block if command contains rm -rf with paths /, /home, /etc. Return 'block: [reason]' or 'approve'." }
```

### 2. Use Appropriate onFailure

```json
// Critical security - block on failure
{ "onFailure": "block" }

// Nice-to-have quality - warn but continue
{ "onFailure": "warn" }

// Optional enhancement - silent continue
{ "onFailure": "ignore" }
```

### 3. Layer Your Hooks

```
PreToolUse  → Prevent bad actions
PostToolUse → React and enhance
Stop        → Final verification
```

### 4. Test Incrementally

1. Start with one hook
2. Test with safe scenarios
3. Add more hooks gradually
4. Monitor for false positives

## Related Resources

- [Hooks Basics](../concepts/hooks-basics.md) - Core concepts and flow
- [Security Best Practices](../guides/security-best-practices.md) - Comprehensive security guide
- [Hooks Guide](https://claude-world.com/articles/hooks-guide) - Full documentation

---

*These patterns are battle-tested from production Claude Code deployments. Customize them for your specific needs.*
