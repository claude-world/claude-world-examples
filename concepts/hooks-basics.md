# Hooks Basics

> Hooks are Claude Code's automation layer—middleware that sits between Claude's intentions and actual execution.

## What are Hooks?

Hooks let you automatically intercept, validate, and modify Claude's actions. Think of them as policies that enforce themselves.

**Key characteristics:**
- **Event-driven** - Triggered at specific points in Claude's workflow
- **Automatic** - No manual intervention needed once configured
- **Flexible** - Can allow, deny, modify, or audit actions

## Hook Events

The events you will use most:

| Event | When Triggered | Purpose |
|-------|----------------|---------|
| `SessionStart` | Session starts or resumes (also after `/clear` and compaction) | Load or re-inject context, persist env vars (command hooks only) |
| `UserPromptSubmit` | User sends prompt | Block a prompt, add context |
| `PreToolUse` | Before tool runs | Allow, deny, ask, or rewrite the call |
| `PermissionRequest` | A permission prompt is about to appear | Approve or deny on the user's behalf |
| `PostToolUse` | After tool succeeds | Format, lint, audit, give Claude feedback |
| `PostToolUseFailure` | After tool fails | Log failures, suggest a fix |
| `Notification` | Claude needs input or permission | Desktop or chat alerts |
| `SubagentStart` / `SubagentStop` | Subagent spawned / finishes | Inject context / check its result |
| `Stop` | Claude finishes responding | Verify completion criteria |
| `PreCompact` / `PostCompact` | Around context compaction | Back up state, log the summary |
| `SessionEnd` | Session ends | Cleanup, final logging |

Current Claude Code also fires these, grouped by area:

- **Setup and environment:** `Setup`, `CwdChanged`, `FileChanged`, `DirectoryAdded`, `InstructionsLoaded`, `ConfigChange`
- **Prompts and tools:** `UserPromptExpansion`, `PermissionDenied`, `PostToolBatch`
- **Tasks and agent teams:** `TaskCreated`, `TaskCompleted`, `TeammateIdle`
- **Errors and models:** `StopFailure`, `PreModelSwitch`, `PostModelSwitch`
- **Worktrees, MCP, and display:** `WorktreeCreate`, `WorktreeRemove`, `Elicitation`, `ElicitationResult`, `MessageDisplay`

Run `/hooks` and choose `All events` to browse every event in your version.

## Hook Flow

```
User Prompt
    │
    ▼
┌─────────────────┐
│ UserPromptSubmit│ ← Block prompt / add context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PreToolUse      │ ← Allow/deny/ask, rewrite input
└────────┬────────┘
         │   (PermissionRequest if a prompt is needed)
         ▼
┌─────────────────┐
│ Tool Execution  │ ← Actual action (Read, Edit, Bash)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PostToolUse     │ ← React to results
└────────┬────────┘
         │   (repeats for every tool call)
         ▼
┌─────────────────┐
│ Stop            │ ← Verify completion
└────────┬────────┘
         │
         ▼
    Response
```

## Configuration Location

Hooks live under the `hooks` key of a settings file: `.claude/settings.json` (project, committed), `.claude/settings.local.json` (personal), `~/.claude/settings.json` (all your projects), or managed policy settings. Plugins ship them in `hooks/hooks.json`, and skills and subagents can declare them in frontmatter. Hooks from every level are merged.

```jsonc
{
  "hooks": {
    "SessionStart": [ /* matcher groups */ ],
    "UserPromptSubmit": [ /* ... */ ],
    "PreToolUse": [ /* ... */ ],
    "PostToolUse": [ /* ... */ ],
    "Stop": [ /* ... */ ],
    "SubagentStop": [ /* ... */ ]
  }
}
```

## Hook Types

### 1. Prompt Hooks

Use a Claude model to evaluate conditions. Claude Code replaces `$ARGUMENTS` in your prompt with the hook's input JSON (or appends the JSON if the placeholder is missing), and the model answers with JSON:

```json
{
  "type": "prompt",
  "prompt": "A Bash command is about to run: $ARGUMENTS. If it deletes or overwrites files outside the project directory, return {\"ok\": false, \"reason\": \"explanation\"}. Otherwise return {\"ok\": true}."
}
```

**Response format (JSON):**
```jsonc
// Allow the action
{"ok": true}

// Block with reason
{"ok": false, "reason": "Command deletes files outside the project"}
```

What `ok: false` does depends on the event: on `PreToolUse` the call is denied (add `"continueOnBlock": true` to hand the reason back to Claude so it can adjust instead of ending the turn), on `Stop` and `SubagentStop` Claude keeps working with the reason as its next instruction, and on `UserPromptSubmit` the prompt is blocked.

> **Important:** Prompt hooks must return `{"ok": ...}` JSON. Plain text responses like "approve" or "block" will not work. Prompt hooks run on tool events, `UserPromptSubmit`, `Stop`, `SubagentStop`, and task/teammate events, but not on `SessionStart`, `SessionEnd`, `Notification`, or `PreCompact`. Default timeout: 30 seconds.

