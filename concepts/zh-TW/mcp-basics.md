# MCP 基礎

> Model Context Protocol (MCP) 透過連接外部工具、資料庫和服務來擴展 Claude Code 的能力。

## 什麼是 MCP？

MCP 是一個開放標準，讓 AI 應用程式連接外部系統。每個 MCP server 都會給 Claude 內建工具以外的新工具：

- **存取外部資料來源**（資料庫、APIs、檔案系統）
- **執行專業工具**（Git、套件管理器、雲服務）
- **維護持久脈絡**（memory、知識圖譜）
- **整合開發工具**（IDEs、CI/CD、專案管理）

MCP servers 並不是 Claude Code 的外掛系統：[plugin](https://code.claude.com/docs/en/plugins) 是一種套件，可以把 MCP servers 與 skills、subagents、hooks 打包在一起。

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

使用 `claude mcp` CLI（或在 session 中使用 `/mcp`）：

```bash
# 透過 HTTP 連接遠端 server（託管服務的建議做法）
claude mcp add --transport http <name> <url>

# 本地 stdio server：-- 之後的內容是啟動 server 的指令
claude mcp add [--scope <scope>] <name> [-e KEY=value] -- <command> [args...]

# Scopes：
# --scope local    → ~/.claude.json，僅此專案、僅自己可用（預設）
# --scope project  → repo 根目錄的 .mcp.json，與團隊共享
# --scope user     → ~/.claude.json，你的所有專案

# 環境變數使用 -e flag：
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.jsonl -- npx -y @modelcontextprotocol/server-memory
```

> **注意：** `-e`（`--env`）為 server 設定環境變數，可接受多組 `KEY=value`。請像上面一樣把 server 名稱放在 `-e` 之前：緊接在 `-e` 後面的名稱會被當成另一組變數。SSE transport 已被棄用，請使用 `--transport http`。

## 必備 MCP Servers

### 1. 檔案系統存取

```bash
claude mcp add --scope project filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem .
```

**能力：** 讀寫檔案、建立目錄、列出內容、搜尋檔案。Claude Code 內建的 Read、Edit、Glob、Grep 工具已涵蓋專案目錄，只有需要存取專案以外的目錄時才加入這個 server。

### 2. Memory（知識圖譜）

```bash
# 重要：務必使用 MEMORY_FILE_PATH 做專案隔離
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.jsonl \
  -- npx -y @modelcontextprotocol/server-memory
```

**能力：** 明確的知識圖譜（entities、relations、observations），存成 JSONL 檔案，可跨 sessions 搜尋。Claude Code 本身已有內建記憶（CLAUDE.md 與 auto memory）；何時值得加入知識圖譜，請見 [Memory 系統](./memory-system.md)。

**警告：** 沒有 `MEMORY_FILE_PATH` 的話，所有專案會共用同一個 memory！

### 3. Git 操作

```bash
# 參考實作的 Git server 是 Python 套件；uvx 不需安裝即可執行
claude mcp add --scope project git \
  -- uvx mcp-server-git --repository .
```

**能力：** Git status、log、diff、分支操作、file blame

### 4. GitHub 整合

```bash
# GitHub 官方遠端 server（舊的 @modelcontextprotocol/server-github 已棄用）
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer <your-github-pat>"
```

**能力：** Issues、PRs、repository 管理、程式碼搜尋、Actions

### 5. Sequential Thinking

```bash
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

**能力：** 結構化推理、多步驟分析、複雜問題拆解

### 6. Context7（即時文件）

```bash
# 遠端 server；到 context7.com 取得 API key（或執行：npx ctx7 setup --claude）
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp \
  --header "Authorization: Bearer <your-context7-api-key>"
```

**能力：** 即時官方文件、最新的函式庫參考

## 資料庫 MCP Servers

PostgreSQL 與 SQLite 的原始參考實作 server 已封存。請優先使用資料庫廠商維護的 server：

### Supabase（PostgreSQL）

```bash
# 官方遠端 server；加入後用 /mcp 完成認證
claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<project-ref>&read_only=true"
```

### MongoDB

```bash
# MongoDB 官方 server，唯讀模式
claude mcp add --scope local mongodb \
  -e MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017/db" \
  -- npx -y mongodb-mcp-server --readOnly
```

不要把資料庫憑證放進 `.mcp.json`：像上面一樣使用 local scope，或在共享設定中引用 `${DATABASE_URL}` 這類環境變數。

## MCP Scope 層級

server 定義的位置決定了誰能使用它：

```
┌─────────────────────────────────────────────┐
│  Managed（組織）                              │
│  位置: managed-mcp.json 或 managed           │
│        settings（由 IT 控制）                 │
├─────────────────────────────────────────────┤
│  Local scope（預設）                          │
│  位置: ~/.claude.json，此專案路徑底下          │
│  用途: 個人或含憑證的 servers                 │
├─────────────────────────────────────────────┤
│  Project scope                               │
│  位置: repo 根目錄的 .mcp.json               │
│  用途: 共享 servers（提交到 git）             │
├─────────────────────────────────────────────┤
│  User scope                                  │
│  位置: ~/.claude.json（最上層）               │
│  用途: 所有專案都用的個人 servers             │
└─────────────────────────────────────────────┘
```

> **重要：** MCP servers 從來不設定在 `settings.json`。請用 `claude mcp add --scope project` 建立或更新 `.mcp.json`；每位使用者第一次使用專案 servers 時，Claude Code 都會請他確認。

同名 server 定義在多處時的**優先順序**：Local > Project > User > plugin 提供的 servers > claude.ai connectors。組織的 managed servers 優先於以上全部。

## MCP Context 成本

MCP tool search 預設開啟：Claude Code 會在需要時才載入 server 的工具定義，而不是每次請求都送出所有工具，所以大型 server 不再一開始就佔用數千個 tokens。不過 servers 仍會增加程序負擔與 context 中的工具名稱，而且每個啟用的 server 都代表 Claude 可以採取的另一組動作。

**最佳實踐：** 只啟用你實際在用的 MCP servers，並用 `/context` 查看 session 的 context 花在哪裡。

## 設定檔

> **重要：** 專案 MCP servers 放在 `.mcp.json`，不是 `.claude/settings.json`。請一律使用 `claude mcp add --scope project` 建立正確的設定。

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
        "MEMORY_FILE_PATH": "./.claude/memory.jsonl"
      }
    }
  }
}
```

遠端 server 需要在 `url` 旁加上 `"type": "http"`；只有 `url` 沒有 `type` 的項目會被拒絕。`${VAR}` 與 `${VAR:-default}` 會從環境變數展開，因此這個檔案可以在不含 secrets 的情況下提交：

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}"
      }
    }
  }
}
```

### 使用者設定（~/.claude.json）

`claude mcp add --scope user` 會寫入 `~/.claude.json` 最上層的 `mcpServers`，`--scope local` 則寫在同一個檔案中目前專案的項目底下。請讓 CLI 管理這個檔案，不要手動編輯。

## MCP 管理指令

```bash
# 列出所有 MCP servers 與連線狀態
claude mcp list

