# MCP 設定範例

> 常見專案類型與服務的 MCP 設定，可直接複製使用。

## 快速設定：必備 MCP 組合

```bash
# 1. GitHub：issues、PRs、Actions（GitHub 官方遠端 server）
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"

# 2. Context7：最新的函式庫文件
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"

# 3. 選用：專案知識圖譜（重要：使用 MEMORY_FILE_PATH）
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

Claude Code 的內建工具已經能讀寫專案檔案並執行 `git`，內建記憶（CLAUDE.md 加上 auto memory）也會跨 sessions 保留。只有需要更多能力時才加入 filesystem、Git 或 memory servers：存取專案以外的目錄、結構化的 Git 工具，或明確的知識圖譜。

用 `claude mcp list` 驗證，或在 session 中執行 `/mcp` 查看狀態並完成 OAuth 登入。

---

## 依專案類型設定

### Web 應用程式（全端）

```bash
# 資料庫（擇一）
# Supabase / PostgreSQL（官方遠端 server，唯讀）
claude mcp add --scope project --transport http supabase \
  "https://mcp.supabase.com/mcp?project_ref=<project-ref>&read_only=true"

# 自架 PostgreSQL（Postgres MCP Pro，唯讀模式）
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://user:pass@localhost:5432/myapp" \
  -- uvx postgres-mcp --access-mode=restricted

# 瀏覽器自動化，用於 UI 測試
claude mcp add --scope project playwright -- npx -y @playwright/mcp@latest

# GitHub 用於 issue/PR 管理
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"

# Context7 用於最新文件
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"
```

### 純 API 後端

```bash
# 資料庫
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://user:pass@localhost:5432/api" \
  -- uvx postgres-mcp --access-mode=restricted

# 錯誤監控
claude mcp add --scope user --transport http sentry https://mcp.sentry.dev/mcp

# Sequential thinking 用於複雜的 API 設計
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

### 靜態網站 / 文件

```bash
# 最小設定：內建工具處理檔案，再加上文件查詢
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"

# 選用：結構化的 Git 歷史工具
claude mcp add --scope project git -- uvx mcp-server-git --repository .
```

### 資料科學 / ML

```bash
# 資料庫
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://user:pass@localhost:5432/analytics" \
  -- uvx postgres-mcp --access-mode=restricted

claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017/analytics" \
  -- npx -y mongodb-mcp-server --readOnly

# Sequential thinking 用於分析流程
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## 完整設定範例

MCP servers 放在 `.mcp.json`（project scope）或 `~/.claude.json`（local 與 user scope），從來不放在 `settings.json`。設定檔負責這些 servers 的核准與權限。

### 專案 Servers（.mcp.json）

`claude mcp add --scope project` 會寫入這個檔案；提交它，讓團隊共用這些 servers：

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/memory.jsonl"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=${SUPABASE_PROJECT_REF}&read_only=true"
    }
  }
}
```

### 專案設定（.claude/settings.json）

預先核准專案的 servers 並設定工具權限。`mcp__<server>__*` 會符合某個 server 的所有工具：

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "enabledMcpjsonServers": ["memory", "playwright", "supabase"],
  "permissions": {
    "allow": ["mcp__memory__*", "mcp__context7__*"],
    "ask": ["mcp__supabase__*"]
  }
}
```

### 使用者 Servers（~/.claude.json）

`~/.claude.json` 也存放 Claude Code 的其他狀態，所以請用 CLI 加入使用者 servers，不要手動編輯：

```bash
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## 資料庫設定模式

PostgreSQL 與 SQLite 的原始參考實作 server（`@modelcontextprotocol/server-postgres` 與 `server-sqlite`）已封存。請改用有在維護的 server。

### PostgreSQL 搭配 Supabase

```bash
# Supabase 官方 server；加入後透過 /mcp 登入
claude mcp add --scope project --transport http supabase \
  "https://mcp.supabase.com/mcp?project_ref=<project-ref>&read_only=true"
```

**或寫在 `.mcp.json`：**

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=${SUPABASE_PROJECT_REF}&read_only=true"
    }
  }
}
```

### PostgreSQL 本地開發

```bash
# Postgres MCP Pro；restricted 模式只執行唯讀交易
claude mcp add --scope local postgres \
  -e DATABASE_URI="postgresql://postgres:postgres@localhost:5432/myapp_dev" \
  -- uvx postgres-mcp --access-mode=restricted
```

### SQLite 用於原型開發

目前沒有官方維護的 SQLite server。原型階段可以讓 Claude 透過 Bash 使用 `sqlite3` CLI，並用 `Bash(sqlite3 ./data/app.db *)` 這類權限規則允許它。

### MongoDB

```bash
# 本地（MongoDB 官方 server）
claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017/myapp" \
  -- npx -y mongodb-mcp-server --readOnly

# MongoDB Atlas
claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb+srv://user:pass@cluster.mongodb.net/myapp" \
  -- npx -y mongodb-mcp-server --readOnly
```

---

## 雲端服務整合

以下都是各服務商的官方遠端 server。加入後執行 `/mcp` 以 OAuth 登入。

### Vercel

```bash
claude mcp add --scope user --transport http vercel https://mcp.vercel.com
```

**能力：** 部署、專案、日誌、文件搜尋

### Cloudflare

```bash
# Workers、KV、R2 與 D1 bindings
claude mcp add --scope user --transport http cloudflare-bindings https://bindings.mcp.cloudflare.com/mcp

