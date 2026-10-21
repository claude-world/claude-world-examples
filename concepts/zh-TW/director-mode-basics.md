# Director Mode 基礎

> 停止當動手做的開發者。開始當團隊導演。

## 問題所在

大多數開發者這樣使用 Claude Code：

```
開發者：「嘿 Claude，你可以幫我加一個登入功能嗎？」
Claude：「當然！你想用什麼驗證方式？」
開發者：「JWT」
Claude：「好的！token 要存在哪裡？」
開發者：「LocalStorage」
Claude：「需要加入 refresh token 邏輯嗎？」
開發者：「要」
... [再來 10 個問題] ...
```

這樣**效率很低**。你花在回答問題的時間比實際完成工作的時間還多。

## Director Mode 解決方案

把自己想成團隊導演，Claude 是你的開發團隊。

好的導演不會：
- 回答每個小問題
- 批准每個小決定
- 微觀管理實作細節

好的導演會：
- 設定清晰的目標
- 提供脈絡和限制條件
- 信任團隊執行
- 審查完成的工作

## 實際應用

### 1. 給予清晰的目標

**不好**：「你可以幫我處理驗證嗎？」

**好**：「實作 JWT 驗證加上 refresh token。把 token 存在 httpOnly cookies。使用現有的 User model。」

### 2. 在 CLAUDE.md 提供脈絡

```markdown
# 專案脈絡

## 架構決策
- 我們使用 JWT 做驗證（不是 sessions）
- 所有 API routes 在 /api 資料夾
- 我們遵循 REST 慣例

## 偏好設定
- TypeScript strict mode
- 優先使用組合而非繼承
- 所有新功能都要寫測試
```

### 3. 讓 Claude 自主執行

有了適當的脈絡，Claude 可以：
- 做出合理的決定而不需要詢問
- 使用平行的 subagents 更快地研究
- 只要你給它可執行的檢查（測試、建置、lint），就能自行驗證成果
- 一次完成整個功能

目前的 Claude Code 預設以 auto mode 啟動互動 session：由分類器代替你審查每個動作，而不是逐一詢問你。`Shift+Tab` 可以切換權限模式，其中包含唯讀、先做規劃的 plan mode。CLAUDE.md 是指引而不是強制機制，所以硬性限制（例如 `git push`）要寫在 `.claude/settings.json` 的權限規則裡。

### 4. 審查，而非監督

不要盯著每一步：
1. 交付任務
2. 讓 Claude 工作
3. 審查完成的 PR
4. 需要時提供回饋

如果方向看起來不對，按 `Esc` 中斷，或按 `Esc Esc`（`/rewind`）把程式碼和對話還原到先前的 checkpoint。

## 思維模式轉變

| 微觀管理者 | Director Mode |
|------------|-----------------|
| 回答每個問題 | 預先提供脈絡 |
| 批准每一步 | 審查完成的工作 |
| 單線程工作 | Parallel agents |
| 看著 Claude 工作 | Claude 工作時做其他事 |
| 1x 生產力 | 5-10x 生產力 |

## 開始使用

1. **撰寫精簡的 CLAUDE.md** - 先用 `/init` 產生起始版本，再加入你的技術棧、偏好和常見模式（目標是 200 行以內）
2. **使用命令式指令** - 「實作 X」而不是「你可以幫忙 X 嗎？」
3. **信任流程** - 讓 Claude 在你的限制條件內做決定
4. **迭代改進** - 根據 Claude 問的問題來改進你的 CLAUDE.md（請 Claude 把答案加進去，或用 `/memory` 開啟檔案）

> Director Mode 是一種工作方式，不是 Claude Code 的內建功能。社群的 [director-mode-lite](https://github.com/claude-world/director-mode-lite) plugin 把它包裝成 `/workflow`、`/focus-problem`、`/smart-commit` 等 skills。安裝方式：先執行 `/plugin marketplace add claude-world/director-mode-lite`，再執行 `/plugin install director-mode-lite@director-mode-lite`（或 clone repo 後執行 `./install.sh`，取得完整的專案本地設定）。以 plugin 安裝時，每個 skill 也可以用帶命名空間的名稱呼叫，例如 `/director-mode-lite:workflow`。

## 範例 Session

```
你：「實作使用者個人資料編輯與頭像上傳」

Claude：[啟動 4 個平行的 Explore subagents]
- Agent 1：分析現有的 user model
- Agent 2：檢查程式碼庫中的檔案上傳模式
- Agent 3：審查 UI 元件庫
- Agent 4：檢查 API route 慣例

[10 秒後]

Claude：「我已經實作了個人資料編輯功能：
- 新增 /api/users/profile endpoint
- 建立 ProfileEditForm 元件
- 整合現有的 S3 上傳服務
- 為所有新程式碼加入測試
- 建立 avatar_url 欄位的 migration

準備好審查了。」
```

總時間：2 分鐘，而不是 30 分鐘的來回溝通。

---

下一篇：[CLAUDE.md 原則](./claude-md-principles.md)
