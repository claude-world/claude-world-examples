# Feature Development Pattern

A structured approach to implementing new features with Claude Code.

## The Pattern

Instead of building features incrementally with constant back-and-forth, give Claude a complete picture and let it implement the entire feature.

## The 5-Step Process

### Step 1: Define the Feature Clearly

**Bad**:
```
"Add a notification system"
```

**Good**:
```
"Implement email notifications for the following events:
1. New user signup → Welcome email
2. Password reset request → Reset link email
3. Order confirmed → Order confirmation email

Requirements:
- Use existing EmailService in /lib/email
- Store notification preferences in User model
- Add API endpoint to update preferences
- Include unsubscribe link in all emails
"
```

### Step 2: Let Claude Analyze

Claude launches parallel agents to understand context:

```
Agent 1: Analyze existing EmailService
Agent 2: Review User model structure
Agent 3: Check existing notification patterns
Agent 4: Examine API route conventions
Agent 5: Look at email templates if any
```

### Step 3: Review the Plan

Claude proposes implementation:

```
"Here's my implementation plan:

1. Database Changes:
   - Add notification_preferences JSONB column to users
   - Create email_logs table for tracking

2. New Files:
   - /lib/notifications/index.ts - Main service
   - /lib/notifications/templates/*.tsx - Email templates
   - /api/users/preferences.ts - API endpoint

3. Modifications:
   - /lib/auth/signup.ts - Trigger welcome email
   - /lib/auth/reset.ts - Trigger reset email
   - /lib/orders/confirm.ts - Trigger order email

4. Tests:
   - Unit tests for notification service
   - Integration tests for email sending
   - API tests for preferences endpoint

Proceed with implementation?"
```

### Step 4: Implement

```
You: "Proceed"

Claude: [Implements everything]
- Creates migration
- Implements notification service
- Adds email templates
- Creates API endpoint
- Updates existing code
- Writes tests
- Runs tests to verify
```

### Step 5: Review and Iterate

```
Claude: "Implementation complete. All tests passing.

Created:
- /lib/notifications/index.ts
- /lib/notifications/templates/welcome.tsx
- /lib/notifications/templates/reset.tsx
- /lib/notifications/templates/order.tsx
- /api/users/preferences.ts
- /prisma/migrations/add_notifications.sql

Modified:
- /lib/auth/signup.ts
- /lib/auth/reset.ts
- /lib/orders/confirm.ts

Tests: 12 new tests, all passing.

Ready for review."
```

## Example: Complete Feature Request

Here's a real-world example of a complete feature request:

```markdown
## Feature: User Dashboard Analytics

### User Story
As a user, I want to see analytics about my activity so I can
understand my usage patterns.

### Requirements

**Data to Display:**
- Total projects created
- Activity over last 30 days (chart)
- Most active project
- Recent activity timeline

**UI Requirements:**
- New /dashboard/analytics page
- Use existing Chart component from /components/ui
- Mobile responsive
- Loading states for data fetching

**API Requirements:**
- GET /api/analytics/summary - Overview stats
- GET /api/analytics/activity?days=30 - Activity data

**Technical Constraints:**
- Cache analytics data (5 min TTL)
- Use existing auth middleware
- Follow current API patterns

### Out of Scope
- Export functionality
- Comparison with other users
- Custom date ranges
```

## Pro Tips

### 1. Reference Existing Patterns

```
"Add a comments feature similar to how we implemented
the reviews feature in /features/reviews"
```

### 2. Specify Edge Cases

```
"Handle these edge cases:
- User with no activity → Show onboarding prompt
- API timeout → Show cached data with stale indicator
- Rate limiting → Queue notifications, send in batch"
```

### 3. Include Acceptance Criteria

```
"Feature is complete when:
- [ ] All tests pass
- [ ] TypeScript has no errors
- [ ] Mobile layout works
- [ ] Loading states implemented
- [ ] Error states handled"
```

### 4. Break Large Features Down

For very large features, break into phases:

```
"Phase 1: Backend
- Database schema
- API endpoints
- Core service logic

Phase 2: Frontend
- UI components
- State management
- Integration

Phase 3: Polish
- Error handling
- Loading states
- Analytics tracking"
```

## Anti-Patterns to Avoid

### Don't: Implement Incrementally

```
You: "Add a button"
Claude: [adds button]
You: "Now add click handler"
Claude: [adds handler]
You: "Now add API call"
...
```

### Do: Implement Completely

```
You: "Add export button that calls /api/export and
downloads the result as CSV"
Claude: [implements everything at once]
```

## Summary

1. **Define completely** - All requirements upfront
2. **Let Claude analyze** - Parallel agents gather context
3. **Review the plan** - Approve before implementation
4. **Implement at once** - Full feature, not increments
5. **Review and iterate** - Feedback on completed work

---

See also: [Parallel Agents](../concepts/parallel-agents.md)
