# CLAUDE.md 原則

> 你的 CLAUDE.md 是團隊的入職文件。讓它發揮作用。

## 什麼是 CLAUDE.md？

CLAUDE.md 是一個 markdown 檔案，Claude Code 在每個 session 開始時都會把它載入 context。這是你提供 Claude 無法單從程式碼推斷出的專案脈絡的機會。

把它想成你在新開發者第一天會給他們的文件。

### CLAUDE.md 檔案放在哪裡

Claude Code 會從多個位置讀取 CLAUDE.md，載入順序由範圍最廣到最具體：

| 範圍 | 位置 | 分享對象 |
|------|------|----------|
| 組織管理政策 | 由 IT 部署，例如 Linux 上的 `/etc/claude-code/CLAUDE.md` | 這台機器上的所有人 |
| 使用者 | `~/.claude/CLAUDE.md` | 只有你，所有專案 |
| 專案 | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 團隊，透過 git |
| 本機 | `./CLAUDE.local.md`（記得加進 `.gitignore`） | 只有你，目前專案 |

你啟動 Claude 的目錄及其上層目錄中的檔案會在啟動時載入。它們會疊加而不是互相覆蓋，越具體的檔案越晚被讀到。子目錄中的 CLAUDE.md 則是按需載入：等 Claude 讀取或編輯該目錄裡的檔案時才載入。如果 repo 有為其他 coding agent 準備的 `AGENTS.md` 但沒有 CLAUDE.md，Claude Code 會改讀 `AGENTS.md`；兩者都保留的話，在 CLAUDE.md 開頭加上 `@AGENTS.md` 匯入它。

執行 `/init` 讓 Claude 根據程式碼庫草擬 CLAUDE.md，`/memory` 開啟你的記憶檔案，`/context` 確認實際載入了哪些檔案。

## 五個原則

### 1. 具體，而非籠統

**不好**：
```markdown
# 我的專案
這是一個網頁應用程式。
```

**好**：
```markdown
# 電商平台

## 技術棧
- Next.js 16 (App Router)
- PostgreSQL + Prisma
- Stripe 處理付款
- Cloudflare R2 存放圖片

## 關鍵目錄
- /app - Next.js 頁面和 API routes
- /lib - 共用工具
- /components - React 元件
- /prisma - 資料庫 schema 和 migrations
```

### 2. 記錄決策，不只是事實

**不好**：
```markdown
我們使用 JWT tokens。
```

**好**：
```markdown
## 驗證
我們使用 JWT tokens 存在 httpOnly cookies（不是 localStorage）。

原因：防止 XSS 攻擊竊取 tokens。

實作方式：
- Access token：15 分鐘過期
- Refresh token：7 天過期
- Refresh endpoint：POST /api/auth/refresh
```

### 3. 包含常用指令

````markdown
## 開發指令

```bash
pnpm dev          # 啟動開發伺服器
pnpm test         # 執行測試
pnpm db:migrate   # 執行 migrations
pnpm db:seed      # 填入測試資料
```

## 提交前檢查
1. 執行 `pnpm typecheck`
2. 執行 `pnpm test`
3. 執行 `pnpm lint`
````

### 4. 設定邊界和偏好

```markdown
## 程式碼偏好

應該做的：
- 使用 TypeScript strict mode
- 為新功能寫測試
- 使用 /components/ui 中現有的 UI 元件
- 遵循程式碼庫中的現有模式

不應該做的：
- 未經詢問就新增依賴
- 修改驗證流程
- 不寫 migration 就修改資料庫 schema
- 使用 any 而非正確的型別
```

> **是指引，不是強制。** Claude 把 CLAUDE.md 當作脈絡：它會盡量遵守這些規則，但這裡沒有任何東西會被強制執行。必須每次都成立的規則，請在 `.claude/settings.json` 的 `permissions` 加上 `deny`（或 `ask`）規則，或使用 [hook](./hooks-basics.md)。[CLAUDE.md 反模式](./claude-md-anti-patterns.md) 有範例。

### 5. 保持更新

你的 CLAUDE.md 應該隨專案演進：

