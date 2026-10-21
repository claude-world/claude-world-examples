# Memory 系統基礎

> 用 Claude Code 的內建記憶建立持久的專案智慧，需要明確的知識圖譜時再加入 Memory MCP——再也不會在 sessions 之間遺失脈絡。

## 問題：Session 失憶症

每個 Claude Code session 都是全新開始。之前的決策、bug 修復和架構選擇都被遺忘：

```
Session 1：「我們決定用 Redis 做快取是因為...」
Session 2：「為什麼我們在用 Redis？」
Session 3：[重複同樣的討論]
```

這是**組織記憶失效**。

## 內建記憶：CLAUDE.md 與 Auto Memory

Claude Code 內建兩層記憶，兩者都會在每個 session 開始時載入：

| | CLAUDE.md 檔案 | Auto memory |
|---|---|---|
| **誰撰寫** | 你（或在你要求時由 Claude 撰寫） | Claude 自行撰寫 |
| **內容** | 指示：指令、慣例、架構 | 學到的事：你的偏好、修正、專案脈絡 |
| **位置** | `./CLAUDE.md`、`~/.claude/CLAUDE.md`、`.claude/rules/` | `~/.claude/projects/<project>/memory/` |
| **載入方式** | 每個 session 完整載入 | `MEMORY.md` 索引的前 200 行（或 25KB），主題檔案需要時才讀取 |

- 執行 `/memory` 開啟這些檔案，並開關 auto memory。
- 說「記住我們所有 API 驗證都用 Zod」，Claude 就可以把它存進 auto memory。如果是整個團隊都要遵守的規則，請要求 Claude 寫進 CLAUDE.md。
- Subagents 可以透過 `memory:` frontmatter 欄位（`user`、`project` 或 `local`）保有自己的記憶。

大多數專案這樣就夠了。如何撰寫好的指示，請見 [CLAUDE.md 原則](./claude-md-principles.md)。

## 選用：Memory MCP 知識圖譜

當你想要結構化、可查詢的知識而不是散文時，再加入 Memory MCP server：以 relations 連結的 entities、透過 repository 讓整個團隊共享的圖譜，或是比 200 行索引能容納更多的事實。

Memory MCP 建立一個**持久的知識圖譜**來儲存：

| 元件 | 描述 | 範例 |
|-----------|-------------|---------| 
| **Entities** | 有類型的命名概念 | `authentication_system` |
| **Observations** | 關於 entities 的事實 | 「使用 JWT tokens」 |
| **Relations** | entities 之間的連結 | `auth` → uses → `redis` |

```
┌──────────────────────────────────────────────────┐
│              知識圖譜                             │
│                                                  │
│  ┌─────────────────┐       ┌──────────────────┐  │
│  │ authentication  │──uses─▶│ redis_cache     │  │
│  │                 │       │                  │  │
│  │ Observations:   │       │ Observations:    │  │
│  │ • 使用 JWT      │       │ • v7.2           │  │
│  │ • 24h TTL       │       │ • <1ms 延遲       │  │
│  └─────────────────┘       └──────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

## 快速設定

### 步驟 1：加入 Memory MCP

```bash
# 關鍵：使用 MEMORY_FILE_PATH 做專案隔離
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

**為什麼專案隔離很重要：**
- 沒有 `MEMORY_FILE_PATH`，所有專案共用同一個 memory
- 每個專案應該有自己的知識圖譜
- 提交到 repo = 團隊共享知識

### 步驟 2：驗證

```bash
claude mcp list

# 應該顯示：
# memory: npx -y @modelcontextprotocol/server-memory - ✓ Connected
```

### 步驟 3：初始化

在 Claude Code 中：

```
「儲存初始專案脈絡到 memory」
```

Claude 會建立專案、技術棧和關鍵決策的 entities。

## 核心工具

這個 server 會提供 Claude 以下工具。你不需要自己呼叫：用一般語言提出要求，Claude 會選擇適合的工具。

