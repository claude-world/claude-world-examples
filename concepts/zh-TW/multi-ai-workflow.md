# Multi-AI 工作流程模式

> 當一個 AI 不夠時：協調 Claude、Codex 和 Gemini CLI。

## 為什麼要用多個 AI CLIs？

每個 AI CLI 有不同的優勢：

| CLI | 最適合 | 權衡 |
|-----|----------|-----------| 
| **Claude Code** | 複雜推理、架構、程式碼審查 | 批量操作較慢 |
| **Codex CLI** | 快速編輯、批量重構、簡單修復 | 脈絡感知較少 |
| **Gemini CLI** | 長時間執行任務、大型程式碼庫 | 互動風格不同 |

把它們一起用可能比只用一個更有效率。

## Handoff 模式

### 何時留在 Claude

```
✓ 複雜的架構決策
✓ 多步驟推理
✓ 帶脈絡的程式碼審查
✓ 帶調查的除錯
✓ 功能實作加測試
✓ 安全敏感的程式碼
```

### 何時 Handoff 給 Codex

```
✓ 批量尋找和替換
✓ 簡單重構（跨檔案重新命名變數）
✓ 機械式轉換
✓ 範本產生
✓ 格式/風格修正
```

### 何時 Handoff 給 Gemini

```
✓ 非常長的任務（>30 分鐘）
✓ 大型程式碼庫探索
✓ 背景處理
✓ 可以在你做其他事時執行的任務
```

## 實際範例

### 範例 1：大型重構

**情境**：將一個模組從 `UserAuth` 重新命名為 `Authentication`，橫跨 50 個檔案。

**方式**：

```
步驟 1：Claude 分析影響
「分析將 UserAuth 重新命名為 Authentication 需要改什麼」

Claude：[啟動 parallel agents]
→ 列出所有包含 UserAuth 的檔案
→ 識別 import 模式
→ 標記潛在的破壞性變更
→ 建立變更計畫

步驟 2：Handoff 給 Codex 做批量變更
「使用上面的計畫，在所有檔案中將 UserAuth 重新命名為 Authentication」

Codex：[快速批量替換]
→ 幾秒內更新 50 個檔案
→ 修復 imports
→ 機械式工作快速完成

步驟 3：Claude 驗證
「驗證重構是否完整和正確」

Claude：[審查變更]
→ 檢查是否有遺漏的參考
→ 執行測試
→ 識別任何問題
```

### 範例 2：測試產生

**情境**：為 20 個工具函式產生測試。

**方式**：

```
步驟 1：Claude 建立模式
「分析我們的測試模式並為工具測試建立範本」

Claude：[分析現有測試]
→ 識別測試結構
→ 建立範本
→ 記錄要涵蓋的 edge cases

步驟 2：Codex 批量產生測試
「依照範本為這 20 個函式產生測試」

Codex：[產生所有 20 個測試檔案]
→ 快速機械式產生
→ 精確遵循範本

步驟 3：Claude 審查並加強
「審查產生的測試並加入遺漏的 edge cases」

Claude：[智慧審查]
→ 加入 Codex 遺漏的 edge cases
→ 改善斷言
→ 確保覆蓋率
```

### 範例 3：長時間執行分析

**情境**：分析一個舊程式碼庫尋找現代化機會。

**方式**：

```
步驟 1：Gemini 做初始掃描（背景）
「掃描整個程式碼庫並建立清單：
- 已棄用的模式
- Dead code
- 缺少的測試
- 安全問題」

Gemini：[背景執行 30+ 分鐘]
→ 你繼續做其他工作
→ 完成時有完整報告

步驟 2：Claude 排列發現的優先順序
「審查 Gemini 的報告並依影響排序」

Claude：[應用判斷]
→ 依嚴重性排序問題
→ 建立行動計畫
→ 估計工作量

步驟 3：用適當的工具執行
→ 安全修復：Claude（需要脈絡）
→ Dead code 移除：Codex（機械式）
→ 模式更新：混合方式
```

## 脈絡傳遞策略

### 策略 1：基於檔案的 Handoff

