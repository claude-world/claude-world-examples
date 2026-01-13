# 規格驅動開發

> 先寫規格，讓 Claude 實作。建構功能最可靠的方式。

## 為何規格驅動？

傳統方法：
```
你：「建構使用者身份驗證系統」
Claude：[對需求做出假設]
        [實作它認為你想要的]
        [你在測試時發現缺陷]
        [來回修正誤解]
```

規格驅動方法：
```
你：[先寫清楚的規格]
Claude：[精確實作規格中的內容]
        [提前詢問釐清問題]
        [交付可預測的結果]
```

**關鍵洞察**：花 30 分鐘寫規格可省下數小時的返工。

## 規格框架

### 1. 問題陳述

每個規格都從 WHY 開始：

```markdown
## Problem Statement

**Current State**: Users must remember passwords for our app.
**Pain Point**: 40% of support tickets are password resets.
**Desired State**: Users can login without passwords.
**Success Metric**: Reduce password reset tickets by 80%.
```

### 2. 使用者故事

定義 WHO 和 WHAT：

```markdown
## User Stories

1. As a **new user**, I want to sign up with my email
   so that I can access the app without creating a password.

2. As a **returning user**, I want to receive a magic link
   so that I can login quickly from any device.

3. As a **security-conscious user**, I want links to expire
   so that my account stays secure if email is compromised.
```

### 3. 驗收標準

清楚定義 DONE：

```markdown
## Acceptance Criteria

### Sign Up Flow
- [ ] User enters email address
- [ ] System sends verification email within 30 seconds
- [ ] Email contains magic link valid for 15 minutes
- [ ] Clicking link creates account and logs user in
- [ ] Invalid/expired links show friendly error message

### Login Flow
- [ ] User enters email address
- [ ] System sends magic link within 30 seconds
- [ ] Link works on any device (not tied to browser)
- [ ] User remains logged in for 30 days
- [ ] "Remember this device" option available

### Security
- [ ] Links are single-use (invalidated after click)
- [ ] Rate limiting: max 5 requests per email per hour
- [ ] Links contain cryptographically secure tokens
- [ ] No sensitive data in URL parameters
```

### 4. 技術限制

定義 HOW（邊界）：

```markdown
## Technical Constraints

### Must Use
- Existing PostgreSQL database
- SendGrid for email delivery
- JWT for session management

### Must Not
- Store passwords (this is passwordless)
- Use SMS (cost prohibitive)
- Require JavaScript for basic flow

### Performance
- Email delivery < 30 seconds
- Login redirect < 500ms
- Support 1000 concurrent logins
```

### 5. 範圍外

定義什麼不建構：

```markdown
## Out of Scope (v1)

- Social login (Google, GitHub) - Phase 2
- Phone number authentication - Phase 2
- Hardware key support (WebAuthn) - Phase 3
- Admin impersonation feature - Not planned
```

## 完整規格模板

```markdown
# Feature: [Name]

## Problem Statement
**Current State**: [What exists now]
**Pain Point**: [What's wrong with it]
**Desired State**: [What we want instead]
**Success Metric**: [How we measure success]

## User Stories
1. As a [role], I want [action] so that [benefit].
2. As a [role], I want [action] so that [benefit].

## Acceptance Criteria

### [Feature Area 1]
- [ ] Criterion 1
- [ ] Criterion 2

### [Feature Area 2]
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Constraints

### Must Use
- [Technology/Pattern]

### Must Not
- [Anti-pattern/Restriction]

### Performance
- [Requirement]

## Out of Scope
- [Feature] - [Reason]

## Open Questions
- [ ] [Question that needs answering]

## Mockups/Diagrams
[Links or embedded images]
```

## 與 Claude 協作

### 步驟 1：撰寫規格

在 markdown 檔案中撰寫你的規格：

```
你："I'm going to write a spec for magic link authentication.
     Review it and ask clarifying questions before we implement."
```

### 步驟 2：釐清輪次

讓 Claude 識別缺口：

```
Claude："I have a few questions about the spec:

1. What happens if user clicks magic link on different device
   than where they requested it?

2. Should we invalidate all existing magic links when a new
   one is requested?

3. What's the behavior for unregistered emails - error or
   auto-create account?"
```

### 步驟 3：精煉規格

根據答案更新：

```markdown
## Clarifications

### Cross-Device Login
- Magic links work on any device
- No device binding required
- Session created on clicking device

### Link Invalidation
- New request invalidates previous links
- Maximum 1 active link per user

### Unregistered Emails
- Auto-create account on first magic link use
- No separate registration required
```

### 步驟 4：實作

現在 Claude 帶著清晰理解實作：

```
你："Implement the magic link authentication per the spec.
     Check off acceptance criteria as you complete them."

Claude：[帶著清晰理解實作]
        [建立符合驗收標準的測試]
        [記錄任何與規格的偏差]
```

