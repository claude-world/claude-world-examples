# Hooks 基礎

> Hooks 是 Claude Code 的自動化層——介於 Claude 意圖和實際執行之間的中介軟體。

## 什麼是 Hooks？

Hooks 讓你可以自動攔截、驗證和修改 Claude 的動作。把它們想成能自我執行的政策。

**主要特性：**
- **事件驅動** - 在 Claude 工作流程的特定時間點觸發
- **自動化** - 設定後不需要人工介入
- **彈性** - 可以允許、拒絕、修改或稽核動作

## Hook 事件

最常用的事件：

| 事件 | 觸發時機 | 用途 |
|-------|----------------|---------|
| `SessionStart` | Session 開始或恢復時（`/clear` 與壓縮後也會觸發） | 載入或重新注入脈絡、保存環境變數（僅限 command hooks） |
| `UserPromptSubmit` | 使用者送出 prompt | 阻擋 prompt、加入脈絡 |
| `PreToolUse` | 工具執行前 | 允許、拒絕、詢問或改寫這次呼叫 |
| `PermissionRequest` | 即將出現權限提示時 | 代替使用者核准或拒絕 |
| `PostToolUse` | 工具成功後 | 格式化、lint、稽核、回饋給 Claude |
| `PostToolUseFailure` | 工具失敗後 | 記錄失敗、建議修正 |
| `Notification` | Claude 需要輸入或權限時 | 桌面或聊天通知 |
| `SubagentStart` / `SubagentStop` | Subagent 啟動 / 結束 | 注入脈絡 / 檢查結果 |
| `Stop` | Claude 完成回應 | 驗證完成條件 |
| `PreCompact` / `PostCompact` | Context 壓縮前後 | 備份狀態、記錄摘要 |
| `SessionEnd` | Session 結束 | 清理、最終記錄 |

目前的 Claude Code 還會觸發以下事件，依領域分組：

- **設定與環境：** `Setup`、`CwdChanged`、`FileChanged`、`DirectoryAdded`、`InstructionsLoaded`、`ConfigChange`
- **Prompts 與工具：** `UserPromptExpansion`、`PermissionDenied`、`PostToolBatch`
- **Tasks 與 agent teams：** `TaskCreated`、`TaskCompleted`、`TeammateIdle`
- **錯誤與模型：** `StopFailure`、`PreModelSwitch`、`PostModelSwitch`
- **Worktrees、MCP 與顯示：** `WorktreeCreate`、`WorktreeRemove`、`Elicitation`、`ElicitationResult`、`MessageDisplay`

執行 `/hooks` 並選擇 `All events`，可瀏覽你目前版本的所有事件。

## Hook 流程

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

## 設定位置

Hooks 放在設定檔的 `hooks` 鍵底下：`.claude/settings.json`（專案，會提交）、`.claude/settings.local.json`（個人）、`~/.claude/settings.json`（你的所有專案），或 managed policy settings。Plugins 把 hooks 放在 `hooks/hooks.json`，skills 與 subagents 也能在 frontmatter 中宣告。各層級的 hooks 會合併。

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

## Hook 類型

### 1. Prompt Hooks

用 Claude 模型評估條件。Claude Code 會把 prompt 中的 `$ARGUMENTS` 替換成 hook 的輸入 JSON（沒有這個佔位符時則附加在最後），模型以 JSON 回答：

```json
{
  "type": "prompt",
  "prompt": "A Bash command is about to run: $ARGUMENTS. If it deletes or overwrites files outside the project directory, return {\"ok\": false, \"reason\": \"explanation\"}. Otherwise return {\"ok\": true}."
}
```

**回應格式（JSON）：**
```jsonc
// Allow the action
{"ok": true}

// Block with reason
{"ok": false, "reason": "Command deletes files outside the project"}
```

`ok: false` 的效果取決於事件：在 `PreToolUse` 上會拒絕這次呼叫（加上 `"continueOnBlock": true` 可把理由交還給 Claude，讓它調整而不是結束這一輪）；在 `Stop` 與 `SubagentStop` 上，Claude 會把理由當成下一個指示繼續工作；在 `UserPromptSubmit` 上則會阻擋 prompt。

> **重要：** Prompt hooks 必須回傳 `{"ok": ...}` JSON。像 "approve" 或 "block" 這類純文字回應無效。Prompt hooks 可用於工具事件、`UserPromptSubmit`、`Stop`、`SubagentStop` 以及 task/teammate 事件，但不能用於 `SessionStart`、`SessionEnd`、`Notification` 或 `PreCompact`。預設逾時：30 秒。

### 2. Command Hooks

執行 shell 指令。指令會從 stdin 收到事件 JSON，並以 exit code（以及選用的 stdout JSON）回應：

