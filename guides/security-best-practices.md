# Security Best Practices

> Build secure applications with Claude from the start.

## Why Security-First?

Security issues are:
- **Expensive to fix later** - 6x more costly in production than in development
- **Reputation-damaging** - One breach can destroy user trust
- **Often invisible** - You don't know you're vulnerable until it's exploited

This guide shows how to use Claude for security-conscious development.

## The Security Mindset

### CLAUDE.md Security Section

Add this to every project:

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

## Common Vulnerabilities & Fixes

### 1. SQL Injection

**Vulnerable Code**:
```javascript
// ❌ NEVER do this
const query = `SELECT * FROM users WHERE id = ${userId}`;
db.query(query);
```

**Claude Command**:
```
"Find all SQL queries that use string concatenation and convert them to parameterized queries"
```

**Secure Code**:
```javascript
// ✅ Always use parameterized queries
const query = 'SELECT * FROM users WHERE id = $1';
db.query(query, [userId]);
```

### 2. Cross-Site Scripting (XSS)

**Vulnerable Code**:
```jsx
// ❌ Dangerous
<div dangerouslySetInnerHTML={{__html: userInput}} />

// ❌ Also dangerous
element.innerHTML = userInput;
```

**Claude Command**:
```
"Find all instances of dangerouslySetInnerHTML and innerHTML that use user input"
```

**Secure Code**:
```jsx
// ✅ Safe - React escapes by default
<div>{userInput}</div>

// ✅ If HTML needed, sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

### 3. Insecure Authentication

**Vulnerable Code**:
```javascript
// ❌ Weak hashing
const hash = crypto.createHash('md5').update(password).digest('hex');

// ❌ Token in localStorage (accessible to XSS)
localStorage.setItem('token', jwt);
```

**Claude Command**:
```
"Review authentication implementation for:
- Weak hashing algorithms (MD5, SHA1)
- Tokens stored in localStorage
- Missing rate limiting on login"
```

**Secure Code**:
```javascript
// ✅ Strong hashing
import bcrypt from 'bcrypt';
const hash = await bcrypt.hash(password, 12);

// ✅ httpOnly cookie (not accessible to JavaScript)
res.cookie('token', jwt, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 15 * 60 * 1000 // 15 minutes
});
```

### 4. Broken Access Control

**Vulnerable Code**:
```javascript
// ❌ No authorization check
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
});
```

**Claude Command**:
```
"Find all API endpoints that access user data without checking permissions"
```

**Secure Code**:
```javascript
// ✅ Always check permissions
app.get('/api/users/:id', requireAuth, async (req, res) => {
  // Check if user can access this resource
  if (req.user.id !== req.params.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Access denied' });
  }

  const user = await User.findById(req.params.id);
  res.json(user);
});
```

### 5. Sensitive Data Exposure

**Vulnerable Code**:
```javascript
// ❌ Logging sensitive data
console.log('Login attempt:', { email, password });

// ❌ Returning sensitive fields
res.json(user); // includes password hash
```

**Claude Command**:
```
"Find all instances where passwords, tokens, or sensitive user data might be logged or exposed"
```

**Secure Code**:
```javascript
// ✅ Never log sensitive data
logger.info('Login attempt', { email, timestamp: new Date() });

// ✅ Exclude sensitive fields
const { password, ...safeUser } = user;
res.json(safeUser);

// ✅ Or use a DTO
res.json(new UserDTO(user));
```

### 6. Security Misconfigurations

**Vulnerable Code**:
```javascript
// ❌ CORS allowing all origins
app.use(cors({ origin: '*' }));

// ❌ Missing security headers
// (no helmet, no CSP)
```

**Claude Command**:
```
"Review security configuration:
- CORS settings
- Security headers (CSP, HSTS, etc.)
- Cookie settings
- Error handling (no stack traces to client)"
```

**Secure Code**:
```javascript
// ✅ Restrictive CORS
app.use(cors({
  origin: ['https://myapp.com'],
  credentials: true
}));

// ✅ Security headers with helmet
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

## Security Audit Workflow

### Step 1: Automated Scan

```
"Run a security scan on this codebase checking for OWASP Top 10 vulnerabilities"
```

Claude will check for:
- Injection flaws
- Broken authentication
- Sensitive data exposure
- XXE
- Broken access control
- Security misconfiguration
- XSS
- Insecure deserialization
- Known vulnerable components
- Insufficient logging