# 顯示單一 server 的設定
claude mcp get <name>

# 加入新 server
claude mcp add --scope project <name> -- <command>

# 移除 server
claude mcp remove --scope project <name>

# 在 session 中：狀態、OAuth 登入、重新連線
/mcp

# 重設專案 MCP 的核准選擇（疑難排解）
claude mcp reset-project-choices
```

## 實際範例

### 資料庫查詢

啟用資料庫 MCP 後：

```
使用者：「顯示最近 7 天註冊的使用者」

Claude：[使用資料庫 MCP]
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

### 專案 Server 尚未核准

互動式 session 中，`.mcp.json` 的 servers 會等待核准。請在啟動提示或 `/mcp` 中核准，或在設定的 `enabledMcpjsonServers` 列出信任的 servers；對你信任的 repository，也可以在 `.claude/settings.local.json` 設定 `enableAllProjectMcpServers: true`。

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
| 持久儲存 | Memory MCP（知識圖譜） | CLAUDE.md、auto memory | 否 |
| 自訂整合 | 可擴展 | 固定 | 透過指令 |
| Context 成本 | 需要時才載入（tool search） | 已包含 | 最小 |

## 開始使用

**今天：**
1. 加入一個你需要的 MCP server（GitHub、你的資料庫或 Context7）
2. 執行 `/mcp` 確認已連線
3. 請 Claude 在實際任務中使用它

**這週：**
1. 透過 `.mcp.json`（`--scope project`）共享團隊 servers
2. 把憑證放在 local scope 或 `${VAR}` 引用中
3. 只有在 CLAUDE.md 與 auto memory 之外還想要明確的知識圖譜時，才加入 memory server

---

*MCP 讓 Claude Code 從獨立助手轉變為整合式開發平台。*

*參考：[Model Context Protocol](https://modelcontextprotocol.io/) | [Claude Code MCP 文件](https://code.claude.com/docs/en/mcp)*
