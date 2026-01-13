# CLAUDE.md 原則

> 你的 CLAUDE.md 是團隊的入職文件。讓它發揮作用。

## 什麼是 CLAUDE.md？

CLAUDE.md 是一個特殊檔案，Claude Code 在每個 session 開始時都會讀取。這是你給 Claude 專案脈絡的機會。

把它想成你在新開發者第一天會給他們的文件。

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
- Next.js 14 (App Router)
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

```markdown
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
```

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

### 5. 保持更新

你的 CLAUDE.md 應該隨專案演進：

- 模式出現時就加入
- 移除過時的資訊
- 記錄新的架構決策
- 包含從 bug 學到的經驗

## 範本

```markdown
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

### 新增 API endpoint
1. 在 /api 建立檔案
2. 在 /types 加入型別
3. 在 /__tests__ 寫測試

### 新增元件
1. 在 /components 建立
2. 使用現有的 design tokens
3. 加入 Storybook story
```

## 進階技巧

1. **從小開始** - 20 行的 CLAUDE.md 比沒有 CLAUDE.md 好
2. **明確指示** - 「使用 X」比「你可能想要使用 X」好
3. **包含範例** - 用範例展示而非只用文字說明
4. **版本控制** - 你的 CLAUDE.md 應該在 git 裡

---

下一篇：[Parallel Agents](./parallel-agents.md)
