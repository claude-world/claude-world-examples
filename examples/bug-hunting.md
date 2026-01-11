# Bug Hunting Pattern

A systematic approach to finding and fixing bugs using parallel agents.

## The Pattern

When you encounter a bug, don't just describe it. Give Claude a clear directive and let parallel agents investigate simultaneously.

## Step-by-Step

### 1. Describe the Bug Clearly

**Bad**:
```
"Something's wrong with login"
```

**Good**:
```
"Bug: Users report being logged out after exactly 15 minutes,
even when actively using the app. Expected: Session should
refresh while user is active."
```

### 2. Let Claude Launch Parallel Investigation

Claude will automatically launch multiple agents:

```
Agent 1 (Explore): Map the authentication flow
Agent 2 (Grep): Search for session/timeout/expiry code
Agent 3 (Grep): Check token refresh logic
Agent 4 (Read): Examine auth middleware
Agent 5 (Bash): Check recent commits to auth files
```

### 3. Review Findings

Claude synthesizes all agent results:

```
"Investigation complete. Found the issue:

In /lib/auth/session.ts:42:
- Session timeout is hardcoded to 15 minutes
- The refresh logic only runs on page load
- Active requests don't trigger refresh

Root cause: Missing activity-based session refresh.

Proposed fix: Add middleware to refresh session on API calls."
```

### 4. Approve and Fix

```
You: "Fix it"

Claude: [Implements the fix]
- Adds session refresh middleware
- Updates existing auth middleware
- Adds tests for the new behavior
- Commits with descriptive message
```

## Example Scenarios

### Scenario 1: UI Bug

```
You: "Bug: The submit button stays disabled after form validation
passes. Steps to reproduce: Fill all fields correctly, button
remains gray."

Claude: [Launches agents]
- Searches for button disabled logic
- Checks form validation state
- Reviews similar forms in codebase
- Finds: Race condition between validation and state update

Claude: "Found it. The validation runs async but the button
checks state synchronously. Adding await fixes it."
```

### Scenario 2: Performance Bug

```
You: "Bug: Dashboard takes 10+ seconds to load for users with
many projects. Works fine for new users."

Claude: [Launches agents]
- Profiles dashboard API endpoint
- Checks database queries
- Reviews pagination logic
- Analyzes N+1 query patterns

Claude: "Found N+1 query in project loading. Each project
triggers a separate query for team members. Adding eager
loading reduces 100 queries to 2."
```

### Scenario 3: Data Bug

```
You: "Bug: Some users have duplicate entries in their activity
log. Not all users, seems random."

Claude: [Launches agents]
- Searches for activity logging code
- Checks for race conditions
- Reviews database constraints
- Examines retry logic

Claude: "Found it. The activity logger retries on timeout but
doesn't check if the first request succeeded. Adding
idempotency key prevents duplicates."
```

## Best Practices

### 1. Include Reproduction Steps

```markdown
Bug: [Description]
Steps:
1. Log in as user
2. Navigate to /settings
3. Click "Save"
4. Error appears

Expected: Settings saved
Actual: "Server error" message
```

### 2. Include Error Messages

```
Bug: API returns 500 error
Error: "TypeError: Cannot read property 'id' of undefined"
Endpoint: POST /api/projects
```

### 3. Mention What You've Tried

```
Bug: Tests failing on CI but passing locally
Tried:
- Clearing cache
- Running with same Node version
- Checking env variables
All seem identical.
```

### 4. Provide Context

```
Bug: Payment processing fails for some users
Context:
- Started after deploying commit abc123
- Only affects Stripe payments, PayPal works
- No errors in our logs
```

## The Investigation Checklist

Claude's parallel agents typically check:

- [ ] Error messages and stack traces
- [ ] Related code files
- [ ] Recent changes (git log)
- [ ] Similar patterns in codebase
- [ ] Test coverage
- [ ] Configuration files
- [ ] External service status
- [ ] Database state

## Summary

1. **Describe clearly** - Bug, steps, expected vs actual
2. **Let Claude investigate** - Parallel agents are fast
3. **Review synthesis** - Claude combines all findings
4. **Approve fix** - One command to implement

Average bug fix time with this pattern: **2-5 minutes**

---

See also: [Director Mode Basics](../concepts/director-mode-basics.md)
