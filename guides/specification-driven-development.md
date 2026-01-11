# Specification-Driven Development

> Write specs first, let Claude implement. The most reliable way to build features.

## Why Specification-Driven?

Traditional approach:
```
You: "Build a user authentication system"
Claude: [makes assumptions about requirements]
        [implements what it thinks you want]
        [you discover gaps during testing]
        [back and forth to fix misunderstandings]
```

Specification-driven approach:
```
You: [write clear spec first]
Claude: [implements exactly what's specified]
        [asks clarifying questions upfront]
        [delivers predictable results]
```

**Key insight**: 30 minutes writing a spec saves hours of rework.

## The Specification Framework

### 1. Problem Statement

Start every spec with WHY:

```markdown
## Problem Statement

**Current State**: Users must remember passwords for our app.
**Pain Point**: 40% of support tickets are password resets.
**Desired State**: Users can login without passwords.
**Success Metric**: Reduce password reset tickets by 80%.
```

### 2. User Stories

Define WHO and WHAT:

```markdown
## User Stories

1. As a **new user**, I want to sign up with my email
   so that I can access the app without creating a password.

2. As a **returning user**, I want to receive a magic link
   so that I can login quickly from any device.

3. As a **security-conscious user**, I want links to expire
   so that my account stays secure if email is compromised.
```

### 3. Acceptance Criteria

Define DONE clearly:

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

### 4. Technical Constraints

Define HOW (boundaries):

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

### 5. Out of Scope

Define what NOT to build:

```markdown
## Out of Scope (v1)

- Social login (Google, GitHub) - Phase 2
- Phone number authentication - Phase 2
- Hardware key support (WebAuthn) - Phase 3
- Admin impersonation feature - Not planned
```

## Complete Specification Template

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

## Working with Claude

### Step 1: Write the Spec

Write your specification in a markdown file:

```
You: "I'm going to write a spec for magic link authentication.
     Review it and ask clarifying questions before we implement."
```

### Step 2: Clarification Round

Let Claude identify gaps:

```
Claude: "I have a few questions about the spec:

1. What happens if user clicks magic link on different device
   than where they requested it?

2. Should we invalidate all existing magic links when a new
   one is requested?

3. What's the behavior for unregistered emails - error or
   auto-create account?"
```

### Step 3: Refine the Spec

Update based on answers:

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

### Step 4: Implementation

Now Claude implements with clarity:

```
You: "Implement the magic link authentication per the spec.
     Check off acceptance criteria as you complete them."

Claude: [Implements with clear understanding]
        [Creates tests matching acceptance criteria]
        [Documents any deviations from spec]
```

### Step 5: Verification

Review against spec:

```
You: "Verify the implementation against the spec.
     List any criteria not yet met."

Claude: "Verification Results:

✅ Sign Up Flow: All criteria met
✅ Login Flow: All criteria met
⚠️ Security: Rate limiting implemented but not tested
❌ Performance: Email delivery at 45 seconds (target: 30s)

Recommended actions:
1. Add rate limiting tests
2. Investigate SendGrid latency"
```

## Advanced Patterns

### 1. Living Specifications

Keep specs updated as implementation evolves:

```markdown
## Changelog

### v1.1 (2024-01-15)
- Added: Device fingerprinting for suspicious login detection
- Changed: Link expiry from 15 to 30 minutes (user feedback)
- Removed: "Remember device" feature (security concern)

### v1.0 (2024-01-01)
- Initial implementation
```

### 2. Spec-Driven Testing

Generate tests from acceptance criteria:

```
You: "Generate test cases from the acceptance criteria.
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

    // ... more tests matching criteria
  });
});
```

### 3. Specification Reviews

Have Claude review specs before implementation:

```
You: "Review this spec for completeness. Identify:
     - Missing acceptance criteria
     - Ambiguous requirements
     - Potential edge cases
     - Security considerations"
```

### 4. Incremental Specifications

For large features, spec in phases:

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

## Common Mistakes

### 1. Vague Acceptance Criteria

```markdown
❌ Bad:
- [ ] System should be fast

✅ Good:
- [ ] API response time < 200ms (p95)
- [ ] Page load time < 1.5s on 3G
```

### 2. Missing Edge Cases

```markdown
❌ Bad:
- [ ] User can login with magic link

✅ Good:
- [ ] User can login with magic link
- [ ] Expired link shows "Link expired, request new one"
- [ ] Already-used link shows "Link already used"
- [ ] Invalid link shows "Invalid link"
```

### 3. No Success Metrics

```markdown
❌ Bad:
## Problem
Users complain about passwords.

✅ Good:
## Problem
**Pain Point**: 40% of support tickets are password resets
**Success Metric**: Reduce password reset tickets by 80%
```

### 4. Scope Creep in Specs

```markdown
❌ Bad:
## Features
- Magic link login
- Social login
- SMS verification
- Biometric auth
- Password fallback

✅ Good:
## In Scope (v1)
- Magic link login

## Out of Scope (v1)
- Social login - Phase 2
- SMS verification - Not planned (cost)
- Biometric auth - Phase 3
- Password fallback - Intentionally excluded
```

## Specification Checklist

Before implementing, verify your spec has:

```
□ Problem Statement
  □ Current state described
  □ Pain point quantified
  □ Desired state clear
  □ Success metric defined

□ User Stories
  □ All user roles covered
  □ Actions and benefits clear

□ Acceptance Criteria
  □ Testable (yes/no verifiable)
  □ Complete (covers all features)
  □ Edge cases included
  □ Error states defined

□ Technical Constraints
  □ Required technologies listed
  □ Restrictions documented
  □ Performance targets set

□ Scope
  □ In-scope clearly defined
  □ Out-of-scope explicitly listed
  □ Phase boundaries clear

□ Open Questions
  □ All ambiguities listed
  □ Questions answered before implementation
```

## Summary

1. **Write specs first** - 30 minutes saves hours
2. **Be specific** - Vague specs = vague implementations
3. **Include criteria** - Define "done" clearly
4. **List constraints** - Bound the solution space
5. **Exclude explicitly** - Say what you're NOT building
6. **Iterate the spec** - Let Claude ask questions
7. **Verify against spec** - Check off criteria
8. **Keep specs living** - Update as you learn

**Golden Rule**: If you can't write it in a spec, you can't build it reliably.

---

See also: [Feature Development](../examples/feature-development.md) | [Production Readiness](./production-readiness.md)
