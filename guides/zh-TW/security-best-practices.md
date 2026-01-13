# 安全最佳實踐

> 從一開始就使用 Claude 建構安全的應用程式。

## 為何安全優先？

安全問題是：
- **後期修復成本高** - 正式環境比開發階段貴 6 倍
- **損害聲譽** - 一次洩露可能摧毀使用者信任
- **通常不可見** - 在被利用前你不知道有漏洞

本指南展示如何使用 Claude 進行安全意識開發。

## 安全心態

### CLAUDE.md 安全區段

添加到每個專案：

```markdown
## Security Guidelines

### Authentication
- All passwords: bcrypt with cost factor 12
- Tokens: httpOnly cookies, not localStorage
- Session timeout: 15 minutes idle, 24 hours max

### Authorization
- Every endpoint checks permissions before processing
- Use UUIDs for resource IDs (not sequential integers)
- Deny by default, allow explicitly

### Input Validation
- Validate ALL user input server-side
- Use parameterized queries (never string concatenation)
- Sanitize output (prevent XSS)

### Secrets
- Never commit secrets to git
- Use environment variables
- Rotate secrets if exposed

### Logging
- Never log passwords, tokens, or PII
- Log authentication events
- Include request IDs for tracing
```

## 常見漏洞與修復

### 1. SQL 注入

**有漏洞的程式碼**：
```javascript
// ❌ 絕對不要這樣做
const query = `SELECT * FROM users WHERE id = ${userId}`;
db.query(query);
```

**Claude 指令**：
```
"Find all SQL queries that use string concatenation and convert them to parameterized queries"
```

**安全程式碼**：
```javascript
// ✅ 總是使用參數化查詢
const query = 'SELECT * FROM users WHERE id = $1';
db.query(query, [userId]);
```

### 2. 跨站腳本（XSS）

**有漏洞的程式碼**：
```jsx
// ❌ 危險
<div dangerouslySetInnerHTML={{__html: userInput}} />

// ❌ 同樣危險
element.innerHTML = userInput;
```

**Claude 指令**：
```
"Find all instances of dangerouslySetInnerHTML and innerHTML that use user input"
```

**安全程式碼**：
```jsx
// ✅ 安全 - React 預設會跳脫
<div>{userInput}</div>

// ✅ 如需 HTML，先消毒
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

### 3. 不安全的身份驗證

**有漏洞的程式碼**：
```javascript
// ❌ 弱雜湊
const hash = crypto.createHash('md5').update(password).digest('hex');

// ❌ Token 在 localStorage（可被 XSS 存取）
localStorage.setItem('token', jwt);
```

**Claude 指令**：
```
"Review authentication implementation for:
- Weak hashing algorithms (MD5, SHA1)
- Tokens stored in localStorage
- Missing rate limiting on login"
```

**安全程式碼**：
```javascript
// ✅ 強雜湊
import bcrypt from 'bcrypt';
const hash = await bcrypt.hash(password, 12);

// ✅ httpOnly cookie（JavaScript 無法存取）
res.cookie('token', jwt, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 15 * 60 * 1000 // 15 分鐘
});
```

### 4. 損壞的存取控制

**有漏洞的程式碼**：
```javascript
// ❌ 無授權檢查
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
});
```

**Claude 指令**：
```
"Find all API endpoints that access user data without checking permissions"
```

**安全程式碼**：
```javascript
// ✅ 總是檢查權限
app.get('/api/users/:id', requireAuth, async (req, res) => {
  // 檢查使用者是否可存取此資源
  if (req.user.id !== req.params.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Access denied' });
  }

  const user = await User.findById(req.params.id);
  res.json(user);
});
```

### 5. 敏感資料暴露

**有漏洞的程式碼**：
```javascript
// ❌ 記錄敏感資料
console.log('Login attempt:', { email, password });

// ❌ 返回敏感欄位
res.json(user); // 包含密碼雜湊
```

**Claude 指令**：
```
"Find all instances where passwords, tokens, or sensitive user data might be logged or exposed"
```

**安全程式碼**：
```javascript
// ✅ 絕不記錄敏感資料
logger.info('Login attempt', { email, timestamp: new Date() });

// ✅ 排除敏感欄位
const { password, ...safeUser } = user;
res.json(safeUser);

// ✅ 或使用 DTO
res.json(new UserDTO(user));
```

### 6. 安全配置錯誤

**有漏洞的程式碼**：
```javascript
// ❌ CORS 允許所有來源
app.use(cors({ origin: '*' }));

// ❌ 缺少安全標頭
// (無 helmet、無 CSP)
```

**Claude 指令**：
```
"Review security configuration:
- CORS settings
- Security headers (CSP, HSTS, etc.)
- Cookie settings
- Error handling (no stack traces to client)"
```

**安全程式碼**：
```javascript
// ✅ 限制性 CORS
app.use(cors({
  origin: ['https://myapp.com'],
  credentials: true
}));

