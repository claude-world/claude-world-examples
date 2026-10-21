# Claude Code Agents 完整指南

> 從單一提示到平行編排 - 掌握 Agents 能讓效率成倍提升

## 快速參考

內建 Agents 隨 Claude Code 提供。其他的是**自訂 Agents**：你在 `.claude/agents/` 中定義、或透過外掛（plugin）安裝的 Markdown 檔案。請見下方的[自訂 Agents](#自訂-agents)。

| Agent | 類別 | 用途 | 模型 | 適用場景 |
|-------|------|------|------|----------|
| `Explore` | 內建 | 唯讀程式碼搜尋 | 主對話的模型 | 檔案搜尋、模式匹配 |
| `Plan` | 內建 | Plan mode 中的研究 | 主對話的模型 | 提出計畫前收集上下文 |
| `general-purpose` | 內建 | 複雜多步驟任務 | 主對話的模型 | 實作、分析 |
| `code-reviewer` | 自訂 | 程式碼品質分析 | `sonnet`（常見） | PR 審查、模式分析 |
| `security-auditor` | 自訂 | 漏洞檢測 | `sonnet` 或 `opus` | 驗證、支付、資料 |
| `test-runner` | 自訂 | 測試執行 | `haiku` 或 `sonnet` | 執行、分析測試 |
| `debugger` | 自訂 | 根本原因分析 | `sonnet`（常見） | Bug 調查 |
| `refactor-assistant` | 自訂 | 程式碼改進 | `sonnet`（常見） | 清理、重構 |
| `doc-writer` | 自訂 | 文件撰寫 | `haiku` 或 `sonnet` | README、API 文件 |

自訂 Agent 使用其 `model:` 欄位指定的模型；未指定時沿用主對話的模型（若你設定了 `CLAUDE_CODE_SUBAGENT_MODEL` 則使用該值）。Claude Code 另有輔助用的 Agents（`claude`、`statusline-setup`、`claude-code-guide`），會在需要時自動使用。

## Agent 工具

所有 Agents 都透過 `Agent` 工具產生（Claude Code v2.1.63 之前稱為 `Task`；在設定與 agent 定義中 `Task(...)` 仍可作為別名使用）。以下範例使用概念性的 JavaScript 語法來說明參數 - Claude Code 內部會處理實際的調用。

**概念語法（僅供說明）：**

```javascript
Agent({
  subagent_type: "Explore",            // Agent 類型：內建或自訂名稱
  description: "Find login handler",   // 顯示在對話紀錄中的簡短標籤
  prompt: "Your task description",     // 必要：要做什麼
  model: "sonnet",                     // 選填：sonnet, opus, haiku, fable, inherit 或完整模型 ID
  effort: "high",                      // 選填：low, medium, high, xhigh, max
  isolation: "worktree",               // 選填：在暫時的 git worktree 中工作
  run_in_background: true              // 選填：不阻塞（從主對話產生時的預設行為）
})
```

> **注意：** 使用 Claude Code 時，你不需要直接撰寫此語法。只需描述你想要什麼（「用 code-reviewer agent 檢查我的變更」、「平行探索 auth、billing 和 API」），Claude Code 會產生適當的 Agents。若要確保某個 Agent 一定執行，可以 @-mention 它：`@"code-reviewer (agent)"`。上述語法僅用於說明底層參數。

## Agent 類型

### Explore Agent（快速、唯讀）

**Explore Agent** 是 Claude Code 內建的搜尋專家。它用一次委派查詢取代一連串手動搜尋，使用主對話的模型，並且在啟動時不載入你的 CLAUDE.md 與 git status，讓研究保持快速、低成本。只有它的摘要會回到你的對話中。

#### 徹底程度等級

Claude 呼叫 Explore 時會選擇徹底程度：

| 等級 | 深度 | 使用案例 |
|------|------|----------|
| `quick` | 針對性查找 | 尋找特定檔案/函式 |
| `medium` | 平衡探索 | 映射模組結構 |
| `very thorough` | 全面分析 | 完整流程分析 |

#### 範例

**快速搜尋：**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Find login handler",
  prompt: "Explore auth (thoroughness: quick). Find login handler."
})
```

**中等探索：**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Map Stripe integration",
  prompt: `
    Explore payment module (thoroughness: medium).
    Find Stripe integration points and webhook handlers.
  `
})
```

