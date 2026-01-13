# CLAUDE.md 反模式

> 從常見錯誤中學習，寫出更有效的專案指引。

## 為什麼這很重要

寫得不好的 CLAUDE.md 會導致：
- Claude 不斷重複問問題
- 程式碼品質不一致
- 浪費 context 在澄清上
- 開發週期變慢

本指南涵蓋最常見的錯誤以及如何修正。

## 反模式

### 1. 模糊的指示

**問題**：指示太籠統，無法執行。

```markdown
# 不好的範例
## 指引
- 寫好的程式碼
- 遵循最佳實踐
- 讓它運作良好
```

**為何失敗**：Claude 每次 session 對「好」和「最佳」的解讀都不同。沒有客觀標準可以遵循。

**修正**：

```markdown
# 好的範例
## 指引
- 使用 TypeScript strict mode（不允許 `any` 型別）
- 函式不超過 30 行
- 所有公開函式必須有 JSDoc 註解
- 錯誤訊息必須包含錯誤碼（例如 ERR_AUTH_001）
```

### 2. 過時的脈絡

**問題**：CLAUDE.md 描述的是專案過去的樣子，而非現在。

```markdown
# 不好的範例
## 技術棧
- React 16 使用 class components
- Redux 做狀態管理
- Jest 做測試

# 現實：專案 6 個月前已遷移到 React 18 + hooks + Zustand
```

**為何失敗**：Claude 為錯誤的版本產生程式碼，導致不斷修正。

**修正**：每季或重大變更後審查 CLAUDE.md：

```markdown
## 技術棧
- React 18.2（僅使用 functional components + hooks）
- Zustand 4.x 做 client state
- React Query 做 server state
- Vitest 做測試（2024 年從 Jest 遷移）

最後更新：2025-01-15
```

### 3. 缺少原因說明

**問題**：說明要做什麼但沒說為什麼。

```markdown
# 不好的範例
## 規則
- 永遠不要用 localStorage
- 一律使用 httpOnly cookies
```

**為何失敗**：Claude 不理解原因，可能在遵循字面意思的同時違反精神。

**修正**：

```markdown
# 好的範例
## 驗證規則
- **永遠不要用 localStorage 存 tokens**
  - 原因：XSS 攻擊可以從 localStorage 竊取 tokens
  - 替代方案：使用 httpOnly cookies（JavaScript 無法存取）

- **一律在 server 端驗證 tokens**
  - 原因：client 端驗證可以被繞過
  - 方式：每個 API 請求都檢查簽章 + 過期時間
```

### 4. 矛盾的指引

**問題**：不同章節給出相衝突的建議。

```markdown
# 不好的範例
## 章節 1：效能
- Inline 所有 critical CSS 以加快 First Contentful Paint

## 章節 2：程式碼風格
- 永遠不要使用 inline styles；所有 CSS 必須在獨立檔案
```

**為何失敗**：Claude 隨機選一個或每次都詢問澄清。

**修正**：識別衝突並加入優先順序/範圍：

```markdown
## CSS 指引

### Critical Path（above-the-fold）
- 在 <head> inline critical CSS 做 FCP 優化
- 使用 Critical 等工具提取 critical CSS

### 一般樣式
- 所有非 critical CSS 放在獨立的 .css 檔案
- 元件樣式使用 CSS modules

優先順序：對於 above-the-fold 內容，效能規則優先於風格規則。
```

### 5. 包山包海

**問題**：CLAUDE.md 超過 2000 行，涵蓋每種可能情境。

```markdown
# 不好的範例：50 頁的指引涵蓋：
- 每個 API endpoint 規格
- 完整的資料庫 schema
- 完整的部署流程
- 3 年前的歷史決策
- 會議記錄
```

**為何失敗**：Claude 的 context window 被低價值資訊填滿，留給實際工作的空間更少。

**修正**：保持 CLAUDE.md 聚焦；連結到詳細文件：

```markdown
# 好的範例

## 快速參考
- 技術：Next.js 14、PostgreSQL、Prisma
- 指令：`pnpm dev`、`pnpm test`、`pnpm db:migrate`

## 核心指引
[10-15 個最重要的規則]

## 詳細文件
- API 規格：參見 `/docs/api/README.md`
- 資料庫：參見 `/prisma/README.md`
- 部署：參見 `/docs/deployment.md`
```

### 6. 只有限制沒有權限

**問題**：CLAUDE.md 全是限制，沒有權限。

```markdown
# 不好的範例
## 規則
- 不要修改 package.json
- 不要變更資料庫 schema
- 不要刪除任何檔案
- 不要修改現有測試
- 不要加入新依賴
```

**為何失敗**：Claude 變得過度謹慎，每件事都要問權限。

**修正**：平衡限制與明確的權限：

