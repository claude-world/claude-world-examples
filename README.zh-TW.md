# Claude World 範例

> 精通 Claude Code 的實用範例與最佳實踐 - 來自 Anthropic 的官方 AI 驅動 CLI 工具

[![Website](https://img.shields.io/badge/網站-claude--world.com-blue)](https://claude-world.com)
[![Discord](https://img.shields.io/badge/Discord-加入社群-7289da)](https://discord.gg/rBtHzSD288)
[![Version](https://img.shields.io/badge/版本-1.0.0-green)](https://github.com/claude-world/claude-world-examples/releases/tag/v1.0.0)

---

**v1.0.0 已發布！** 網站已上線 [claude-world.com](https://claude-world.com) - 使用 Claude Code + Director Mode 在 48 小時內從零到上線。

---

## 什麼是 Claude World？

Claude World 是一個致力於幫助開發者精通 **Claude Code** 的社群 - Anthropic 官方的 AI 輔助軟體開發 CLI 工具。

我們專注於：
- **Director Mode** - 從「動手做的開發者」轉變為「團隊導演」的思維轉換
- **高效工作流程** - 平行代理、最少干擾、自主執行
- **最佳實踐** - 來自真實生產專案的實戰經驗
- **進階功能** - Hooks、MCP、Memory、Extended Thinking 等

## 目錄結構

```
claude-world-examples/
├── concepts/           # 核心概念與心智模型
├── examples/           # 實用程式碼範例
├── guides/             # 深度指南與教學
├── templates/          # 即用模板（CLAUDE.md、工作流程）
└── case-studies/       # 真實專案案例研究
```

## 內容概覽

### 核心概念

| 概念 | 說明 | 難度 |
|------|------|------|
| [Director Mode 基礎](./concepts/zh-TW/director-mode-basics.md) | 讓你生產力提升 10 倍的思維轉換 | 初級 |
| [CLAUDE.md 原則](./concepts/zh-TW/claude-md-principles.md) | 如何撰寫有效的專案指令 | 初級 |
| [Hooks 基礎](./concepts/zh-TW/hooks-basics.md) | 自動化政策與防護機制 | 初級 |
| [MCP 基礎](./concepts/zh-TW/mcp-basics.md) | 用外部工具和資料庫擴展 Claude | 初級 |
| [Memory 系統](./concepts/zh-TW/memory-system.md) | 建立持久的專案智慧 | 初級 |
| [CLAUDE.md 反模式](./concepts/zh-TW/claude-md-anti-patterns.md) | 常見錯誤及修正方法 | 中級 |
| [平行代理](./concepts/zh-TW/parallel-agents.md) | 同時執行 5 個代理加速工作 | 中級 |
| [AI 輔助工作流程](./concepts/zh-TW/ai-assisted-workflow.md) | 將 Claude Code 作為生產力倍增器 | 中級 |
| [多 AI 工作流程](./concepts/zh-TW/multi-ai-workflow.md) | 協調 Claude、Codex 和 Gemini CLI | 高級 |

### 實用範例

| 範例 | 說明 | 使用場景 |
|------|------|----------|
| [簡單 CLAUDE.md](./examples/zh-TW/simple-claude-md.md) | 精簡但有效的 CLAUDE.md 模板 | 快速開始 |
| [Bug 搜尋模式](./examples/zh-TW/bug-hunting.md) | 使用平行代理快速找到 bug | 除錯 |
| [功能開發](./examples/zh-TW/feature-development.md) | 結構化的功能開發方法 | 實作 |
| [重構模式](./examples/zh-TW/refactoring-patterns.md) | 用 Claude 系統化改善程式碼 | 程式碼品質 |
| [Hooks 模式](./examples/zh-TW/hooks-patterns.md) | 生產環境就緒的 hook 配置 | 自動化 |
| [MCP 設定](./examples/zh-TW/mcp-setup.md) | 完整的 MCP 配置範例 | 整合 |
| [GitHub Actions 自動化](./examples/zh-TW/github-actions-automation.md) | 用 Claude API 建立自動化工作流程 | CI/CD |
| [多語言 Astro](./examples/zh-TW/multi-language-astro.md) | 完整的多語言網站設定 | i18n |
| [Supabase + Cloudflare](./examples/supabase-cloudflare-integration.md) | 免費託管與資料庫的全端整合 | 全端 |

### 指南

| 指南 | 說明 | 時間 |
|------|------|------|
| [Agents 指南](./guides/zh-TW/agents-guide.md) | 所有 Claude Code agents 的完整指南 | 25 分鐘 |
| [Extended Thinking](./guides/zh-TW/extended-thinking.md) | 用 thinking mode 解鎖更深層推理 | 15 分鐘 |
| [快速參考卡](./guides/zh-TW/quick-reference.md) | 快速查閱的單頁視覺指南 | 5 分鐘 |
| [生產環境準備](./guides/zh-TW/production-readiness.md) | 上線前的檢查清單 | 15 分鐘 |
| [安全最佳實踐](./guides/zh-TW/security-best-practices.md) | 從一開始就建立安全的應用程式 | 20 分鐘 |
| [規格驅動開發](./guides/zh-TW/specification-driven-development.md) | 先寫規格，可靠地實作 | 30 分鐘 |

### 模板

| 模板 | 說明 |
|------|------|
| [依框架分類的 CLAUDE.md](./templates/zh-TW/claude-md-templates.md) | React、Next.js、Python、Go 等即用模板 |
| [Release 監控工作流程](./templates/release-monitor-workflow.yml) | 自動監控 release 的 GitHub Actions 工作流程 |

### 案例研究

| 案例研究 | 說明 |
|----------|------|
| [48 小時建站](./case-studies/zh-TW/48-hour-website.md) | 在 48 小時內從零到上線建立 claude-world.com |

## claude-world.com 涵蓋的主題

網站涵蓋這些進階主題（範例即將推出）：

| 主題 | 文章 |
|------|------|
| **基礎** | [從操作者到導演：思維轉換](https://claude-world.com/zh-tw/articles/mindset-shift) |
| **框架** | [Director Mode 框架](https://claude-world.com/zh-tw/articles/director-mode) |
| **配置** | [CLAUDE.md 設計原則](https://claude-world.com/zh-tw/articles/claude-md-design) |
| **Agents** | [Claude Code Agents：完整指南](https://claude-world.com/zh-tw/articles/agents-guide) |
| **多代理** | [多代理架構模式](https://claude-world.com/zh-tw/articles/multi-agent-patterns) |
| **Skills** | [Claude Code Skills：完整指南](https://claude-world.com/zh-tw/articles/skills-guide) |
| **Hooks** | [Claude Code Hooks：自動化政策](https://claude-world.com/zh-tw/articles/hooks-guide) |
| **MCP** | [Model Context Protocol 指南](https://claude-world.com/zh-tw/articles/mcp-guide) |
| **Memory** | [建立持久的專案智慧](https://claude-world.com/zh-tw/articles/memory-system-guide) |
| **Context7** | [存取最新文檔](https://claude-world.com/zh-tw/articles/context7-integration) |
| **Extended Thinking** | [解鎖更深層推理](https://claude-world.com/zh-tw/articles/extended-thinking-guide) |
| **SpecKit** | [規格驅動開發](https://claude-world.com/zh-tw/articles/speckit-guide) |
| **除錯** | [進階除錯技巧](https://claude-world.com/zh-tw/articles/debugging-techniques) |
| **安全** | [安全優先開發](https://claude-world.com/zh-tw/articles/security-first) |
| **CI/CD** | [Pipeline 整合](https://claude-world.com/zh-tw/articles/cicd-integration) |

## 快速開始

### 1. 安裝 Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. 在專案中建立 CLAUDE.md

```markdown
# 專案指令

## 技術棧
- [你的框架]
- [你的資料庫]

## 開發規範
- 提交前執行測試
- 使用 TypeScript strict mode

## 自主操作
- 讀取任何檔案
- 執行測試
- 建立/修改原始碼

## 需要確認
- 推送到遠端
- 刪除檔案
- 修改環境變數
```

### 3. 啟動 Claude Code

```bash
claude
```

## Director Mode 思維

### 傳統方式（動手做的開發者模式）：
```
你：「可以幫我修這個 bug 嗎？」
Claude：「當然！首先，讓我問...」
你：[等待問題]
Claude：[問 5 個問題]
你：[回答問題]
Claude：[終於開始工作]
```

### Director Mode 方式：
```
你：「修復登入 bug」
Claude：[立即啟動 3 個平行代理]
       [代理 1：搜尋認證程式碼]
       [代理 2：檢查錯誤日誌]
       [代理 3：檢視最近變更]
       [找到並修復 bug]
       [提交清晰的訊息]
你：[檢視完成的工作]
```

**核心原則**：你是導演。Claude 是你的自主團隊。定義目標，讓他們執行。

### 三大支柱

1. **目標優於指令** - 定義成果，而非步驟
2. **團隊委派** - 信任平行代理同時工作
3. **成果驗證** - 檢視結果，而非每個動作

## 模型選擇

為每個任務選擇正確的模型：

| 模型 | 最適合 | 速度 | 成本 |
|------|--------|------|------|
| **Haiku 4.5** | Explore agents、檔案搜尋、模式匹配 | 快 | 低 |
| **Sonnet 4.5** | 實作、程式碼審查、重構 | 平衡 | 中 |
| **Opus 4.5** | 架構決策、安全審計、複雜推理 | 深入 | 高 |

**快速提示**：按 `Option+P`（macOS）或 `Alt+P`（Windows/Linux）在提示時切換模型。

## 社群

- **網站**：[claude-world.com](https://claude-world.com)
- **Discord**：[Claude Code Builders Taiwan](https://discord.gg/rBtHzSD288)
- **Twitter**：[@lukashanren1](https://twitter.com/lukashanren1)

## 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解指南。

### 如何貢獻

1. **範例**：新增展示實際模式的範例
2. **模板**：為不同框架建立 CLAUDE.md 模板
3. **指南**：撰寫特定主題的深度指南
4. **翻譯**：幫助將內容翻譯成其他語言

如有討論和問題，歡迎加入我們的 [Discord 社群](https://discord.gg/rBtHzSD288)。

## 授權

MIT License - 請參閱 [LICENSE](./LICENSE)

---

由 Claude World 社群使用 Claude Code 建立。

*最後更新：2026-01-13*
