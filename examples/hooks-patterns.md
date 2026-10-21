# Hooks Patterns

> Battle-tested hook configurations for real-world scenarios - from security guardrails to automated workflows.

## Overview

This guide provides complete, copy-paste-ready hook patterns organized by use case. Each pattern includes the full configuration and explains when and why to use it.

Add the JSON to `.claude/settings.json`. Script-based patterns expect the script in `.claude/hooks/` (run `chmod +x .claude/hooks/*.sh`) and use `jq` to read the hook input from stdin.

## Pattern Categories

| Category | Purpose | Risk Level |
|----------|---------|------------|
| [Security](#security-patterns) | Prevent destructive actions | Critical |
| [Quality](#quality-patterns) | Enforce code standards | Medium |
| [Workflow](#workflow-patterns) | Automate repetitive tasks | Low |
| [Audit](#audit-patterns) | Track and log actions | Low |

---

## Security Patterns

Security patterns use deterministic enforcement: permission deny rules and command hooks give the same answer every time and cost no model call. Prompt hooks are for judgment calls (see Patterns 8, 12, and 15).

### 1. Block Destructive Commands

**Use case**: Prevent accidental data loss or irreversible operations

```bash
#!/bin/bash
# .claude/hooks/block-destructive.sh - PreToolUse hook for Bash
COMMAND=$(jq -r '.tool_input.command // empty')

PATTERNS=(
  'rm -(rf|fr) +(/|~)/?\*?( |$)'          # rm -rf on / or the home directory
  '(drop|truncate) +(table|database)'     # DROP TABLE, DROP DATABASE, TRUNCATE TABLE
  'delete +from +[a-z0-9_."]+ *(;|"|$)'   # DELETE FROM without WHERE
  'git push( .*)? (--force|-f)( |$)'      # force push
  'git reset +--hard'                     # discards uncommitted work
)

for pattern in "${PATTERNS[@]}"; do
  if grep -Eqi -- "$pattern" <<<"$COMMAND"; then
    echo "Blocked: '$COMMAND' matches a destructive pattern. Ask the user to run it manually." >&2
    exit 2
  fi
done
exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-destructive.sh",
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

**Why this works**:
- Deterministic: the same command always gets the same answer, with no model call
- Allows safe versions (e.g., `rm -rf ./node_modules` doesn't match)
- Exit 2 blocks the call and Claude reads the stderr reason, so it can choose a safer approach
- `onFailure: "block"` keeps the gate closed if the script is missing or `jq` isn't installed
- Pattern lists are never complete (`rm -r -f /`, `find / -delete`), so add permission deny rules too and turn on `/sandbox` for an OS-level boundary

### 2. Protect Sensitive Files

**Use case**: Keep secrets unreadable and critical configuration files unmodified

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./credentials/**)",
      "Edit(./private/**)",
      "Edit(**/*.pem)",
      "Edit(**/*.key)",
      "Edit(**/id_rsa*)",
      "Edit(./config/production.*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh",
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# .claude/hooks/protect-files.sh - PreToolUse hook for Edit|Write
FILE_PATH=$(jq -r '.tool_input.file_path // empty')
FILE_PATH="${FILE_PATH//\\//}"   # normalize Windows separators

case "$FILE_PATH" in
  */.env | */.env.* | */secrets/* | */credentials/* | */private/* | \
  *.pem | *.key | */id_rsa* | */config/production.* | */.git/*)
    echo "Blocked: $FILE_PATH is a protected file. Ask the user to change it manually." >&2
    exit 2
    ;;
esac
exit 0
```

- The deny rules are enforced by Claude Code itself. A `Read` deny also blocks `Edit` and `Write` on that path, and covers Bash file commands it recognizes, such as `cat .env`
- Only `Read(...)` and `Edit(...)` path rules are consulted: `Write(...)` path rules are accepted but never checked, and a `.claudeignore` file has no effect
- The hook adds what rules can't express (any `.git/` path, a custom message Claude reads)
- Neither stops a script that opens files itself; the sandbox's `filesystem.denyRead` setting covers Bash subprocesses

### 3. Git Push Protection

**Use case**: Never force-push; confirm before pushing to main

```bash
#!/bin/bash
# .claude/hooks/git-push-guard.sh - PreToolUse hook, runs only for git push
INPUT=$(cat)
COMMAND=$(jq -r '.tool_input.command // empty' <<<"$INPUT")
BRANCH=$(git -C "$(jq -r '.cwd // empty' <<<"$INPUT")" branch --show-current 2>/dev/null)

decide() {  # $1 = allow | deny | ask, $2 = reason
  jq -n --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: $d, permissionDecisionReason: $r}}'
  exit 0
}

if grep -Eq -- '(^| )(--force[a-z-]*|-f|\+[^ ]+)( |=|$)' <<<"$COMMAND"; then
  decide deny "Force push requires manual execution"
fi
if grep -Eq -- '[ :](main|master)( |$)' <<<"$COMMAND" || [[ "$BRANCH" =~ ^(main|master)$ ]]; then
  decide ask "Direct push to main/master: confirm, or open a pull request instead"
fi
exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git push *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/git-push-guard.sh",
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

The `if` field spawns the script only for `git push` commands. The script answers with the `PreToolUse` JSON decision form: `deny` blocks the call and tells Claude why, and `ask` shows the normal permission prompt with your reason, even in auto mode.

### 4. API Key Leak Prevention

**Use case**: Block commits containing secrets

```bash
#!/bin/bash
# .claude/hooks/scan-staged-secrets.sh - PreToolUse hook, runs only for git commit
CWD=$(jq -r '.cwd // empty')
SECRET_RE='(sk-[A-Za-z0-9_-]{20,}|(sk|pk)_live_[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'

# Staged changes, plus unstaged tracked changes that `git commit -a` would include
if { git -C "$CWD" diff --cached -U0; git -C "$CWD" diff -U0; } 2>/dev/null | grep '^+' | grep -Eq -- "$SECRET_RE"; then
  echo "Blocked: the changes look like they contain a secret (API key, token, or private key). Remove it and load it from an environment variable instead." >&2
  exit 2
fi
exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git commit *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scan-staged-secrets.sh",
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

A prompt hook can't do this job: it only sees the hook input (the command text), not the staged diff. The `Read(./.env)` deny rule from Pattern 2 keeps Claude from reading secrets in the first place; this hook catches the ones that slip into code. For broader coverage, call a dedicated secret scanner from the same script.

---

## Quality Patterns

### 5. Test Before Commit

**Use case**: Ensure tests pass before any commit

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git commit *)",
            "command": "out=$(npm test 2>&1) || { printf '%s\\n' \"$out\" | tail -n 30 >&2; echo 'Tests failed: fix them before committing.' >&2; exit 2; }",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

The `if` field spawns the test run only for `git commit`, including compound commands such as `npm run lint && git commit -m "..."`. Exit 2 blocks the commit, and Claude sees the last 30 lines of test output as the reason.

> **Important:** Hooks that match the same event run in parallel, not as a chain, and there is no `condition` field, so a prompt hook can't gate a sibling command hook. Put the condition in `if` or inside the command itself.

### 6. Lint on File Save

**Use case**: Auto-lint files after editing

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "f=$(jq -r '.tool_input.file_path'); case \"$f\" in *.js|*.jsx|*.ts|*.tsx) npx eslint --fix \"$f\" >&2 || exit 2 ;; esac"
          }
        ]
      }
    ]
  }
}
```

The command reads the edited path from stdin, skips files that aren't JavaScript or TypeScript, and runs ESLint with `--fix`. If problems remain, exit 2 shows ESLint's output to Claude so it can fix them (a `PostToolUse` hook can't undo the edit).

> **Note:** `Edit|Write` only sees changes made by Claude's file tools. A file rewritten by a Bash command doesn't trigger it; use a `FileChanged` hook for specific files, or lint the whole tree from a `Stop` hook.

### 7. TypeScript Compile Check

**Use case**: Verify TypeScript compiles after changes

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "case \"$(jq -r '.tool_input.file_path')\" in *.ts|*.tsx) npx tsc --noEmit >&2 || exit 2 ;; esac",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

> **Tip:** `tsc --noEmit` checks the whole project. On a large codebase, add `"asyncRewake": true` so the check runs in the background and wakes Claude only when it exits 2 with errors.

### 8. Verify Tests Exist

**Use case**: Ensure new features have tests

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Claude is about to stop. Hook input: $ARGUMENTS\n\nRead last_assistant_message. If it says new functionality or new source files were added under src/ and does not mention adding or updating tests in tests/ or __tests__/, respond {\"ok\": false, \"reason\": \"Add tests for the new code before finishing.\"}. Otherwise respond {\"ok\": true}."
          }
        ]
      }
    ]
  }
}
```

