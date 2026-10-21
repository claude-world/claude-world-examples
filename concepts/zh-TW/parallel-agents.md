# Parallel Agents

> 為什麼一次做一件事，當你可以同時做五件？

## 循序工作的問題

傳統的 AI 助手工作流程：

```
步驟 1：搜尋檔案（5 秒）
步驟 2：讀取檔案 A（3 秒）
步驟 3：讀取檔案 B（3 秒）
步驟 4：搜尋模式（5 秒）
步驟 5：分析結果（5 秒）

總計：21 秒（循序）
```

## Parallel Agents 解決方案

Claude Code 可以透過 Agent 工具（以前稱為 Task）同時啟動多個 subagents。每個 subagent 在自己的 context window 中工作，最後回報摘要：

```
Agent 1：搜尋檔案         ─┐
Agent 2：讀取檔案 A       ─┼─ 全部同時執行
Agent 3：讀取檔案 B       ─┤
Agent 4：搜尋模式         ─┤
Agent 5：分析程式碼庫      ─┘

總計：5 秒（平行）= max(個別時間)
```

**結果**：同樣的工作大約快 4 倍，而且主對話只會收到摘要。

Claude 從主對話啟動的 subagents 預設在背景執行，所以它們執行時你可以繼續工作。按 `Ctrl+B` 可以把執行中的任務移到背景，`/tasks` 可以查看每個 subagent 的模型與狀態。預設最多可以同時執行 20 個 subagents（用 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` 調整上限）。

## 何時使用 Parallel Agents

### 好的使用情境

1. **探索程式碼庫**
   - Agent 1：找出所有 TypeScript 檔案
   - Agent 2：搜尋 API routes
   - Agent 3：尋找測試檔案
   - Agent 4：檢查設定檔

2. **Bug 追蹤**
   - Agent 1：搜尋錯誤訊息
   - Agent 2：檢查最近的 git commits
   - Agent 3：尋找相關測試
   - Agent 4：找出類似的程式碼模式

3. **程式碼審查**
   - Agent 1：檢查安全問題
   - Agent 2：分析測試覆蓋率
   - Agent 3：審查程式碼風格
   - Agent 4：檢查文件

4. **功能規劃**
   - Agent 1：分析現有架構
   - Agent 2：找出類似功能
   - Agent 3：檢查依賴
   - Agent 4：審查 API 慣例

### 何時不要使用

- 任務依賴前一個結果
- 簡單的單檔案操作
- 需要維持嚴格順序時
- 多個 agents 同時編輯相同檔案（為每個 agent 設定 `isolation: "worktree"`，或依序編輯）

## 實際運作方式

### 範例：尋找 Bug

你說：
```
「使用者驗證有 bug - 使用者會隨機被登出」
```

Claude 啟動 5 個平行的 subagents：

```
Agent 1（Explore）：分析 auth 模組結構
Agent 2（Explore）：搜尋「logout」和「session」
Agent 3（Explore）：搜尋 token 過期邏輯
Agent 4（Explore）：檢查 auth middleware
Agent 5（general-purpose）：用 git log 查看最近 auth 相關的 commits
```

Grep、Read、Bash 是每個 subagent 使用的工具；Explore 與 general-purpose 才是 agent 類型。五項調查會同時進行，而不是一個接一個。

Claude 然後綜合：
```
「找到問題：在 auth/middleware.ts:47，token
過期檢查使用 < 而非 <=，導致 tokens
提早 1 秒過期。這是修復方式...」
```

### 範例：新增功能

你說：
```
「新增密碼重設功能」
```

Claude 啟動平行研究：

```
Agent 1：檢查現有的 email 服務
Agent 2：審查 user model 和 auth 模式
Agent 3：尋找類似流程（註冊、驗證）
Agent 4：檢查 API route 慣例
Agent 5：審查測試模式
```

然後帶著你程式碼庫模式的完整脈絡來實作。

## 最佳實踐

### 1. 給出清晰、完整的任務

**不好**：「幫我理解程式碼」

**好**：「分析使用者驗證如何運作，包含登入流程、session 管理和 token 刷新邏輯」

### 2. 信任流程

讓 subagents 完成工作，再讓 Claude 綜合結果。它們在背景執行，所以你可以繼續工作，或用 `/tasks` 查看進度，而不必打斷它們。

### 3. 在 CLAUDE.md 提供脈絡

你的 CLAUDE.md 越好，parallel agents 就越聰明：

```markdown
## 關鍵區域

### 驗證（/lib/auth）
- JWT 為基礎，帶 refresh tokens
- Middleware 在 /middleware/auth.ts
- User model 在 /prisma/schema.prisma

### API Routes（/app/api）
- RESTful 慣例
- 錯誤處理在 /lib/errors.ts
- 使用 Zod 驗證
```

## 效率數學

| 方式 | 5 個任務 × 每個 5 秒 |
|----------|---------------------|
| 循序 | 25 秒 |
| 平行 | 5 秒 |
| **加速** | **5x** |

對於有許多獨立子任務的複雜任務，加速幅度會隨 agents 數量增加，直到達到同時執行的上限。每個 subagent 也會消耗自己的 tokens，所以平行化是用成本換取時間。需要彼此協調的長時間平行工作，請參考 agent teams（實驗性，`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）。

## 總結

1. Claude Code 可以平行執行多個 subagents，預設在背景執行
2. 用於探索、bug 追蹤、程式碼審查和功能規劃
3. 提供清晰的脈絡讓 agents 更聰明
4. 信任流程 - 不要微觀管理

---

回到 [README](../../README.zh-TW.md)