# Cloudflare 文件（不需要登入）
claude mcp add --scope user --transport http cloudflare-docs https://docs.mcp.cloudflare.com/mcp
```

**能力：** Workers、Pages、D1 資料庫、R2 儲存、文件

### Netlify

```bash
claude mcp add --scope user netlify -- npx -y @netlify/mcp
```

**能力：** 部署、表單、functions、環境變數

---

## 團隊/協作 MCP

### Linear（專案管理）

```bash
claude mcp add --scope user --transport http linear https://mcp.linear.app/mcp
```

### Notion

```bash
claude mcp add --scope user --transport http notion https://mcp.notion.com/mcp
```

### Slack

```bash
claude mcp add --scope user --transport http slack https://mcp.slack.com/mcp
```

MCP tool search 預設開啟，Claude Code 只在需要時才載入各 server 的工具定義，所以即使是大型 server 也不會一開始就佔滿 context。但仍然只啟用你會用到的 servers。

---

## Memory 隔離模式

Claude Code 內建的 auto memory 本來就是以 repository 區分（`~/.claude/projects/<project>/memory/`）。以下模式適用於你加入 memory MCP server 的情況。

### 每個專案獨立 Memory（建議）

```bash
# 每個專案有自己的 memory 檔案
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

### 使用者全域 Memory

```bash
# 所有專案共用一個 memory（個人知識）
claude mcp add --scope user memory \
  -e MEMORY_FILE_PATH="$HOME/.claude/global-memory.jsonl" \
  -- npx -y @modelcontextprotocol/server-memory
```

### 混合做法

專案的 `.mcp.json`：

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/project-memory.jsonl"
      }
    }
  }
}
```

個人 server，在 user scope 加入一次即可：

```bash
claude mcp add --scope user personal-memory \
  -e MEMORY_FILE_PATH="$HOME/.claude/personal-memory.jsonl" \
  -- npx -y @modelcontextprotocol/server-memory
```

---

## 環境變數管理

### 使用 .env 檔案

在專案根目錄建立 `.env`（並加入 `.gitignore`）：

```env
DATABASE_URI=postgresql://user:pass@localhost:5432/myapp
GITHUB_PAT=github_pat_xxxxxxxxxxxx
SUPABASE_PROJECT_REF=abcdefghijklmnop
```

在 `.mcp.json` 中引用這些變數。Claude Code 會從啟動它的環境展開 `${VAR}` 與 `${VAR:-default}`，所以請先把 `.env` 載入 shell（例如使用 `direnv`，或 `set -a; source .env; set +a`）：

```json
{
  "mcpServers": {
    "postgres": {
      "command": "uvx",
      "args": ["postgres-mcp", "--access-mode=restricted"],
      "env": {
        "DATABASE_URI": "${DATABASE_URI}"
      }
    }
  }
}
```

### 使用 Shell 環境

```bash
# 先 export
export GITHUB_PAT="github_pat_xxxxxxxxxxxx"

# 再加入 server；CLI 儲存前 shell 會先展開 $GITHUB_PAT
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer $GITHUB_PAT"
```

---

## 驗證與疑難排解

### 驗證設定

```bash
# 列出所有已設定的 MCP servers 與連線狀態
claude mcp list

# 顯示單一 server 的設定
claude mcp get github

# 在 Claude Code session 中
# 執行 /mcp 查看狀態、登入或重新連線
```

### 常見問題與修正

**MCP 未載入：**

```bash
# 重設並重新加入
claude mcp reset-project-choices
claude mcp add --scope project <name> -- <command>
```

**專案 Server 等待核准：**

在啟動提示或 `/mcp` 中核准，或在 `.claude/settings.json` 中列出：
```json
{
  "enabledMcpjsonServers": ["memory", "supabase"]
}
```

**環境變數無效：**

1. 確認變數已在啟動 `claude` 的 shell 中 export（`echo $DATABASE_URI`）
2. 確認 `.mcp.json` 中使用 `${VAR}` 語法（不是 `$VAR`）
3. 修改後重新啟動 Claude Code

**資料庫連線失敗：**

```bash
# 先在 Claude 之外測試連線
psql "$DATABASE_URI"

# 檢查 port 是否可存取
nc -zv localhost 5432
```

---

## 設定檢查清單

### 新專案設定

- [ ] 加入 GitHub 與 Context7 servers（user scope）
- [ ] 若適用，加入資料庫 server（含憑證時用 local scope）
- [ ] 若需要知識圖譜，加入 memory server 並設定 `MEMORY_FILE_PATH`
- [ ] 執行 `claude mcp list` 驗證
- [ ] 在 session 中執行 `/mcp` 登入 OAuth servers

### 團隊導入

- [ ] 在 README 中記錄需要的 MCP servers
- [ ] 提交使用 `${VAR}` 引用、不含 secrets 的 `.mcp.json`
- [ ] 加入列出必要變數的 `.env.example`
- [ ] 把 `.claude/memory.jsonl` 加入 `.gitignore` 或提交（依團隊偏好）

---

## 快速參考

| MCP | Scope | 用途 |
|-----|-------|----------|
| github | user | Issues、PRs、Actions |
| context7 | user | 即時文件 |
| supabase / postgres / mongodb | project 或 local | 資料庫存取 |
| playwright | project | 瀏覽器自動化與 UI 測試 |
| memory | project | 明確的知識圖譜 |
| git | project | 結構化 Git 工具（選用） |
| sequential-thinking | user | 複雜推理 |
| vercel / cloudflare / netlify | user | 部署 |
| linear / notion / slack / sentry | user | 團隊工具 |

---

*MCP 概念與架構請見 [MCP 基礎](../../concepts/zh-TW/mcp-basics.md)*

*參考：[Model Context Protocol](https://modelcontextprotocol.io/) | [Claude Code MCP 文件](https://code.claude.com/docs/en/mcp)*