### 2. Command Hooks

Run shell commands. The command receives the event as JSON on stdin and answers with its exit code (and, optionally, JSON on stdout):

```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-command.sh",
  "timeout": 30,
  "onFailure": "block"
}
```

**Exit codes:**
- `0` - Success. JSON on stdout, if any, is applied; plain stdout from `SessionStart` and `UserPromptSubmit` becomes context for Claude
- `2` - Blocking error. stderr is the reason: it blocks `PreToolUse`, rejects `UserPromptSubmit`, and keeps `Stop` from ending the turn
- Anything else - Non-blocking error. The action goes ahead

**onFailure options** (`command` and `http` hooks, Claude Code 2.1.295+):
- `block` - If the hook can't start, exits with a code other than 0 or 2, times out, or prints invalid JSON, block the action as exit 2 would (fail closed)
- `continue` - Let the action go ahead when the hook fails (fail open)

There is no `warn` or `ignore` value. `onFailure` has no effect on `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle`, or `async` hooks.

Use command hooks for anything that must always hold: they are deterministic and cost no model call. Save prompt hooks for judgment calls a script can't make. Claude Code also supports `http` hooks (POST the JSON to a URL), `mcp_tool` hooks (call a tool on a connected MCP server), and experimental `agent` hooks (a subagent that can read files before answering `ok`/`reason`).

## Hook Structure

```jsonc
{
  "hooks": {
    "EventName": [                    // e.g. "PreToolUse"
      {
        "matcher": "ToolName",        // e.g. "Bash" or "Edit|Write"; omit for events without matchers
        "hooks": [
          {
            "type": "command",        // or "prompt", "http", "mcp_tool", "agent"
            "if": "Bash(git *)",      // optional; one permission rule, tool events only
            "command": "...",         // prompt hooks use "prompt": "... $ARGUMENTS ..."
            "timeout": 60,            // optional, in seconds
            "statusMessage": "...",   // optional spinner text
            "onFailure": "block"      // optional; "continue" or "block"
          }
        ]
      }
    ]
  }
}
```

### Matchers

- `"Bash"` - Match a specific tool (matchers are case-sensitive)
- `"Edit|Write"` - Match either tool; use this for file edits
- `"mcp__github__.*"` - Regex; every tool from one MCP server (the `.*` is required)
- `"*"`, `""`, or no matcher - Match everything
- Non-tool events match other fields: `SessionStart` matches `startup`, `resume`, `clear`, `compact`, or `fork`; `SubagentStart`/`SubagentStop` match the agent type; `Notification` matches the notification type
- Events such as `UserPromptSubmit`, `Stop`, `TeammateIdle`, `PostToolBatch`, `TaskCreated`, `TaskCompleted`, and `CwdChanged` have no matcher support, so omit the field

