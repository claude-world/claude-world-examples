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
        "prompt": "Analyze the bash command for destructive operations. Block if it contains: rm -rf (with root/home paths), DROP TABLE, DROP DATABASE, git push --force, git reset --hard (affecting remote), DELETE FROM without WHERE, TRUNCATE TABLE. Return {\"ok\": true} or {\"ok\": false, \"reason\": \"explanation\"}."
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
        "prompt": "Check if the target file path is sensitive. Block writes to: .env, .env.*, secrets/, credentials/, private/, *.pem, *.key, id_rsa*, config/production.*. Return {\"ok\": true} or {\"ok\": false, \"reason\": \"Protected file\"}."
      }]
    }, {
      "matcher": "Edit",
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if the target file path is sensitive. Block edits to: .env, .env.*, secrets/, credentials/, private/, *.pem, *.key, id_rsa*, config/production.*. Return {\"ok\": true} or {\"ok\": false, \"reason\": \"Protected file\"}."
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
        "prompt": "If the bash command contains 'git push': 1) Block if --force or -f flag is present (return {\"ok\": false, \"reason\": \"Force push requires manual execution\"}). 2) Block if pushing to main/master without PR (return {\"ok\": false, \"reason\": \"Direct push to main requires confirmation\"}). 3) Otherwise return {\"ok\": true}."
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
        "prompt": "If the bash command is 'git add' or 'git commit', check staged content for secrets patterns: API keys (sk-*, pk_*, AKIA*), tokens, passwords in plain text, private keys. If secrets are found, return {\"ok\": false, \"reason\": \"Potential secret detected - review staged changes\"}. Otherwise return {\"ok\": true}."
      }]
    }]
  }
}
```

---

## Quality Patterns

### 5. Test Before Commit

**Use case**: Ensure tests pass before any commit

> **Note:** Command hooks receive tool input via stdin JSON. For bash commands that require parsing, use prompt hooks which can analyze the input and return JSON responses.

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "If the bash command is 'git commit' (with any flags), return {\"ok\": true} to proceed to the test runner. Otherwise return {\"ok\": true}. The next hook will run npm test.",
        "type": "command",
        "command": "npm test --passWithNoTests",
        "onFailure": "block"
      }]
    }]
  }
}
```

**Simplified prompt-based version**:

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

> **Note:** File path information is provided via stdin JSON to hooks. The example below shows a conceptual approach—actual implementation depends on your hook receiving the correct JSON structure.

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "prompt",
        "prompt": "After editing a file, run ESLint on it. Read the file path from the tool input and execute: npx eslint --fix [filepath]. If ESLint finds fixable issues, mention them. Return {\"ok\": true}."
      }]
    }, {
      "matcher": "Write",
      "hooks": [{
        "type": "prompt",
        "prompt": "After writing a file, run ESLint on it. Read the file path from the tool input and execute: npx eslint --fix [filepath]. If ESLint finds fixable issues, mention them. Return {\"ok\": true}."
      }]
    }]
  }
}
```

> **Alternative:** For linting that doesn't depend on file path context, use `git ls-files | xargs eslint` to lint all tracked files.

### 7. TypeScript Compile Check

**Use case**: Verify TypeScript compiles after changes

> **Note:** This pattern uses a prompt hook to check if TypeScript files were modified, then runs the compiler.

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "prompt",
        "prompt": "If the edited file has .ts or .tsx extension, run: npx tsc --noEmit. Report any TypeScript errors. Return {\"ok\": true}."
      }]
    }]
  }
}
```

> **Alternative:** Run TypeScript compiler on all files without conditional checks:

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

## Environment Variables and Hook Input

### Available Environment Variables

Hooks have access to these environment variables:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Project root directory path |
| `CLAUDE_ENV_FILE` | Path to `.env` file for environment persistence |
| `CLAUDE_CODE_REMOTE` | Remote repository URL (if git repo) |

> **Important:** The examples in earlier sections that referenced `$CLAUDE_TOOL_INPUT` and `$CLAUDE_FILE_PATH` were conceptual. These variables are not available as environment variables.

### Hook Input (stdin JSON)

For `PreToolUse` and `PostToolUse` hooks, tool context is provided via stdin:

```json
{
  "tool_name": "Bash" | "Edit" | "Write" | "Read",
  "tool_input": { /* tool-specific input */ },
  "cwd": "/path/to/project"
}
```

For file operations (`Edit`, `Write`, `Read`), the `tool_input` contains:
```json
{
  "file_path": "/path/to/file",
  "old_string": "...",  // For Edit
  "new_string": "..."   // For Edit/Write
}
```

> **Recommendation:** Use prompt hooks which receive this JSON input and can intelligently process it, rather than command hooks that try to parse non-existent environment variables.

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
