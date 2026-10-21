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

# Reality: Project migrated to React 19 + hooks + Zustand 6 months ago
```

**Why it fails**: Claude generates code for the wrong version, causing constant corrections.

**Fix**: Review CLAUDE.md quarterly or after major changes, and run `/doctor prompt-audit` to flag references to files or commands that no longer exist:

```markdown
## Tech Stack
- React 19 (functional components + hooks only)
- Zustand 5.x for client state
- TanStack Query v5 for server state
- Vitest for testing (migrated from Jest in 2024)

Last updated: 2026-10-01
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

Conflicts also hide across files. Nested CLAUDE.md files, `.claude/rules/`, and your user-level instructions all load together and none of them overrides the others, so Claude may follow either side. `/doctor prompt-audit` reports instruction files that contradict each other.

### 5. The Kitchen Sink

**Problem**: CLAUDE.md is 2000+ lines covering every possible scenario.

```markdown
# Bad Example: 50 pages of guidelines covering:
- Every API endpoint specification
- Full database schema
- Complete deployment procedures
- File-by-file descriptions of the codebase
- Historical decisions from 3 years ago
- Meeting notes
```

**Why it fails**: CLAUDE.md loads in full every session. Low-value information fills the context window, and adherence drops: the rules that matter get lost in the noise.

**Fix**: Keep each CLAUDE.md under ~200 lines. Link to detailed docs, and turn procedures into skills:

```markdown
# Good Example

## Quick Reference
- Tech: Next.js 16, PostgreSQL, Prisma
- Commands: `pnpm dev`, `pnpm test`, `pnpm db:migrate`

## Core Guidelines
[10-15 most important rules]

## Detailed Documentation
- API spec: See `/docs/api/README.md`
- Database: See `/prisma/README.md`
- Deployment: Use the `/deploy` skill (`.claude/skills/deploy/SKILL.md`)
```

Guidance that only matters in one area belongs in `.claude/rules/`. A rule with `paths:` frontmatter loads only when Claude works with matching files, for example `.claude/rules/database.md`:

```markdown
---
paths:
  - "prisma/**"
---

# Database Rules
- Every schema change needs a migration (`pnpm db:migrate`)
- Never edit applied migrations in `prisma/migrations/`
```

Don't reach for `@path` imports to shrink the file: imported files load at launch too. A plain path reference, as above, lets Claude open the doc only when it needs it.

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

> **CLAUDE.md doesn't grant or block anything.** These lists steer Claude's judgment; Claude Code enforces tool access separately, through `permissions` in `.claude/settings.json` and the permission mode you choose (`Shift+Tab`, or `defaultMode` in settings). The same intent maps onto three rule types, checked deny first, then ask, then allow:

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

Rules match the command as written (`git push origin main --force` slips past the deny rule but still hits the `ask` rule), so pair a narrow deny with a broader ask. For checks a pattern can't express, use a PreToolUse [hook](./hooks-basics.md).

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

````markdown
## API Guidelines

### Response Format
```jsonc
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
````

### 8. The Stale Examples

**Problem**: Code examples use deprecated patterns or old syntax.

````markdown
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
````

**Why it fails**: Claude copies the example pattern, generating outdated code.

**Fix**: Update examples when patterns change:

````markdown
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
````

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

If Claude asks a question that CLAUDE.md already answers, the phrasing is probably ambiguous. If it keeps breaking a rule that's written down, the file is probably too long and the rule is getting lost, or the rule needs enforcement (a permission rule or hook) rather than prose. Run `/context` to confirm the file loaded at all.

## The CLAUDE.md Health Check

Run this periodic check:

```markdown
## Monthly CLAUDE.md Review

1. [ ] Tech stack matches actual dependencies
2. [ ] Examples use current patterns
3. [ ] No contradictory guidelines (`/doctor prompt-audit` helps)
4. [ ] Permissions are balanced (not all restrictions); hard limits live in settings.json or hooks
5. [ ] Under ~200 lines (path-specific rules in `.claude/rules/`, procedures in skills)
6. [ ] "Last updated" date is current
7. [ ] New team members can understand it
8. [ ] `/context` lists the expected files under Memory files
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
5. **Keep it focused** - Under ~200 lines; rules, skills, and links for the rest
6. **Balance permissions** - Enable, don't just restrict; enforce hard limits in settings.json
7. **Make it explicit** - No "as usual" or "standard way"
8. **Update examples** - Code samples must match current patterns

---

See also: [CLAUDE.md Principles](./claude-md-principles.md) | [Director Mode Basics](./director-mode-basics.md)
