# Hooks 基礎

> Hooks 是 Claude Code 的自動化層——介於 Claude 意圖和實際執行之間的中介軟體。

## 什麼是 Hooks？

Hooks 讓你可以自動攔截、驗證和修改 Claude 的動作。把它們想成能自我執行的政策。

**主要特性：**
- **事件驅動** - 在 Claude 工作流程的特定時間點觸發
- **自動化** - 設定後不需要人工介入
- **彈性** - 可以批准、拒絕、修改或稽核動作

## Hook 事件

| 事件 | 觸發時機 | 用途 |
|-------|----------------|---------| 
| `SessionStart` | Session 開始 | 載入脈絡、驗證環境 |
| `UserPromptSubmit` | 使用者送出提示 | 驗證輸入、加入脈絡 |
| `PreToolUse` | 工具執行前 | 批准、拒絕或修改動作 |
| `PostToolUse` | 工具執行後 | 稽核、反應、觸發後續動作 |
| `Stop` | Claude 停止 | 驗證完成標準 |
| `SubagentStop` | Subagent 完成 | 確保 subagent 任務完成 |
| `SessionEnd` | Session 結束 | 清理、最終日誌記錄 |
| `PermissionRequest` | 需要權限時 | 批准/拒絕權限請求 |

> **注意：** 較新版本可能提供額外的事件如 `Notification` 和 `PreCompact`。請查看 `claude --version` 和官方文件了解最新的事件類型。

## Hook 流程

```
使用者提示
    │
    ▼
┌─────────────────┐
│ UserPromptSubmit│ ← 驗證/修改提示
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PreToolUse      │ ← 批准/拒絕/修改動作
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 工具執行         │ ← 實際動作（Read、Write、Bash）
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PostToolUse     │ ← 對結果做出反應
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stop            │ ← 驗證完成
└────────┬────────┘
         │
         ▼
    回應
```

## 設定位置

Hooks 設定在 `.claude/settings.json`：

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

## Hook 類型

### 1. Prompt Hooks

使用 Claude 來評估條件。Prompt hooks 透過 stdin JSON 接收脈絡並以 JSON 回應：

```json
{
  "type": "prompt",
  "prompt": "檢查指令是否具破壞性。回傳 {\"ok\": true} 或 {\"ok\": false, \"reason\": \"說明\"}。"
}
```

**回應格式（JSON）：**
```json
// 允許動作
{"ok": true}

// 阻擋並說明原因
{"ok": false, "reason": "指令包含對系統路徑執行 rm -rf"}
```

> **重要：** Prompt hooks 必須回傳有效的 JSON。純文字回應如 "approve" 或 "block" 將無法正確運作。

### 2. Command Hooks

執行 shell 指令：

```json
{
  "type": "command",
  "command": "npm test",
  "onFailure": "block"
}
```

**onFailure 選項：**
- `block` - 指令失敗時停止
- `warn` - 顯示警告但繼續
- `ignore` - 靜默忽略失敗

## Hook 結構

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

- `"Bash"` - 匹配特定工具
- `"*"` - 匹配所有工具（萬用字元）

## 基本範例

### 阻擋危險指令

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "如果指令包含對系統路徑的 rm -rf、DROP TABLE 或 git push --force，回傳 {\"ok\": false, \"reason\": \"破壞性指令已阻擋\"}。否則回傳 {\"ok\": true}。"
      }]
    }]
  }
}
```

### 程式碼變更後自動執行測試

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

### 完成前驗證測試

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "如果程式碼被修改，驗證測試已執行。如果沒有執行測試則阻擋。"
      }]
    }]
  }
}
```

## Hooks 與其他控制機制比較

| 功能 | Hooks | Permissions | CLAUDE.md |
|---------|-------|-------------|-----------|
| 自動化 | 是 | 是 | 否 |
| 條件邏輯 | 是 | 否 | 否 |
| Shell 指令 | 是 | 否 | 否 |
| 設定複雜度 | 中等 | 簡單 | 簡單 |

**使用 Hooks 當：**
- 你需要條件邏輯
- 你想要自動執行
- 你需要執行外部指令
- 你想要稽核軌跡

**使用 Permissions 做：**
- 簡單的允許/拒絕規則
- 靜態的檔案存取控制

**使用 CLAUDE.md 做：**
- 指引和偏好
- 脈絡和文件

## 快速開始

1. **建立 `.claude/settings.json`** 如果不存在

2. **加入簡單的安全 hook：**
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "如果指令具破壞性（rm -rf、DROP TABLE），回傳 {\"ok\": false, \"reason\": \"已阻擋\"}。否則回傳 {\"ok\": true}。"
      }]
    }]
  }
}
```

3. **用安全情境測試**

4. **逐步擴展** - 依需要加入更多 hooks

## 最佳實踐

1. **從簡單開始** - 一次一個 hook
2. **明確表達** - 清晰的指示，清晰的回應
3. **適當分層** - PreToolUse 預防，PostToolUse 稽核，Stop 驗證
4. **徹底測試** - Hooks 影響每個 Claude 動作

## 技術說明

- **逾時：** Hooks 有 10 分鐘的逾時（v2.1.3+）。長時間執行的 hooks 會被終止。
- **順序執行：** 鏈中的 Hooks 依序執行。如果一個阻擋，後續 hooks 會被跳過。
- **錯誤處理：** 使用 `onFailure` 控制 hooks 失敗時的行為。

## 環境變數

Hooks 可以存取這些環境變數：

| 變數 | 說明 |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | 專案根目錄路徑 |
| `CLAUDE_ENV_FILE` | `.env` 檔案的路徑，用於環境持久化 |
| `CLAUDE_CODE_REMOTE` | 遠端 repository URL（如果是 git repo） |

> **CLAUDE_ENV_FILE：** 對於需要在 bash 指令間持久化環境變數的 `SessionStart` hooks 非常重要。設定此變數指向專案的 `.env` 檔案。

### Hook 輸入（stdin JSON）

對於 `PreToolUse` 和 `PostToolUse` hooks，脈絡透過 stdin 提供：

```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "npm test"},
  "cwd": "/path/to/project"
}
```

> **注意：** 本文件的範例使用簡化的 prompts。在正式環境中，hooks 接收結構化的 JSON 輸入並必須回傳 JSON 回應。

## 相關資源

- [完整 Hooks 指南](https://claude-world.com/articles/hooks-guide) - 完整文件
- [安全最佳實踐](../guides/security-best-practices.md) - 安全模式
- [CLAUDE.md 原則](./claude-md-principles.md) - 專案設定

---

*Hooks 將 Claude 從被動的助手轉變為執行政策的夥伴。*
