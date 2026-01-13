# Bug 追蹤模式

一種使用 parallel agents 系統性找出和修復 bug 的方法。

## 模式

當你遇到 bug 時，不要只是描述它。給 Claude 一個清楚的指令，讓 parallel agents 同時進行調查。

## 步驟說明

### 1. 清楚描述 Bug

**不好的寫法**：
```
「登入有問題」
```

**好的寫法**：
```
「Bug: 使用者回報在活動使用 app 時，恰好 15 分鐘後被登出。
預期: 使用者活動時 session 應該要更新。」
```

### 2. 讓 Claude 啟動 Parallel 調查

Claude 會自動啟動多個 agents：

```
Agent 1 (Explore): 對應認證流程
Agent 2 (Grep): 搜尋 session/timeout/expiry 程式碼
Agent 3 (Grep): 檢查 token 更新邏輯
Agent 4 (Read): 檢視 auth middleware
Agent 5 (Bash): 檢查近期 auth 檔案的 commits
```

### 3. 審視發現

Claude 綜合所有 agent 的結果：

```
「調查完成。找到問題了：

在 /lib/auth/session.ts:42:
- Session timeout 硬編碼為 15 分鐘
- 更新邏輯只在頁面載入時執行
- 活動請求不會觸發更新

根本原因: 缺少基於活動的 session 更新。

建議修復: 添加 middleware 在 API 呼叫時更新 session。」
```

### 4. 批准並修復

```
你: 「修好它」

Claude: [實作修復]
- 添加 session 更新 middleware
- 更新現有 auth middleware
- 為新行為添加測試
- 以描述性訊息提交
```

## 範例情境

### 情境 1: UI Bug

```
你: 「Bug: 表單驗證通過後，提交按鈕仍保持禁用狀態。
重現步驟: 正確填寫所有欄位，按鈕仍是灰色的。」

Claude: [啟動 agents]
- 搜尋按鈕禁用邏輯
- 檢查表單驗證狀態
- 審視程式碼庫中類似的表單
- 發現: 驗證和狀態更新之間存在競態條件

Claude: 「找到了。驗證是非同步執行的，但按鈕同步檢查狀態。
添加 await 可以修復。」
```

### 情境 2: 效能 Bug

```
你: 「Bug: 對於有很多專案的使用者，Dashboard 載入需要 10 秒以上。
新使用者則正常運作。」

Claude: [啟動 agents]
- 分析 dashboard API 端點
- 檢查資料庫查詢
- 審視分頁邏輯
- 分析 N+1 查詢模式

Claude: 「在專案載入中發現 N+1 查詢。每個專案都會觸發一個
單獨的團隊成員查詢。添加 eager loading 可以將 100 個查詢
減少到 2 個。」
```

### 情境 3: 資料 Bug

```
你: 「Bug: 部分使用者的活動日誌有重複條目。
不是所有使用者，看起來是隨機的。」

Claude: [啟動 agents]
- 搜尋活動記錄程式碼
- 檢查競態條件
- 審視資料庫約束
- 檢視重試邏輯

Claude: 「找到了。活動記錄器在 timeout 時重試，但不會檢查
第一個請求是否成功。添加冪等性 key 可以防止重複。」
```

## 最佳實踐

### 1. 包含重現步驟

```markdown
Bug: [描述]
步驟:
1. 以使用者身分登入
2. 導航到 /settings
3. 點擊「儲存」
4. 出現錯誤

預期: 設定已儲存
實際: 「伺服器錯誤」訊息
```

### 2. 包含錯誤訊息

```
Bug: API 回傳 500 錯誤
錯誤: "TypeError: Cannot read property 'id' of undefined"
端點: POST /api/projects
```

### 3. 提及你已嘗試過的方法

```
Bug: 測試在 CI 失敗但本地通過
已嘗試:
- 清除快取
- 使用相同 Node 版本執行
- 檢查環境變數
看起來都一樣。
```

### 4. 提供 Context

```
Bug: 部分使用者的支付處理失敗
Context:
- 部署 commit abc123 後開始
- 只影響 Stripe 支付，PayPal 正常
- 我們的 logs 沒有錯誤
```

## 調查檢查清單

Claude 的 parallel agents 通常會檢查：

- [ ] 錯誤訊息和堆疊追蹤
- [ ] 相關程式碼檔案
- [ ] 近期變更 (git log)
- [ ] 程式碼庫中類似的模式
- [ ] 測試覆蓋率
- [ ] 設定檔
- [ ] 外部服務狀態
- [ ] 資料庫狀態

## 總結

1. **清楚描述** - Bug、步驟、預期 vs 實際
2. **讓 Claude 調查** - Parallel agents 很快
3. **審視綜合結果** - Claude 結合所有發現
4. **批准修復** - 一個指令完成實作

使用這個模式的平均 bug 修復時間：**2-5 分鐘**

---

另見：[Director Mode 基礎](../concepts/director-mode-basics.md)