// ✅ 使用 helmet 的安全標頭
import helmet from 'helmet';
app.use(helmet());

// ✅ Content Security Policy
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
  }
}));
```

## 安全稽核工作流程

### 步驟 1：自動掃描

```
"Run a security scan on this codebase checking for OWASP Top 10 vulnerabilities"
```

Claude 將檢查：
- 注入缺陷
- 損壞的身份驗證
- 敏感資料暴露
- XXE
- 損壞的存取控制
- 安全配置錯誤
- XSS
- 不安全的反序列化
- 已知漏洞元件
- 不足的日誌記錄

### 步驟 2：身份驗證審查

```
"Review all authentication and authorization code:
- How are passwords stored?
- How are sessions managed?
- Are there rate limits on auth endpoints?
- Is MFA available?"
```

### 步驟 3：輸入驗證審查

```
"Find all places where user input is used and verify:
- Server-side validation exists
- Parameterized queries for database
- Output encoding for HTML
- File upload restrictions"
```

### 步驟 4：機密稽核

```
"Search for hardcoded secrets, API keys, or credentials in:
- Source code
- Configuration files
- Environment files
- Git history"
```

### 步驟 5：相依套件稽核

```
"Check dependencies for known vulnerabilities using npm audit or similar"
```

## 依功能的安全檢查清單

### 使用者註冊
```
□ 密碼強度要求已強制
□ 需要電子郵件驗證
□ 註冊端點有速率限制
□ CAPTCHA 防止濫用
□ URL 參數中無敏感資料
```

### 登入
```
□ 密碼驗證使用 Bcrypt/Argon2
□ 嘗試失敗後帳戶鎖定
□ 登入端點有速率限制
□ 安全的 session token 產生
□ httpOnly、secure cookies
□ CSRF 防護
```

### 密碼重設
```
□ Token 快速過期（15-60 分鐘）
□ Token 只能使用一次
□ 不需要舊密碼（他們忘了）
□ 密碼變更的電子郵件通知
□ 重設請求有速率限制
```

### API 端點
```
□ 需要身份驗證（或明確公開）
□ 資源存取有授權檢查
□ 所有參數有輸入驗證
□ 每使用者/IP 有速率限制
□ 適當的錯誤回應（無敏感資訊）
```

### 檔案上傳
```
□ 檔案類型驗證（不僅是副檔名）
□ 檔案大小限制
□ 惡意軟體掃描
□ 儲存在 web root 之外
□ 隨機化檔名
```

### 支付處理
```
□ 使用成熟的支付提供者（Stripe 等）
□ 絕不儲存完整卡號
□ PCI DSS 合規
□ 所有交易的稽核日誌
□ 詐騙檢測
```

## Claude 安全指令

### 快速安全檢查
```
"Quick security check: find the top 5 most critical security issues in this codebase"
```

### 提交前安全審查
```
"Review these changes for security issues before I commit"
```

### 相依套件漏洞檢查
```
"Check if any of our dependencies have known security vulnerabilities"
```

### 滲透測試準備
```
"Prepare a list of potential attack vectors for penetration testing this application"
```

### 安全文件
```
"Generate security documentation covering:
- Authentication flow
- Authorization model
- Data encryption
- Audit logging"
```

## 安全反模式

### 不要：自己寫加密
```javascript
// ❌ 自訂加密
function encrypt(data) {
  return data.split('').map(c =>
    String.fromCharCode(c.charCodeAt(0) + 1)
  ).join('');
}
```

### 要：使用成熟的函式庫
```javascript
// ✅ 使用經過驗證的函式庫
import { createCipheriv, randomBytes } from 'crypto';
```

### 不要：只信任客戶端驗證
```javascript
// ❌ 只在前端檢查
if (form.checkValidity()) {
  submitToServer(formData);
}
```

### 要：總是在伺服器端驗證
```javascript
// ✅ 伺服器端驗證
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});
const validated = schema.parse(req.body);
```

### 不要：在程式碼中儲存機密
```javascript
// ❌ 寫死的機密
const API_KEY = 'sk_live_abc123...';
```

### 要：使用環境變數
```javascript
// ✅ 環境變數
const API_KEY = process.env.API_KEY;
if (!API_KEY) throw new Error('API_KEY required');
```

## 總結

1. **在 CLAUDE.md 添加安全區段** - 將安全作為一等公民
2. **使用參數化查詢** - 防止 SQL 注入
3. **消毒輸出** - 防止 XSS
4. **強身份驗證** - bcrypt、httpOnly cookies、速率限制
5. **處處檢查授權** - 每個端點、每個資源
6. **絕不記錄敏感資料** - 密碼、token、PII
7. **使用安全標頭** - helmet、CSP、HSTS
8. **保持相依套件更新** - 定期 npm audit
9. **定期安全審查** - 使用 Claude 進行自動掃描

**黃金法則**：假設所有輸入都是惡意的，直到驗證過。

---

另請參閱：[正式環境就緒](./production-readiness.md) | [快速參考卡](./quick-reference.md)
