# Claude Code Agents 完整指南

> 從單一提示到平行編排 - 掌握 Agents 可提升 5-10 倍效率

## 快速參考

| Agent | 用途 | 預設模型 | 適用場景 |
|-------|------|----------|----------|
| `Explore` | 快速程式碼導航 | Haiku 4.5 | 檔案搜尋、模式匹配 |
| `general-purpose` | 複雜多步驟任務 | Sonnet 4.5 | 實作、分析 |
| `code-reviewer` | 程式碼品質分析 | Sonnet 4.5 | PR 審查、模式分析 |
| `security-auditor` | 漏洞檢測 | Sonnet 4.5 | 驗證、支付、資料 |
| `test-runner` | 測試執行 | Haiku 4.5 | 執行、分析測試 |
| `debugger` | 根本原因分析 | Sonnet 4.5 | Bug 調查 |
| `refactor-assistant` | 程式碼改進 | Sonnet 4.5 | 清理、重構 |
| `doc-writer` | 文件撰寫 | Haiku/Sonnet | README、API 文件 |

## Task 工具

所有 Agents 都透過 `Task` 工具產生。以下範例使用概念性的 JavaScript 語法來說明參數 - Claude Code 內部會處理實際的調用。

**概念語法（僅供說明）：**

```javascript
Task({
  subagent_type: "Explore",           // 必要：Agent 類型
  model: "haiku",                      // 選填：haiku, sonnet, opus
  prompt: "Your task description",     // 必要：要做什麼
  run_in_background: false             // 選填：非同步執行
})
```

> **注意：** 使用 Claude Code 時，你不需要直接撰寫此語法。只需描述你想要什麼，Claude Code 會產生適當的 Agents。上述語法僅用於說明底層參數。

## Agent 類型

### Explore Agent（最快）

**Explore Agent** 是 Claude Code 的效率利器。由 Haiku 4.5 驅動，它用一個智能查詢取代 5 個手動搜尋操作。

#### 徹底程度等級

| 等級 | 時間 | 使用案例 |
|------|------|----------|
| `quick` | 10-30 秒 | 尋找特定檔案/函式 |
| `medium` | 30-60 秒 | 映射模組結構 |
| `very thorough` | 60-120 秒 | 完整流程分析 |

#### 範例

**快速搜尋：**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: "Explore auth (thoroughness: quick). Find login handler."
})
```

**中等探索：**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: `
    Explore payment module (thoroughness: medium).
    Find Stripe integration points and webhook handlers.
  `
})
```

**深度分析：**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: `
    Explore authentication (thoroughness: very thorough).
    Map complete auth flow: login → session → token refresh → logout.
  `
})
```

#### 為何 Explore 更快

**舊方法（5 個手動步驟）：**
```
Glob *auth*.ts          → 15 秒
Grep "JWT"              → 15 秒
Read auth/index.ts      → 10 秒
Grep middleware         → 15 秒
Read test files         → 10 秒
總計：65 秒
```

**新方法（1 個 Explore Agent）：**
```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: "Explore auth (thoroughness: medium). Map JWT, middleware, tests."
})
// 總計：30-45 秒
```

### general-purpose Agent

用於需要更深度推理的複雜多步驟任務。

```javascript
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Implement user profile editing feature.
    - Add API endpoint for profile updates
    - Create form component with validation
    - Include image upload support
    - Follow existing patterns in src/api/
  `
})
```

### code-reviewer Agent

專門處理程式碼品質和最佳實踐。

```javascript
Task({
  subagent_type: "code-reviewer",
  model: "sonnet",
  prompt: `
    Review changes in the authentication module.
    Check for:
    - Code quality and patterns
    - Error handling
    - Test coverage
    - Documentation

    Provide findings with severity levels.
  `
})
```

### security-auditor Agent

對於驗證、支付和資料處理程式碼至關重要。

```javascript
Task({
  subagent_type: "security-auditor",
  model: "sonnet",  // 關鍵程式碼使用 "opus"
  prompt: `
    Audit the authentication module.
    Check for OWASP Top 10:
    - Injection vulnerabilities
    - Broken authentication
    - Sensitive data exposure
    - Broken access control

    Report findings with severity.
  `
})
```

**使用時機：**
| 場景 | 優先級 |
|------|--------|
| 驗證/登入變更 | 高 |
| 支付程式碼 | 關鍵 |
| 使用者資料處理 | 高 |
| API 端點 | 中 |
| 檔案上傳 | 高 |

### test-runner Agent

處理測試執行和覆蓋率分析。

```javascript
Task({
  subagent_type: "test-runner",
  model: "haiku",
  prompt: `
    Run all tests related to user authentication.
    Report:
    - Pass/fail status
    - Coverage percentage
    - Failed test details
  `
})
```

### debugger Agent

系統性根本原因分析。

```javascript
Task({
  subagent_type: "debugger",
  model: "sonnet",
  prompt: `
    Investigate: TypeError: Cannot read 'id' of undefined
    at CheckoutForm.handleSubmit (checkout.tsx:45)

    Context: Error occurs when submitting with empty cart.

    Find root cause and suggest fix.
  `
})
```

### refactor-assistant Agent

改進程式碼但不改變功能。

```javascript
Task({
  subagent_type: "refactor-assistant",
  model: "sonnet",
  prompt: `
    Refactor utils/helpers.ts:
    - Split into focused modules
    - Remove dead code
    - Improve naming
    - Add TypeScript types
  `
})
```

### doc-writer Agent

建立和更新文件。

```javascript
Task({
  subagent_type: "doc-writer",
  model: "sonnet",
  prompt: `
    Document the user API endpoints.
    Include:
    - Endpoint descriptions
    - Request/response formats
    - Authentication requirements
    - Error codes
    - Examples
  `
})
```

