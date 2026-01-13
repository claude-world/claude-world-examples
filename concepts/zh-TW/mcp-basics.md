# MCP 基礎

> Model Context Protocol (MCP) 透過連接外部工具、資料庫和服務來擴展 Claude Code 的能力。

## 什麼是 MCP？

MCP 是 Claude Code 的外掛系統。把 MCP servers 想成給 Claude 超越基本能力的外掛：

- **存取外部資料來源**（資料庫、APIs、檔案系統）
- **執行專業工具**（Git、套件管理器、雲服務）
- **維護持久脈絡**（memory、知識圖譜）
- **整合開發工具**（IDEs、CI/CD、專案管理）

## MCP 架構

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code CLI                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │                 MCP Client                       │    │
│  │  管理與 MCP servers 的連線                        │    │
│  └─────────────────────────────────────────────────┘    │
│            │              │              │               │
│            ▼              ▼              ▼               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ MCP Server 1 │ │ MCP Server 2 │ │ MCP Server 3 │     │
│  │ (filesystem) │ │   (memory)   │ │    (git)     │     │
│  └──────────────┘ └──────────────┘ └──────────────┘     │
│            │              │              │               │
│            ▼              ▼              ▼               │
│      本地檔案         知識圖譜        Git Repository        │
└─────────────────────────────────────────────────────────┘
```

## 新增 MCP Servers

請務必使用官方 CLI 方法：

```bash
# 基本語法
claude mcp add --scope <scope> <name> [options] -- <command>

# Scopes：
# --scope user     → ~/.claude/settings.json（所有專案）
# --scope project  → .claude/settings.json（此專案）

# 環境變數使用 -e flag：
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory
```

> **注意：** `-e` flag 為 MCP server 設定環境變數。可使用多個 `-e` flags 設定多個變數。

## 基本 MCP Servers

### 1. 檔案系統存取

```bash
claude mcp add --scope project filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem .
```

**能力：** 讀寫檔案、建立目錄、列出內容、檔案搜尋

### 2. Memory（知識圖譜）

```bash
# 重要：務必使用 MEMORY_FILE_PATH 做專案隔離
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.json \
  -- npx -y @modelcontextprotocol/server-memory
```

**能力：** 持久化知識儲存、跨 session 記憶、語意搜尋

**警告：** 沒有 `MEMORY_FILE_PATH`，所有專案會共用同一個 memory！

### 3. Git 操作

```bash
claude mcp add --scope project git \
  -- npx -y @modelcontextprotocol/server-git
```

**能力：** Git status、log、diff、branch 操作、file blame

### 4. GitHub 整合

```bash
claude mcp add --scope user github \
  -e GITHUB_TOKEN=<your-token> \
  -- npx -y @modelcontextprotocol/server-github
```

**能力：** Issues、PRs、repository 管理、程式碼搜尋

### 5. Sequential Thinking

```bash
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

**能力：** 結構化推理、多步驟分析、複雜問題分解

### 6. Context7（即時文件）

```bash
claude mcp add --scope user context7 \
  -- npx -y context7-mcp
```

**能力：** 即時官方文件、最新的函式庫參考

## 資料庫 MCP Servers

### PostgreSQL

```bash
claude mcp add --scope project postgres \
  -e DATABASE_URL="postgresql://user:pass@localhost:5432/db" \
  -- npx -y @modelcontextprotocol/server-postgres
```

### SQLite

```bash
claude mcp add --scope project sqlite \
  -e DATABASE_PATH="./data/app.db" \
  -- npx -y @modelcontextprotocol/server-sqlite
```

### MongoDB

```bash
claude mcp add --scope project mongodb \
  -e MONGODB_URI="mongodb://localhost:27017/db" \
  -- npx -y @modelcontextprotocol/server-mongodb
```

## MCP Scope 層級

MCP servers 遵循 Claude Code 的四層層級：

```
┌─────────────────────────────────────────────┐
│  Layer 1: Enterprise                         │
│  位置: /etc/claude-code/settings.json        │
│  控制: IT 部門（allowlist）                   │
├─────────────────────────────────────────────┤
│  Layer 2: User Global                        │
│  位置: ~/.claude/settings.json               │
│  用途: 個人 MCP servers（github 等）          │
├─────────────────────────────────────────────┤
│  Layer 3: Project                            │
│  位置: .mcp.json（不是 settings.json）        │
│  用途: 專案專用（db、memory）                 │
├─────────────────────────────────────────────┤
│  Layer 4: Project Local                      │
│  位置: .mcp.local.json                       │
│  用途: 個人覆寫（gitignored）                 │
└─────────────────────────────────────────────┘
```

