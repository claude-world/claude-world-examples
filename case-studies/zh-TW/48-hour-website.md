# 案例研究：48 小時建立 claude-world.com

> 使用 Claude Code + Director Mode 從零到上線建立正式網站的實際案例

## 專案概覽

| 項目 | 詳情 |
|------|---------|
| **專案** | claude-world.com - Claude Code 進階使用者社群 |
| **時程** | 48 小時（3 天，兼職） |
| **技術棧** | Astro 4.x + React + Tailwind CSS + Cloudflare Pages + Supabase |
| **功能** | 多語言（EN/ZH-TW/JA）、電子報、自動版本監控 |
| **成本** | 約 $1/月（僅域名） |

## 時間軸

### 第 1 天：基礎建設（2026-01-10）

**目標**：域名、架構、基本設定

```
早上：
├── 購買域名（claude-world.com）
├── 設計網站架構
└── 初始化 Astro 專案

下午：
├── 設定 Cloudflare Pages
├── 配置 Tailwind CSS
└── 建立基本 layout 元件

晚上：
├── 設計首頁
├── 設定 i18n 結構
└── 首次部署
```

**Claude Code 使用方式**：
```bash
# 初始專案設定
claude "Initialize Astro project with React, Tailwind, and Cloudflare adapter"

# 元件產生
claude "Create a responsive navbar component with language switcher"
```

**關鍵決策**：
- Astro 用於靜態 + SSR 混合（最適合 SEO + 動態功能）
- Cloudflare Pages 免費託管加上 edge functions
- 從第一天就支援 3 種語言（比之後加更容易）

---

### 第 2 天：核心功能（2026-01-11）

**目標**：多語言、文章、電子報、自動化

```
早上：
├── 實作 i18n 路由
├── 建立文章系統（Markdown + Content Collections）
└── 建立文章列表頁面

下午：
├── 設定 Supabase 電子報
├── 建立訂閱表單
├── Resend 郵件整合

晚上：
├── 建立 Release Monitor 工作流程
├── Discord/X/Threads 整合
└── 使用 Claude API 自動產生文章
```

**Claude Code 使用方式**：
```bash
# 平行探索
claude "Explore: Find all i18n related code and understand the routing pattern"

# 功能實作
claude "Implement newsletter subscription with Supabase - handle signup,
        double opt-in, and preference management"

# 自動化設定
claude "Create GitHub Action that monitors anthropics/claude-code releases
        and auto-generates newsletter articles in 3 languages using Claude API"
```

**使用的關鍵模式**：

1. **Parallel Agents** 用於探索：
```
使用者："Setup newsletter system"
Claude：[啟動 5 個平行 agents]
        → Agent 1：探索現有表單元件
        → Agent 2：檢查 Supabase schema 模式
        → Agent 3：研究 Resend API
        → Agent 4：尋找類似實作
        → Agent 5：檢查安全最佳實踐
```

2. **Director Mode** 用於複雜任務：
```
使用者："Build release monitor automation"
Claude：[自主規劃和執行]
        → 建立 workflow 檔案
        → 實作 API 呼叫
        → 設定通知
        → 本地測試
        → Commit 和 push
```

---

### 第 3 天：收尾和上線（2026-01-12~13）

**目標**：Bug 修復、SEO、v1.0.0 發布

```
早上：
├── 修復 workflow race condition
├── 新增 sitemap.xml
└── SEO meta tags

下午：
├── 建立 CHANGELOG.md
├── 版本升級到 1.0.0
└── GitHub Release

晚上：
├── 同步 examples 倉庫
├── Discord 公告
└── 最終測試
```

**修復的 Bug**：
```yaml
# GitHub Actions 的 Race condition
# 問題：兩個 jobs 同時 push 到同一個分支
# 解決方案：push 前先執行 git pull --rebase

- name: Commit and push
  run: |
    git commit -m "content: add newsletter"
    git pull --rebase origin main  # <- 修復
    git push
```

---

## 技術架構