- 模式出現時就加入（一個好時機：Claude 第二次犯同樣的錯）
- 移除過時的資訊
- 記錄新的架構決策
- 包含從 bug 學到的經驗

直接編輯檔案（`/memory` 可以開啟它），或請 Claude「把這個加進 CLAUDE.md」。舊的 `#` 快速新增捷徑已經移除。定期執行 `/doctor prompt-audit`：Claude 會標出為舊模型寫的指示、指向已不存在的檔案或指令的內容，以及互相矛盾之處，接著提出修改建議，在你同意之前不會更動任何內容。

## 當 CLAUDE.md 變長時

每個 CLAUDE.md 盡量控制在約 200 行以內。整個檔案每個 session 都會載入，檔案太長會降低遵循度：重要的規則會被淹沒在雜訊裡。對每一行問自己：「刪掉這行會讓 Claude 犯錯嗎？」如果不會，就刪掉。

| 內容 | 放在哪裡 |
|------|----------|
| 每個 session 都需要的事實：指令、慣例、結構 | `CLAUDE.md` |
| 只適用於程式碼庫某一部分的指引 | `.claude/rules/*.md`，搭配 `paths:` frontmatter |
| 多步驟流程：部署、發布、migrations | Skill，放在 `.claude/skills/<name>/SKILL.md` |
| 絕對不能違反的規則 | `.claude/settings.json` 的 `permissions`，或 hooks |

帶有 `paths:` frontmatter 的規則只會在 Claude 處理符合的檔案時載入：

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API 規則
- 用 Zod 驗證 request body
- 錯誤回應使用 `src/lib/errors.ts` 定義的格式
```

`@path` 匯入（例如 `See @docs/architecture.md`）可以幫你整理較長的檔案，但被匯入的檔案一樣會在啟動時載入，所以不會節省 context。不加 `@` 的一般路徑不會被匯入；任務需要時，Claude 可以自己開啟該檔案。

Claude 也有預設開啟的 **auto memory**：它替自己記下關於你的偏好和修正的筆記，存放在 `~/.claude/projects/<project>/memory/`。CLAUDE.md 放的是你希望 Claude 知道的事；auto memory 放的是 Claude 自己學到的事。兩者都可以用 `/memory` 管理。

## 範本

````markdown
# [專案名稱]

> 一句話描述

## 技術棧
- [框架]
- [資料庫]
- [關鍵函式庫]

## 目錄結構
```
/src
  /components  - React 元件
  /lib         - 工具程式
  /api         - API routes
```

## 開發

### 設定
```bash
pnpm install
cp .env.example .env
pnpm db:migrate
```

### 指令
```bash
pnpm dev      # 開發
pnpm test     # 測試
pnpm build    # 正式環境建置
```

## 架構決策

### [決策 1]
內容：[描述]
原因：[理由]

### [決策 2]
內容：[描述]
原因：[理由]

## 程式碼規範

### 應該做的
- [規範 1]
- [規範 2]

### 不應該做的
- [反模式 1]
- [反模式 2]

## 常見任務

<!-- 保持簡短。較長的流程（部署、發布）應該放進 skill。 -->

### 新增 API endpoint
1. 在 /api 建立檔案
2. 在 /types 加入型別
3. 在 /__tests__ 寫測試

### 新增元件
1. 在 /components 建立
2. 使用現有的 design tokens
3. 加入 Storybook story
````

## 進階技巧

1. **從小開始** - 先用 `/init` 產生草稿再精簡。20 行的 CLAUDE.md 比沒有 CLAUDE.md 好
2. **明確指示** - 「使用 X」比「你可能想要使用 X」好
3. **包含範例** - 用範例展示而非只用文字說明
4. **版本控制** - 把 `CLAUDE.md` commit 進 git；個人筆記放在已加入 gitignore 的 `CLAUDE.local.md`
5. **確認載入了什麼** - `/context` 會列出目前 session 載入的記憶檔案
6. **給人看的筆記寫在註解裡** - 區塊層級的 `<!-- HTML 註解 -->` 會在 Claude 讀到檔案之前被移除

---

下一篇：[Parallel Agents](./parallel-agents.md)