> **重要：** 專案範圍的 MCP servers 存在 `.mcp.json`（不是 `.claude/settings.json`）。使用 `claude mcp add --scope project` 會自動建立/更新正確的檔案。

**優先順序：** Local (.mcp.local.json) > Project (.mcp.json) > User (~/.claude.json) > Enterprise (/etc/claude-code/settings.json)

## MCP Context 成本

每個 MCP server 會消耗 context tokens。請注意：

| MCP Server | 約略 Tokens | 建議 |
|------------|----------------|----------------|
| hubspot | ~1,800 | 小型 |
| netlify | ~2,000 | 小型 |
| figma | ~2,500 | 可接受 |
| notion | 已優化 | 官方 |
| vercel | ~3,000 | 可接受 |
| stripe | ~4,000 | 中型 |
| linear | ~6,200 | 大型 |
| atlassian | ~7,100 | 大型 |
| asana | ~12,800 | 太大 |
| sentry | ~14,000 | 謹慎使用 |

**最佳實踐：** 只啟用你實際在用的 MCP servers。

## 設定檔

> **重要：** 專案 MCP servers 放在 `.mcp.json`，不是 `.claude/settings.json`。請務必使用 `claude mcp add --scope project` 來建立正確的設定。

### 專案 MCP 設定（.mcp.json）

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/memory.json"
      }
    }
  }
}
```

### 使用者全域設定（~/.claude.json）

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## MCP 管理指令

```bash
# 列出所有 MCP servers
claude mcp list

# 新增 server
claude mcp add --scope project <name> -- <command>

# 移除 server
claude mcp remove --scope project <name>

# 檢查 server 狀態
claude mcp status

# 重設專案 MCP 選擇（疑難排解）
claude mcp reset-project-choices
```

## 實際範例

### 資料庫查詢

啟用 postgres MCP 後：

```
使用者：「顯示最近 7 天註冊的使用者」

Claude：[使用 postgres MCP]
  → 查詢：SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'
  → 回傳格式化的結果
```

### 知識持久化

啟用 memory MCP 後：

```
使用者：「記住我們所有 API 驗證都用 Zod」

Claude：[使用 memory MCP]
  → 建立 entity：「API Validation」
  → 加入 observation：「所有 API 驗證都使用 Zod」
  → 在未來的 sessions 可用
```

### GitHub 整合

啟用 github MCP 後：

```
使用者：「為登入 bug 建立一個 issue」

Claude：[使用 github MCP]
  → 建立包含標題、內容、標籤的 issue
  → 連結到相關程式碼
```

## 疑難排解

### Server 未載入

```bash
# 檢查 server 是否已註冊
claude mcp list

# 重設並重新加入
claude mcp reset-project-choices
claude mcp add --scope project <name> -- <command>
```

### 權限問題

確保專案設定中有 `enableAllProjectMcpServers: true`。

### 環境變數問題

在設定檔中使用 `${VAR_NAME}` 語法設定環境變數：

```json
{
  "env": {
    "DATABASE_URL": "${DATABASE_URL}"
  }
}
```

## MCP 與其他工具比較

| 功能 | MCP | 內建工具 | Hooks |
|---------|-----|----------------|-------|
| 外部資料存取 | 主要用途 | 有限 | 否 |
| 持久儲存 | Memory MCP | 僅限 Session | 否 |
| 自訂整合 | 可擴展 | 固定 | 透過指令 |
| Context 成本 | 可變 | 已包含 | 最小 |

## 開始使用

**今天：**
1. 加入 filesystem 和 memory MCP 到你的專案
2. 使用 `MEMORY_FILE_PATH` 做專案隔離
3. 儲存一個重要決策到 memory

**這週：**
1. 如果適用，加入資料庫 MCP
2. 設定 GitHub MCP 做 issue 追蹤
3. 探索 memory 指令（/memory-*）

---

*MCP 將 Claude Code 從獨立的助手轉變為整合的開發平台。*

*參考：[Model Context Protocol](https://modelcontextprotocol.io/) | [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code)*