`Stop` has no matcher. On `ok: false`, Claude keeps working with the reason as its next instruction. A prompt hook only sees the hook input (here, Claude's final message), not your files; to check the repository itself, use `"type": "agent"` (experimental), which can read files before answering, at the cost of a subagent run every time Claude stops.

---

## Workflow Patterns

### 9. Auto-Format on Edit

**Use case**: Apply Prettier formatting automatically

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "file=$(jq -r '.tool_input.file_path'); npx prettier --write --ignore-unknown \"$file\" || true"
          }
        ]
      }
    ]
  }
}
```

`onFailure` only accepts `continue` or `block`. To keep a best-effort formatter quiet, end the command with `|| true` so a Prettier error never shows up as a hook error.

### 10. Session Context Loading

**Use case**: Load project context at session start

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Project: $(basename \"$CLAUDE_PROJECT_DIR\")\"; echo \"Branch: $(git branch --show-current 2>/dev/null || echo 'not a git repo')\"; echo \"Uncommitted files: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')\""
          }
        ]
      }
    ]
  }
}
```

Plain stdout from a `SessionStart` hook is added to Claude's context. Keep it fast: without a matcher it runs on every start, resume, `/clear`, and compaction. Use `"matcher": "compact"` to re-inject reminders only after compaction. `SessionStart` supports command hooks, not prompt hooks.

