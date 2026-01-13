# MCP 設定範例

> 常見 MCP 設定的完整設定配方 - 複製、貼上，然後根據你的專案調整。

## 快速設定：基本 MCP 堆疊

適用於大多數專案的最小 MCP 設定：

```bash
# 1. 檔案系統存取（專案範圍）
claude mcp add --scope project filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem .

# 2. 具有專案隔離的 Memory（關鍵：使用 MEMORY_FILE_PATH）
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.json \
  -- npx -y @modelcontextprotocol/server-memory

# 3. Git 操作
claude mcp add --scope project git \
  -- npx -y @modelcontextprotocol/server-git
```

**結果：** Claude 現在可以讀寫檔案、跨 session 記住決策，以及管理 Git 操作。

---

## 按專案類型設定

### 網頁應用程式（全端）

```bash
# 核心堆疊
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory
claude mcp add --scope project git -- npx -y @modelcontextprotocol/server-git

# 資料庫（選擇一個）
# PostgreSQL
claude mcp add --scope project postgres \
  -e DATABASE_URL="${DATABASE_URL}" \
  -- npx -y @modelcontextprotocol/server-postgres

# SQLite（用於本地開發）
claude mcp add --scope project sqlite \
  -e DATABASE_PATH="./data/dev.db" \
  -- npx -y @modelcontextprotocol/server-sqlite

# GitHub 用於 issue/PR 管理
claude mcp add --scope user github \
  -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-github

# Context7 用於最新文件
claude mcp add --scope user context7 \
  -- npx -y context7-mcp
```

### 純 API 後端

```bash
# 核心
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory

# 資料庫
claude mcp add --scope project postgres \
  -e DATABASE_URL="${DATABASE_URL}" \
  -- npx -y @modelcontextprotocol/server-postgres

# Sequential thinking 用於複雜 API 設計
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

### 靜態網站 / 文件

```bash
# 最小設定
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory
claude mcp add --scope project git -- npx -y @modelcontextprotocol/server-git

# Context7 用於參考函式庫
claude mcp add --scope user context7 \
  -- npx -y context7-mcp
```

### 資料科學 / ML

```bash
# 核心
claude mcp add --scope project filesystem -- npx -y @modelcontextprotocol/server-filesystem .
claude mcp add --scope project memory -e MEMORY_FILE_PATH=./.claude/memory.json -- npx -y @modelcontextprotocol/server-memory

# 資料庫
claude mcp add --scope project postgres \
  -e DATABASE_URL="${DATABASE_URL}" \
  -- npx -y @modelcontextprotocol/server-postgres

# Sequential thinking 用於分析工作流程
claude mcp add --scope user sequential-thinking \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## 完整設定檔範例

### 專案設定（.claude/settings.json）

**最小設定：**

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
  },
  "enableAllProjectMcpServers": true
}
```

**全端應用程式：**

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
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  },
  "enableAllProjectMcpServers": true
}
```

### 使用者設定（~/.claude/settings.json）

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "context7-mcp"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## 資料庫設定模式

### PostgreSQL with Supabase

```bash
# 使用 Supabase dashboard 的連線字串
claude mcp add --scope project postgres \
  -e DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  -- npx -y @modelcontextprotocol/server-postgres
```

**或透過 settings.json：**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${SUPABASE_DATABASE_URL}"
      }
    }
  }
}
```

### PostgreSQL 本地開發

```bash
claude mcp add --scope project postgres \
  -e DATABASE_URL="postgresql://localhost:5432/myapp_dev" \
  -- npx -y @modelcontextprotocol/server-postgres
```

### SQLite 用於原型設計

```bash
# 如果資料庫檔案不存在會自動建立
claude mcp add --scope project sqlite \
  -e DATABASE_PATH="./data/app.db" \
  -- npx -y @modelcontextprotocol/server-sqlite
```

### MongoDB

```bash
# 本地
claude mcp add --scope project mongodb \
  -e MONGODB_URI="mongodb://localhost:27017/myapp" \
  -- npx -y @modelcontextprotocol/server-mongodb

# MongoDB Atlas
claude mcp add --scope project mongodb \
  -e MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/myapp" \
  -- npx -y @modelcontextprotocol/server-mongodb
```

---

## 雲端服務整合

### Vercel

```bash
claude mcp add --scope user vercel \
  -e VERCEL_TOKEN="${VERCEL_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-vercel
```

**功能：** 部署專案、管理網域、查看部署

### Cloudflare

```bash
claude mcp add --scope user cloudflare \
  -e CLOUDFLARE_API_TOKEN="${CF_API_TOKEN}" \
  -- npx -y @anthropic-ai/mcp-server-cloudflare
