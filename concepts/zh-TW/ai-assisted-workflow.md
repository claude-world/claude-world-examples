# AI 輔助開發工作流程

> 如何將 Claude Code 當作力量放大器，而不只是程式碼助手

## 典範轉移

傳統開發：
```
開發者 → 寫程式碼 → 測試 → 除錯 → 重複
```

AI 輔助開發：
```
導演 → 定義目標 → Claude 執行 → 審查結果 → 發布
```

關鍵洞察：**你不是在用 AI 幫助寫程式碼。你是在指揮一個 AI agents 團隊。**

## 力量放大器效應

| 指標 | 傳統 | AI 輔助 | 倍數 |
|--------|-------------|-------------|------------|
| 程式碼行數/小時 | 50-100 | 500-1000 | 10x |
| 探索檔案數/session | 10-20 | 100-200 | 10x |
| 脈絡切換 | 很多 | 很少 | 0.2x |
| 決策疲勞 | 高 | 低 | 0.3x |

## 核心原則

### 1. 目標而非指令

**不要這樣**：
```
「建立一個叫 UserService.ts 的檔案，包含一個 class，
有 getUserById、createUser 和 updateUser 方法...」
```

**要這樣**：
```
「依照現有的 service 模式實作使用者 CRUD 操作」
```

讓 Claude 搞清楚細節。你的工作是結果，不是步驟。

### 2. 平行探索

**不要這樣**：
```
「搜尋驗證程式碼」
[等待]
「現在搜尋 user model」
[等待]
「現在檢查 middleware」
```

**要這樣**：
```
「用 subagents 探索驗證系統（thoroughness: medium）」
```

Claude 會把彼此獨立的搜尋委派給 Explore subagents 平行執行，每個都在自己的 context window 中運作並回報摘要，讓你的主對話保持乾淨。

### 3. 自主執行

**不要這樣**：
```
Claude：「要建立檔案嗎？」
你：「要」
Claude：「要加入 import 嗎？」
你：「要」
Claude：「要執行測試嗎？」
你：「要」
```

**要在 `.claude/settings.json` 設定權限規則**：
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test *)",
      "Bash(git add *)",
      "Bash(git commit *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(npm run migrate *)"
    ]
  }
}
```

目前的 Claude Code 預設以 auto mode 啟動互動 session，例行的編輯和指令不會跳出詢問，而明確的 `ask` 和 `deny` 規則在每種模式下都仍然有效。在 CLAUDE.md 保留一份對應的「自主操作／需要確認」清單，讓 Claude 了解你的意圖，但光靠 CLAUDE.md 並不會強制執行任何事。

### 4. 審查，而非監督

**不要**：盯著每一個按鍵

**要**：審查完成的工作
```
你：「實作這個功能」
[Claude 工作 5 分鐘]
Claude：「完成。建立了 3 個檔案，加入測試，全部通過。」
你：[審查 diff，批准或請求修改]
```

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    AI 輔助工作流程                           │
└─────────────────────────────────────────────────────────────┘

1. 定義
   ├── 你想要什麼結果？
   ├── 有什麼限制條件？
   └── 驗收標準是什麼？

2. 委派
   ├── 給 Claude 目標
   ├── 讓它探索和規劃（plan mode：Shift+Tab）
   └── 信任平行執行

3. 審查
   ├── 檢查結果
   ├── 驗證測試通過
   └── 批准、迭代，或 /rewind

4. 發布
   ├── Commit 變更
   ├── Push 到遠端
   └── 監控部署
```

## 實際範例

### 範例 1：Bug 修復

**傳統方式**（約 30 分鐘）：
```
1. 閱讀錯誤報告
2. 搜尋相關程式碼
3. 加入 console.logs
4. 重現問題
5. 找出根本原因
6. 寫修復
7. 測試修復
8. 移除 console.logs
9. 寫測試
10. Commit
```

**AI 輔助方式**（約 5 分鐘）：
```
你：「修復登入逾時 bug。錯誤：'Session expired after 5 minutes'」

Claude：[啟動 parallel agents]
        → Agent 1：在程式碼庫搜尋錯誤訊息
        → Agent 2：檢查 session 設定
        → Agent 3：審查 auth middleware
        → Agent 4：檢查最近的 commits
        → Agent 5：尋找逾時設定

Claude：「找到問題：session.maxAge 設為 300000ms（5 分鐘）
         而非 3600000ms（1 小時）。已在 auth/config.ts 修復。
         加入測試。已 commit。」
```

### 範例 2：新功能

**傳統方式**（約 4 小時）：
```
1. 規劃功能
2. 設計 API
3. 建立資料庫 schema
4. 實作後端
5. 寫測試
6. 實作前端
7. 整合測試
8. 文件
```

**AI 輔助方式**（約 1 小時）：
```
你：「加入使用者個人頭像上傳功能。
需求：
- 上傳到 S3
- 調整大小為 200x200
- 更新使用者個人資料
- 在 navbar 顯示」

Claude：[自主工作]
        → 建立 API endpoint
        → 加入 S3 整合
        → 實作圖片處理
        → 更新前端
        → 寫測試
        → 更新型別

Claude：「功能完成。修改了 8 個檔案，建立 2 個新檔案。
         測試通過。預覽在 /profile/settings。」
```

### 範例 3：程式碼審查

**傳統方式**（約 20 分鐘）：
```
1. 讀完整個 PR
2. 檢查每個檔案
3. 本地執行測試
4. 寫評論
5. 請求修改
```

