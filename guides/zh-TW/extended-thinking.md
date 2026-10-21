# Extended Thinking 指南

> 解鎖更深層的推理，用於架構決策、安全稽核和複雜問題解決

## 快速參考

| 模型 | Thinking | Claude Code 中的預設強度 | 強度等級 |
|------|----------|--------------------------|----------|
| **Opus 5.5** | 永遠開啟（自適應） | `medium` | low / medium / high / xhigh / max |
| **Sonnet 5.5** | 永遠開啟（自適應） | `medium` | low / medium / high / xhigh / max |
| **Haiku 5.5** | 永遠開啟（自適應） | `medium` | low / medium / high / xhigh / max |
| **Fable 5.1** | 永遠開啟（自適應） | `high` | low / medium / high / xhigh / max |

在目前的模型上，你不需要開關 thinking。你設定的是**強度等級（effort）**，模型會在每一步自行決定是否思考、思考多少。

## 什麼是 Extended Thinking？

Extended thinking 是 Claude 回應前所做的推理。目前的模型使用**自適應推理**：簡單的步驟快速回答，困難的步驟深入推理，而強度等級會調整兩者之間的平衡。

```
一般模式：
┌────────┐       ┌──────────┐
│ Prompt │  ───► │ Response │
└────────┘       └──────────┘

Extended Thinking：
┌────────┐    ┌──────────────────┐    ┌──────────┐
│ Prompt │ ─► │ Internal Reason  │ ─► │ Response │
└────────┘    │ (deeper thinking)│    └──────────┘
              └──────────────────┘
```

## 控制 Thinking

### 方法 1：/effort（主要控制方式）

```
/effort          → open the effort slider
/effort high     → set a level for this model (saved as your default)
/effort auto     → clear your saved level
```

你也可以在 `/model` 選單中用左右方向鍵調整強度。Session 標題會顯示目前的等級，例如 "with medium effort"。

### 方法 2：啟動時設定

```bash
claude --effort xhigh                  # this session only
CLAUDE_CODE_EFFORT_LEVEL=high claude   # overrides settings and frontmatter
```

### 方法 3：設定檔

`.claude/settings.json`：
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "effortLevel": "high"
}
```

`effortLevel` 接受 `low`、`medium`、`high` 或 `xhigh`；`max` 不會被儲存，只套用在單一 session。用 `/effort` 選擇等級時，Claude Code 會依模型把它存在使用者設定的 `modelSettings` 底下。

### 方法 4：單次使用 `ultrathink`

```
"ultrathink: why does this cache invalidation fail under concurrent writes?"
```

在 prompt 任何位置加入 `ultrathink`，就能在那一輪要求更深入的推理，而不改變你的強度設定。"think hard" 或 "think more" 等其他說法只是一般文字，不是關鍵字。

### 方法 5：Skill 與 Subagent 的 Frontmatter

Skill 或 subagent 可以帶有自己的等級，在它執行期間生效：

```markdown
---
name: security-reviewer
description: Reviews authentication and payment code for vulnerabilities
model: opus
effort: max
---

Review the code you are given for security issues and report findings with severity levels.
```

### 關閉 Thinking（僅限舊模型）

Opus 5.5、Sonnet 5.5、Haiku 5.5 與 Fable 模型永遠會思考。`Option+T`（macOS）/ `Alt+T`（Windows/Linux）、`/config` 中的 thinking 開關（`alwaysThinkingEnabled`）以及 `MAX_THINKING_TOKENS=0`，只影響 Opus 4.6、Sonnet 4.6 等舊模型。要在目前的模型上減少思考，請降低強度。

Thinking 預設會折疊。按 `Ctrl+O` 開啟 transcript 檢視器閱讀內容。按 `Option+P`（macOS）或 `Alt+P`（Windows/Linux）可以在不清除 prompt 的情況下切換模型。

## 強度等級

| 強度 | 使用情境 |
|--------|----------|
| `low` | 逐步檢視結果的快速互動：腦力激盪、初稿、重新命名 |
| `medium` | 5.5 模型的預設：範圍明確的日常工作 |
| `high` | 需要驗證的工作，例如修正既有程式碼庫中的 bug |
| `xhigh` | 以更多 token 換取更深入的推理：架構與取捨分析 |
| `max` | 希望 Claude 自行處理到底的困難問題，例如尋找安全漏洞 |

`max` 可能出現報酬遞減，也容易過度思考，廣泛採用前請先測試。**Ultracode** 是另一個設定（`/effort ultracode`），不是強度等級：它會讓 Claude 在目前強度下，為重要任務編排動態工作流程。

### 設定強度等級

**在 prompts 中：** prompt 無法改變等級，但 Claude 會在等級範圍內遵循指引：
```
"This one matters. Take the time to check edge cases before you answer."
```
要改變等級本身，請用 `/effort`，或單次使用 `ultrathink`。

**用於 subagent：**
```javascript
// Conceptual: Claude makes this call when you ask for a high-effort subagent
Agent({
  subagent_type: "general-purpose",
  description: "Design payment architecture",
  model: "opus",
  effort: "high",
  prompt: `
    Design the payment processing architecture.
    Consider all edge cases and failure modes.
  `
})
```

## 何時提高強度

### 高價值情境

| 情境 | 強度 | 原因 |
|----------|--------|-----|
| 架構決策 | xhigh | 避免數月的重工 |
| 安全審查 | max | 及早發現漏洞 |
| 複雜重構 | high | 更好的設計模式 |
| Bug 調查 | high | 更快找到根本原因 |
| 取捨分析 | xhigh | 有依據的決策 |

### 以下情況保持低強度

- 檔案搜尋（使用 Explore subagent）
- 模式比對
- 簡單的程式碼變更
- 文件更新
- 例行測試

## Extended Thinking 模式

### 模式 1：架構決策

```
/effort xhigh