### 11. Prompt Enhancement

**Use case**: Add context to user prompts automatically

```bash
#!/bin/bash
# .claude/hooks/prompt-context.sh - UserPromptSubmit hook
PROMPT=$(jq -r '.prompt // empty')

if grep -Eqi 'the (bug|error)' <<<"$PROMPT"; then
  echo "Recent commits, newest first:"
  git log --oneline -5 2>/dev/null
fi
if grep -Eqi 'the feature' <<<"$PROMPT"; then
  echo "Feature specifications live in docs/."
fi
exit 0
```

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/prompt-context.sh"
          }
        ]
      }
    ]
  }
}
```

Plain stdout from a `UserPromptSubmit` hook is added as context next to the prompt (or print JSON with `hookSpecificOutput.additionalContext`). Write it as facts rather than orders, and keep it quick: it runs before every prompt with a 30-second default timeout. `UserPromptSubmit` has no matcher. A prompt hook can't add context; it can only allow or block the prompt.

### 12. Auto-Commit Message Enhancement

**Use case**: Improve commit messages with conventional commits format

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "if": "Bash(git commit *)",
            "prompt": "A git commit is about to run. Hook input: $ARGUMENTS\n\nIf the commit message does not start with a Conventional Commits type (feat:, fix:, docs:, style:, refactor:, test:, chore:), respond {\"ok\": false, \"reason\": \"Rewrite the message in Conventional Commits format, for example: fix: handle empty cart\"}. Otherwise respond {\"ok\": true}.",
            "continueOnBlock": true
          }
        ]
      }
    ]
  }
}
```

