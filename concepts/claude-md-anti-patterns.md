# CLAUDE.md Anti-Patterns

> Learn from common mistakes to write more effective project instructions.

## Why This Matters

A poorly written CLAUDE.md causes:
- Repeated questions from Claude
- Inconsistent code quality
- Wasted context on clarifications
- Slower development cycles

This guide covers the most common mistakes and how to fix them.

## The Anti-Patterns

### 1. The Vague Directive

**Problem**: Instructions too generic to be actionable.

```markdown
# Bad Example
## Guidelines
- Write good code
- Follow best practices
- Make it work well
```

**Why it fails**: Claude interprets "good" and "best" differently each session. There's no objective standard to follow.

**Fix**:

```markdown
# Good Example
## Guidelines
- Use TypeScript strict mode (no `any` types)
- Functions under 30 lines
- All public functions must have JSDoc comments
- Error messages must include error codes (e.g., ERR_AUTH_001)
```

### 2. The Outdated Context

**Problem**: CLAUDE.md describes the project as it was, not as it is.

```markdown
# Bad Example
## Tech Stack
- React 16 with class components
- Redux for state management
- Jest for testing

# Reality: Project migrated to React 18 + hooks + Zustand 6 months ago
```

**Why it fails**: Claude generates code for the wrong version, causing constant corrections.

**Fix**: Review CLAUDE.md quarterly or after major changes:

```markdown
## Tech Stack
- React 18.2 (functional components + hooks only)
- Zustand 4.x for client state
- React Query for server state
- Vitest for testing (migrated from Jest in 2024)

Last updated: 2025-01-15
```

### 3. The Missing Why

**Problem**: States what to do but not why.

```markdown
# Bad Example
## Rules
- Never use localStorage
- Always use httpOnly cookies
```

**Why it fails**: Claude doesn't understand the reasoning and may violate the spirit while following the letter.

**Fix**:

```markdown
# Good Example
## Authentication Rules
- **Never use localStorage for tokens**
  - Why: XSS attacks can steal tokens from localStorage
  - Instead: Use httpOnly cookies (inaccessible to JavaScript)

- **Always validate tokens server-side**
  - Why: Client-side validation can be bypassed
  - How: Check signature + expiry on every API request
```

### 4. The Contradictory Guidelines

**Problem**: Different sections give conflicting advice.

```markdown
# Bad Example
## Section 1: Performance
- Inline all critical CSS for faster First Contentful Paint

## Section 2: Code Style
- Never use inline styles; all CSS must be in separate files
```

**Why it fails**: Claude picks one randomly or asks for clarification every time.

**Fix**: Identify conflicts and add priority/scope:

```markdown
## CSS Guidelines

### Critical Path (above-the-fold)
- Inline critical CSS in <head> for FCP optimization
- Use tools like Critical to extract critical CSS

### General Styles
- All non-critical CSS in separate .css files
- Use CSS modules for component styles

Priority: Performance rules override style rules for above-the-fold content.
```

### 5. The Kitchen Sink

**Problem**: CLAUDE.md is 2000+ lines covering every possible scenario.

```markdown
# Bad Example: 50 pages of guidelines covering:
- Every API endpoint specification
- Full database schema
- Complete deployment procedures
- Historical decisions from 3 years ago
- Meeting notes
```

**Why it fails**: Claude's context window fills up with low-value information, leaving less room for actual work.

**Fix**: Keep CLAUDE.md focused; link to detailed docs:

```markdown
# Good Example

## Quick Reference
- Tech: Next.js 14, PostgreSQL, Prisma
- Commands: `pnpm dev`, `pnpm test`, `pnpm db:migrate`

## Core Guidelines
[10-15 most important rules]

## Detailed Documentation
- API spec: See `/docs/api/README.md`
- Database: See `/prisma/README.md`
- Deployment: See `/docs/deployment.md`
```

### 6. The No-Permissions Trap

**Problem**: CLAUDE.md is all restrictions, no permissions.

```markdown
# Bad Example
## Rules
- Don't modify package.json
- Don't change database schema
- Don't delete any files
- Don't modify existing tests
- Don't add new dependencies
```