### Step 2: Authentication Review

```
"Review all authentication and authorization code:
- How are passwords stored?
- How are sessions managed?
- Are there rate limits on auth endpoints?
- Is MFA available?"
```

### Step 3: Input Validation Review

```
"Find all places where user input is used and verify:
- Server-side validation exists
- Parameterized queries for database
- Output encoding for HTML
- File upload restrictions"
```

### Step 4: Secrets Audit

```
"Search for hardcoded secrets, API keys, or credentials in:
- Source code
- Configuration files
- Environment files
- Git history"
```

### Step 5: Dependency Audit

```
"Check dependencies for known vulnerabilities using npm audit or similar"
```

## Security Checklist by Feature

### User Registration
```
□ Password strength requirements enforced
□ Email verification required
□ Rate limiting on registration endpoint
□ CAPTCHA for abuse prevention
□ No sensitive data in URL parameters
```

### Login
```
□ Bcrypt/Argon2 for password verification
□ Account lockout after failed attempts
□ Rate limiting on login endpoint
□ Secure session token generation
□ httpOnly, secure cookies
□ CSRF protection
```

### Password Reset
```
□ Token expires quickly (15-60 min)
□ Token is single-use
□ Old password not required (they forgot it)
□ Email notification of password change
□ Rate limiting on reset requests
```

### API Endpoints
```
□ Authentication required (or explicitly public)
□ Authorization checked for resource access
□ Input validation on all parameters
□ Rate limiting per user/IP
□ Proper error responses (no sensitive info)
```

### File Upload
```
□ File type validation (not just extension)
□ File size limits
□ Malware scanning
□ Stored outside web root
□ Randomized filenames
```

### Payment Processing
```
□ Use established payment provider (Stripe, etc.)
□ Never store full card numbers
□ PCI DSS compliance
□ Audit logging for all transactions
□ Fraud detection
```

## Claude Security Commands

### Quick Security Check
```
"Quick security check: find the top 5 most critical security issues in this codebase"
```

### Pre-Commit Security Review
```
"Review these changes for security issues before I commit"
```

### Dependency Vulnerability Check
```
"Check if any of our dependencies have known security vulnerabilities"
```

### Penetration Test Preparation
```
"Prepare a list of potential attack vectors for penetration testing this application"
```

### Security Documentation
```
"Generate security documentation covering:
- Authentication flow
- Authorization model
- Data encryption
- Audit logging"
```

## Security Anti-Patterns

### Don't: Roll Your Own Crypto
```javascript
// ❌ Custom encryption
function encrypt(data) {
  return data.split('').map(c =>
    String.fromCharCode(c.charCodeAt(0) + 1)
  ).join('');
}
```

### Do: Use Established Libraries
```javascript
// ✅ Use proven libraries
import { createCipheriv, randomBytes } from 'crypto';
```

### Don't: Trust Client-Side Validation Only
```javascript
// ❌ Only checking on frontend
if (form.checkValidity()) {
  submitToServer(formData);
}
```

### Do: Always Validate Server-Side
```javascript
// ✅ Server-side validation
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});
const validated = schema.parse(req.body);
```

### Don't: Store Secrets in Code
```javascript
// ❌ Hardcoded secrets
const API_KEY = 'sk_live_abc123...';
```

### Do: Use Environment Variables
```javascript
// ✅ Environment variables
const API_KEY = process.env.API_KEY;
if (!API_KEY) throw new Error('API_KEY required');
```

## Summary

1. **Add security section to CLAUDE.md** - Make security a first-class concern
2. **Use parameterized queries** - Prevent SQL injection
3. **Sanitize output** - Prevent XSS
4. **Strong authentication** - bcrypt, httpOnly cookies, rate limiting
5. **Check authorization everywhere** - Every endpoint, every resource
6. **Never log sensitive data** - Passwords, tokens, PII
7. **Use security headers** - helmet, CSP, HSTS
8. **Keep dependencies updated** - Regular npm audit
9. **Regular security reviews** - Use Claude for automated scanning

**Golden Rule**: Assume all input is malicious until validated.

---

See also: [Production Readiness](./production-readiness.md) | [Quick Reference Cards](./quick-reference.md)