`ok: false` denies the call; `continueOnBlock: true` returns the reason to Claude as the tool error, so it rewrites the message and commits again instead of ending the turn. Prompt hooks can't ask the user; for a confirmation prompt, use a command hook that returns `permissionDecision: "ask"` (Pattern 3).

---

## Audit Patterns

### 13. Action Logging

**Use case**: Log all file modifications for audit trail

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{time: (now | todate), tool: .tool_name, target: (.tool_input.file_path // .tool_input.command)}' >> \"$CLAUDE_PROJECT_DIR\"/.claude/audit.log"
          }
        ]
      }
    ]
  }
}
```

Each line records the time, the tool, and the file path or command. Commands can contain secrets, so keep `.claude/audit.log` out of git.

### 14. Session Summary

**Use case**: Keep a log of what each turn accomplished and which files changed

```bash
#!/bin/bash
# .claude/hooks/session-log.sh - Stop hook
INPUT=$(cat)
{
  echo "## $(date -u +%Y-%m-%dT%H:%M:%SZ) session $(jq -r '.session_id' <<<"$INPUT")"
  echo
  jq -r '.last_assistant_message // "(no message)"' <<<"$INPUT"
  echo
  echo "Changed files:"
  git -C "$(jq -r '.cwd' <<<"$INPUT")" status --short 2>/dev/null
  echo
} >> "$CLAUDE_PROJECT_DIR/.claude/session-log.md"
exit 0
```

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/session-log.sh"
          }
        ]
      }
    ]
  }
}
```

> **Why not a prompt hook that generates a summary?** A prompt hook can only answer `{"ok": true}` or `{"ok": false, "reason": "..."}`. Its text never reaches you, and `ok: false` on `Stop` just makes Claude keep working. Claude's own closing message is already in `last_assistant_message`.

### 15. Subagent Completion Tracking

**Use case**: Track and verify subagent results

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "code-reviewer",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "A subagent is about to finish. Hook input: $ARGUMENTS\n\nCheck last_assistant_message: 1) Does it answer the task it was given? 2) Does it report errors it did not resolve? 3) Does it end with a clear list of findings? If any check fails, respond {\"ok\": false, \"reason\": \"<what the subagent still needs to do>\"}. Otherwise respond {\"ok\": true}."
          }
        ]
      }
    ]
  }
}
```

`SubagentStop` matches on the agent type: here a custom `code-reviewer` subagent from `.claude/agents/` (it isn't built in). Omit the matcher to check every subagent; plugin agents use scoped names such as `^my-plugin:reviewer$`. On `ok: false`, the subagent keeps working with the reason as its next instruction.

---

## Complete Production Configuration

Here's a comprehensive `.claude/settings.json` combining multiple patterns (scripts from Patterns 1, 2, and 4):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Edit(**/*.pem)",
      "Edit(**/*.key)"
    ]
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Project: $(basename \"$CLAUDE_PROJECT_DIR\") @ $(git branch --show-current 2>/dev/null || echo 'no-git')\""
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-destructive.sh",
            "onFailure": "block"
          },
          {
            "type": "command",
            "if": "Bash(git commit *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scan-staged-secrets.sh",
            "onFailure": "block"
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh",
            "onFailure": "block"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "file=$(jq -r '.tool_input.file_path'); npx prettier --write --ignore-unknown \"$file\" || true"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Claude is about to stop. Hook input: $ARGUMENTS\n\nIf last_assistant_message shows code changes but does not say the tests were run, or mentions failing tests or TODOs left behind, respond {\"ok\": false, \"reason\": \"<what to finish first>\"}. Otherwise respond {\"ok\": true}."
          }
        ]
      }
    ]
  }
}
```

---

## Environment Variables and Hook Input

### Available Environment Variables

Hooks have access to these environment variables:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Project root where the session started; use it to reference scripts |
| `CLAUDE_ENV_FILE` | A file path Claude Code provides to `SessionStart`, `Setup`, `CwdChanged`, and `FileChanged` hooks; append `export VAR=value` lines to persist variables for later Bash commands |
| `CLAUDE_CODE_REMOTE` | `"true"` in remote/web sessions; unset in the local CLI |
| `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` | Plugin directories, for hooks shipped in a plugin |