"Design the real-time notification system.
Requirements:
- 100K concurrent users
- <100ms delivery latency
- Support mobile and web
- Handle offline users

Analyze options and recommend architecture."
```

### 模式 2：安全稽核

```
/model opus
/effort max

"Review authentication.

Check for:
- OWASP Top 10 vulnerabilities
- JWT best practices
- Session management issues
- Rate limiting gaps

Report findings with severity levels."
```

### 模式 3：取捨分析

```
"ultrathink about this decision.

Option A: Monolith with modular structure
Option B: Microservices from start

Context:
- 3-person team
- MVP stage
- Unknown scale requirements

Analyze both with pros, cons, and recommendation."
```

### 模式 4：複雜除錯

```
"ultrathink: analyze this production issue.

Symptoms:
- Response time: 50ms → 2s at 500 RPS
- CPU: 30%, Memory: 60%
- Database connections spike
- No errors in logs

Identify potential causes and investigation steps."
```

### 模式 5：遷移規劃

```
/effort high

"Create migration plan from MongoDB to PostgreSQL.

Current state:
- 50 collections
- 10M documents
- 5 dependent services
- Zero downtime requirement

Deliverables:
1. Migration strategy
2. Schema design
3. Service update plan
4. Rollback strategy
5. Testing approach"
```

## Extended Thinking 與 Agents

### 依任務選擇模型與強度

```
Explore Agents：     主模型，或 model: haiku 的自訂 Explore - 速度
實作：               Sonnet，medium 強度 - 平衡
關鍵審查：           Opus，high 或 max 強度 - 品質
```

Subagents 會繼承主對話的 thinking 設定。Explore 使用主對話的模型；要用 Haiku 探索，請定義一個名為 `Explore`、設定 `model: haiku` 的專案 subagent。

### Explore Agent

```javascript
Agent({
  subagent_type: "Explore",
  description: "Find authentication patterns",
  prompt: "Find authentication patterns (thoroughness: medium)"
})
```

**幾乎不需要思考** - 單純的搜尋與探索。

### 實作 Agent（Sonnet，Medium 強度）

```javascript
Agent({
  subagent_type: "general-purpose",
  description: "Implement OAuth PKCE flow",
  model: "sonnet",
  effort: "medium",
  prompt: `
    Implement OAuth 2.0 with PKCE flow.
    Consider:
    - State management
    - Token storage
    - Refresh handling
    - Error recovery
  `
})
```

### 審查 Agent（Opus，Max 強度）

```javascript
Agent({
  subagent_type: "security-auditor", // a custom agent in .claude/agents/, not built in
  description: "Review payment security",
  model: "opus",
  effort: "max",
  prompt: `
    Security review the payment integration.
    Check for:
    - PCI compliance issues
    - Data exposure risks
    - Authentication bypasses
  `
})
```

### 多階段搭配 Thinking

設計時深入推理，執行時追求速度：

```
階段 1（Opus，xhigh 強度）：
- 設計遷移策略
- 規劃架構

階段 2（Sonnet，medium 強度）：
- 實作每個遷移步驟
- 撰寫測試

階段 3（Haiku，low 強度）：
- 平行執行測試
- 產生報告
```

## Context 影響

**重要：** Thinking tokens 會以 output 計費，即使內容是折疊的。

```
較低強度：
├── 每一步的 thinking tokens 較少
├── 回應較快
└── 成本較低