### 步驟 5：驗證

對照規格審查：

```
你："Verify the implementation against the spec.
     List any criteria not yet met."

Claude："Verification Results:

✅ Sign Up Flow: All criteria met
✅ Login Flow: All criteria met
⚠️ Security: Rate limiting implemented but not tested
❌ Performance: Email delivery at 45 seconds (target: 30s)

Recommended actions:
1. Add rate limiting tests
2. Investigate SendGrid latency"
```

## 進階模式

### 1. 活文件規格

隨著實作演進更新規格：

```markdown
## Changelog

### v1.1 (2024-01-15)
- Added: Device fingerprinting for suspicious login detection
- Changed: Link expiry from 15 to 30 minutes (user feedback)
- Removed: "Remember device" feature (security concern)

### v1.0 (2024-01-01)
- Initial implementation
```

### 2. 規格驅動測試

從驗收標準產生測試：

```
你："Generate test cases from the acceptance criteria.
     Each criterion should have at least one test."
```

```javascript
describe('Magic Link Authentication', () => {
  describe('Sign Up Flow', () => {
    it('sends verification email within 30 seconds', async () => {
      const start = Date.now();
      await requestMagicLink('new@example.com');
      const elapsed = Date.now() - start;
      expect(elapsed).toBeLessThan(30000);
    });

    it('creates magic link valid for 15 minutes', async () => {
      const { token, expiresAt } = await requestMagicLink('new@example.com');
      const validity = expiresAt - Date.now();
      expect(validity).toBe(15 * 60 * 1000);
    });

    // ... 更多符合標準的測試
  });
});
```

### 3. 規格審查

讓 Claude 在實作前審查規格：

```
你："Review this spec for completeness. Identify:
     - Missing acceptance criteria
     - Ambiguous requirements
     - Potential edge cases
     - Security considerations"
```

### 4. 漸進式規格

對於大型功能，分階段規格：

```markdown
# Magic Link Auth - Phase 1 (MVP)

## Scope
- Basic email/magic link flow
- Single device support

---

# Magic Link Auth - Phase 2

## Scope
- Multi-device support
- Device management UI

---

# Magic Link Auth - Phase 3

## Scope
- Social login integration
- SSO support
```

## 常見錯誤

### 1. 模糊的驗收標準

```markdown
❌ 不好：
- [ ] System should be fast

✅ 好的：
- [ ] API response time < 200ms (p95)
- [ ] Page load time < 1.5s on 3G
```

### 2. 缺少邊緣案例

```markdown
❌ 不好：
- [ ] User can login with magic link

✅ 好的：
- [ ] User can login with magic link
- [ ] Expired link shows "Link expired, request new one"
- [ ] Already-used link shows "Link already used"
- [ ] Invalid link shows "Invalid link"
```

### 3. 無成功指標

```markdown
❌ 不好：
## Problem
Users complain about passwords.

✅ 好的：
## Problem
**Pain Point**: 40% of support tickets are password resets
**Success Metric**: Reduce password reset tickets by 80%
```

### 4. 規格中的範圍蔓延

```markdown
❌ 不好：
## Features
- Magic link login
- Social login
- SMS verification
- Biometric auth
- Password fallback

✅ 好的：
## In Scope (v1)
- Magic link login

## Out of Scope (v1)
- Social login - Phase 2
- SMS verification - Not planned (cost)
- Biometric auth - Phase 3
- Password fallback - Intentionally excluded
```

## 規格檢查清單

實作前，驗證你的規格有：

```
□ 問題陳述
  □ 描述當前狀態
  □ 量化痛點
  □ 明確期望狀態
  □ 定義成功指標

□ 使用者故事
  □ 涵蓋所有使用者角色
  □ 動作和效益清晰

□ 驗收標準
  □ 可測試（是/否可驗證）
  □ 完整（涵蓋所有功能）
  □ 包含邊緣案例
  □ 定義錯誤狀態

□ 技術限制
  □ 列出必要技術
  □ 記錄限制
  □ 設定效能目標

□ 範圍
  □ 明確定義範圍內
  □ 明確列出範圍外
  □ 清楚階段邊界

□ 待解問題
  □ 列出所有模糊處
  □ 實作前回答問題
```

## 總結

1. **先寫規格** - 30 分鐘省下數小時
2. **要具體** - 模糊規格 = 模糊實作
3. **包含標準** - 清楚定義「完成」
4. **列出限制** - 限定解決方案空間
5. **明確排除** - 說明你不建構什麼
6. **迭代規格** - 讓 Claude 提問
7. **對照規格驗證** - 勾選標準
8. **保持規格活著** - 隨學習更新

**黃金法則**：如果你無法在規格中寫出來，你就無法可靠地建構它。

---

另請參閱：[Feature Development](../examples/feature-development.md) | [Production Readiness](./production-readiness.md)
