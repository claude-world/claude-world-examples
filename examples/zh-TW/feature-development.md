# 功能開發模式

一種使用 Claude Code 實作新功能的結構化方法。

## 模式

與其不斷來回地逐步建立功能，不如給 Claude 完整的全貌，讓它實作整個功能。

## 5 步驟流程

### 步驟 1: 清楚定義功能

**不好的寫法**：
```
「添加通知系統」
```

**好的寫法**：
```
「為以下事件實作電子郵件通知：
1. 新使用者註冊 → 歡迎郵件
2. 密碼重設請求 → 重設連結郵件
3. 訂單確認 → 訂單確認郵件

需求：
- 使用 /lib/email 中現有的 EmailService
- 在 User model 中儲存通知偏好設定
- 添加 API 端點來更新偏好設定
- 所有郵件包含取消訂閱連結
」
```

### 步驟 2: 讓 Claude 分析

Claude 啟動 parallel agents 來理解 context：

```
Agent 1: 分析現有 EmailService
Agent 2: 審視 User model 結構
Agent 3: 檢查現有通知模式
Agent 4: 檢視 API 路由慣例
Agent 5: 查看現有郵件範本
```

### 步驟 3: 審視計畫

Claude 提出實作方案：

```
「這是我的實作計畫：

1. 資料庫變更：
   - 在 users 添加 notification_preferences JSONB 欄位
   - 建立 email_logs 資料表用於追蹤

2. 新檔案：
   - /lib/notifications/index.ts - 主服務
   - /lib/notifications/templates/*.tsx - 郵件範本
   - /api/users/preferences.ts - API 端點

3. 修改：
   - /lib/auth/signup.ts - 觸發歡迎郵件
   - /lib/auth/reset.ts - 觸發重設郵件
   - /lib/orders/confirm.ts - 觸發訂單郵件

4. 測試：
   - 通知服務的單元測試
   - 郵件發送的整合測試
   - 偏好設定端點的 API 測試

要繼續實作嗎？」
```

### 步驟 4: 實作

```
你: 「繼續」

Claude: [實作所有內容]
- 建立 migration
- 實作通知服務
- 添加郵件範本
- 建立 API 端點
- 更新現有程式碼
- 撰寫測試
- 執行測試驗證
```

### 步驟 5: 審視和迭代

```
Claude: 「實作完成。所有測試通過。

已建立：
- /lib/notifications/index.ts
- /lib/notifications/templates/welcome.tsx
- /lib/notifications/templates/reset.tsx
- /lib/notifications/templates/order.tsx
- /api/users/preferences.ts
- /prisma/migrations/add_notifications.sql

已修改：
- /lib/auth/signup.ts
- /lib/auth/reset.ts
- /lib/orders/confirm.ts

測試: 12 個新測試，全部通過。

準備好審視。」
```

## 範例：完整功能請求

這是一個真實世界完整功能請求的範例：

```markdown
## 功能: 使用者儀表板分析

### 使用者故事

作為使用者，我想要看到我的活動分析，以便了解我的使用模式。

### 需求

**要顯示的資料：**
- 總專案建立數
- 過去 30 天的活動（圖表）
- 最活躍的專案
- 近期活動時間軸

**UI 需求：**
- 新的 /dashboard/analytics 頁面
- 使用 /components/ui 中現有的 Chart 元件
- 行動裝置響應式
- 資料載入的 loading 狀態

**API 需求：**
- GET /api/analytics/summary - 概覽統計
- GET /api/analytics/activity?days=30 - 活動資料

**技術限制：**
- 快取分析資料（5 分鐘 TTL）
- 使用現有 auth middleware
- 遵循現有 API 模式

### 不在範圍內
- 匯出功能
- 與其他使用者比較
- 自訂日期範圍
```

## 專業技巧

### 1. 參考現有模式

```
「添加類似我們在 /features/reviews 中實作的
評論功能的留言功能」
```

### 2. 指定邊界情況

```
「處理這些邊界情況：
- 沒有活動的使用者 → 顯示引導提示
- API timeout → 顯示快取資料並標示過時
- 速率限制 → 排隊通知，批次發送」
```

### 3. 包含驗收標準

```
「功能完成條件：
- [ ] 所有測試通過
- [ ] TypeScript 沒有錯誤
- [ ] 行動裝置版面正常
- [ ] 已實作 loading 狀態
- [ ] 已處理錯誤狀態」
```

### 4. 分解大型功能

對於非常大的功能，分成階段：

```
「階段 1: 後端
- 資料庫 schema
- API 端點
- 核心服務邏輯

階段 2: 前端
- UI 元件
- 狀態管理
- 整合

階段 3: 優化
- 錯誤處理
- Loading 狀態
- 分析追蹤」
```

## 要避免的反模式

### 不要：漸進式實作

```
你: 「添加一個按鈕」
Claude: [添加按鈕]
你: 「現在添加點擊處理器」
Claude: [添加處理器]
你: 「現在添加 API 呼叫」
...
```

### 要：完整實作

```
你: 「添加匯出按鈕，呼叫 /api/export 並
下載結果為 CSV」
Claude: [一次實作所有內容]
```

## 總結

1. **完整定義** - 所有需求一次提出
2. **讓 Claude 分析** - Parallel agents 收集 context
3. **審視計畫** - 實作前先批准
4. **一次實作** - 完整功能，而非增量
5. **審視和迭代** - 對完成的工作給予回饋

---

另見：[Parallel Agents](../concepts/parallel-agents.md)