較高強度：
├── 每一步有更多推理與自我檢查
├── 回應較慢、tokens 較多
└── Session 中途切換等級或模型時，會在沒有 prompt cache 的情況下重送 context
```

**建議：** 依任務選擇等級，避免在同一個 session 中來回切換強度。

### 監控 Context 使用量

- `/context` 顯示 context window 被什麼佔用
- `/usage` 顯示方案用量與限制
- Session 標題會顯示強度等級，自訂的 status line 也可以顯示（`/statusline`）

長時間 session 處理例行工作時，請降低強度：
```
/effort low
```

## 設定

### 透過 /effort 與 /model

`/effort` 設定等級；`/model` 選擇模型，並有自己的強度滑桿。兩者都會立即生效，並為該模型保存你的選擇。

### 專案設定

```json
{
  "model": "sonnet",
  "effortLevel": "medium"
}
```

### 為敏感程式碼自動提高強度

Claude Code 沒有觸發 thinking 的關鍵字設定，但 skill 可以做到類似效果：設定 `paths`，讓 Claude 在處理符合的檔案時載入它，再設定在 skill 啟用期間生效的 `effort`。

```markdown
---
name: sensitive-code-review
description: Deep review for authentication, payment, and admin code. Use when changing files in these areas.
paths:
  - "src/auth/**"
  - "src/payment/**"
  - "src/admin/**"
effort: max
---

Before finishing a change in these directories, check it for OWASP Top 10 issues,
authorization gaps, and secrets in code. Report findings with severity levels.
```

## 成本效益矩陣

| 情境 | 建議強度 | 品質提升 | ROI |
|----------|------------------|--------------|-----|
| 架構決策 | xhigh | 避免數月的重工 | 非常高 |
| 安全審查 | max | 發現漏洞 | 非常高 |
| 複雜重構 | high | 更好的設計 | 高 |
| Bug 調查 | high | 更快找到根本原因 | 高 |
| 例行程式撰寫 | low 或 medium | 些微改善 | 低 |

## 最佳實踐

### 1. 明確表達

**好的：**
```
"ultrathink: review this authorization middleware for privilege escalation."
```

**模糊的：**
```
"Analyze this code."
```

### 2. 提供豐富的脈絡

```
"Design the caching layer.

Context:
- Current: No caching, 200ms average response
- Goal: <50ms for 80% of requests
- Constraints: Redis available, 5GB memory budget
- Traffic: 10K RPM, 80% reads

Consider cache invalidation and stampede prevention."
```

### 3. 要求結構化輸出

```
"Think through this architecture decision.

Output format:
1. Options considered (3-5)
2. Evaluation criteria
3. Analysis matrix
4. Recommendation with rationale
5. Risk assessment"
```

### 4. 依任務選擇模型與強度

| 任務類型 | 模型 | 強度 |
|-----------|-------|--------|
| 快速搜尋 | Haiku（自訂 Explore） | low |
| 一般程式碼 | Sonnet | medium |
| 複雜邏輯 | Sonnet | high |
| 關鍵審查 | Opus | high 或 max |
| 架構 | Opus | xhigh |

### 5. 分階段工作

```
高風險決策 → Opus，xhigh 強度
實作 → Sonnet，medium 強度
驗證 → Haiku 平行 agents，low 強度
```

## 常見錯誤

### 錯誤 1：所有事情都用最高強度

```
❌ 檔案搜尋用 max 強度
❌ 簡單編輯用 max 強度
❌ 執行測試用 max 強度

✅ 速度型任務用 low 強度與 Explore
✅ 把 high、xhigh、max 留給重要的決策
```

### 錯誤 2：沒有提供脈絡

```
❌ "Design authentication."

✅ "Design authentication for:
   - 100K users
   - Mobile + web
   - OAuth + email/password
   - HIPAA compliance required"
```

### 錯誤 3：忽略強度等級

```
❌ 永遠使用預設強度

✅ Low 強度：批次操作
✅ Medium 強度：開發任務
✅ High 或 xhigh 強度：架構、棘手的 bug
✅ Max 強度：安全稽核
```

## 總結

| 原則 | 行動 |
|-----------|--------|
| 選擇性使用 | 只為高價值決策提高強度 |
| 依任務選擇模型 | Haiku → Sonnet → Opus |
| 提供脈絡 | 脈絡越多，思考越好 |
| 要求結構 | 要求格式化的輸出 |
| 監控 context | 長時間 session 注意用量 |

---

**相關：**
- [Agents 指南](./agents-guide.md) - 搭配 thinking 使用 agents
- [Extended Thinking 文章](https://claude-world.com/articles/extended-thinking-guide) - 完整深入解析
- [模型設定](https://code.claude.com/docs/en/model-config) - 官方強度與 thinking 參考

返回 [README](../../README.zh-TW.md)