**深度分析：**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Map complete auth flow",
  prompt: `
    Explore authentication (thoroughness: very thorough).
    Map complete auth flow: login → session → token refresh → logout.
  `
})
```

#### 為何 Explore 更有效率

**舊方法（在主對話中手動執行 5 個步驟）：**
```
Glob *auth*.ts          → 檔案清單進入你的上下文
Grep "JWT"              → 每個匹配結果都進入你的上下文
Read auth/index.ts      → 整個檔案進入你的上下文
Grep middleware         → 更多匹配結果
Read test files         → 更多檔案
結果：上下文被不會再用到的搜尋輸出塞滿
```

**新方法（1 個 Explore Agent）：**
```javascript
Agent({
  subagent_type: "Explore",
  description: "Map auth module",
  prompt: "Explore auth (thoroughness: medium). Map JWT, middleware, tests."
})
// 搜尋在 Explore 自己的上下文視窗中進行，只有摘要會回傳
```

#### 讓 Explore 使用 Haiku

Explore 預設並不是由 Haiku 驅動。若想用較低成本的模型來探索，請在 `.claude/agents/`（專案）或 `~/.claude/agents/`（使用者）中定義一個名為 `Explore` 的 subagent。它會覆蓋內建版本，並使用自己的 `model`：

```markdown
---
name: Explore
description: Fast read-only codebase search. Use for finding files, symbols, and patterns.
tools: Read, Grep, Glob
model: haiku
---