```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-command.sh",
  "timeout": 30,
  "onFailure": "block"
}
```

**Exit codes：**
- `0` - 成功。stdout 上的 JSON（如果有）會被套用；`SessionStart` 與 `UserPromptSubmit` 的純文字 stdout 會成為 Claude 的脈絡
- `2` - 阻擋錯誤。stderr 是理由：它會阻擋 `PreToolUse`、拒絕 `UserPromptSubmit`，並讓 `Stop` 無法結束這一輪
- 其他 - 非阻擋錯誤。動作照常進行

**onFailure 選項**（`command` 與 `http` hooks，Claude Code 2.1.295+）：
- `block` - hook 無法啟動、以 0 或 2 以外的 code 結束、逾時或輸出無效 JSON 時，像 exit 2 一樣阻擋動作（fail closed）
- `continue` - hook 失敗時讓動作繼續（fail open）

沒有 `warn` 或 `ignore` 這兩個值。`onFailure` 對 `Stop`、`SubagentStop`、`TaskCompleted`、`TeammateIdle` 或 `async` hooks 沒有作用。

必須永遠成立的規則請用 command hooks：它們是確定性的，也不需要呼叫模型。Prompt hooks 留給腳本無法判斷的情況。Claude Code 也支援 `http` hooks（把 JSON POST 到某個 URL）、`mcp_tool` hooks（呼叫已連線 MCP server 的工具），以及實驗性的 `agent` hooks（一個可以先讀檔案再回答 `ok`/`reason` 的 subagent）。

## Hook 結構

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

- `"Bash"` - 符合特定工具（matchers 區分大小寫）
- `"Edit|Write"` - 符合任一工具；檔案編輯請用這個
- `"mcp__github__.*"` - 正規表示式；某個 MCP server 的所有工具（`.*` 不可省略）
- `"*"`、`""` 或不寫 matcher - 符合全部
- 非工具事件比對其他欄位：`SessionStart` 比對 `startup`、`resume`、`clear`、`compact` 或 `fork`；`SubagentStart`/`SubagentStop` 比對 agent 類型；`Notification` 比對通知類型
- `UserPromptSubmit`、`Stop`、`TeammateIdle`、`PostToolBatch`、`TaskCreated`、`TaskCompleted`、`CwdChanged` 等事件不支援 matcher，請省略這個欄位

