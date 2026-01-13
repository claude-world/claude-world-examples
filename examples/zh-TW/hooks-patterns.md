# Hooks 模式

> 經過實戰驗證的 hook 設定，適用於真實世界情境 - 從安全防護到自動化工作流程。

## 概述

本指南提供完整、可直接複製貼上的 hook 模式，按使用情境分類。每個模式都包含完整設定，並解釋何時以及為何使用它。

## 模式分類

| 分類 | 用途 | 風險等級 |
|----------|---------|------------|
| [安全](#安全模式) | 防止破壞性操作 | 關鍵 |
| [品質](#品質模式) | 強制程式碼標準 | 中等 |
| [工作流程](#工作流程模式) | 自動化重複任務 | 低 |
| [稽核](#稽核模式) | 追蹤和記錄操作 | 低 |

---

## 安全模式

### 1. 阻擋破壞性指令

**使用情境**：防止意外資料遺失或不可逆操作

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

**為什麼有效**：
- 捕捉常見的破壞性模式
- 允許安全版本（例如 `rm -rf ./node_modules` 通常是安全的）
- 在阻擋訊息中提供原因

### 2. 保護敏感檔案

**使用情境**：防止修改關鍵設定檔

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

### 3. Git Push 保護

**使用情境**：在推送到遠端前要求確認

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

### 4. API Key 洩漏防護

**使用情境**：阻擋包含密鑰的提交

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

## 品質模式

### 5. 提交前測試

**使用情境**：確保任何提交前測試都通過

> **注意：** Command hooks 透過 stdin JSON 接收工具輸入。對於需要解析的 bash 指令，使用 prompt hooks 可以分析輸入並回傳 JSON 回應。

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

**簡化的 prompt 版本**：

> **注意：** 下方的 `condition` 語法是概念範例，展示預期行為。實際上，Claude Code hooks 是依序評估的——如果 prompt hook 回傳 "approve"，鏈中的後續 hooks 將會執行。

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

> **重要：** 依序評估意味著鏈中的所有 hooks 都會執行，除非某個阻擋。要有條件執行，請在 command 本身中使用 shell script 邏輯。

### 6. 儲存檔案時 Lint

**使用情境**：編輯後自動 lint 檔案

> **注意：** 檔案路徑資訊透過 stdin JSON 提供給 hooks。以下範例展示概念性方法——實際實作取決於你的 hook 接收到正確的 JSON 結構。

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

> **替代方案：** 對於不依賴檔案路徑 context 的 linting，使用 `git ls-files | xargs eslint` 來 lint 所有追蹤的檔案。

### 7. TypeScript 編譯檢查

**使用情境**：驗證變更後 TypeScript 可以編譯

> **注意：** 這個模式使用 prompt hook 檢查是否修改了 TypeScript 檔案，然後執行編譯器。

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

> **替代方案：** 在所有檔案上執行 TypeScript 編譯器，不需條件檢查：

### 8. 驗證測試存在

**使用情境**：確保新功能有測試

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

## 工作流程模式

### 9. 編輯時自動格式化

**使用情境**：自動套用 Prettier 格式化

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

### 10. Session Context 載入

**使用情境**：在 session 開始時載入專案 context

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

### 11. Prompt 增強

**使用情境**：自動為使用者 prompts 添加 context

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

### 12. 自動增強 Commit 訊息

**使用情境**：使用 conventional commits 格式改善提交訊息

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

## 稽核模式

### 13. 操作記錄

**使用情境**：記錄所有檔案修改以供稽核追蹤

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

### 14. Session 摘要

**使用情境**：在 session 結束時產生摘要

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

### 15. Subagent 完成追蹤

**使用情境**：追蹤和驗證 subagent 結果

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

## 完整生產環境設定

這是結合多種模式的完整 hooks 設定：

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

## 環境變數和 Hook 輸入

### 可用的環境變數

Hooks 可以存取這些環境變數：

| 變數 | 描述 |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | 專案根目錄路徑 |
| `CLAUDE_ENV_FILE` | `.env` 檔案路徑，用於環境持久化 |
| `CLAUDE_CODE_REMOTE` | 遠端倉庫 URL（如果是 git repo） |

> **重要：** 前面章節中參考 `$CLAUDE_TOOL_INPUT` 和 `$CLAUDE_FILE_PATH` 的範例是概念性的。這些變數不作為環境變數提供。

### Hook 輸入（stdin JSON）

對於 `PreToolUse` 和 `PostToolUse` hooks，工具 context 透過 stdin 提供：

```json
{
  "tool_name": "Bash" | "Edit" | "Write" | "Read",
  "tool_input": { /* 工具特定輸入 */ },
  "cwd": "/path/to/project"
}
```

對於檔案操作（`Edit`、`Write`、`Read`），`tool_input` 包含：
```json
{
  "file_path": "/path/to/file",
  "old_string": "...",  // For Edit
  "new_string": "..."   // For Edit/Write
}
```

> **建議：** 使用 prompt hooks，它們接收這個 JSON 輸入並可以智慧處理，而不是 command hooks 嘗試解析不存在的環境變數。

## 撰寫 Hooks 的技巧

### 1. Prompts 要具體

```json
// 不好 - 太模糊
{ "prompt": "Check if this is safe" }

// 好 - 明確標準
{ "prompt": "Block if command contains rm -rf with paths /, /home, /etc. Return 'block: [reason]' or 'approve'." }
```

### 2. 使用適當的 onFailure

```json
// 關鍵安全 - 失敗時阻擋
{ "onFailure": "block" }

// 錦上添花的品質 - 警告但繼續
{ "onFailure": "warn" }

// 可選增強 - 靜默繼續
{ "onFailure": "ignore" }
```

### 3. 分層你的 Hooks

```
PreToolUse  → 防止不當操作
PostToolUse → 反應和增強
Stop        → 最終驗證
```

### 4. 漸進式測試

1. 從一個 hook 開始
2. 用安全情境測試
3. 逐步添加更多 hooks
4. 監控誤報

## 相關資源

- [Hooks 基礎](../concepts/hooks-basics.md) - 核心概念和流程
- [安全最佳實踐](../guides/security-best-practices.md) - 全面的安全指南
- [Hooks 指南](https://claude-world.com/articles/hooks-guide) - 完整文件

---

*這些模式來自生產環境 Claude Code 部署的實戰經驗。根據你的特定需求進行自訂。*