```

**功能：** Workers、Pages、D1 資料庫、R2 儲存、DNS

### Netlify

```bash
claude mcp add --scope user netlify \
  -e NETLIFY_AUTH_TOKEN="${NETLIFY_AUTH_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-netlify
```

**功能：** 部署、表單、functions、環境變數

---

## 團隊/協作 MCP

### Linear（專案管理）

```bash
claude mcp add --scope user linear \
  -e LINEAR_API_KEY="${LINEAR_API_KEY}" \
  -- npx -y @modelcontextprotocol/server-linear
```

**警告：** ~6,200 tokens - 謹慎使用

### Notion

```bash
claude mcp add --scope user notion \
  -e NOTION_TOKEN="${NOTION_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-notion
```

**注意：** 官方 Notion MCP 已針對較低 token 使用量進行最佳化

### Slack

```bash
claude mcp add --scope user slack \
  -e SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-slack
```

---

## Memory 隔離模式

### 按專案 Memory（建議）

```bash
# 每個專案有自己的 memory 檔案
claude mcp add --scope project memory \
  -e MEMORY_FILE_PATH=./.claude/memory.json \
  -- npx -y @modelcontextprotocol/server-memory
```

**結果：** Memory 隨專案提交，團隊共享

### 使用者全域 Memory

```bash
# 跨所有專案的單一 memory（個人知識）
claude mcp add --scope user memory \
  -e MEMORY_FILE_PATH=~/.claude/global-memory.json \
  -- npx -y @modelcontextprotocol/server-memory
```

**結果：** 個人知識跨所有專案持久化

### 混合方法

```json
{
  "mcpServers": {
    "project-memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.claude/project-memory.json"
      }
    }
  }
}
```

在使用者設定中：
```json
{
  "mcpServers": {
    "personal-memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "~/.claude/personal-memory.json"
      }
    }
  }
}
```

---

## 環境變數管理

### 使用 .env 檔案

在專案根目錄建立 `.env`：

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
SUPABASE_DATABASE_URL=postgresql://postgres:[pass]@db.xxx.supabase.co:5432/postgres
```

在 settings.json 中參考：

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### 使用 Shell 環境

```bash
# 先 export
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# 然後添加 MCP（從環境取得）
claude mcp add --scope user github \
  -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
  -- npx -y @modelcontextprotocol/server-github
```

---

## 驗證與疑難排解

### 驗證設定

```bash
# 列出所有已設定的 MCP servers
claude mcp list

# 檢查狀態
claude mcp status

# 在 Claude Code session 中
# 輸入：「有哪些 MCP servers 可用？」
```

### 常見問題與修復

**MCP 無法載入：**

```bash
# 重設並重新添加
claude mcp reset-project-choices
claude mcp add --scope project <name> -- <command>
```

**權限被拒絕：**

確保在 `.claude/settings.json` 中：
```json
{
  "enableAllProjectMcpServers": true
}
```

**環境變數不起作用：**

1. 檢查 `.env` 檔案存在且值正確
2. 確保使用 `${VAR}` 語法（不是 `$VAR`）
3. 變更後重啟 Claude Code

**資料庫連線失敗：**

```bash
# 先在 Claude 外測試連線
psql $DATABASE_URL

# 檢查 port 是否可存取
nc -zv localhost 5432
```

---

## 設定檢查清單

### 新專案設定

- [ ] 添加 filesystem MCP
- [ ] 添加 memory MCP 並設定 `MEMORY_FILE_PATH`
- [ ] 添加 git MCP
- [ ] 如果適用，添加 database MCP
- [ ] 執行 `claude mcp list` 驗證
- [ ] 用「哪些 MCP servers 正在運作？」測試

### 團隊 Onboarding

- [ ] 在 README 中記錄所需的 MCP servers
- [ ] 建立 `.claude/settings.json` 範本
- [ ] 添加 `.env.example` 包含所需變數
- [ ] 將 `.claude/memory.json` 加入 `.gitignore` 或提交（團隊偏好）

---

## 快速參考

| MCP | 範圍 | 使用情境 |
|-----|-------|----------|
| filesystem | project | 檔案操作 |
| memory | project | 專案知識 |
| git | project | 版本控制 |
| postgres/sqlite/mongodb | project | 資料庫存取 |
| github | user | Issues、PRs |
| context7 | user | 即時文件 |
| sequential-thinking | user | 複雜推理 |
| vercel/cloudflare/netlify | user | 部署 |

---

*MCP 概念和架構，請見 [MCP 基礎](../concepts/mcp-basics.md)*

*參考：[MCP 官方 Registry](https://modelcontextprotocol.io/) | [Claude Code 文件](https://docs.anthropic.com/en/docs/claude-code)*