要在工具事件上做更細的過濾，可以在 handler 加上 `"if"`。它接受一條[權限規則](https://code.claude.com/docs/en/permissions)，所以 `"if": "Bash(git commit *)"` 只會在 commit 指令時執行 handler。

## 基本範例

### 阻擋危險指令

搭配小腳本的 command hook 是確定性的，也不需要呼叫模型。把它存成 `.claude/hooks/block-dangerous.sh` 並執行 `chmod +x`：

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

Exit 2 會阻擋這次呼叫並讓 Claude 看到 stderr 訊息；`onFailure: "block"` 讓腳本遺失或當掉時閘門仍保持關閉。模式清單只是最後防線，不是邊界：請搭配權限 deny 規則與 `/sandbox`。

### 程式碼變更後自動執行測試

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

`PostToolUse` hook 無法撤銷編輯，但 exit 2 會把測試輸出顯示給 Claude，讓它修正失敗。測試很慢時可加上 `"asyncRewake": true`：測試在背景執行，只有失敗時才喚醒 Claude。

### 完成前驗證測試

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

`Stop` 沒有 matcher。模型回傳 `ok: false` 時，Claude 會把理由當成下一個指示繼續工作；連續八次延續且期間沒有任何工具呼叫時，Claude Code 會覆寫這個 hook。如果只是一次性的條件，內建的 `/goal` 指令可以在目前 session 設定同類型的檢查。

## Hooks 與其他控制機制比較

| 功能 | Hooks | Permissions | CLAUDE.md |
|---------|-------|-------------|-----------|
| 由 Claude Code 強制執行 | 是 | 是 | 否（僅為指引） |
| 條件邏輯 | 是 | 否 | 否 |
| Shell 指令 | 是 | 否 | 否 |
| 設定複雜度 | 中等 | 簡單 | 簡單 |

**使用 Hooks 的時機：**
- 需要條件邏輯
- 想要自動化強制執行
- 需要執行外部指令
- 想要稽核紀錄

**使用 Permissions 的時機：**
- 簡單的允許/拒絕規則，例如 `Bash(git push *)`
- 靜態的檔案存取控制，例如 `Read(./.env)` 或 `Edit(./config/**)`
- 硬性限制：即使 hook 回傳 `allow`，deny 規則依然生效

**使用 CLAUDE.md 的時機：**
- 指南與偏好
- 脈絡與文件

## 快速開始

1. **建立 `.claude/settings.json`**（如果還不存在）

2. **加入一個簡單的安全 hook：**
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

3. **用安全的情境測試** - 執行 `/hooks` 確認已載入，再請 Claude 在測試用 repository 中 force-push

4. **逐步擴展** - 需要時再加入更多 hooks

## 最佳實踐

1. **從簡單開始** - 一次一個 hook
2. **明確** - 規則清楚；prompt hooks 回答 `{"ok": ...}`，command hooks 用 exit 2 加上 stderr 理由
3. **適當分層** - Permission 規則設定硬性限制，PreToolUse 預防，PostToolUse 稽核，Stop 驗證
4. **優先使用確定性檢查** - 必須永遠成立的規則用 command hooks，需要判斷的用 prompt hooks
5. **徹底測試** - Hooks 影響 Claude 的每個動作；依賴腳本前先用範例 JSON 測試

## 技術說明

- **逾時：** `command`、`http`、`mcp_tool` hooks 預設 600 秒（`UserPromptSubmit` 上為 30 秒），`prompt` 預設 30 秒，`agent` 預設 60 秒。可用 `timeout`（秒）逐一覆寫。`SessionEnd` hooks 共用 1.5 秒的預算，除非你設定更長的 `timeout`。
- **平行執行：** 符合同一事件的所有 hooks 會平行執行。一個 hook 拒絕不會讓其他 hooks 停止；對 `PreToolUse` 來說，最嚴格的回答勝出（`deny` > `defer` > `ask` > `allow`）。在多個設定檔中定義的相同 handler 只會執行一次。
- **錯誤處理：** 預設情況下，當掉或逾時的 hook 是非阻擋錯誤，動作會繼續（fail open）。安全閘門請設定 `"onFailure": "block"`，讓它 fail closed。

## 環境變數

Hooks 可以使用這些環境變數：

| 變數 | 說明 |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Session 開始時的專案根目錄。腳本請寫成 `"$CLAUDE_PROJECT_DIR"/.claude/hooks/check.sh` |
| `CLAUDE_ENV_FILE` | Claude Code 提供給 `SessionStart`、`Setup`、`CwdChanged`、`FileChanged` hooks 的檔案路徑。在其中附加 `export` 行，可為之後的 Bash 指令設定變數 |
| `CLAUDE_CODE_REMOTE` | 遠端/網頁 sessions 中為 `"true"`；本地 CLI 中不會設定 |
| `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` | Plugin 的安裝與資料目錄，供 plugin hooks 使用 |
| `CLAUDE_EFFORT` | Hook 執行時生效的 effort 等級 |

> **CLAUDE_ENV_FILE：** 這個變數不需要你自己設定。Claude Code 會提供路徑，並在每個 Bash 指令前執行檔案內容，所以 `SessionStart` hook 可以這樣保存環境變數：

```bash
#!/bin/bash
# SessionStart hook: persist variables for Claude's later Bash commands
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=development' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

沒有 `$CLAUDE_FILE_PATH` 或 `$CLAUDE_TOOL_INPUT` 這類變數。工具細節會以 JSON 從 stdin 傳入。

### Hook 輸入（stdin JSON）

每個 command hook 都會從 stdin 收到事件 JSON。Bash 呼叫的 `PreToolUse` hook 會收到：

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

檔案工具會把絕對路徑放在 `tool_input.file_path`。用 `jq` 讀取欄位，例如 `jq -r '.tool_input.file_path'`。

### Hook 輸出（決策）

Exit 0 且沒有輸出代表「沒有異議」：這次呼叫仍會經過正常的權限流程。需要更細的控制時，`PreToolUse` hook 以 exit 0 結束並輸出決策（`allow`、`deny`、`ask` 或 `defer`）：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Database writes are not allowed"
  }
}
```

`PostToolUse`、`Stop`、`SubagentStop` 與 `UserPromptSubmit` hooks 則使用最上層的 `{"decision": "block", "reason": "..."}`。

## 相關資源

- [完整 Hooks 指南](https://claude-world.com/articles/hooks-guide) - 完整文件
- [Hooks Reference](https://code.claude.com/docs/en/hooks) - 官方事件與 schema 參考
- [Hooks 模式](../../examples/zh-TW/hooks-patterns.md) - 可直接複製的模式
- [安全最佳實踐](../../guides/zh-TW/security-best-practices.md) - 安全模式
- [CLAUDE.md 原則](./claude-md-principles.md) - 專案設定

---

*Hooks 讓 Claude 從被動助手轉變為執行政策的夥伴。*
