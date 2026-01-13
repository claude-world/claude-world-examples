# Extended Thinking 指南

> 解鎖更深層的推理，用於架構決策、安全稽核和複雜問題解決

## 快速參考

| 模型 | Extended Thinking | 預設 | 強度等級 |
|------|-------------------|------|----------|
| **Opus 4.5** | 是 | 開啟（v2.0.67+） | low / medium / high |
| **Sonnet 4.5** | 是 | 關閉 | N/A |
| **Haiku 4.5** | 是 | 關閉 | N/A |

## 什麼是 Extended Thinking？

Extended Thinking（也稱為「Thinking Mode」）讓 Claude 在回應前有更多時間來思考複雜問題。

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

## 啟用 Extended Thinking

### 方法 1：透過 /config

```
Thinking Mode: ON
```

### 方法 2：透過設定

> **注意：** 以下設定顯示概念性配置。實際 Claude Code 設定可能使用不同的屬性名稱。請在 Claude Code 中查看 `/config` 以獲取當前選項。

`.claude/settings.json`：
```json
{
  "model": "opus"
}
```

Thinking mode 通常透過 `/config` 互動式控制，而不是設定檔。

### 方法 3：在提示中

```
"Enable extended thinking for this security analysis."
```

### 方法 4：快速模型切換

在提示時按 `Option+P`（macOS）或 `Alt+P`（Windows/Linux）。

## 強度等級（僅限 Opus 4.5）

| 強度 | 思考深度 | 使用案例 |
|------|----------|----------|
| `low` | 最小 | 快速任務、批次操作 |
| `medium` | 平衡 | 預設，大多數開發任務 |
| `high` | 最大 | 架構、安全、關鍵決策 |

### 設定強度等級

**在提示中：**
```
"Analyze this authentication system with high effort.
I need thorough security analysis."
```

**在 Task 工具中：**
```javascript
Task({
  subagent_type: "general-purpose",
  model: "opus",
  prompt: `
    Effort: high

    Design the payment processing architecture.
    Consider all edge cases and failure modes.
  `
})
```

## 何時使用 Extended Thinking

### 高價值場景

| 場景 | 強度 | 原因 |
|------|------|------|
| 架構決策 | High | 避免數月的返工 |
| 安全審查 | High | 及早發現漏洞 |
| 複雜重構 | Medium | 更好的設計模式 |
| Bug 調查 | Medium | 更快的根本原因分析 |
| 權衡分析 | High | 做出明智決策 |

### 跳過 Thinking 的情況

- 檔案搜尋（使用 Explore Agent）
- 模式匹配
- 簡單程式碼變更
- 文件更新
- 常規測試

## Extended Thinking 模式

### 模式 1：架構決策

```
"Enable high-effort thinking.

Design the real-time notification system.
Requirements:
- 100K concurrent users
- <100ms delivery latency
- Support mobile and web
- Handle offline users

Analyze options and recommend architecture."
```

### 模式 2：安全稽核

```
"Using Opus with high effort, review authentication.

Check for:
- OWASP Top 10 vulnerabilities
- JWT best practices
- Session management issues
- Rate limiting gaps

Report findings with severity levels."
```

### 模式 3：權衡分析

```
"Think deeply about this decision.

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
"Use extended thinking to analyze this production issue.

Symptoms:
- Response time: 50ms → 2s at 500 RPS
- CPU: 30%, Memory: 60%
- Database connections spike
- No errors in logs

Identify potential causes and investigation steps."
```

### 模式 5：遷移規劃

```
"Effort: high

Create migration plan from MongoDB to PostgreSQL.

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

### 依任務選擇模型

```
Explore Agents：     Haiku（無 thinking）- 速度
實作：               Sonnet（可選 thinking）- 平衡
關鍵審查：           Opus（預設 thinking）- 品質
```

### Explore Agent（無 Thinking）

```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: "Find authentication patterns (thoroughness: medium)"
})
```

**不需要 thinking** - 純粹的搜尋和發現。

### 實作 Agent（Sonnet + Thinking）

```javascript
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Enable thinking mode.

    Implement OAuth 2.0 with PKCE flow.
    Consider:
    - State management
    - Token storage
    - Refresh handling
    - Error recovery
  `
})
```

### 審查 Agent（Opus + High Effort）

```javascript
Task({
  subagent_type: "security-auditor",
  model: "opus",
  prompt: `
    Effort: high

    Security review the payment integration.
    Check for:
    - PCI compliance issues
    - Data exposure risks
    - Authentication bypasses
  `
})
```