```markdown
## Handoff 檔案：handoff-context.md

### 任務
將所有 `oldFunction` 實例重新命名為 `newFunction`

### 脈絡
- 要修改的檔案：/src/utils/*.ts、/src/components/*.tsx
- 模式：`oldFunction(` → `newFunction(`
- 也要更新：imports、exports、型別定義

### Claude 完成的
- [x] 影響分析
- [x] 識別 47 個檔案

### 給 Codex 的
- [ ] 執行替換
- [ ] 更新 imports
```

### 策略 2：Checkpoint 模式

```
1. Claude 在分析後建立 checkpoint
   → 儲存狀態到 .claude-checkpoint.json

2. 其他 CLI 讀取 checkpoint
   → 理解已完成的內容
   → 知道下一步要做什麼

3. Claude 驗證最終狀態
   → 與預期結果比較
   → 處理 edge cases
```

### 策略 3：Git Branch 隔離

```bash
# Claude 在分析 branch 工作
git checkout -b feature/auth-refactor-analysis
# Claude 做分析工作

# Codex 在實作 branch 工作
git checkout -b feature/auth-refactor-impl
# Codex 做機械式變更

# 合併後 Claude 驗證
git checkout feature/auth-refactor-analysis
git merge feature/auth-refactor-impl
# Claude 審查合併後的結果
```

## 決策框架

```
┌─────────────────────────────────────────┐
│         我應該用哪個 CLI？               │
└─────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ 是否複雜/需要細緻處理？│
        └───────────┬───────────┘
               是   │  否
                    │    │
    ┌───────────────┘    └──────────────┐
    ▼                                   ▼
┌─────────┐                    ┌───────────────────┐
│ CLAUDE  │                    │ 是否批量/批次？    │
└─────────┘                    └─────────┬─────────┘
                                    是   │  否
                               ┌─────────┘  │
                               ▼            ▼
                          ┌───────┐   ┌───────────────┐
                          │ CODEX │   │ 是否長時間     │
                          └───────┘   │ 執行？         │
                                      └───────┬───────┘
                                         是   │  否
                                    ┌─────────┘  │
                                    ▼            ▼
                               ┌────────┐   ┌────────┐
                               │ GEMINI │   │ CLAUDE │
                               └────────┘   └────────┘
```

## 最佳實踐

### 1. 從 Claude 開始

Claude 擅長理解任務和建立計畫：

```
「我需要更新所有 API endpoints 使用新的 auth 模式。
為這次遷移建立計畫。」
```

### 2. 記錄 Handoff 點

切換 CLIs 時要明確：

```markdown
## Handoff 給 Codex

### 已完成的
- 分析完成
- 模式已識別
- 列出 34 個檔案

### 要做的
- 在列出的檔案中將模式 A 替換為模式 B
- 不要修改：/src/auth/core.ts（需要人工審查）
```

### 3. 批量操作後驗證

一律回到 Claude 做驗證：

```
「Codex 已完成批量重新命名。驗證：
1. 所有參考都已更新
2. 測試仍然通過
3. 沒有遺漏的 edge cases」
```

### 4. 保持人類參與

對於關鍵操作：

```
Claude → Codex → 人工審查 → Claude 驗證
            ↓
    批量變更需要人類核准
    然後 Claude 才驗證
```

## 要避免的反模式

### 不要：用 Codex 做複雜邏輯

```
✗ 「Codex，重構這個驗證流程使用 JWT」
  → 缺乏脈絡，可能破壞安全性

✓ 「Claude，重構驗證使用 JWT」
  → 理解影響，處理 edge cases
```

### 不要：用 Claude 做機械式工作

```
✗ 「Claude，在所有 200 個檔案中將 'foo' 重新命名為 'bar'」
  → 浪費 Claude 的能力，慢

✓ 「Codex，在所有 200 個檔案中將 'foo' 重新命名為 'bar'」
  → 快速，非常適合機械式任務
```

### 不要：Handoffs 之間遺失脈絡

```
✗ 「Codex，完成 Claude 開始的工作」
  → Codex 不知道 Claude 做了什麼

✓ 「Codex，根據 handoff-context.md，完成重新命名操作」
  → 清楚傳遞脈絡
```

## 總結

| 步驟 | CLI | 目的 |
|------|-----|---------| 
| 1. 分析 | Claude | 理解任務，建立計畫 |
| 2. 批量執行 | Codex | 快速機械式變更 |
| 3. 長時間任務 | Gemini | 背景處理 |
| 4. 驗證 | Claude | 審查、測試、完成 |

關鍵洞察：**在工作的每個階段使用正確的工具**。

---

另見：[Director Mode 基礎](./director-mode-basics.md) | [Parallel Agents](./parallel-agents.md)