You are a read-only search agent. Find what was asked, cite file paths and
line numbers, and return a short summary. Never modify files.
```

### Plan Agent

Claude 在 plan mode（用 `Shift+Tab` 切換）中會使用內建的 **Plan** Agent，在提出計畫前先研究你的程式碼庫。它是唯讀的、使用主對話的模型，你很少需要直接呼叫它。

### general-purpose Agent

用於同時需要探索與行動的複雜多步驟任務。它擁有 subagent 可用的所有工具，除非呼叫時傳入 `model`，否則使用主對話的模型。

```javascript
Agent({
  subagent_type: "general-purpose",
  description: "Implement profile editing",
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

### 自訂 Agents

本節的 Agents **並非 Claude Code 內建**。每一個都是自訂 subagent：一個帶有 YAML frontmatter 的 Markdown 檔案，Claude 可以依名稱委派給它。取得方式有兩種：

- **安裝外掛。** [Director Mode Lite](https://github.com/claude-world/director-mode-lite) 提供 `code-reviewer`、`debugger` 和 `doc-writer`：執行 `/plugin marketplace add claude-world/director-mode-lite`，再執行 `/plugin install director-mode-lite@director-mode-lite`。外掛提供的 Agents 會以帶命名空間的名稱出現，例如 `director-mode-lite:code-reviewer`。
- **自己定義**在 `.claude/agents/<name>.md`（此專案；提交到版本控制即可與團隊共享）或 `~/.claude/agents/<name>.md`（你的所有專案）。也可以直接請 Claude 建立：「在 .claude/agents/ 建立一個 security-auditor agent，它會……」。

```markdown
---
name: security-auditor
description: Security specialist for auth, payments, and data handling. Use proactively after changes to security-sensitive code.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a security auditor. Check the changed code against the OWASP Top 10,
report each finding with severity and file:line, and suggest a concrete fix.
```

以下範例使用一般名稱，假設每個 Agent 都定義在 `.claude/agents/` 中。呼叫時傳入的 `model` 會在該次呼叫中覆蓋 Agent 自己的 `model:`。所有 frontmatter 欄位請見 [Designing Agents](../designing-agents.md)。

#### code-reviewer

專門處理程式碼品質和最佳實踐。

```javascript
Agent({
  subagent_type: "code-reviewer",
  description: "Review auth changes",
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

#### security-auditor

對於驗證、支付和資料處理程式碼至關重要。

```javascript
Agent({
  subagent_type: "security-auditor",
  description: "Audit auth module",
  model: "opus",  // 關鍵程式碼：單次呼叫覆蓋模型
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

#### test-runner

處理測試執行和覆蓋率分析。

```javascript
Agent({
  subagent_type: "test-runner",
  description: "Run auth tests",
  prompt: `
    Run all tests related to user authentication.
    Report:
    - Pass/fail status
    - Coverage percentage
    - Failed test details
  `
})
```

#### debugger

系統性根本原因分析。

```javascript
Agent({
  subagent_type: "debugger",
  description: "Debug checkout TypeError",
  prompt: `
    Investigate: TypeError: Cannot read 'id' of undefined
    at CheckoutForm.handleSubmit (checkout.tsx:45)

    Context: Error occurs when submitting with empty cart.

    Find root cause and suggest fix.
  `
})
```

#### refactor-assistant

改進程式碼但不改變功能。

```javascript
Agent({
  subagent_type: "refactor-assistant",
  description: "Refactor helpers module",
  prompt: `
    Refactor utils/helpers.ts:
    - Split into focused modules
    - Remove dead code
    - Improve naming
    - Add TypeScript types
  `
})
```

#### doc-writer

建立和更新文件。

```javascript
Agent({
  subagent_type: "doc-writer",
  description: "Document user API",
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

彼此獨立的 Agents 會同時執行。Claude 從主對話產生的 subagent 會在背景啟動，所以它們執行時你可以繼續工作（預設最多同時 20 個）。

### 模式 1：分析蜂群

啟動 5 個 Explore Agents 進行全面分析：

```javascript
// 全部平行執行
Agent({ subagent_type: "Explore", description: "Map auth files",
  prompt: "Map auth file structure (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Find JWT patterns",
  prompt: "Find JWT patterns (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Analyze middleware",
  prompt: "Analyze middleware (thoroughness: medium)" })
Agent({ subagent_type: "Explore", description: "Check auth tests",
  prompt: "Check auth tests (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Review recent changes",
  prompt: "Review recent changes (thoroughness: quick)" })
```

### 模式 2：實作 + 審查

先建構，再平行驗證：

```javascript
// 階段 1：實作
Agent({
  subagent_type: "general-purpose",
  description: "Implement profile feature",
  model: "sonnet",
  prompt: "Implement user profile feature"
})

// 階段 2：平行審查（在階段 1 之後）
Agent({ subagent_type: "code-reviewer", description: "Review code quality",
  prompt: "Review code quality" })
Agent({ subagent_type: "security-auditor", description: "Security review",
  prompt: "Security review" })
Agent({ subagent_type: "test-runner", description: "Run tests",
  prompt: "Run and analyze tests" })
```

### 模式 3：多檔案重構

將工作分配給多個 Agents：

```javascript
// 每個 Agent 處理一個檔案
Agent({ subagent_type: "general-purpose", description: "Refactor checkout.ts",
  model: "sonnet", prompt: "Refactor payment/checkout.ts to new pattern" })
Agent({ subagent_type: "general-purpose", description: "Refactor subscription.ts",
  model: "sonnet", prompt: "Refactor payment/subscription.ts to new pattern" })
Agent({ subagent_type: "general-purpose", description: "Refactor refund.ts",
  model: "sonnet", prompt: "Refactor payment/refund.ts to new pattern" })
Agent({ subagent_type: "general-purpose", description: "Update payment types",
  model: "sonnet", prompt: "Update payment/types.ts for new pattern" })
```

可能修改相同檔案的 Agents 不應共用同一份工作目錄。傳入 `isolation: "worktree"` 讓每個 Agent 在自己的暫時 git worktree 中工作（預設從你的預設分支建立，而非目前的 `HEAD`），或使用內建的 `/batch` skill，它會把大型變更拆成獨立單元，每個單元在各自的 worktree 中執行。

### 模式 4：Bug 調查

平行假設測試：

```javascript
Agent({ subagent_type: "Explore", description: "Check session changes",
  prompt: "Search for session handling changes (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Look for race conditions",
  prompt: "Check for race conditions (thoroughness: medium)" })
Agent({ subagent_type: "Explore", description: "Review error logs",
  prompt: "Review error logs (thoroughness: quick)" })
Agent({ subagent_type: "Explore", description: "Find timeout configs",
  prompt: "Find timeout configurations (thoroughness: quick)" })

// Explore 的結果回來後，Claude 再把它們交給下一個 Agent
Agent({ subagent_type: "debugger", description: "Find root cause",
  prompt: "Analyze most likely root cause from exploration" })
```

## 模型選擇

| 任務類型 | 模型 | 成本 | 速度 |
|----------|------|------|------|
| 快速搜尋 | Haiku 5.5 | $ | 最快 |
| 模式匹配 | Haiku 5.5 | $ | 最快 |
| 測試執行 | Haiku 5.5 | $ | 最快 |
| 簡單文件 | Haiku 5.5 | $ | 最快 |
| 程式碼審查 | Sonnet 5.5 | $$ | 快 |
| 實作 | Sonnet 5.5 | $$ | 快 |
| 除錯 | Sonnet 5.5 | $$ | 快 |
| 安全稽核 | Sonnet 5.5 / Opus 5.5 | $$-$$$ | 快-中等 |
| 架構設計 | Opus 5.5 | $$$ | 中等 |
| 高難度長時程工作 | Fable 5.1 | $$$$ | 較慢 |

**關鍵權衡**（官方描述；API 價格以每百萬輸入/輸出 tokens 計）：
- Haiku 5.5：「for high-volume, latency-sensitive tasks such as classification, extraction, and routing」（自 $0.10 / $0.50 起）
- Sonnet 5.5：「the best combination of speed and intelligence」（$2 / $10）
- Opus 5.5：「for long-running agentic coding and knowledge work」（$4 / $20）；是 Claude Code 在 Pro、Max、Team、Enterprise 與 API 帳戶上的預設模型，因此除非你另外指定，subagent 也會沿用它
- Fable 5.1：「for demanding reasoning and long-horizon agentic work」；永遠不是預設模型，需以 `/model fable` 選擇（在部分方案中會計入 usage credits）

## 背景 Agents

Claude 從主對話產生的 subagent 本來就會在背景啟動。用於長時間執行的任務：

```javascript
Agent({
  subagent_type: "security-auditor",
  description: "Full security audit",
  model: "opus",
  prompt: "Comprehensive security audit of entire codebase",
  run_in_background: true
})
```

查看背景工作：
- `/tasks` 列出背景工作（包含剛完成的 subagent），並顯示每個 subagent 的模型與強度等級
- 輸入框下方的 subagent 面板會顯示執行中的 Agents；打開某一列即可閱讀它的對話紀錄
- `Ctrl+B` 把前景執行中的任務或 Agent 移到背景
- 每個背景 Agent 的結果會以完成通知的形式送達 Claude，Claude 再向你回報

## 最佳實踐

### 1. 選擇正確的 Agent

```
檔案搜尋       → Explore（內建）
實作           → general-purpose（內建，sonnet）
程式碼品質     → code-reviewer（自訂，sonnet）
安全           → security-auditor（自訂，sonnet/opus）
測試           → test-runner（自訂，haiku/sonnet）
Bug            → debugger（自訂，sonnet）
清理           → refactor-assistant（自訂，sonnet）
文件           → doc-writer（自訂，haiku/sonnet）
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

subagent 會以全新的上下文視窗啟動：它看到的是 Claude 為它撰寫的提示（以及你的 CLAUDE.md，Explore 和 Plan 除外），而不是你的對話內容。

```javascript
Agent({
  subagent_type: "general-purpose",
  description: "Migrate user service",
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
Agent({ ..., prompt: "Analyze file A" })
Agent({ ..., prompt: "Analyze file B" })
Agent({ ..., prompt: "Analyze file C" })
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
| 匹配模型與任務 | Haiku 用於搜尋、Sonnet 用於實作、Opus 用於最困難的推理 |
| 保持提示聚焦 | 每個 Agent 一個明確目標 |
| 串連相依工作 | 階段 1 → 階段 2 → 階段 3 |

---

**相關：**
- [Parallel Agents](../../concepts/zh-TW/parallel-agents.md) - 平行模式深入探討
- [Designing Agents](../designing-agents.md) - 撰寫你自己的自訂 Agents（英文）
- [Multi-Agent Patterns](https://claude-world.com/articles/multi-agent-patterns) - 進階編排

返回 [README](../../README.zh-TW.md)