### 多階段與 Thinking

設計使用 thinking，執行使用速度：

```
階段 1（Opus，high effort）：
- 設計遷移策略
- 規劃架構

階段 2（Sonnet，無 thinking）：
- 實作每個遷移步驟
- 撰寫測試

階段 3（Haiku，無 thinking）：
- 平行執行測試
- 產生報告
```

## 上下文影響

**重要：** Extended Thinking 內部使用額外的 tokens。

```
一般模式：
├── Prompt Cache：高度有效
├── 上下文使用：可預測
└── Token 效率：高

Extended Thinking：
├── Prompt Cache：效果較差
├── 上下文使用：可變
└── Token 效率：較低（但品質更高）
```

**建議：** 選擇性地對高價值決策使用 thinking。

### 監控上下文使用

狀態列（v2.0.65+）：
```
Context: 45% used | Thinking: enabled | Model: opus
```

對於長時間會話，對常規任務禁用 thinking：
```
"Disable thinking for these routine file updates."
```

## 配置

### 透過 /config 指令

配置 thinking mode 的建議方式是透過 `/config` 互動式選單：

```
Thinking Mode: ON / OFF
Model: opus / sonnet / haiku
```

### 專案設定

> **注意：** 以下配置是概念性範例，展示可能的自動化模式。截至 Claude Code 2.1.x，thinking mode 主要透過 `/config` 控制。這些進階配置可能在未來版本或自訂設定中支援。

```json
{
  "model": "sonnet"
}
```

### 概念：自動啟用觸發器

此模式目前在標準 Claude Code 設定中不支援，但說明了自動 thinking 觸發器可能如何運作：

```json
{
  "thinkingTriggers": {
    "keywords": ["security", "architecture", "design"],
    "paths": ["auth/", "payment/", "admin/"],
    "operations": ["create-file", "refactor"]
  }
}
```

> **當前方式：** 使用口語指示如「enable extended thinking for this security analysis」來為特定任務啟用 thinking mode。

## 成本效益矩陣

| 場景 | 時間成本 | 品質提升 | ROI |
|------|----------|----------|-----|
| 架構決策 | +30 秒 | 避免數月返工 | 非常高 |
| 安全審查 | +45 秒 | 發現漏洞 | 非常高 |
| 複雜重構 | +20 秒 | 更好設計 | 高 |
| Bug 調查 | +15 秒 | 更快根因 | 高 |
| 常規程式碼 | +10 秒 | 邊際改善 | 低 |

## 最佳實踐

### 1. 明確表達

**好：**
```
"Enable extended thinking for this security analysis."
```

**模糊：**
```
"Analyze this code."
```

### 2. 提供豐富上下文

```
"Using high-effort thinking, design the caching layer.

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

### 4. 匹配模型與任務

| 任務類型 | 模型 | Thinking |
|----------|------|----------|
| 快速搜尋 | Haiku | OFF |
| 標準程式碼 | Sonnet | OFF |
| 複雜邏輯 | Sonnet | ON |
| 關鍵審查 | Opus | ON（預設） |
| 架構 | Opus | ON + High effort |

### 5. 分階段工作

```
高風險決策 → Opus with thinking
實作 → Sonnet
驗證 → Haiku parallel agents
```

## 常見錯誤

### 錯誤 1：對所有事情使用 Thinking

```
❌ 對檔案搜尋啟用 thinking
❌ 對簡單編輯啟用 thinking
❌ 對測試執行啟用 thinking

✅ 對速度任務使用 Haiku/Explore
✅ 保留 thinking 給重要決策
```

### 錯誤 2：不提供上下文

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
❌ 總是使用預設強度

✅ Low effort：批次操作
✅ Medium effort：開發任務
✅ High effort：架構、安全
```

## 總結

| 原則 | 行動 |
|------|------|
| 選擇性使用 | 僅用於高價值決策 |
| 匹配模型與任務 | Haiku → Sonnet → Opus |
| 提供上下文 | 更多上下文 = 更好思考 |
| 要求結構 | 請求格式化輸出 |
| 監控上下文 | 在長會話中留意使用量 |

---

**相關：**
- [Agents Guide](./agents-guide.md) - 使用 Agents 與 thinking
- [Extended Thinking Article](https://claude-world.com/articles/extended-thinking-guide) - 完整深入探討

返回 [README](../README.md)
