# Production Readiness Checklist

> Before you ship: a systematic review framework with Claude.

## Why This Matters

Shipping to production without a checklist leads to:
- Security vulnerabilities discovered in production
- Performance issues under real load
- Missing error handling causing silent failures
- Debugging blind spots from inadequate logging

This guide provides a framework for Claude-assisted production review.

## The Checklist

### 1. Security Review

```
┌────────────────────────────────────────────────────────────────┐
│                      SECURITY CHECKLIST                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ AUTHENTICATION                                              │
│    ├── [ ] Passwords hashed (bcrypt/argon2, not MD5/SHA1)     │
│    ├── [ ] Tokens are httpOnly cookies (not localStorage)     │
│    ├── [ ] Token expiration is reasonable (15min-24hr)        │
│    ├── [ ] Refresh token rotation implemented                  │
│    └── [ ] Failed login rate limiting                          │
│                                                                │
│  □ AUTHORIZATION                                               │
│    ├── [ ] Every endpoint checks permissions                   │
│    ├── [ ] No direct object references (use UUIDs)            │
│    ├── [ ] Admin functions require admin role                  │
│    └── [ ] API keys are scoped appropriately                   │
│                                                                │
│  □ INPUT VALIDATION                                            │
│    ├── [ ] All user input validated server-side               │
│    ├── [ ] SQL injection prevention (parameterized queries)   │
│    ├── [ ] XSS prevention (output encoding)                   │
│    └── [ ] File upload validation (type, size, content)       │
│                                                                │
│  □ SECRETS                                                     │
│    ├── [ ] No secrets in code or git history                  │
│    ├── [ ] Environment variables for all secrets              │
│    ├── [ ] .env files in .gitignore                           │
│    └── [ ] Secrets rotated after any exposure                  │
│                                                                │
│  □ DEPENDENCIES                                                │
│    ├── [ ] No known vulnerabilities (npm audit / snyk)        │
│    ├── [ ] Dependencies are up to date                         │
│    └── [ ] Lock file committed (package-lock.json)            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Claude Command**:
```
"Run a security audit on this codebase. Check for:
- Authentication issues
- Authorization bypasses
- Input validation gaps
- Exposed secrets
- Vulnerable dependencies"
```

### 2. Performance Review

```
┌────────────────────────────────────────────────────────────────┐
│                     PERFORMANCE CHECKLIST                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ DATABASE                                                    │
│    ├── [ ] Indexes on frequently queried columns              │
│    ├── [ ] No N+1 query patterns                              │
│    ├── [ ] Connection pooling configured                       │
│    ├── [ ] Slow query logging enabled                          │
│    └── [ ] Query timeout limits set                            │
│                                                                │
│  □ API                                                         │
│    ├── [ ] Response times < 200ms (p95)                       │
│    ├── [ ] Pagination for list endpoints                       │
│    ├── [ ] Response size limits                                │
│    ├── [ ] Caching headers (ETags, Cache-Control)             │
│    └── [ ] Compression enabled (gzip/brotli)                   │
│                                                                │
│  □ FRONTEND                                                    │
│    ├── [ ] Bundle size optimized (code splitting)             │
│    ├── [ ] Images optimized (WebP, lazy loading)              │
│    ├── [ ] Critical CSS inlined                                │
│    ├── [ ] Core Web Vitals passing (LCP, FID, CLS)            │
│    └── [ ] CDN configured for static assets                    │
│                                                                │
│  □ LOAD HANDLING                                               │
│    ├── [ ] Rate limiting on all endpoints                      │
│    ├── [ ] Graceful degradation under load                     │
│    ├── [ ] Memory limits configured                            │
│    └── [ ] Auto-scaling configured (if applicable)             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Claude Command**:
```
"Analyze performance of this codebase:
- Find N+1 queries
- Identify missing indexes
- Check for unbounded data fetching
- Review caching strategy"
```

### 3. Reliability Review