**AI 輔助方式**（約 3 分鐘）：
```
你：「審查 PR #123」   （或執行 /review 123）

Claude：[平行分析]
        → 程式碼品質檢查
        → 安全掃描
        → 測試覆蓋率分析
        → 架構審查
        → 文件檢查

Claude：「PR 審查摘要：
         ✅ 測試通過
         ✅ 無安全問題
         ⚠️ UserService.ts:42 缺少 null 檢查
         ⚠️ 考慮為新 endpoint 加入 rate limiting
         📝 為匯出的函式加入 JSDoc」
```

## 設定你的工作流程

### 1. 建立有效的 CLAUDE.md

```markdown
# 專案：[名稱]

## 技術棧
[列出你的技術]

## 自主操作
- 讀寫原始碼檔案
- 執行測試和建置
- Git 操作（本地）
- 安裝依賴

## 需要確認
- Git push
- 資料庫 migrations
- API key 變更
- 正式環境部署

## 程式碼標準
[你的慣例]

## 測試要求
[你的測試政策]
```

用 `/init` 產生起始版本，維持在 200 行以內，並用上面示範的權限規則來落實「需要確認」清單。

### 2. 使用 Session 為基礎的開發

```
Session 1：「設定專案結構」
Session 2：「實作核心資料模型」
Session 3：「建構 API endpoints」
Session 4：「建立前端元件」
Session 5：「整合和測試」
```

每個 session = 清晰的目標 + 自主執行 + 審查。不相關的任務之間執行 `/clear`；用 `claude --continue` 或 `/resume` 接續先前的 session。

### 3. 善用模型選擇

| 任務類型 | 模型 | 原因 |
|-----------|-------|------|
| 快速查找、簡單編輯 | Haiku 5.5 | 快速、低成本，適合大量且講求低延遲的任務 |
| 實作 | Sonnet 5.5 | 速度與智慧的最佳組合 |
| 架構 | Opus 5.5 | 長時間的 agentic coding 與知識工作 |
| 安全審查 | Opus 5.5 搭配 `high` 或 `max` effort | 徹底分析 |

快速切換：`/model haiku|sonnet|opus`，或 `Option+P`（macOS）／`Alt+P`（Windows/Linux）。用 `/effort` 調整推理深度（5.5 系列模型預設為 `medium`），或在單一提示中加入 `ultrathink`。在 Pro、Max、Team、Enterprise 和 API 帳號上，`default` 模型是 Opus 5.5。Fable 5.1（`/model fable`）的官方定位是「適合高難度推理與長時程的 agentic 工作」，永遠不會是預設模型，在部分方案中會以 usage credits 計費。

內建的 Explore subagent 使用你主對話的模型。若想用 Haiku 做探索，請自行定義一個 `model: haiku` 的 `Explore` subagent。

### 4. 信任流程

最困難的部分是**放手讓出控制權**。

```
❌ 「讓我看看你在做什麼...」
❌ 「等等，那部分我想自己做...」
❌ 「你確定那個方式嗎？」

✅ 「這是目標。執行。」
✅ [審查完成的工作]
✅ 「發布」或「試試不同的方式」
```

## 衡量成功

### 時間指標

追蹤這些專案指標：

| 指標 | AI 之前 | AI 之後 |
|--------|-----------|----------|
| 功能實作 | X 小時 | Y 小時 |
| Bug 調查 | X 分鐘 | Y 分鐘 |
| 程式碼審查 | X 分鐘 | Y 分鐘 |
| 文件 | X 小時 | Y 小時 |

### 品質指標

AI 輔助開發通常改善：
- 測試覆蓋率（只要 CLAUDE.md 有要求，Claude 就會寫測試）
- 文件（Claude 邊寫程式碼邊記錄）
- 一致性（Claude 精確地遵循模式）
- 安全性（Claude 檢查常見問題；可在你的 branch 上執行 `/security-review`）

## 常見陷阱

### 1. 微觀管理

**問題**：給出逐步指令
**解決方案**：給目標，不是步驟

### 2. 不信任 Parallel Agents

**問題**：一次執行一個搜尋
**解決方案**：請 Claude 使用 subagents（例如 Explore），或讓 Claude 平行化

### 3. 跳過 CLAUDE.md

**問題**：每個 session 重新解釋脈絡
**解決方案**：投資時間寫好 CLAUDE.md

### 4. 任務選錯模型

**問題**：用高 effort 的 Opus 做簡單搜尋
**解決方案**：快速查找用 Haiku 5.5 或 `/effort low`，coding 用 Sonnet 5.5 或 Opus 5.5

## 48 小時心態

這個工作流程讓 [claude-world.com](https://claude-world.com) 在 48 小時內建成：

- **第 1 天**：架構 + 基本設定
- **第 2 天**：所有功能實作完成
- **第 3 天**：修飾 + 發布

秘訣：**從第一分鐘就用 Director Mode 思維。**

你不是在更快地寫程式碼。你在完全不同的層次上運作。

---

## 相關資源

- [Director Mode 基礎](./director-mode-basics.md)
- [Parallel Agents](./parallel-agents.md)
- [48 小時網站案例研究](../../case-studies/zh-TW/48-hour-website.md)
- [CLAUDE.md 原則](./claude-md-principles.md)

---

*停止寫程式碼。開始指揮結果。*