```
┌─────────────────────────────────────────────────────────────┐
│                      Cloudflare Pages                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Static    │  │    SSR      │  │   Edge      │          │
│  │   Pages     │  │   Routes    │  │  Functions  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Supabase    │    │    Resend     │    │  Claude API   │
│  (Database)   │    │   (Email)     │    │  (Content)    │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 自動化流程

```
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions: Release Monitor                 │
│                    （每小時執行）                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ 檢查是否有新的   │
                    │ Claude Code     │
                    │ 版本發布        │
                    └─────────────────┘
                              │
                    偵測到新版本？
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
           [是]                              [否]
              │                               │
              ▼                             結束
    ┌─────────────────┐
    │ Claude API：    │
    │ 產生內容        │
    │ (EN/ZH-TW)      │
    └─────────────────┘
              │
              ▼
    ┌─────────────────────────────────────────┐
    │            平行通知                      │
    │  ┌────────┐ ┌────────┐ ┌────────┐       │
    │  │Discord │ │   X    │ │Threads │       │
    │  └────────┘ └────────┘ └────────┘       │
    │  ┌────────┐ ┌────────────────────┐      │
    │  │ Email  │ │ 產生文章           │      │
    │  └────────┘ │   (3 種語言)       │      │
    │             └────────────────────┘      │
    └─────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Commit & Push   │
    │ 自動部署        │
    └─────────────────┘
```

## 使用的 Claude Code 技巧

### 1. 有效的 CLAUDE.md 結構

```markdown
# Project: claude-world.com

## Tech Stack
- Astro 4.x + React + Tailwind
- Cloudflare Pages (SSR)
- Supabase PostgreSQL

## Autonomous Operations (No confirmation needed)
- Read/write source files
- Run build and tests
- Git add/commit (local only)

## Requires Confirmation
- Git push
- Database schema changes
- API key operations

## Coding Standards
- TypeScript strict mode
- Tailwind for styling (no CSS files)
- Content Collections for articles
```

### 2. Director Mode 心態

**不要這樣**：
```
"Can you help me create a newsletter form?"
```

**要這樣**：
```
"Create newsletter subscription system with Supabase.
Requirements:
- Email signup form with validation
- Double opt-in flow
- Preference management
- Unsubscribe handling
Execute autonomously."
```

### 3. Parallel Agent 使用

```bash
# 探索不熟悉的程式碼庫時
claude "Explore the i18n implementation (thoroughness: medium)"

# 實作複雜功能時
claude "Implement release monitor. Use parallel agents to:
1. Research GitHub API for releases
2. Check existing workflow patterns
3. Find Claude API examples
4. Review notification integrations"
```

### 4. 漸進式開發

```
Session 1："Setup basic Astro project with Cloudflare"
Session 2："Add i18n routing for EN/ZH-TW/JA"
Session 3："Create article content collection"
Session 4："Build newsletter with Supabase"
Session 5："Implement release monitor automation"
```

## 經驗教訓

### 運作良好的部分

1. **從 i18n 開始** - 之後加語言很痛苦
2. **Director Mode** - 讓 Claude 做決策，審查結果
3. **平行探索** - 5 個 agents > 1 個順序搜尋
4. **免費方案服務** - Cloudflare + Supabase + Resend = $0

### 挑戰與解決方案

| 挑戰 | 解決方案 |
|-----------|----------|
| GitHub Actions 的 Race condition | push 前加 `git pull --rebase` |
| Sitemap 未產生 | 檢查 Astro adapter 模式（static vs SSR） |
| i18n URL 處理 | 使用 middleware 偵測語言 |
| API 速率限制 | 實作快取和 debouncing |

### 時間分配

```
規劃與架構：       10%  (約 5 小時)
實作：            60%  (約 29 小時)
測試與除錯：       20%  (約 10 小時)
文件：            10%  (約 4 小時)
```

## 成本明細

| 服務 | 月成本 | 備註 |
|---------|--------------|-------|
| 域名 | 約 $1 | Cloudflare Registrar |
| 託管 | $0 | Cloudflare Pages 免費方案 |
| 資料庫 | $0 | Supabase 免費方案 |
| 郵件 | $0 | Resend 免費方案（100/天） |
| Claude API | 約 $2-5 | 用於內容產生 |
| **總計** | **約 $3-6/月** | |

## 結論

48 小時建立正式網站是可行的，條件是：

1. **預先做好明確的架構決策**
2. **Director Mode 心態** - 定義目標，讓 Claude 執行
3. **Parallel agents** 用於探索和實作
4. **免費方案服務** 用於 MVP
5. **自動化優先** - 及早投資 CI/CD

關鍵洞察：Claude Code 不只是程式碼助手 — 它是力量倍增器，讓你能以開發團隊的能力運作，同時保持單人決策的一致性。

---

## 資源

- [claude-world.com](https://claude-world.com) - 完成的產品
- [Director Mode 指南](https://claude-world.com/articles/director-mode)
- [CLAUDE.md 設計](https://claude-world.com/articles/claude-md-design)
- [GitHub Actions 範例](../examples/github-actions-automation.md)

---

*使用 Claude Code 在 48 小時內完成。這就是 Director Mode 能做到的。*