```
┌────────────────────────────────────────────────────────────────┐
│                     RELIABILITY CHECKLIST                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ ERROR HANDLING                                              │
│    ├── [ ] All async operations have try/catch                │
│    ├── [ ] Errors have meaningful messages                     │
│    ├── [ ] Error codes documented                              │
│    ├── [ ] Unhandled rejection handlers                        │
│    └── [ ] Graceful error pages (not stack traces)            │
│                                                                │
│  □ RESILIENCE                                                  │
│    ├── [ ] External API calls have timeouts                   │
│    ├── [ ] Retry logic with backoff for transient failures    │
│    ├── [ ] Circuit breakers for failing dependencies          │
│    ├── [ ] Fallback behavior defined                           │
│    └── [ ] Health check endpoint (/health)                     │
│                                                                │
│  □ DATA INTEGRITY                                              │
│    ├── [ ] Database transactions for multi-step operations    │
│    ├── [ ] Idempotent operations where applicable             │
│    ├── [ ] Backup strategy documented                          │
│    └── [ ] Data migration tested                               │
│                                                                │
│  □ DEPLOYMENT                                                  │
│    ├── [ ] Zero-downtime deployment strategy                  │
│    ├── [ ] Rollback procedure documented                       │
│    ├── [ ] Database migrations reversible                      │
│    └── [ ] Feature flags for risky changes                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Claude Command**:
```
"Review error handling and resilience:
- Find unhandled promise rejections
- Check for missing timeouts on external calls
- Verify transaction usage
- Identify single points of failure"
```

### 4. Observability Review

```
┌────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY CHECKLIST                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ LOGGING                                                     │
│    ├── [ ] Structured logging (JSON format)                   │
│    ├── [ ] Request ID in all logs                              │
│    ├── [ ] User ID in authenticated requests                  │
│    ├── [ ] No sensitive data in logs (passwords, tokens)      │
│    ├── [ ] Log levels used appropriately                       │
│    └── [ ] Logs shipped to central location                    │
│                                                                │
│  □ MONITORING                                                  │
│    ├── [ ] Application metrics collected                       │
│    ├── [ ] Error rate tracking                                 │
│    ├── [ ] Response time tracking                              │
│    ├── [ ] Database query metrics                              │
│    └── [ ] Business metrics (signups, conversions)             │
│                                                                │
│  □ ALERTING                                                    │
│    ├── [ ] Error rate spike alerts                             │
│    ├── [ ] Response time degradation alerts                   │
│    ├── [ ] Disk space / memory alerts                          │
│    ├── [ ] SSL certificate expiry alerts                       │
│    └── [ ] On-call rotation defined                            │
│                                                                │
│  □ DEBUGGING                                                   │
│    ├── [ ] Source maps available in production                │
│    ├── [ ] Error tracking service configured (Sentry)         │
│    ├── [ ] Request tracing available                           │
│    └── [ ] Feature to enable debug logging per-request        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Claude Command**:
```
"Review logging and monitoring setup:
- Check for sensitive data in logs
- Verify structured logging format
- Identify gaps in error tracking
- Review alerting coverage"
```

### 5. Testing Review

```
┌────────────────────────────────────────────────────────────────┐
│                      TESTING CHECKLIST                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ COVERAGE                                                    │
│    ├── [ ] Unit test coverage > 70%                           │
│    ├── [ ] Critical paths have integration tests              │
│    ├── [ ] API endpoints have contract tests                  │
│    └── [ ] Edge cases covered                                  │
│                                                                │
│  □ QUALITY                                                     │
│    ├── [ ] Tests are deterministic (no flaky tests)           │
│    ├── [ ] Tests run in CI on every PR                         │
│    ├── [ ] Test data isolated (not shared state)              │
│    └── [ ] Mocks for external services                         │
│                                                                │
│  □ SCENARIOS                                                   │
│    ├── [ ] Happy path tested                                   │
│    ├── [ ] Error conditions tested                             │
│    ├── [ ] Boundary conditions tested                          │
│    ├── [ ] Concurrent access tested                            │
│    └── [ ] Permission boundaries tested                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Claude Command**:
```
"Analyze test coverage and quality:
- Identify untested critical paths
- Find flaky tests
- Check for missing edge case tests
- Verify permission testing"
```

### 6. Documentation Review

```
┌────────────────────────────────────────────────────────────────┐
│                   DOCUMENTATION CHECKLIST                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ DEVELOPER DOCS                                              │
│    ├── [ ] README with setup instructions                     │
│    ├── [ ] Architecture overview                               │
│    ├── [ ] API documentation (OpenAPI/Swagger)                │
│    └── [ ] Contributing guidelines                             │
│                                                                │
│  □ OPERATIONS DOCS                                             │
│    ├── [ ] Deployment procedure                                │
│    ├── [ ] Rollback procedure                                  │
│    ├── [ ] Runbooks for common issues                          │
│    └── [ ] Environment configuration                           │
│                                                                │
│  □ CODE DOCS                                                   │
│    ├── [ ] Complex logic has comments                          │
│    ├── [ ] Public APIs have JSDoc/docstrings                  │
│    └── [ ] Architecture decisions recorded (ADRs)             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Using Claude for Production Review