You don't point `CLAUDE_ENV_FILE` anywhere yourself; a `SessionStart` hook just appends to it:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "[ -n \"$CLAUDE_ENV_FILE\" ] && echo 'export NODE_ENV=development' >> \"$CLAUDE_ENV_FILE\"; exit 0"
          }
        ]
      }
    ]
  }
}
```

> **Important:** There are no `$CLAUDE_FILE_PATH`, `$CLAUDE_FILE_PATHS`, or `$CLAUDE_TOOL_INPUT` environment variables. Everything about the tool call arrives as JSON on stdin.

### Hook Input (stdin JSON)

Every command hook receives the event as JSON on stdin. A `PreToolUse` hook for an `Edit` call gets:

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/my-project/abc123.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/home/user/my-project/src/app.ts",
    "old_string": "const retries = 3;",
    "new_string": "const retries = 5;",
    "replace_all": false
  },
  "tool_use_id": "toolu_01ABC123"
}
```

Where to find the fields you need:

| Tool | Fields in `tool_input` |
|------|------------------------|
| `Bash` | `command`, `description`, `timeout`, `run_in_background` |
| `Edit` | `file_path`, `old_string`, `new_string`, `replace_all` |
| `Write` | `file_path`, `content` |
| `Read` | `file_path`, `offset`, `limit` |

File paths are always absolute. `PostToolUse` hooks also receive `tool_response`.

> **Recommendation:** Parse stdin with `jq` in a command hook for anything deterministic. Use prompt hooks, which receive the same JSON through `$ARGUMENTS`, for judgment calls.

## Tips for Writing Hooks

### 1. Be Specific with Prompts

```jsonc
// Bad - too vague, no input, no response format
{ "type": "prompt", "prompt": "Check if this is safe" }

// Good - explicit criteria, the input via $ARGUMENTS, the exact response schema
{ "type": "prompt", "prompt": "Command: $ARGUMENTS. If it deletes or overwrites files outside the project directory (cwd), respond {\"ok\": false, \"reason\": \"...\"}. Otherwise respond {\"ok\": true}." }
```

### 2. Use Appropriate onFailure

```jsonc
// Security gate - if the hook can't start, crashes, or times out, block the action (fail closed)
{ "type": "command", "command": "...", "onFailure": "block" }

// Nice-to-have helper - failures never block the action (fail open)
{ "type": "command", "command": "...", "onFailure": "continue" }
```

`onFailure` takes only `"continue"` or `"block"` (Claude Code 2.1.295+); there is no `warn` or `ignore`. To silence a best-effort hook, end its command with `|| true`. The field has no effect on `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle`, or `async` hooks.

### 3. Layer Your Hooks

```
permissions.deny → Hard limits Claude Code always enforces
PreToolUse       → Prevent bad actions
PostToolUse      → React and enhance
Stop             → Final verification
```

Hooks within one event run in parallel, so each hook must make sense on its own.

### 4. Test Incrementally

1. Start with one hook
2. Test with safe scenarios: pipe sample JSON into the script, e.g. `echo '{"tool_input":{"command":"rm -rf /"}}' | .claude/hooks/block-destructive.sh; echo $?`
3. Add more hooks gradually, checking `/hooks` to confirm each one loaded
4. Monitor for false positives (`claude --debug` writes hook runs to the debug log)

## Related Resources

- [Hooks Basics](../concepts/hooks-basics.md) - Core concepts and flow
- [Security Best Practices](../guides/security-best-practices.md) - Comprehensive security guide
- [Hooks Guide](https://claude-world.com/articles/hooks-guide) - Full documentation
- [Hooks Reference](https://code.claude.com/docs/en/hooks) - Official event and schema reference

---

*These patterns are battle-tested from production Claude Code deployments. Customize them for your specific needs.*