| 工具 | 描述 |
|---------|-------------|
| `create_entities` / `create_relations` | 儲存新知識到圖譜 |
| `add_observations` | 為既有 entity 加入事實 |
| `search_nodes` | 搜尋名稱、類型與 observations |
| `open_nodes` / `read_graph` | 讀取特定 entities 或整個圖譜 |
| `delete_entities` / `delete_observations` / `delete_relations` | 移除過時的知識 |

內建的 `/memory` 指令管理的是 CLAUDE.md 與 auto memory 檔案，不是這個圖譜。`/memory-save` 或 `/memory-audit` 這類指令只有在 plugin 或你自己的 skills 加入時才存在。

### 用自然語言提出要求

```
「儲存這個決策到 memory：我們選擇 PostgreSQL 是因為支援 JSONB」

「我們對快取策略知道什麼？」

「更新 memory：Token TTL 從 24 小時改為 7 天」
```

## 應該儲存什麼

### 1. 架構決策（最重要）

```
Entity: database_choice
Type: decision
Observations:
- 「選擇 PostgreSQL 是因為支援 JSONB」
- 「曾考慮 MySQL 但需要 JSON 查詢」
- 「決策日期：2026-01-05」
```

**為什麼？** 避免重複討論已決定的主題。

### 2. Bug 修復

```
Entity: auth_timeout_bug
Type: bug_fix
Observations:
- 「問題：使用者 5 分鐘後被登出」
- 「根本原因：Token refresh 競爭條件」
- 「解決方案：Refresh 加上 Mutex」
- 「PR: #234」
```

**為什麼？** 避免重新引入已修復的 bugs。

### 3. 設計模式

```
Entity: error_handling_pattern
Type: pattern
Observations:
- 「非同步操作使用 Result type」
- 「domain layer 永不拋出例外」
- 「只在邊界記錄錯誤」
```

**為什麼？** 確保一致的實作。

### 4. 外部整合

```
Entity: stripe_integration
Type: integration
Observations:
- 「API 版本：2024-11-20」
- 「Webhook：/api/webhooks/stripe」
- 「使用 Stripe Checkout」
```

**為什麼？** 快速參考整合細節。

## Memory 模式

### 模式 1：Session 開始載入

每個 session 開始時載入脈絡：

```
「我們對我正在開發的功能知道什麼？」
```

### 模式 2：立即記錄

做出決策後立即儲存：

```
「儲存這個決策到 memory：我們使用 Redis 做
session 快取是因為它能為 10K+ 並發 sessions
提供亞毫秒級延遲。」
```

### 模式 3：Bug 脈絡

修復 bugs 時：

```
「儲存這個 bug 修復到 memory：登入逾時是由於
token refresh 競爭條件造成的。用 mutex 修復。
檔案：auth/refresh.ts」
```

### 模式 4：每月審計

```
「審計 memory 圖譜：列出過時、重複或互相矛盾的項目」
```

然後清理：
```
「清理關於舊驗證系統的過時 observations」
```

## 知識圖譜結構

server 會把圖譜以 JSON Lines 格式存在 `MEMORY_FILE_PATH`；`read_graph` 會以這個形式回傳：

```json
{
  "entities": [
    {
      "name": "authentication_system",
      "entityType": "component",
      "observations": [
        "使用 JWT tokens 做 stateless 驗證",
        "Tokens 24 小時後過期",
        "實作在 auth/ 目錄"
      ]
    }
  ],
  "relations": [
    {
      "from": "authentication_system",
      "to": "redis_cache",
      "relationType": "uses"
    }
  ]
}
```

## 儲存選項

| 選項 | 路徑 | 使用情境 |
|--------|------|----------|
| **內建 auto memory** | `~/.claude/projects/<project>/memory/` | 每個 repository 的個人學習紀錄（預設開啟，不共享） |
| **專案圖譜**（團隊建議） | `./.claude/memory.jsonl` | 團隊共享，提交到 repo |
| **使用者圖譜** | `~/.claude/memory.jsonl` | 個人模式，跨專案 |
| **混合** | 兩種圖譜 | 專案決策 + 個人偏好 |

## Memory 與 CLAUDE.md 比較