### Step 1: Security Scan

```
"Perform a security review of this codebase focusing on OWASP Top 10"
```

### Step 2: Performance Analysis

```
"Analyze this codebase for performance issues:
- Database query efficiency
- N+1 patterns
- Missing caching opportunities
- Bundle size issues"
```

### Step 3: Reliability Check

```
"Review error handling and resilience patterns:
- Unhandled errors
- Missing timeouts
- Transaction boundaries
- Recovery mechanisms"
```

### Step 4: Generate Report

```
"Create a production readiness report summarizing:
- Critical issues (must fix before launch)
- High priority issues (fix soon after launch)
- Medium issues (add to backlog)
- Good practices already in place"
```

## Example Production Review Session

```
You: "Run production readiness check before we launch next week"

Claude: [Launches parallel agents]
→ Agent 1: Security scan
→ Agent 2: Performance analysis
→ Agent 3: Error handling review
→ Agent 4: Test coverage check
→ Agent 5: Documentation audit

[2 minutes later]

Claude: "Production Readiness Report:

CRITICAL (Block Launch):
1. /api/admin/users endpoint missing auth check (security)
2. User passwords stored with MD5 (security)

HIGH PRIORITY (Fix within 1 week):
1. N+1 query in /api/projects (performance)
2. No rate limiting on auth endpoints (security)
3. Missing error handling in payment flow (reliability)

MEDIUM (Add to backlog):
1. Test coverage at 45% (target: 70%)
2. No structured logging
3. Missing API documentation

GOOD:
✓ Input validation with Zod
✓ HTTPS enforced
✓ Dependencies up to date
✓ Health check endpoint exists"
```

## Post-Launch Checklist

```
┌────────────────────────────────────────────────────────────────┐
│                   POST-LAUNCH CHECKLIST                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  □ IMMEDIATELY AFTER LAUNCH                                    │
│    ├── [ ] Verify all services running                        │
│    ├── [ ] Check error rates (should be near zero)            │
│    ├── [ ] Verify key user flows work                          │
│    └── [ ] Monitor for unusual traffic patterns                │
│                                                                │
│  □ FIRST 24 HOURS                                              │
│    ├── [ ] Review all errors that occurred                    │
│    ├── [ ] Check performance metrics vs expectations          │
│    ├── [ ] Verify logging is capturing expected data          │
│    └── [ ] Gather initial user feedback                        │
│                                                                │
│  □ FIRST WEEK                                                  │
│    ├── [ ] Address any issues discovered                       │
│    ├── [ ] Review usage patterns                               │
│    ├── [ ] Tune alerting thresholds                            │
│    └── [ ] Document lessons learned                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Summary

Use this checklist with Claude to systematically review:

1. **Security** - Auth, input validation, secrets, dependencies
2. **Performance** - Database, API, frontend, load handling
3. **Reliability** - Error handling, resilience, data integrity
4. **Observability** - Logging, monitoring, alerting
5. **Testing** - Coverage, quality, scenarios
6. **Documentation** - Developer, operations, code

**Command to run full review**:
```
"Perform a complete production readiness review using the standard checklist"
```

---

See also: [Quick Reference Cards](./quick-reference.md) | [Security Best Practices](./security-best-practices.md)