## 平行 Agent 模式

### 模式 1：分析蜂群

啟動 5 個 Explore Agents 進行全面分析：

```javascript
// 全部平行執行
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Map auth file structure (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Find JWT patterns (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Analyze middleware (thoroughness: medium)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Check auth tests (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Review recent changes (thoroughness: quick)" })
```

### 模式 2：實作 + 審查

同時建構和驗證：

```javascript
// 階段 1：實作
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "Implement user profile feature"
})

// 階段 2：平行審查（在階段 1 之後）
Task({ subagent_type: "code-reviewer", model: "sonnet",
  prompt: "Review code quality" })
Task({ subagent_type: "security-auditor", model: "sonnet",
  prompt: "Security review" })
Task({ subagent_type: "test-runner", model: "haiku",
  prompt: "Run and analyze tests" })
```

### 模式 3：多檔案重構

將工作分配給多個 Agents：

```javascript
// 每個 Agent 處理一個檔案
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Refactor payment/checkout.ts to new pattern" })
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Refactor payment/subscription.ts to new pattern" })
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Refactor payment/refund.ts to new pattern" })
Task({ subagent_type: "general-purpose", model: "sonnet",
  prompt: "Update payment/types.ts for new pattern" })
```

### 模式 4：Bug 調查

平行假設測試：

```javascript
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Search for session handling changes (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Check for race conditions (thoroughness: medium)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Review error logs (thoroughness: quick)" })
Task({ subagent_type: "Explore", model: "haiku",
  prompt: "Find timeout configurations (thoroughness: quick)" })
Task({ subagent_type: "debugger", model: "sonnet",
  prompt: "Analyze most likely root cause from exploration" })
```

## 模型選擇

| 任務類型 | 模型 | 成本 | 速度 |
|----------|------|------|------|
| 快速搜尋 | Haiku 4.5 | $ | 快 |
| 模式匹配 | Haiku 4.5 | $ | 快 |
| 測試執行 | Haiku 4.5 | $ | 快 |
| 簡單文件 | Haiku 4.5 | $ | 快 |
| 程式碼審查 | Sonnet 4.5 | $$ | 平衡 |
| 實作 | Sonnet 4.5 | $$ | 平衡 |
| 除錯 | Sonnet 4.5 | $$ | 平衡 |
| 安全稽核 | Sonnet/Opus | $$-$$$ | 平衡-深度 |
| 架構設計 | Opus 4.5 | $$$ | 深度 |

**關鍵權衡：**
- Haiku 4.5：比 Sonnet 快 2 倍、成本 1/3
- Sonnet 4.5：最佳程式碼撰寫效能
- Opus 4.5：最高智能，預設 Thinking Mode

## 背景 Agents

用於長時間執行的任務：

```javascript
Task({
  subagent_type: "security-auditor",
  model: "opus",
  prompt: "Comprehensive security audit of entire codebase",
  run_in_background: true
})
```

檢查背景任務：
```javascript
TaskOutput({ task_id: "...", block: false })
```

## 最佳實踐

### 1. 選擇正確的 Agent

```
檔案搜尋       → Explore (haiku)
實作           → general-purpose (sonnet)
程式碼品質     → code-reviewer (sonnet)
安全           → security-auditor (sonnet/opus)
測試           → test-runner (haiku)
Bug            → debugger (sonnet)
清理           → refactor-assistant (sonnet)
文件           → doc-writer (haiku/sonnet)
```

### 2. 保持提示聚焦

**太廣泛：**
```
"Analyze everything about the codebase"
```

**聚焦：**
```
"Explore auth module (thoroughness: medium). Find JWT handling and session management."
```

### 3. 提供上下文

```javascript
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Context: Migrating from REST to GraphQL.
    Pattern: Use new ApiClient from src/lib/api.ts

    Task: Refactor user service to use GraphQL.
  `
})
```

### 4. 盡可能使用平行

獨立任務應同時執行：

```javascript
// 這些是獨立的 - 平行執行
Task({ ..., prompt: "Analyze file A" })
Task({ ..., prompt: "Analyze file B" })
Task({ ..., prompt: "Analyze file C" })
```

### 5. 串連相依任務

順序任務應分階段：

```
階段 1：Explore（收集上下文）
階段 2：Implement（使用階段 1 的上下文）
階段 3：Review（驗證階段 2）
```

## 常見工作流程

### 新功能開發

```
1. Explore (quick)：理解現有模式
2. general-purpose：實作功能
3. test-runner：執行測試
4. code-reviewer + security-auditor：審查（平行）
5. doc-writer：更新文件
```

### Bug 修復

```
1. 4x Explore（平行）：從多個角度調查
2. debugger：綜合發現，識別根本原因
3. general-purpose：實作修復
4. test-runner：驗證修復，添加回歸測試
```

### 程式碼審查

```
1. Explore：理解變更
2. code-reviewer：品質檢查
3. security-auditor：安全檢查
4. test-runner：覆蓋率分析
```

## 總結

| 原則 | 行動 |
|------|------|
| 從 Explore 開始 | 大多數任務使用 `thoroughness: medium` |
| 平行化一切 | 獨立任務 = 平行 Agents |
| 匹配模型與任務 | Haiku 用於搜尋、Sonnet 用於實作 |
| 保持提示聚焦 | 每個 Agent 一個明確目標 |
| 串連相依工作 | 階段 1 → 階段 2 → 階段 3 |

---

**相關：**
- [Parallel Agents](../concepts/parallel-agents.md) - 平行模式深入探討
- [Multi-Agent Patterns](https://claude-world.com/articles/multi-agent-patterns) - 進階編排

返回 [README](../README.md)