```markdown
## 權限

### 可以自由做
- 建立/修改 /src 裡的檔案
- 執行測試並修復失敗
- 重構程式碼同時維護測試
- 從核准清單加入依賴（參見 /docs/approved-deps.md）

### 需要提及
- 資料庫 schema 變更（需要 migration）
- 新的 API endpoints（需要文件）
- 移除功能（需要棄用計畫）

### 禁止
- 未經審查修改 auth/security 程式碼
- Force push 到 main
- 刪除測試檔案
```

### 7. 隱含假設

**問題**：假設 Claude 知道沒有文件記載的事情。

```markdown
# 不好的範例
## API 指引
- 遵循我們的標準模式
- 使用常用的錯誤格式
- 像平常一樣檢查權限
```

**為何失敗**：「我們的標準」和「平常」沒有定義就沒有意義。

**修正**：把一切都明確化：

```markdown
## API 指引

### 回應格式
```json
{
  "success": true|false,
  "data": { ... } | null,
  "error": { "code": "ERR_XXX", "message": "..." } | null
}
```

### 權限檢查模式
```typescript
// 每個受保護的 endpoint 都以此開始：
const user = await requireAuth(req);
if (!hasPermission(user, 'resource:action')) {
  throw new ForbiddenError('ERR_PERM_001');
}
```
```

### 8. 過時的範例

**問題**：程式碼範例使用已棄用的模式或舊語法。

```markdown
# 不好的範例
## 元件模式
```jsx
class UserProfile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { user: null };
  }
  componentDidMount() {
    this.fetchUser();
  }
  // ...
}
```

**為何失敗**：Claude 複製範例模式，產生過時的程式碼。

**修正**：模式變更時更新範例：

```markdown
## 元件模式
```tsx
// 資料載入元件的標準模式
export function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  if (isLoading) return <Skeleton />;
  return <ProfileCard user={user} />;
}
```
```

## 診斷檢查清單

當 Claude 不斷問同樣的問題時，使用這個檢查清單：

| 症狀 | 可能原因 | 修正 |
|---------|--------------|-----|
| 「要用什麼驗證方式？」 | 缺少 auth 章節 | 記錄驗證方式 |
| 「要用哪個資料庫？」 | 缺少技術棧 | 加入清楚的技術棧 |
| 「錯誤格式是什麼？」 | 缺少 API 標準 | 加入回應格式 |
| 「需要加測試嗎？」 | 缺少測試政策 | 加入測試指引 |
| 「這應該放哪裡？」 | 缺少專案結構 | 加入目錄指南 |
| 「可以安裝 X 嗎？」 | 缺少依賴政策 | 加入核准的依賴清單 |

## CLAUDE.md 健康檢查

定期執行這個檢查：

```markdown
## 每月 CLAUDE.md 審查

1. [ ] 技術棧符合實際依賴
2. [ ] 範例使用目前的模式
3. [ ] 沒有矛盾的指引
4. [ ] 權限是平衡的（不只是限制）
5. [ ] 不超過 500 行（連結到詳細文件）
6. [ ] 「最後更新」日期是最新的
7. [ ] 新團隊成員能理解
```

## 快速修正

### 問題：Claude 不斷問 X

**解決方案**：加入 FAQ 章節：

```markdown
## 給 Claude 的 FAQ

問：需要寫測試嗎？
答：要，一律要。工具函式寫單元測試，API endpoints 寫整合測試。

問：用什麼 logging 函式庫？
答：使用 `pino`。從 `@/lib/logger` import。

問：如何處理錯誤？
答：從 `@/lib/errors` 拋出 typed errors。永遠不要用 generic Error()。
```

### 問題：Claude 產生不一致的程式碼

**解決方案**：加入「不要 vs 要」章節：

```markdown
## 風格指南快速參考

| 不要 | 要 |
|-------|-----|
| `any` 型別 | 正確的 TypeScript 型別 |
| `console.log` | `logger.info()` |
| Inline styles | Tailwind classes |
| `var` | `const` 或 `let` |
| 巢狀 callbacks | async/await |
```

## 總結

1. **要具體** - 不要用「好」或「最佳」這類模糊詞彙
2. **保持更新** - 專案變更時就更新
3. **解釋原因** - 脈絡幫助 Claude 做出更好的決定
4. **解決衝突** - 規則衝突時設定優先順序
5. **保持聚焦** - 連結到詳細文件而非嵌入
6. **平衡權限** - 賦能，而不只是限制
7. **明確表達** - 不要用「像平常一樣」或「標準方式」
8. **更新範例** - 程式碼範例必須符合目前模式

---

另見：[CLAUDE.md 原則](./claude-md-principles.md) | [Director Mode 基礎](./director-mode-basics.md)