| 使用 CLAUDE.md 做 | 使用 Auto Memory 做 | 使用 Memory MCP 做 |
|-------------------|---------------------|--------------------|
| 靜態政策與規則 | 你的偏好與修正 | 以 entities 連結的決策與理由 |
| 建置與測試指令 | Claude 工作中學到的脈絡 | 之後要查詢的 bug 修復與解決方案 |
| 專案結構 | 會隨時間改變的事實 | 透過 repo 共享的團隊知識 |
| 工作流程定義 | 個人、單機的筆記 | 元件之間的關係 |

**關鍵差異：** CLAUDE.md 每次都完整載入，所以請控制在約 200 行以內。Auto memory 只載入簡短的索引，需要時才讀主題檔案。Memory MCP 圖譜則按需查詢。三者都不會強制執行任何事；必須遵守的規則請用權限或 hooks。

## 最佳實踐

### 1. 立即儲存

```
「現在就儲存這個決策到 memory，趁我們還記得脈絡。」
```

### 2. 要具體

❌ 不好：「使用 PostgreSQL」

✅ 好：「選擇 PostgreSQL 是因為使用者偏好儲存需要 JSONB 支援」

### 3. 包含脈絡

加入「為什麼」而不只是「什麼」：

```
「選擇 Redis 而非 Memcached 是因為我們需要
session 管理的資料結構（lists、sets）」
```

### 4. 使用時間標記

```
Observations:
- 「[2026-01-05] 初始選擇：MySQL」
- 「[2026-01-08] 遷移到 PostgreSQL 使用 JSONB」
```

### 5. 標記信心程度

```
Observations:
- 「[已確認] 驗證使用 JWT」
- 「[假設] Token TTL 是 24 小時（待驗證）」
- 「[過時] 之前使用 session cookies」
```

## 疑難排解

### Memory 沒有持久化

1. 檢查 `MEMORY_FILE_PATH` 設定正確
2. 驗證檔案寫入權限
3. 執行 `claude mcp list` 確認 MCP 啟用中

### 搜尋找不到結果

1. 搜尋是不分大小寫的子字串比對，涵蓋名稱、類型與 observations，所以可以試試更短的詞
2. 使用更廣泛的搜尋詞
3. 檢查 observations 包含搜尋詞

### 重複的 Entities

1. 請 Claude 審計圖譜中的重複項目
2. 合併重複項：「合併 entity A 和 B」
3. 更新 relations 到合併後的 entity

## 與工作流程整合

### 與 /workflow 搭配

`/workflow` 來自社群的 [director-mode-lite](https://github.com/claude-world/director-mode-lite) plugin；任何實作要求都適用同樣的方式：

```
「根據我們現有的模式和決策實作使用者個人資料編輯。」

Claude：
→ 搜尋 memory 找模式、慣例
→ 找到錯誤處理模式、API 慣例
→ 依照已建立的模式實作
```

### 與多 Session 專案搭配

```
第 1 天：「我們在建立支付系統。儲存架構。」
第 2 天：「繼續支付工作。我們昨天決定了什麼？」
第 3 天：「完成支付整合。還剩什麼？」
```

Memory 在所有 sessions 之間提供連續性。

## 開始使用檢查清單

**今天：**
- [ ] 執行 `/memory`，確認 auto memory 已開啟
- [ ] 儲存一個架構決策（寫進 CLAUDE.md 或圖譜）
- [ ] 如果想要共享的知識圖譜，再加入 Memory MCP

**這週：**
- [ ] 建立初始知識圖譜
- [ ] 儲存所有主要決策
- [ ] 整合到日常工作流程

**這個月：**
- [ ] 完整的知識圖譜覆蓋
- [ ] 建立團隊慣例
- [ ] 排程定期的 memory 審計

---

*Memory 將 Claude Code 從無狀態的工具轉變為有知識的夥伴。建立你的知識圖譜，每個 session 都能帶著完整脈絡開始。*

*相關：[Memory System Guide](https://claude-world.com/articles/memory-system-guide) | [MCP 基礎](./mcp-basics.md)*