**Why it fails**: Claude becomes overly cautious, asking permission for everything.

**Fix**: Balance restrictions with explicit permissions:

```markdown
## Permissions

### Can Do Freely
- Create/modify files in /src
- Run tests and fix failures
- Refactor code while maintaining tests
- Add dependencies from our approved list (see /docs/approved-deps.md)

### Requires Mention
- Database schema changes (need migration)
- New API endpoints (need documentation)
- Removing functionality (need deprecation plan)

### Prohibited
- Modifying auth/security code without review
- Force pushing to main
- Deleting test files
```

### 7. The Implicit Assumption

**Problem**: Assumes Claude knows things that aren't documented.

```markdown
# Bad Example
## API Guidelines
- Follow our standard patterns
- Use the usual error format
- Check permissions as we normally do
```

**Why it fails**: "Our standard" and "as usual" mean nothing without definition.

**Fix**: Make everything explicit:

```markdown
## API Guidelines

### Response Format
```json
{
  "success": true|false,
  "data": { ... } | null,
  "error": { "code": "ERR_XXX", "message": "..." } | null
}
```

### Permission Check Pattern
```typescript
// Every protected endpoint starts with:
const user = await requireAuth(req);
if (!hasPermission(user, 'resource:action')) {
  throw new ForbiddenError('ERR_PERM_001');
}
```
```

### 8. The Stale Examples

**Problem**: Code examples use deprecated patterns or old syntax.

```markdown
# Bad Example
## Component Pattern
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

**Why it fails**: Claude copies the example pattern, generating outdated code.

**Fix**: Update examples when patterns change:

```markdown
## Component Pattern
```tsx
// Standard pattern for data-fetching components
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

## Diagnostic Checklist

When Claude keeps asking the same questions, use this checklist:

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "What authentication method?" | Missing auth section | Document auth approach |
| "Which database to use?" | Missing tech stack | Add clear tech stack |
| "What error format?" | Missing API standards | Add response format |
| "Should I add tests?" | Missing test policy | Add testing guidelines |
| "Where should this go?" | Missing project structure | Add directory guide |
| "Can I install X?" | Missing dependency policy | Add approved deps list |

## The CLAUDE.md Health Check

Run this periodic check:

```markdown
## Monthly CLAUDE.md Review

1. [ ] Tech stack matches actual dependencies
2. [ ] Examples use current patterns
3. [ ] No contradictory guidelines
4. [ ] Permissions are balanced (not all restrictions)
5. [ ] Under 500 lines (link to detailed docs)
6. [ ] "Last updated" date is current
7. [ ] New team members can understand it
```

## Quick Fixes

### Problem: Claude keeps asking about X

**Solution**: Add a FAQ section:

```markdown
## FAQ for Claude

Q: Should I write tests?
A: Yes, always. Unit tests for utilities, integration tests for API endpoints.

Q: What logging library?
A: Use `pino`. Import from `@/lib/logger`.

Q: How to handle errors?
A: Throw typed errors from `@/lib/errors`. Never use generic Error().
```

### Problem: Claude generates inconsistent code

**Solution**: Add a "Don't vs Do" section:

```markdown
## Style Guide Quick Reference

| Don't | Do |
|-------|-----|
| `any` type | Proper TypeScript types |
| `console.log` | `logger.info()` |
| Inline styles | Tailwind classes |
| `var` | `const` or `let` |
| Nested callbacks | async/await |
```

## Summary

1. **Be specific** - No vague terms like "good" or "best"
2. **Stay current** - Update when the project changes
3. **Explain why** - Context helps Claude make better decisions
4. **Resolve conflicts** - Prioritize when rules clash
5. **Keep it focused** - Link to detailed docs instead of embedding
6. **Balance permissions** - Enable, don't just restrict
7. **Make it explicit** - No "as usual" or "standard way"
8. **Update examples** - Code samples must match current patterns

---

See also: [CLAUDE.md Principles](./claude-md-principles.md) | [Director Mode Basics](./director-mode-basics.md)
