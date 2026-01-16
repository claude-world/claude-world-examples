# API Endpoint Design Patterns

> Production-ready patterns for building secure, scalable API endpoints with Astro and Cloudflare Pages.

This guide covers battle-tested patterns for API development used by [claude-world.com](https://claude-world.com), including request validation, rate limiting, CSRF protection, error handling, and authentication.

---

## Overview

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| [Astro API Routes](#1-astro-api-routes-basics) | Basic endpoint structure | All API endpoints |
| [Cloudflare Edge](#2-cloudflare-edge-functions) | Edge deployment | Production APIs |
| [Request Validation](#3-request-validation-and-sanitization) | Input safety | All user inputs |
| [Rate Limiting](#4-rate-limiting-patterns) | Abuse prevention | Public endpoints |
| [CSRF Protection](#5-csrf-protection) | Security | State-changing operations |
| [Error Handling](#6-error-handling-and-responses) | User experience | All endpoints |
| [Authentication](#7-authentication-patterns) | Access control | Protected resources |

**Architecture:**

```
Request Flow:

  Client  -->  Cloudflare  -->  Astro API  -->  Supabase
    |            Edge              Route           |
    |            |                  |              |
    |        WAF + Rate        Security +         |
    |        Limiting          Validation         |
    |                               |              |
    <---------  JSON Response  <----+<-------------
```

---

## 1. Astro API Routes Basics

### File Structure

```
src/pages/api/
├── newsletter.ts          # POST /api/newsletter
├── unsubscribe.ts         # POST, GET /api/unsubscribe
├── preferences.ts         # GET, POST /api/preferences
├── articles.json.ts       # GET /api/articles.json (static)
├── events/
│   ├── register.ts        # POST /api/events/register
│   └── check-in.ts        # POST /api/events/check-in
└── analytics/
    ├── stats.ts           # GET /api/analytics/stats
    └── github.ts          # GET /api/analytics/github
```

### Basic Endpoint Structure

```typescript
// src/pages/api/example.ts
import type { APIRoute } from 'astro';

// CRITICAL: Disable prerendering for dynamic endpoints
export const prerender = false;

// POST handler
export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();

    // Process request...

    return new Response(
      JSON.stringify({ success: true, data: result }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  } catch (error) {
    console.error('API error:', error);
    return new Response(
      JSON.stringify({ success: false, error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};

// GET handler (same file can export multiple methods)
export const GET: APIRoute = async ({ url }) => {
  const param = url.searchParams.get('id');

  return new Response(
    JSON.stringify({ data: param }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  );
};
```

### Static vs Dynamic Endpoints

```typescript
// STATIC: Prerendered at build time (good for read-only data)
// src/pages/api/articles.json.ts
export const prerender = true;

export const GET: APIRoute = async () => {
  const articles = await getCollection('articles');

  return new Response(JSON.stringify(articles), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=3600', // Cache 1 hour
    },
  });
};

// DYNAMIC: Server-rendered on each request (for user data)
// src/pages/api/user/profile.ts
export const prerender = false;

export const GET: APIRoute = async ({ request }) => {
  // Authenticate and return user-specific data
  const user = await authenticateRequest(request);
  return new Response(JSON.stringify(user), { status: 200 });
};
```

---

## 2. Cloudflare Edge Functions

### Astro Configuration

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'hybrid',  // Static by default, SSR opt-in via prerender = false
  adapter: cloudflare({
    platformProxy: {
      enabled: true,  // Enable local dev with Cloudflare features
    },
  }),
});
```

### Cloudflare-Specific Headers

```typescript
// src/pages/api/geo-aware.ts
export const prerender = false;

export const GET: APIRoute = async ({ request }) => {
  // Cloudflare provides these headers automatically
  const headers = {
    clientIP: request.headers.get('CF-Connecting-IP'),
    country: request.headers.get('CF-IPCountry'),
    city: request.headers.get('CF-IPCity'),
    region: request.headers.get('CF-IPRegion'),
    timezone: request.headers.get('CF-Timezone'),
    isBot: request.headers.get('CF-Bot-Score'),
  };

  return new Response(
    JSON.stringify({ geo: headers }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  );
};
```

### Accessing Cloudflare Runtime

```typescript
// src/pages/api/with-kv.ts
import type { APIRoute } from 'astro';

export const prerender = false;

export const GET: APIRoute = async ({ locals }) => {
  // Access Cloudflare runtime via locals (requires adapter config)
  const runtime = locals.runtime;

  // Access KV namespace (if configured in wrangler.toml)
  // const kv = runtime.env.MY_KV_NAMESPACE;
  // const value = await kv.get('my-key');

  return new Response(JSON.stringify({ ok: true }), { status: 200 });
};
```

### wrangler.toml Configuration

```toml
# wrangler.toml
name = "my-project"
compatibility_date = "2025-01-01"
compatibility_flags = ["nodejs_compat"]

pages_build_output_dir = "./dist"

[vars]
PUBLIC_SUPABASE_URL = "https://your-project.supabase.co"

# KV Namespace for sessions/cache
# [[kv_namespaces]]
# binding = "SESSION_KV"
# id = "your-kv-namespace-id"

# D1 Database (optional)
# [[d1_databases]]
# binding = "DB"
# database_id = "your-d1-database-id"
```

---

## 3. Request Validation and Sanitization

### Complete Validation Library

```typescript
// src/lib/validation.ts

/**
 * Validation result type
 */
interface ValidationResult<T> {
  valid: boolean;
  data?: T;
  errors?: string[];
}

/**
 * Email validation with common checks
 */
export function validateEmail(email: unknown): ValidationResult<string> {
  if (typeof email !== 'string') {
    return { valid: false, errors: ['Email must be a string'] };
  }

  const trimmed = email.trim().toLowerCase();

  // Basic format check
  if (!trimmed || !trimmed.includes('@')) {
    return { valid: false, errors: ['Invalid email format'] };
  }

  // More strict regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(trimmed)) {
    return { valid: false, errors: ['Invalid email format'] };
  }

  // Length check
  if (trimmed.length > 254) {
    return { valid: false, errors: ['Email too long'] };
  }

  // Block disposable email domains (optional)
  const disposableDomains = ['tempmail.com', 'throwaway.email'];
  const domain = trimmed.split('@')[1];
  if (disposableDomains.includes(domain)) {
    return { valid: false, errors: ['Disposable emails not allowed'] };
  }

  return { valid: true, data: trimmed };
}

/**
 * String sanitization - remove dangerous characters
 */
export function sanitizeString(
  input: unknown,
  options: { maxLength?: number; allowHtml?: boolean } = {}
): ValidationResult<string> {
  const { maxLength = 1000, allowHtml = false } = options;

  if (typeof input !== 'string') {
    return { valid: false, errors: ['Input must be a string'] };
  }

  let sanitized = input.trim();

  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '');

  // Strip HTML if not allowed
  if (!allowHtml) {
    sanitized = sanitized.replace(/<[^>]*>/g, '');
  }

  // Truncate to max length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.slice(0, maxLength);
  }

  return { valid: true, data: sanitized };
}

/**
 * Enum validation
 */
export function validateEnum<T extends string>(
  value: unknown,
  allowed: readonly T[],
  defaultValue?: T
): ValidationResult<T> {
  if (typeof value !== 'string') {
    if (defaultValue) return { valid: true, data: defaultValue };
    return { valid: false, errors: [`Must be one of: ${allowed.join(', ')}`] };
  }

  if (allowed.includes(value as T)) {
    return { valid: true, data: value as T };
  }

  if (defaultValue) {
    return { valid: true, data: defaultValue };
  }

  return { valid: false, errors: [`Must be one of: ${allowed.join(', ')}`] };
}

/**
 * UUID validation
 */
export function validateUUID(value: unknown): ValidationResult<string> {
  if (typeof value !== 'string') {
    return { valid: false, errors: ['ID must be a string'] };
  }

  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(value)) {
    return { valid: false, errors: ['Invalid ID format'] };
  }

  return { valid: true, data: value.toLowerCase() };
}

/**
 * Request body parser with validation
 */
export async function parseAndValidate<T>(
  request: Request,
  schema: { [K in keyof T]: (value: unknown) => ValidationResult<T[K]> }
): Promise<ValidationResult<T>> {
  let body: Record<string, unknown>;

  try {
    body = await request.json();
  } catch {
    return { valid: false, errors: ['Invalid JSON body'] };
  }

  const result: Partial<T> = {};
  const errors: string[] = [];

  for (const [key, validator] of Object.entries(schema)) {
    const validation = (validator as (value: unknown) => ValidationResult<unknown>)(body[key]);
    if (!validation.valid) {
      errors.push(`${key}: ${validation.errors?.join(', ')}`);
    } else {
      (result as Record<string, unknown>)[key] = validation.data;
    }
  }

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  return { valid: true, data: result as T };
}
```

### Using Validation in API Routes

```typescript
// src/pages/api/newsletter.ts
import type { APIRoute } from 'astro';
import { validateEmail, validateEnum } from '../../lib/validation';
import { SECURITY_HEADERS } from '../../lib/security';

export const prerender = false;

const SUPPORTED_LANGUAGES = ['en', 'zh-tw', 'ja'] as const;
type SupportedLanguage = typeof SUPPORTED_LANGUAGES[number];

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const { email, source = 'website', language = 'en' } = body;

    // Validate email
    const emailResult = validateEmail(email);
    if (!emailResult.valid) {
      return new Response(
        JSON.stringify({ success: false, errors: emailResult.errors }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    // Validate language (with fallback)
    const langResult = validateEnum(language, SUPPORTED_LANGUAGES, 'en');
    const validLanguage = langResult.data as SupportedLanguage;

    // Process with validated data
    const result = await subscribeToNewsletter(
      emailResult.data!,
      source,
      validLanguage
    );

    return new Response(
      JSON.stringify({ success: true, ...result }),
      { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  } catch (error) {
    console.error('Newsletter API error:', error);
    return new Response(
      JSON.stringify({ success: false, error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }
};
```

---

## 4. Rate Limiting Patterns

### In-Memory Rate Limiter

```typescript
// src/lib/rate-limit.ts

interface RateLimitEntry {
  timestamps: number[];
  blockedUntil?: number;
}

// In-memory store (per-instance)
const rateLimitStore = new Map<string, RateLimitEntry>();

export interface RateLimitConfig {
  windowMs: number;        // Time window in milliseconds
  maxRequests: number;     // Max requests per window
  blockDurationMs?: number; // Block duration after exceeding
}

// Preset configurations for different endpoint types
export const RATE_LIMIT_CONFIGS = {
  // Strict: Registration, newsletter (prevent spam)
  strict: {
    windowMs: 60 * 1000,           // 1 minute
    maxRequests: 5,                 // 5 requests
    blockDurationMs: 5 * 60 * 1000, // Block 5 minutes
  },
  // Standard: General API endpoints
  standard: {
    windowMs: 60 * 1000,           // 1 minute
    maxRequests: 30,                // 30 requests
    blockDurationMs: 60 * 1000,    // Block 1 minute
  },
  // Lenient: Read-only endpoints
  lenient: {
    windowMs: 60 * 1000,           // 1 minute
    maxRequests: 100,               // 100 requests
    // No blocking, just throttle
  },
} as const;

/**
 * Get client identifier from request
 * Uses Cloudflare headers for accurate IP detection
 */
export function getClientId(request: Request): string {
  // Cloudflare provides real client IP
  const cfIp = request.headers.get('CF-Connecting-IP');
  if (cfIp) return cfIp;

  // Fallback headers
  const xForwardedFor = request.headers.get('X-Forwarded-For');
  if (xForwardedFor) return xForwardedFor.split(',')[0].trim();

  const xRealIp = request.headers.get('X-Real-IP');
  if (xRealIp) return xRealIp;

  // Last resort: hash user-agent
  const userAgent = request.headers.get('User-Agent') || 'unknown';
  return `ua-${hashString(userAgent)}`;
}

function hashString(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16);
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetAt: number;
  retryAfter?: number;
}

/**
 * Check rate limit for a client/endpoint combination
 */
export function checkRateLimit(
  clientId: string,
  endpoint: string,
  config: RateLimitConfig
): RateLimitResult {
  const now = Date.now();
  const key = `${clientId}:${endpoint}`;

  // Periodic cleanup (1% chance)
  if (Math.random() < 0.01) cleanupStore();

  let entry = rateLimitStore.get(key);

  // Check if blocked
  if (entry?.blockedUntil && entry.blockedUntil > now) {
    return {
      allowed: false,
      remaining: 0,
      resetAt: entry.blockedUntil,
      retryAfter: Math.ceil((entry.blockedUntil - now) / 1000),
    };
  }

  // Initialize entry
  if (!entry) {
    entry = { timestamps: [] };
    rateLimitStore.set(key, entry);
  }

  // Remove old timestamps
  const windowStart = now - config.windowMs;
  entry.timestamps = entry.timestamps.filter(ts => ts > windowStart);

  // Check limit
  if (entry.timestamps.length >= config.maxRequests) {
    if (config.blockDurationMs) {
      entry.blockedUntil = now + config.blockDurationMs;
    }
    const resetAt = entry.blockedUntil || (entry.timestamps[0] + config.windowMs);
    return {
      allowed: false,
      remaining: 0,
      resetAt,
      retryAfter: Math.ceil((resetAt - now) / 1000),
    };
  }

  // Record request
  entry.timestamps.push(now);

  return {
    allowed: true,
    remaining: config.maxRequests - entry.timestamps.length,
    resetAt: now + config.windowMs,
  };
}

function cleanupStore(): void {
  const now = Date.now();
  const maxAge = 10 * 60 * 1000;

  for (const [key, entry] of rateLimitStore.entries()) {
    const hasRecentActivity = entry.timestamps.some(ts => now - ts < maxAge);
    const isStillBlocked = entry.blockedUntil && entry.blockedUntil > now;
    if (!hasRecentActivity && !isStillBlocked) {
      rateLimitStore.delete(key);
    }
  }
}

/**
 * Create rate limit response headers
 */
export function rateLimitHeaders(result: RateLimitResult): Record<string, string> {
  const headers: Record<string, string> = {
    'X-RateLimit-Remaining': result.remaining.toString(),
    'X-RateLimit-Reset': Math.ceil(result.resetAt / 1000).toString(),
  };
  if (result.retryAfter) {
    headers['Retry-After'] = result.retryAfter.toString();
  }
  return headers;
}

/**
 * Create 429 Too Many Requests response
 */
export function rateLimitResponse(result: RateLimitResult): Response {
  return new Response(
    JSON.stringify({
      success: false,
      error: 'Too many requests. Please try again later.',
      retryAfter: result.retryAfter,
    }),
    {
      status: 429,
      headers: {
        'Content-Type': 'application/json',
        ...rateLimitHeaders(result),
      },
    }
  );
}
```

### Using Rate Limiting

```typescript
// src/pages/api/newsletter.ts
import type { APIRoute } from 'astro';
import {
  checkRateLimit,
  getClientId,
  rateLimitResponse,
  rateLimitHeaders,
  RATE_LIMIT_CONFIGS,
} from '../../lib/rate-limit';
import { SECURITY_HEADERS } from '../../lib/security';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  // 1. Rate limiting (check first - cheapest operation)
  const clientId = getClientId(request);
  const rateLimitResult = checkRateLimit(clientId, 'newsletter', RATE_LIMIT_CONFIGS.strict);

  if (!rateLimitResult.allowed) {
    return rateLimitResponse(rateLimitResult);
  }

  // 2. Process request...
  try {
    const result = await processNewsletter(request);
    const rlHeaders = rateLimitHeaders(rateLimitResult);

    return new Response(
      JSON.stringify(result),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          ...SECURITY_HEADERS,
          ...rlHeaders,  // Include rate limit info
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }
};
```

### Cloudflare Rate Limiting (Production)

For multi-instance deployments, use Cloudflare Rate Limiting Rules:

```
Cloudflare Dashboard > Security > WAF > Rate limiting rules

Rule 1: Newsletter Signup
- URI Path: equals /api/newsletter
- Method: POST
- Rate: 5 requests per 60 seconds per IP
- Action: Block for 5 minutes

Rule 2: Event Registration
- URI Path: starts with /api/events/
- Method: POST
- Rate: 10 requests per 60 seconds per IP
- Action: Block for 1 minute

Rule 3: General API
- URI Path: starts with /api/
- Rate: 100 requests per 60 seconds per IP
- Action: Challenge (CAPTCHA)
```

---

## 5. CSRF Protection

### Security Library

```typescript
// src/lib/security.ts

// Allowed origins for CSRF protection
const ALLOWED_ORIGINS = [
  'https://your-domain.com',
  'https://www.your-domain.com',
];

// Add localhost for development
if (import.meta.env.DEV) {
  ALLOWED_ORIGINS.push(
    'http://localhost:4321',
    'http://localhost:3000',
    'http://127.0.0.1:4321',
    'http://127.0.0.1:3000'
  );
}

/**
 * Validate request origin for CSRF protection
 * Returns true if origin is valid
 */
export function validateOrigin(request: Request): boolean {
  const origin = request.headers.get('Origin');
  const referer = request.headers.get('Referer');

  // Permissive in development
  if (import.meta.env.DEV) {
    return true;
  }

  // Check Origin header first (most reliable)
  if (origin) {
    return ALLOWED_ORIGINS.some(allowed => origin === allowed);
  }

  // Fall back to Referer header
  if (referer) {
    try {
      const refererUrl = new URL(referer);
      return ALLOWED_ORIGINS.some(allowed => refererUrl.origin === allowed);
    } catch {
      return false;
    }
  }

  // No origin info - reject for safety
  return false;
}

/**
 * Create 403 Forbidden response for CSRF failures
 */
export function csrfForbiddenResponse(): Response {
  return new Response(
    JSON.stringify({ success: false, error: 'Forbidden' }),
    {
      status: 403,
      headers: { 'Content-Type': 'application/json' }
    }
  );
}

/**
 * Security headers for all API responses
 */
export const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Cache-Control': 'no-store, max-age=0',
};

/**
 * Create secure JSON response
 */
export function secureJsonResponse(
  data: unknown,
  status: number = 200
): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...SECURITY_HEADERS,
    },
  });
}
```

### CSRF Protection in API Routes

```typescript
// src/pages/api/unsubscribe.ts
import type { APIRoute } from 'astro';
import { validateOrigin, csrfForbiddenResponse, SECURITY_HEADERS } from '../../lib/security';

export const prerender = false;

// POST: State-changing operation - requires CSRF check
export const POST: APIRoute = async ({ request }) => {
  // Always validate origin for POST/PUT/DELETE
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  try {
    const { email, id } = await request.json();
    // Process unsubscribe...
    return new Response(
      JSON.stringify({ success: true }),
      { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }
};

// GET: Safe method - redirect to confirmation page
// This pattern prevents CSRF via email links
export const GET: APIRoute = async ({ url }) => {
  const email = url.searchParams.get('email');
  const id = url.searchParams.get('id');

  // Redirect to confirmation page where user clicks button (POST)
  return new Response(null, {
    status: 302,
    headers: {
      Location: `/unsubscribe?email=${encodeURIComponent(email || '')}&id=${id || ''}`,
    },
  });
};
```

### CSRF-Safe Pattern for Email Links

```
Email Link Flow:

1. Email contains: /api/unsubscribe?id=xxx
2. GET request redirects to: /unsubscribe?id=xxx (confirmation page)
3. User clicks "Confirm" button on page
4. POST request to: /api/unsubscribe (with Origin header)
5. CSRF check passes, unsubscribe processed

This prevents attackers from unsubscribing users via hidden img/form tags.
```

---

## 6. Error Handling and Responses

### Standard Response Format

```typescript
// Success response
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2026-01-16T10:00:00Z",
    "requestId": "req_abc123"
  }
}

// Error response
{
  "success": false,
  "error": "Short error message for users",
  "code": "VALIDATION_ERROR",
  "details": ["email: Invalid format", "name: Required"],
  "meta": {
    "timestamp": "2026-01-16T10:00:00Z",
    "requestId": "req_abc123"
  }
}
```

### Response Helper Functions

```typescript
// src/lib/response.ts
import { SECURITY_HEADERS } from './security';

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  code?: string;
  details?: string[];
  meta?: {
    timestamp: string;
    requestId?: string;
  };
}

function generateRequestId(): string {
  return `req_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function buildMeta(requestId?: string) {
  return {
    timestamp: new Date().toISOString(),
    requestId: requestId || generateRequestId(),
  };
}

/**
 * Success response
 */
export function successResponse<T>(
  data: T,
  status: number = 200,
  extraHeaders: Record<string, string> = {}
): Response {
  const body: ApiResponse<T> = {
    success: true,
    data,
    meta: buildMeta(),
  };

  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...SECURITY_HEADERS,
      ...extraHeaders,
    },
  });
}

/**
 * Error response
 */
export function errorResponse(
  message: string,
  status: number = 400,
  options: {
    code?: string;
    details?: string[];
    extraHeaders?: Record<string, string>;
  } = {}
): Response {
  const body: ApiResponse = {
    success: false,
    error: message,
    code: options.code,
    details: options.details,
    meta: buildMeta(),
  };

  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...SECURITY_HEADERS,
      ...(options.extraHeaders || {}),
    },
  });
}

/**
 * Common error responses
 */
export const CommonErrors = {
  badRequest: (message = 'Bad request', details?: string[]) =>
    errorResponse(message, 400, { code: 'BAD_REQUEST', details }),

  unauthorized: (message = 'Unauthorized') =>
    errorResponse(message, 401, { code: 'UNAUTHORIZED' }),

  forbidden: (message = 'Forbidden') =>
    errorResponse(message, 403, { code: 'FORBIDDEN' }),

  notFound: (message = 'Not found') =>
    errorResponse(message, 404, { code: 'NOT_FOUND' }),

  validationError: (errors: string[]) =>
    errorResponse('Validation failed', 400, { code: 'VALIDATION_ERROR', details: errors }),

  internalError: (message = 'Internal server error') =>
    errorResponse(message, 500, { code: 'INTERNAL_ERROR' }),
};
```

### Error Handling Pattern

```typescript
// src/pages/api/events/register.ts
import type { APIRoute } from 'astro';
import { successResponse, errorResponse, CommonErrors } from '../../../lib/response';
import { validateOrigin, csrfForbiddenResponse } from '../../../lib/security';
import { checkRateLimit, getClientId, rateLimitResponse, RATE_LIMIT_CONFIGS } from '../../../lib/rate-limit';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  // 1. Rate limiting
  const clientId = getClientId(request);
  const rateLimit = checkRateLimit(clientId, 'events/register', RATE_LIMIT_CONFIGS.strict);
  if (!rateLimit.allowed) {
    return rateLimitResponse(rateLimit);
  }

  // 2. CSRF protection
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  // 3. Parse and validate
  let body: { eventSlug?: string; email?: string; name?: string };
  try {
    body = await request.json();
  } catch {
    return CommonErrors.badRequest('Invalid JSON body');
  }

  // 4. Validate required fields
  const errors: string[] = [];
  if (!body.eventSlug) errors.push('eventSlug: Required');
  if (!body.email || !body.email.includes('@')) errors.push('email: Valid email required');
  if (!body.name || body.name.trim().length < 2) errors.push('name: At least 2 characters required');

  if (errors.length > 0) {
    return CommonErrors.validationError(errors);
  }

  // 5. Process request
  try {
    const result = await registerForEvent(
      body.eventSlug!,
      body.email!,
      body.name!.trim()
    );

    if (result.success) {
      return successResponse({
        message: 'Successfully registered!',
        registration: result.registration,
      });
    } else {
      return errorResponse(result.error || 'Registration failed', 400);
    }
  } catch (error) {
    // Log error internally but don't expose details
    console.error('Event registration error:', error);
    return CommonErrors.internalError();
  }
};
```

---

## 7. Authentication Patterns

### API Key Authentication

```typescript
// src/lib/auth.ts

interface AuthResult {
  authenticated: boolean;
  userId?: string;
  error?: string;
}

/**
 * Validate API key from header
 */
export function validateApiKey(request: Request): AuthResult {
  const authHeader = request.headers.get('Authorization');

  if (!authHeader) {
    return { authenticated: false, error: 'No authorization header' };
  }

  // Bearer token format
  if (!authHeader.startsWith('Bearer ')) {
    return { authenticated: false, error: 'Invalid authorization format' };
  }

  const apiKey = authHeader.slice(7);

  // Validate against stored keys (in production, check database)
  const validKeys: Record<string, string> = {
    'sk_live_abc123': 'user_1',
    'sk_live_def456': 'user_2',
  };

  const userId = validKeys[apiKey];
  if (!userId) {
    return { authenticated: false, error: 'Invalid API key' };
  }

  return { authenticated: true, userId };
}

/**
 * Middleware-style auth check
 */
export function requireAuth(request: Request): Response | AuthResult {
  const auth = validateApiKey(request);

  if (!auth.authenticated) {
    return new Response(
      JSON.stringify({ success: false, error: auth.error }),
      {
        status: 401,
        headers: {
          'Content-Type': 'application/json',
          'WWW-Authenticate': 'Bearer',
        },
      }
    );
  }

  return auth;
}
```

### Session-Based Authentication (with Supabase)

```typescript
// src/lib/auth-supabase.ts
import { getSupabaseClient } from './supabase';

interface SessionUser {
  id: string;
  email: string;
  role: string;
}

/**
 * Validate session token from cookie or header
 */
export async function validateSession(request: Request): Promise<SessionUser | null> {
  // Get token from cookie or header
  const cookieHeader = request.headers.get('Cookie');
  const authHeader = request.headers.get('Authorization');

  let token: string | null = null;

  // Try cookie first
  if (cookieHeader) {
    const cookies = Object.fromEntries(
      cookieHeader.split(';').map(c => {
        const [key, ...val] = c.trim().split('=');
        return [key, val.join('=')];
      })
    );
    token = cookies['session_token'];
  }

  // Fall back to header
  if (!token && authHeader?.startsWith('Bearer ')) {
    token = authHeader.slice(7);
  }

  if (!token) return null;

  // Validate with Supabase
  const supabase = getSupabaseClient();
  if (!supabase) return null;

  const { data: { user }, error } = await supabase.auth.getUser(token);

  if (error || !user) return null;

  return {
    id: user.id,
    email: user.email || '',
    role: user.role || 'user',
  };
}
```

### Protected Endpoint Example

```typescript
// src/pages/api/admin/stats.ts
import type { APIRoute } from 'astro';
import { validateSession } from '../../../lib/auth-supabase';
import { successResponse, CommonErrors } from '../../../lib/response';

export const prerender = false;

export const GET: APIRoute = async ({ request }) => {
  // 1. Authenticate
  const user = await validateSession(request);

  if (!user) {
    return CommonErrors.unauthorized('Authentication required');
  }

  // 2. Authorize (check role)
  if (user.role !== 'admin') {
    return CommonErrors.forbidden('Admin access required');
  }

  // 3. Return protected data
  const stats = await getAdminStats();

  return successResponse(stats);
};
```

---

## 8. Common Endpoints

### Newsletter Subscription

```typescript
// src/pages/api/newsletter.ts
import type { APIRoute } from 'astro';
import { subscribeToNewsletter, type SupportedLanguage } from '../../lib/supabase';
import { checkRateLimit, getClientId, rateLimitResponse, rateLimitHeaders, RATE_LIMIT_CONFIGS } from '../../lib/rate-limit';
import { validateOrigin, csrfForbiddenResponse, SECURITY_HEADERS } from '../../lib/security';

export const prerender = false;

const SUPPORTED_LANGUAGES: SupportedLanguage[] = ['en', 'zh-tw', 'ja'];

export const POST: APIRoute = async ({ request }) => {
  // CSRF protection
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  // Rate limiting (strict for signup)
  const clientId = getClientId(request);
  const rateLimitResult = checkRateLimit(clientId, 'newsletter', RATE_LIMIT_CONFIGS.strict);

  if (!rateLimitResult.allowed) {
    return rateLimitResponse(rateLimitResult);
  }

  try {
    const body = await request.json();
    const { email, source = 'website', language = 'en' } = body;

    if (!email) {
      return new Response(
        JSON.stringify({ error: 'Email is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    // Validate language with fallback
    const validLanguage: SupportedLanguage = SUPPORTED_LANGUAGES.includes(language)
      ? language
      : 'en';

    const result = await subscribeToNewsletter(email, source, validLanguage);
    const rlHeaders = rateLimitHeaders(rateLimitResult);

    if (result.success) {
      return new Response(
        JSON.stringify({ message: 'Successfully subscribed!', subscriberId: result.subscriberId }),
        { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS, ...rlHeaders } }
      );
    } else {
      return new Response(
        JSON.stringify({ error: result.error }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS, ...rlHeaders } }
      );
    }
  } catch (error) {
    console.error('Newsletter API error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }
};
```

### Contact Form

```typescript
// src/pages/api/contact.ts
import type { APIRoute } from 'astro';
import { validateOrigin, csrfForbiddenResponse, SECURITY_HEADERS } from '../../lib/security';
import { checkRateLimit, getClientId, rateLimitResponse, RATE_LIMIT_CONFIGS } from '../../lib/rate-limit';
import { sanitizeString, validateEmail } from '../../lib/validation';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  // CSRF check
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  // Rate limiting (prevent spam)
  const clientId = getClientId(request);
  const rateLimit = checkRateLimit(clientId, 'contact', RATE_LIMIT_CONFIGS.strict);
  if (!rateLimit.allowed) {
    return rateLimitResponse(rateLimit);
  }

  try {
    const body = await request.json();
    const { name, email, message } = body;

    // Validate
    const errors: string[] = [];

    const nameResult = sanitizeString(name, { maxLength: 100 });
    if (!nameResult.valid || !nameResult.data || nameResult.data.length < 2) {
      errors.push('Name is required (2-100 characters)');
    }

    const emailResult = validateEmail(email);
    if (!emailResult.valid) {
      errors.push('Valid email is required');
    }

    const messageResult = sanitizeString(message, { maxLength: 5000 });
    if (!messageResult.valid || !messageResult.data || messageResult.data.length < 10) {
      errors.push('Message is required (10-5000 characters)');
    }

    if (errors.length > 0) {
      return new Response(
        JSON.stringify({ success: false, errors }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    // Store in database or send email
    await saveContactMessage({
      name: nameResult.data!,
      email: emailResult.data!,
      message: messageResult.data!,
      ip: clientId,
      userAgent: request.headers.get('User-Agent') || 'unknown',
      timestamp: new Date().toISOString(),
    });

    return new Response(
      JSON.stringify({ success: true, message: 'Message sent successfully' }),
      { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  } catch (error) {
    console.error('Contact API error:', error);
    return new Response(
      JSON.stringify({ success: false, error: 'Failed to send message' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }
};
```

### Analytics Endpoint

```typescript
// src/pages/api/analytics/stats.ts
import type { APIRoute } from 'astro';
import { getAnalytics } from '../../../lib/analytics';
import { SECURITY_HEADERS } from '../../../lib/security';

export const prerender = false;

export const GET: APIRoute = async ({ url }) => {
  const project = url.searchParams.get('project') || 'default';
  const days = parseInt(url.searchParams.get('days') || '30', 10);

  try {
    const stats = await getAnalytics(project, days);

    return new Response(
      JSON.stringify(stats),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=300', // Cache 5 minutes
          ...SECURITY_HEADERS,
        },
      }
    );
  } catch (error) {
    console.error('Analytics API error:', error);
    // Return empty stats on error (graceful degradation)
    return new Response(
      JSON.stringify({ data: [], error: false }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS },
      }
    );
  }
};
```

---

## Security Checklist

- [x] **CSRF Protection**: Validate Origin/Referer on all POST/PUT/DELETE
- [x] **Rate Limiting**: Strict limits on signup/auth, standard on general APIs
- [x] **Input Validation**: Validate and sanitize all user inputs
- [x] **Error Handling**: Never expose internal errors to clients
- [x] **Security Headers**: X-Content-Type-Options, X-Frame-Options, Cache-Control
- [x] **Authentication**: Use secure token-based auth for protected endpoints
- [x] **Logging**: Log errors internally, not to responses
- [x] **HTTPS**: Enforce HTTPS in production (Cloudflare handles this)

## Production Checklist

- [x] Set `prerender = false` for all dynamic endpoints
- [x] Configure `wrangler.toml` with correct settings
- [x] Set secrets via `wrangler secret put`
- [x] Configure Cloudflare Rate Limiting Rules in Dashboard
- [x] Enable Cloudflare WAF for additional protection
- [x] Test all endpoints with invalid/malicious inputs
- [x] Monitor error rates in Cloudflare Analytics

---

## Directory Structure

```
src/
├── lib/
│   ├── security.ts         # CSRF protection, security headers
│   ├── rate-limit.ts       # Rate limiting utilities
│   ├── validation.ts       # Input validation helpers
│   ├── response.ts         # Standard response builders
│   ├── auth.ts             # Authentication utilities
│   └── supabase.ts         # Database client
└── pages/
    └── api/
        ├── newsletter.ts   # POST - Newsletter signup
        ├── unsubscribe.ts  # POST, GET - Unsubscribe
        ├── contact.ts      # POST - Contact form
        ├── preferences.ts  # GET, POST - User preferences
        ├── events/
        │   ├── register.ts # POST - Event registration
        │   └── check-in.ts # POST - QR check-in
        └── analytics/
            └── stats.ts    # GET - Public stats
```

---

## Resources

- [Astro API Routes Documentation](https://docs.astro.build/en/guides/endpoints/)
- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/functions/)
- [Cloudflare Rate Limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [Supabase + Cloudflare Integration](./supabase-cloudflare-integration.md)
- [Newsletter System](./newsletter-system.md)

---

*These patterns are battle-tested from the production deployment of [claude-world.com](https://claude-world.com), serving thousands of requests daily on Cloudflare Pages.*
