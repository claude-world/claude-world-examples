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

# 現實：專案 6 個月前已遷移到 React 19 + hooks + Zustand
```

**為何失敗**：Claude 為錯誤的版本產生程式碼，導致不斷修正。

**修正**：每季或重大變更後審查 CLAUDE.md，並執行 `/doctor prompt-audit` 找出指向已不存在的檔案或指令的內容：

```markdown
## 技術棧
- React 19（僅使用 functional components + hooks）
- Zustand 5.x 做 client state
- TanStack Query v5 做 server state
- Vitest 做測試（2024 年從 Jest 遷移）

最後更新：2026-10-01
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

衝突也會藏在不同檔案之間。子目錄的 CLAUDE.md、`.claude/rules/` 和你的使用者層級指示會一起載入，彼此不會互相覆蓋，所以 Claude 可能遵循任何一方。`/doctor prompt-audit` 會回報互相矛盾的指示檔案。

### 5. 包山包海

**問題**：CLAUDE.md 超過 2000 行，涵蓋每種可能情境。

```markdown
# 不好的範例：50 頁的指引涵蓋：
- 每個 API endpoint 規格
- 完整的資料庫 schema
- 完整的部署流程
- 逐檔說明整個程式碼庫
- 3 年前的歷史決策
- 會議記錄
```

**為何失敗**：CLAUDE.md 每個 session 都會完整載入。低價值資訊填滿 context window，遵循度也跟著下降：真正重要的規則被淹沒在雜訊裡。

**修正**：每個 CLAUDE.md 控制在約 200 行以內。連結到詳細文件，並把流程改寫成 skill：

```markdown
# 好的範例

## 快速參考
- 技術：Next.js 16、PostgreSQL、Prisma
- 指令：`pnpm dev`、`pnpm test`、`pnpm db:migrate`

## 核心指引
[10-15 個最重要的規則]

## 詳細文件
- API 規格：參見 `/docs/api/README.md`
- 資料庫：參見 `/prisma/README.md`
- 部署：使用 `/deploy` skill（`.claude/skills/deploy/SKILL.md`）
```

只跟某個區域有關的指引，應該放在 `.claude/rules/`。帶有 `paths:` frontmatter 的規則只會在 Claude 處理符合的檔案時載入，例如 `.claude/rules/database.md`：

```markdown
---
paths:
  - "prisma/**"
---

# 資料庫規則
- 每次 schema 變更都需要 migration（`pnpm db:migrate`）
- 永遠不要修改 `prisma/migrations/` 中已套用的 migrations
```

別想用 `@path` 匯入來縮短檔案：被匯入的檔案同樣會在啟動時載入。像上面那樣寫一般路徑，Claude 就只會在需要時才開啟該文件。

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

> **CLAUDE.md 不會授予或封鎖任何權限。** 這些清單引導的是 Claude 的判斷；工具存取權是由 Claude Code 另外強制執行的，靠的是 `.claude/settings.json` 裡的 `permissions`，以及你選擇的權限模式（`Shift+Tab`，或設定中的 `defaultMode`）。同樣的意圖可以對應到三種規則類型，檢查順序是先 deny、再 ask、最後 allow：

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(pnpm test *)",
      "Bash(pnpm lint *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Edit(src/auth/**)"
    ],
    "deny": [
      "Bash(git push --force *)"
    ]
  }
}
```

規則比對的是指令的實際寫法（`git push origin main --force` 會繞過 deny 規則，但仍會被 `ask` 規則攔下），所以要把範圍窄的 deny 和範圍寬的 ask 搭配使用。規則模式表達不了的檢查，請改用 PreToolUse [hook](./hooks-basics.md)。

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

````markdown
## API 指引

### 回應格式
```jsonc
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
````

### 8. 過時的範例

**問題**：程式碼範例使用已棄用的模式或舊語法。

````markdown
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
````

**為何失敗**：Claude 複製範例模式，產生過時的程式碼。

**修正**：模式變更時更新範例：

````markdown
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
````

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

如果 Claude 問的問題 CLAUDE.md 裡已經有答案，通常是措辭不夠明確。如果它一直違反已經寫下的規則，可能是檔案太長、規則被淹沒了，或者這條規則需要的是強制執行（權限規則或 hook），而不是文字說明。執行 `/context` 確認檔案到底有沒有載入。

## CLAUDE.md 健康檢查

定期執行這個檢查：

```markdown
## 每月 CLAUDE.md 審查

1. [ ] 技術棧符合實際依賴
2. [ ] 範例使用目前的模式
3. [ ] 沒有矛盾的指引（`/doctor prompt-audit` 可以幫忙）
4. [ ] 權限是平衡的（不只是限制）；硬性限制放在 settings.json 或 hooks
5. [ ] 不超過約 200 行（路徑相關規則放 `.claude/rules/`，流程放 skills）
6. [ ] 「最後更新」日期是最新的
7. [ ] 新團隊成員能理解
8. [ ] `/context` 的 Memory files 列出了預期的檔案
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
5. **保持聚焦** - 控制在約 200 行以內；其餘交給 rules、skills 和連結
6. **平衡權限** - 賦能，而不只是限制；硬性限制交給 settings.json 強制執行
7. **明確表達** - 不要用「像平常一樣」或「標準方式」
8. **更新範例** - 程式碼範例必須符合目前模式

---

另見：[CLAUDE.md 原則](./claude-md-principles.md) | [Director Mode 基礎](./director-mode-basics.md)