For finer filtering on tool events, add `"if"` to a handler. It takes one [permission rule](https://code.claude.com/docs/en/permissions), so `"if": "Bash(git commit *)"` spawns the handler only for commit commands.

## Essential Examples

### Block Dangerous Commands

A command hook with a small script is deterministic and needs no model call. Save this as `.claude/hooks/block-dangerous.sh` and run `chmod +x` on it:

```bash
#!/bin/bash
# .claude/hooks/block-dangerous.sh - PreToolUse hook for Bash
COMMAND=$(jq -r '.tool_input.command // empty')

for pattern in 'rm -(rf|fr) +(/|~)/?\*?( |$)' 'drop +(table|database)' 'git push( .*)? (--force|-f)( |$)'; do
  if grep -Eqi -- "$pattern" <<<"$COMMAND"; then
    echo "Blocked: destructive command (matched '$pattern'). Ask the user to run it manually." >&2
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
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous.sh",
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

Exit 2 blocks the call and shows Claude the stderr message; `onFailure: "block"` keeps the gate closed if the script is missing or crashes. Pattern lists are a backstop, not a boundary: pair them with permission deny rules and `/sandbox`.

### Auto-Run Tests After Code Changes

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npm test --silent >&2 || exit 2",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

A `PostToolUse` hook can't undo the edit, but exit 2 shows the test output to Claude so it fixes the failure. For a slow suite, add `"asyncRewake": true`: the tests run in the background and Claude is woken only when they fail.

### Verify Tests Before Completion

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Claude is about to stop. Hook input: $ARGUMENTS\n\nIf last_assistant_message shows that code was modified but does not say the tests were run and passed, return {\"ok\": false, \"reason\": \"Run the test suite and fix any failures before finishing.\"}. Otherwise return {\"ok\": true}."
          }
        ]
      }
    ]
  }
}
```

`Stop` has no matcher. When the model returns `ok: false`, Claude keeps working with the reason as its next instruction; Claude Code overrides the hook after eight consecutive continuations without a tool call. For a one-off condition, the built-in `/goal` command sets up the same kind of check for the current session.

## Hooks vs Other Controls

| Feature | Hooks | Permissions | CLAUDE.md |
|---------|-------|-------------|-----------|
| Enforced by Claude Code | Yes | Yes | No (guidance only) |
| Conditional logic | Yes | No | No |
| Shell commands | Yes | No | No |
| Setup complexity | Medium | Easy | Easy |

**Use Hooks when:**
- You need conditional logic
- You want automatic enforcement
- You need external command execution
- You want audit trails

**Use Permissions for:**
- Simple allow/deny rules, such as `Bash(git push *)`
- Static file access control, such as `Read(./.env)` or `Edit(./config/**)`
- Hard limits: deny rules still apply when a hook returns `allow`

**Use CLAUDE.md for:**
- Guidelines and preferences
- Context and documentation

## Quick Start

1. **Create `.claude/settings.json`** if it doesn't exist

2. **Add a simple security hook:**
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
            "command": "jq -r '.tool_input.command' | grep -Eq -- '(^| )(--force|-f)( |$)' && { echo 'Blocked: force push. Run it yourself if you mean it.' >&2; exit 2; }; exit 0"
          }
        ]
      }
    ]
  }
}
```

3. **Test with a safe scenario** - Run `/hooks` to confirm it loaded, then ask Claude to force-push in a scratch repository

4. **Expand gradually** - Add more hooks as needed

## Best Practices

1. **Start simple** - One hook at a time
2. **Be explicit** - Clear rules; `{"ok": ...}` answers for prompt hooks, exit 2 plus a stderr reason for command hooks
3. **Layer appropriately** - Permission rules set hard limits, PreToolUse prevents, PostToolUse audits, Stop verifies
4. **Prefer deterministic checks** - Command hooks for rules that must always hold, prompt hooks for judgment
5. **Test thoroughly** - Hooks affect every Claude action; pipe sample JSON into your scripts before you rely on them

## Technical Notes

- **Timeout:** Defaults are 600 seconds for `command`, `http`, and `mcp_tool` hooks (30 seconds on `UserPromptSubmit`), 30 seconds for `prompt`, and 60 seconds for `agent`. Override per hook with `timeout` (in seconds). `SessionEnd` hooks share a 1.5-second budget unless you set a longer `timeout`.
- **Parallel execution:** All hooks that match an event run in parallel. One hook's deny doesn't stop the others from running; for `PreToolUse` the most restrictive answer wins (`deny` > `defer` > `ask` > `allow`). Identical handlers defined in several settings files run once.
- **Error handling:** By default a hook that crashes or times out is a non-blocking error, so the action goes ahead (fail open). Set `"onFailure": "block"` on security gates so they fail closed.

## Environment Variables

Hooks have access to these environment variables:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Project root where the session started. Reference scripts as `"$CLAUDE_PROJECT_DIR"/.claude/hooks/check.sh` |
| `CLAUDE_ENV_FILE` | A file path Claude Code provides to `SessionStart`, `Setup`, `CwdChanged`, and `FileChanged` hooks. Append `export` lines to it to set variables for later Bash commands |
| `CLAUDE_CODE_REMOTE` | `"true"` in remote/web sessions; unset in the local CLI |
| `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` | Plugin install and data directories, for plugin hooks |
| `CLAUDE_EFFORT` | The effort level in effect when the hook runs |

> **CLAUDE_ENV_FILE:** You don't set this variable yourself. Claude Code provides the path and runs the file's contents before each Bash command, so a `SessionStart` hook can persist environment variables like this:

```bash
#!/bin/bash
# SessionStart hook: persist variables for Claude's later Bash commands
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=development' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

There are no `$CLAUDE_FILE_PATH` or `$CLAUDE_TOOL_INPUT` variables. Tool details arrive as JSON on stdin.

### Hook Input (stdin JSON)

Every command hook receives the event as JSON on stdin. A `PreToolUse` hook for a Bash call gets:

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/my-project/abc123.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {"command": "npm test"},
  "tool_use_id": "toolu_01ABC123"
}
```

File tools put the absolute path in `tool_input.file_path`. Read fields with `jq`, for example `jq -r '.tool_input.file_path'`.

### Hook Output (decisions)

Exit 0 with no output means "no objection": the call still goes through the normal permission flow. For finer control, a `PreToolUse` hook exits 0 and prints a decision (`allow`, `deny`, `ask`, or `defer`):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Database writes are not allowed"
  }
}
```

`PostToolUse`, `Stop`, `SubagentStop`, and `UserPromptSubmit` hooks use a top-level `{"decision": "block", "reason": "..."}` instead.

## Related Resources

- [Full Hooks Guide](https://claude-world.com/articles/hooks-guide) - Comprehensive documentation
- [Hooks Reference](https://code.claude.com/docs/en/hooks) - Official event and schema reference
- [Hooks Patterns](../examples/hooks-patterns.md) - Copy-paste patterns
- [Security Best Practices](../guides/security-best-practices.md) - Security patterns
- [CLAUDE.md Principles](./claude-md-principles.md) - Project configuration

---

*Hooks transform Claude from a reactive assistant to a policy-enforcing partner.*
