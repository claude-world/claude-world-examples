# 簡單的 CLAUDE.md 範本

一個精簡但有效的 CLAUDE.md，你可以根據任何專案來調整。

## 範本

```markdown
# [你的專案名稱]

> 簡短描述這個專案做什麼

## 技術棧

- **框架**: [例如 Next.js 14, Express, Django]
- **資料庫**: [例如 PostgreSQL, MongoDB, SQLite]
- **語言**: [例如 TypeScript, Python, Go]

## 專案結構

```
/src
  /components   - UI 元件
  /lib          - 工具函式和輔助程式
  /api          - API 路由/處理器
  /types        - TypeScript 型別
/tests          - 測試檔案
/docs           - 文件
```

## 快速指令

```bash
npm run dev     # 啟動開發伺服器
npm run test    # 執行測試
npm run build   # 建置生產版本
npm run lint    # 檢查程式碼風格
```

## 開發指引

### 要做的事

- 為新功能撰寫測試
- 使用 TypeScript 嚴格模式
- 遵循現有程式碼模式
- 保持函式小而專注

### 不要做的事

- 無故添加依賴
- 跳過錯誤處理
- 使用 `any` 型別
- 在生產程式碼中留下 console.logs

## 常見模式

### API 回應格式

```typescript
{
  success: boolean;
  data?: T;
  error?: string;
}
```

### 元件結構

```typescript
// components/FeatureName/index.tsx - 主要匯出
// components/FeatureName/FeatureName.tsx - 元件
// components/FeatureName/FeatureName.test.tsx - 測試
```
```

## 自訂技巧

### 適用於 React/Next.js 專案

添加：
```markdown
## 狀態管理

- 使用 React Query 處理伺服器狀態
- 使用 Zustand 處理客戶端狀態
- 避免 prop drilling - 使用 context

## 樣式

- 所有樣式使用 Tailwind CSS
- 使用 cn() 輔助函式處理條件類別
- 設計 tokens 放在 tailwind.config.ts
```

### 適用於 API/後端專案

添加：
```markdown
## API 設計

- RESTful 端點
- 版本控制: /api/v1/...
- 認證: Authorization header 中使用 Bearer token

## 錯誤處理

- 使用自訂錯誤類別
- 將所有錯誤記錄到監控系統
- 回傳一致的錯誤格式
```

### 適用於 CLI 工具

添加：
```markdown
## CLI 結構

- 指令放在 /src/commands
- 使用 Commander.js 解析
- 所有輸出透過 logger 工具

## 測試

- 每個指令都要有單元測試
- 整合測試放在 /tests/integration
- 在測試中 mock 檔案系統
```

## 為什麼這樣有效

1. **Context** - Claude 立即了解你的技術棧
2. **結構** - Claude 可以導航你的程式碼庫
3. **指令** - Claude 可以執行你的腳本
4. **指引** - Claude 遵循你的慣例
5. **模式** - Claude 產生一致的程式碼

## 下一步

從這個範本開始，當你注意到以下情況時進行擴展：

- Claude 一直問的問題 → 加到 CLAUDE.md
- Claude 應該遵循的模式 → 記錄下來
- Claude 應該知道的決策 → 寫下來

---

另見：[CLAUDE.md 原則](../concepts/claude-md-principles.md)
