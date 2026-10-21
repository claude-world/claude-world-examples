# Hooks 模式

> 經過實戰驗證的 hook 設定，涵蓋真實情境——從安全防護到自動化工作流程。

## 概述

本指南提供依使用情境分類、可直接複製使用的完整 hook 模式。每個模式都包含完整設定，並說明何時以及為什麼使用。

把 JSON 加到 `.claude/settings.json`。使用腳本的模式預期腳本放在 `.claude/hooks/`（執行 `chmod +x .claude/hooks/*.sh`），並用 `jq` 從 stdin 讀取 hook 輸入。

## 模式分類

| 分類 | 用途 | 風險等級 |
|----------|---------|------------|
| [安全](#安全模式) | 防止破壞性動作 | 關鍵 |
| [品質](#品質模式) | 強制程式碼標準 | 中等 |
| [工作流程](#工作流程模式) | 自動化重複任務 | 低 |
| [稽核](#稽核模式) | 追蹤並記錄動作 | 低 |

---

## 安全模式

安全模式採用確定性的強制機制：權限 deny 規則與 command hooks 每次都給出相同答案，也不需要呼叫模型。Prompt hooks 用於需要判斷的情況（見模式 8、12、15）。

### 1. 阻擋破壞性指令

**使用情境**：防止意外的資料遺失或不可逆的操作

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

**為什麼有效**：
- 確定性：同一個指令永遠得到相同答案，不需要呼叫模型
- 允許安全的版本（例如 `rm -rf ./node_modules` 不會被比對到）
- Exit 2 會阻擋這次呼叫，Claude 會讀到 stderr 的理由，進而選擇更安全的做法
- `onFailure: "block"` 讓腳本遺失或未安裝 `jq` 時，閘門仍保持關閉
- 模式清單永遠不完整（`rm -r -f /`、`find / -delete`），所以也要加上權限 deny 規則，並開啟 `/sandbox` 取得作業系統層級的邊界

### 2. 保護敏感檔案

**使用情境**：讓 secrets 無法被讀取，關鍵設定檔不被修改

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

- Deny 規則由 Claude Code 本身強制執行。`Read` deny 也會阻擋同一路徑上的 `Edit` 與 `Write`，並涵蓋它能辨識的 Bash 檔案指令，例如 `cat .env`
- 只有 `Read(...)` 與 `Edit(...)` 路徑規則會被檢查：`Write(...)` 路徑規則雖然被接受但永遠不會被檢查，`.claudeignore` 檔案也沒有作用
- Hook 補上規則無法表達的部分（任何 `.git/` 路徑、讓 Claude 讀到的自訂訊息）
- 兩者都擋不住自行開檔的腳本；sandbox 的 `filesystem.denyRead` 設定可以涵蓋 Bash 子程序

### 3. Git Push 保護

**使用情境**：永遠不 force-push；推送到 main 前先確認

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

`if` 欄位只會在 `git push` 指令時啟動腳本。腳本以 `PreToolUse` 的 JSON 決策格式回答：`deny` 會阻擋這次呼叫並告訴 Claude 原因，`ask` 會顯示帶有你的理由的正常權限提示，即使在 auto mode 下也一樣。

### 4. API Key 外洩防護

**使用情境**：阻擋包含 secrets 的 commits

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

Prompt hook 做不到這件事：它只看得到 hook 輸入（指令文字），看不到已暫存的 diff。模式 2 的 `Read(./.env)` deny 規則從一開始就讓 Claude 讀不到 secrets；這個 hook 則攔下不小心混進程式碼的那些。要更全面的涵蓋，可以在同一個腳本中呼叫專門的 secret 掃描工具。

---

## 品質模式

### 5. Commit 前先測試

**使用情境**：確保任何 commit 之前測試都通過

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

`if` 欄位只會在 `git commit` 時啟動測試，包括 `npm run lint && git commit -m "..."` 這類複合指令。Exit 2 會阻擋 commit，Claude 會看到測試輸出的最後 30 行作為理由。

> **重要：** 符合同一事件的 hooks 會平行執行，而不是串成一條鏈，也沒有 `condition` 欄位，所以 prompt hook 無法控制同層的 command hook。請把條件放在 `if` 或指令本身之中。

### 6. 儲存檔案時 Lint

**使用情境**：編輯後自動 lint 檔案

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

這個指令從 stdin 讀取被編輯的路徑，跳過不是 JavaScript 或 TypeScript 的檔案，並以 `--fix` 執行 ESLint。如果仍有問題，exit 2 會把 ESLint 的輸出顯示給 Claude 讓它修正（`PostToolUse` hook 無法撤銷編輯）。

> **注意：** `Edit|Write` 只看得到 Claude 檔案工具做的變更。被 Bash 指令改寫的檔案不會觸發它；特定檔案請用 `FileChanged` hook，或在 `Stop` hook 中 lint 整個專案。

### 7. TypeScript 編譯檢查

**使用情境**：變更後確認 TypeScript 能編譯

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

> **提示：** `tsc --noEmit` 會檢查整個專案。在大型程式碼庫中，加上 `"asyncRewake": true`，讓檢查在背景執行，只有以 exit 2 回報錯誤時才喚醒 Claude。

### 8. 確認測試存在

**使用情境**：確保新功能有測試

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

`Stop` 沒有 matcher。`ok: false` 時，Claude 會把理由當成下一個指示繼續工作。Prompt hook 只看得到 hook 輸入（這裡是 Claude 的最後訊息），看不到你的檔案；要檢查 repository 本身，請用 `"type": "agent"`（實驗性），它能在回答前讀取檔案，代價是每次 Claude 停止時都要跑一次 subagent。

---

## 工作流程模式

### 9. 編輯時自動格式化

**使用情境**：自動套用 Prettier 格式

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

`onFailure` 只接受 `continue` 或 `block`。要讓盡力而為的格式化工具保持安靜，在指令結尾加上 `|| true`，Prettier 的錯誤就不會顯示成 hook 錯誤。

### 10. Session 脈絡載入

**使用情境**：在 session 開始時載入專案脈絡

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

`SessionStart` hook 的純文字 stdout 會加入 Claude 的脈絡。請保持快速：沒有 matcher 時，它會在每次啟動、恢復、`/clear` 與壓縮時執行。使用 `"matcher": "compact"` 可以只在壓縮後重新注入提醒。`SessionStart` 支援 command hooks，不支援 prompt hooks。

### 11. Prompt 增強

**使用情境**：自動為使用者 prompts 加入脈絡

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

`UserPromptSubmit` hook 的純文字 stdout 會作為脈絡加在 prompt 旁邊（或輸出含 `hookSpecificOutput.additionalContext` 的 JSON）。請寫成事實而不是命令，並保持快速：它會在每個 prompt 前執行，預設逾時 30 秒。`UserPromptSubmit` 沒有 matcher。Prompt hook 無法加入脈絡，只能允許或阻擋 prompt。

### 12. 自動強化 Commit 訊息

**使用情境**：用 Conventional Commits 格式改善 commit 訊息

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

`ok: false` 會拒絕這次呼叫；`continueOnBlock: true` 會把理由當成工具錯誤交還給 Claude，讓它改寫訊息後重新 commit，而不是結束這一輪。Prompt hooks 無法詢問使用者；需要確認提示時，請用回傳 `permissionDecision: "ask"` 的 command hook（模式 3）。

---

## 稽核模式

### 13. 動作記錄

**使用情境**：記錄所有檔案修改作為稽核紀錄

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

每一行記錄時間、工具，以及檔案路徑或指令。指令可能包含 secrets，所以請不要把 `.claude/audit.log` 提交到 git。

### 14. Session 摘要

**使用情境**：記錄每一輪完成了什麼、改了哪些檔案

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

> **為什麼不用產生摘要的 prompt hook？** Prompt hook 只能回答 `{"ok": true}` 或 `{"ok": false, "reason": "..."}`。它的文字永遠不會傳到你手上，而 `Stop` 上的 `ok: false` 只會讓 Claude 繼續工作。Claude 自己的結尾訊息已經在 `last_assistant_message` 裡。

### 15. Subagent 完成追蹤

**使用情境**：追蹤並驗證 subagent 的結果

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

`SubagentStop` 依 agent 類型比對：這裡是 `.claude/agents/` 中的自訂 `code-reviewer` subagent（它不是內建的）。省略 matcher 即可檢查所有 subagents；plugin agents 使用 `^my-plugin:reviewer$` 這類帶範圍的名稱。`ok: false` 時，subagent 會把理由當成下一個指示繼續工作。

---

## 完整的生產環境設定

以下是結合多個模式的完整 `.claude/settings.json`（腳本來自模式 1、2、4）：

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

## 環境變數與 Hook 輸入

### 可用的環境變數

Hooks 可以使用這些環境變數：

| 變數 | 說明 |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Session 開始時的專案根目錄；用它來引用腳本 |
| `CLAUDE_ENV_FILE` | Claude Code 提供給 `SessionStart`、`Setup`、`CwdChanged`、`FileChanged` hooks 的檔案路徑；附加 `export VAR=value` 行，可為之後的 Bash 指令保存變數 |
| `CLAUDE_CODE_REMOTE` | 遠端/網頁 sessions 中為 `"true"`；本地 CLI 中不會設定 |
| `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` | Plugin 目錄，供 plugin 內附的 hooks 使用 |

`CLAUDE_ENV_FILE` 不需要你自己指定位置；`SessionStart` hook 只要附加內容即可：

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

> **重要：** 沒有 `$CLAUDE_FILE_PATH`、`$CLAUDE_FILE_PATHS` 或 `$CLAUDE_TOOL_INPUT` 這些環境變數。工具呼叫的一切資訊都會以 JSON 從 stdin 傳入。

### Hook 輸入（stdin JSON）

每個 command hook 都會從 stdin 收到事件 JSON。`Edit` 呼叫的 `PreToolUse` hook 會收到：

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

需要的欄位在哪裡：

| 工具 | `tool_input` 中的欄位 |
|------|------------------------|
| `Bash` | `command`、`description`、`timeout`、`run_in_background` |
| `Edit` | `file_path`、`old_string`、`new_string`、`replace_all` |
| `Write` | `file_path`、`content` |
| `Read` | `file_path`、`offset`、`limit` |

檔案路徑永遠是絕對路徑。`PostToolUse` hooks 還會收到 `tool_response`。

> **建議：** 任何確定性的檢查，都用 command hook 搭配 `jq` 解析 stdin。需要判斷的情況再用 prompt hooks，它們透過 `$ARGUMENTS` 收到同樣的 JSON。

## 撰寫 Hooks 的技巧

### 1. Prompts 要具體

```jsonc
// Bad - too vague, no input, no response format
{ "type": "prompt", "prompt": "Check if this is safe" }

// Good - explicit criteria, the input via $ARGUMENTS, the exact response schema
{ "type": "prompt", "prompt": "Command: $ARGUMENTS. If it deletes or overwrites files outside the project directory (cwd), respond {\"ok\": false, \"reason\": \"...\"}. Otherwise respond {\"ok\": true}." }
```

### 2. 使用適當的 onFailure

```jsonc
// Security gate - if the hook can't start, crashes, or times out, block the action (fail closed)
{ "type": "command", "command": "...", "onFailure": "block" }

// Nice-to-have helper - failures never block the action (fail open)
{ "type": "command", "command": "...", "onFailure": "continue" }
```

`onFailure` 只接受 `"continue"` 或 `"block"`（Claude Code 2.1.295+）；沒有 `warn` 或 `ignore`。要讓盡力而為的 hook 保持安靜，在指令結尾加上 `|| true`。這個欄位對 `Stop`、`SubagentStop`、`TaskCompleted`、`TeammateIdle` 或 `async` hooks 沒有作用。

### 3. 分層設計 Hooks

```
permissions.deny → Hard limits Claude Code always enforces
PreToolUse       → Prevent bad actions
PostToolUse      → React and enhance
Stop             → Final verification
```

同一事件中的 hooks 會平行執行，所以每個 hook 都必須能獨立運作。

### 4. 逐步測試

1. 從一個 hook 開始
2. 用安全的情境測試：把範例 JSON 導入腳本，例如 `echo '{"tool_input":{"command":"rm -rf /"}}' | .claude/hooks/block-destructive.sh; echo $?`
3. 逐步加入更多 hooks，並用 `/hooks` 確認每個都已載入
4. 監控誤判（`claude --debug` 會把 hook 執行寫進 debug log）

## 相關資源

- [Hooks 基礎](../../concepts/zh-TW/hooks-basics.md) - 核心概念與流程
- [安全最佳實踐](../../guides/zh-TW/security-best-practices.md) - 完整的安全指南
- [Hooks 指南](https://claude-world.com/articles/hooks-guide) - 完整文件
- [Hooks Reference](https://code.claude.com/docs/en/hooks) - 官方事件與 schema 參考

---

*這些模式經過生產環境 Claude Code 部署的實戰驗證。請依你的需求自訂。*
