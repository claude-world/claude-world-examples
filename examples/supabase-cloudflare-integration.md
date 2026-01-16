# Supabase + Cloudflare Pages Integration

> Build full-stack applications with free hosting (Cloudflare Pages) and free database tier (Supabase).

This guide covers the complete integration pattern used by [claude-world.com](https://claude-world.com), including project setup, database integration, edge functions, and common patterns.

---

## Overview

| Component | Purpose | Cost |
|-----------|---------|------|
| Cloudflare Pages | Static hosting + Edge Functions | Free |
| Supabase | PostgreSQL database + Auth | Free tier |
| Astro | Static site generator with SSR | Free |

**Total cost for MVP**: $0/month (domain ~$10/year)

---

## 1. Project Setup

### Directory Structure

```
project/
├── src/
│   ├── lib/
│   │   ├── supabase.ts      # Database client
│   │   ├── rate-limit.ts    # Rate limiting
│   │   └── security.ts      # CSRF protection
│   └── pages/
│       └── api/             # Edge functions
├── supabase/
│   └── migrations/          # SQL migrations
├── wrangler.toml            # Cloudflare config
├── .env.example             # Environment template
└── .dev.vars                # Local dev secrets (gitignored)
```

### wrangler.toml (Cloudflare Configuration)

```toml
# Cloudflare Pages configuration
name = "your-project"
compatibility_date = "2025-01-01"
compatibility_flags = ["nodejs_compat"]

# Build output directory
pages_build_output_dir = "./dist"

# Environment variables
[vars]
PUBLIC_SUPABASE_URL = "https://your-project.supabase.co"
# IMPORTANT: For production, set ANON_KEY as a secret:
# wrangler secret put PUBLIC_SUPABASE_ANON_KEY

# Optional: KV Namespace for sessions
# [[kv_namespaces]]
# binding = "SESSION"
# id = "your-kv-namespace-id"
```

### Environment Variables

```bash
# .env.example
PUBLIC_SUPABASE_URL=https://your-project.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# .dev.vars (for local development, gitignored)
PUBLIC_SUPABASE_URL=https://your-project.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

**Setting Production Secrets:**

```bash
# Set secrets via Cloudflare CLI
wrangler secret put PUBLIC_SUPABASE_ANON_KEY

# Or via Cloudflare Dashboard:
# Pages > Your Project > Settings > Environment variables
```

---

## 2. Database Integration

### Supabase Client

```typescript
// src/lib/supabase.ts
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY || '';

// Singleton pattern - create client only when needed
let supabase: SupabaseClient | null = null;

export function getSupabaseClient(): SupabaseClient | null {
  if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('Supabase credentials not configured');
    return null;
  }
  if (!supabase) {
    supabase = createClient(supabaseUrl, supabaseAnonKey);
  }
  return supabase;
}

// Type-safe interfaces
export interface Subscriber {
  id?: string;
  email: string;
  source: string;
  preferred_language: 'en' | 'zh-tw' | 'ja';
  subscribed_at?: string;
  confirmed?: boolean;
  unsubscribed_at?: string | null;
}

// Example function with graceful fallback
export async function subscribeToNewsletter(
  email: string,
  source: string = 'website',
  language: 'en' | 'zh-tw' | 'ja' = 'en'
): Promise<{ success: boolean; error?: string }> {
  // Validate email
  if (!email || !email.includes('@')) {
    return { success: false, error: 'Invalid email address' };
  }

  const client = getSupabaseClient();

  // Graceful fallback when Supabase is not configured
  if (!client) {
    console.log('Newsletter subscription (no Supabase):', { email, source, language });
    return { success: true }; // Allow development without database
  }

  try {
    // Check if already subscribed
    const { data: existing } = await client
      .from('newsletter_subscribers')
      .select('id, unsubscribed_at')
      .eq('email', email.toLowerCase())
      .single();

    if (existing) {
      if (existing.unsubscribed_at) {
        // Re-subscribe
        await client
          .from('newsletter_subscribers')
          .update({ unsubscribed_at: null, source, preferred_language: language })
          .eq('id', existing.id);
      }
      // Generic success to prevent email enumeration
      return { success: true };
    }

    // New subscription
    await client
      .from('newsletter_subscribers')
      .insert({
        email: email.toLowerCase(),
        source,
        preferred_language: language,
        confirmed: true, // Single opt-in
      });

    return { success: true };
  } catch (err) {
    console.error('Newsletter subscription error:', err);
    return { success: false, error: 'Failed to subscribe. Please try again.' };
  }
}
```

### Database Migrations

```sql
-- supabase/migrations/001_create_newsletter.sql

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  source TEXT DEFAULT 'website',
  preferred_language VARCHAR(10) DEFAULT 'en' CHECK (preferred_language IN ('en', 'zh-tw', 'ja')),
  subscribed_at TIMESTAMPTZ DEFAULT NOW(),
  confirmed BOOLEAN DEFAULT FALSE,
  unsubscribed_at TIMESTAMPTZ
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_newsletter_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_newsletter_source ON newsletter_subscribers(source);

-- Enable Row Level Security (CRITICAL for production)
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anonymous inserts (for signup)
CREATE POLICY "Allow anonymous inserts" ON newsletter_subscribers
  FOR INSERT TO anon
  WITH CHECK (true);

-- Policy: Deny reads to anonymous users (protect email list)
-- Only authenticated/service role can read
CREATE POLICY "Deny anonymous reads" ON newsletter_subscribers
  FOR SELECT TO anon
  USING (false);
```

**Running Migrations:**

```bash
# Via Supabase Dashboard
# Go to: SQL Editor > New Query > Paste and Run

# Or via Supabase CLI
supabase db push
```

---

## 3. Edge Functions (API Routes)

### Rate Limiting

```typescript
// src/lib/rate-limit.ts

interface RateLimitEntry {
  timestamps: number[];
  blockedUntil?: number;
}

// In-memory store (per-instance)
const rateLimitStore = new Map<string, RateLimitEntry>();

export interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  blockDurationMs?: number;
}

// Preset configurations
export const RATE_LIMIT_CONFIGS = {
  strict: {
    windowMs: 60 * 1000,           // 1 minute
    maxRequests: 5,                 // 5 requests
    blockDurationMs: 5 * 60 * 1000, // Block 5 minutes
  },
  standard: {
    windowMs: 60 * 1000,
    maxRequests: 30,
    blockDurationMs: 60 * 1000,
  },
  lenient: {
    windowMs: 60 * 1000,
    maxRequests: 100,
  },
} as const;

// Get client IP (Cloudflare provides this)
export function getClientId(request: Request): string {
  // CF-Connecting-IP is the real client IP on Cloudflare
  const cfIp = request.headers.get('CF-Connecting-IP');
  if (cfIp) return cfIp;

  const xForwardedFor = request.headers.get('X-Forwarded-For');
  if (xForwardedFor) return xForwardedFor.split(',')[0].trim();

  return 'unknown';
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetAt: number;
  retryAfter?: number;
}

export function checkRateLimit(
  clientId: string,
  endpoint: string,
  config: RateLimitConfig
): RateLimitResult {
  const now = Date.now();
  const key = `${clientId}:${endpoint}`;

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

  if (!entry) {
    entry = { timestamps: [] };
    rateLimitStore.set(key, entry);
  }

  // Clean old timestamps
  const windowStart = now - config.windowMs;
  entry.timestamps = entry.timestamps.filter(ts => ts > windowStart);

  // Check limit
  if (entry.timestamps.length >= config.maxRequests) {
    if (config.blockDurationMs) {
      entry.blockedUntil = now + config.blockDurationMs;
    }
    return {
      allowed: false,
      remaining: 0,
      resetAt: entry.blockedUntil || (entry.timestamps[0] + config.windowMs),
      retryAfter: Math.ceil(config.windowMs / 1000),
    };
  }

  entry.timestamps.push(now);

  return {
    allowed: true,
    remaining: config.maxRequests - entry.timestamps.length,
    resetAt: now + config.windowMs,
  };
}

export function rateLimitResponse(result: RateLimitResult): Response {
  return new Response(
    JSON.stringify({ error: 'Too many requests', retryAfter: result.retryAfter }),
    {
      status: 429,
      headers: {
        'Content-Type': 'application/json',
        'Retry-After': (result.retryAfter || 60).toString(),
      },
    }
  );
}
```

### CSRF Protection

```typescript
// src/lib/security.ts

const ALLOWED_ORIGINS = [
  'https://your-domain.com',
  'https://www.your-domain.com',
];

// Add localhost for development
if (import.meta.env.DEV) {
  ALLOWED_ORIGINS.push(
    'http://localhost:4321',
    'http://localhost:3000'
  );
}

export function validateOrigin(request: Request): boolean {
  const origin = request.headers.get('Origin');
  const referer = request.headers.get('Referer');

  // Permissive in development
  if (import.meta.env.DEV) return true;

  // Check Origin header
  if (origin) {
    return ALLOWED_ORIGINS.includes(origin);
  }

  // Fall back to Referer
  if (referer) {
    try {
      const refererUrl = new URL(referer);
      return ALLOWED_ORIGINS.includes(refererUrl.origin);
    } catch {
      return false;
    }
  }

  return false; // Reject if no origin info
}

export function csrfForbiddenResponse(): Response {
  return new Response(
    JSON.stringify({ error: 'Forbidden' }),
    { status: 403, headers: { 'Content-Type': 'application/json' } }
  );
}

export const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Cache-Control': 'no-store, max-age=0',
};
```

### API Route Example

```typescript
// src/pages/api/newsletter.ts
import type { APIRoute } from 'astro';
import { subscribeToNewsletter } from '../../lib/supabase';
import { checkRateLimit, getClientId, rateLimitResponse, RATE_LIMIT_CONFIGS } from '../../lib/rate-limit';
import { validateOrigin, csrfForbiddenResponse, SECURITY_HEADERS } from '../../lib/security';

// Ensure server-side rendering (not static)
export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  // 1. CSRF protection
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  // 2. Rate limiting
  const clientId = getClientId(request);
  const rateLimitResult = checkRateLimit(clientId, 'newsletter', RATE_LIMIT_CONFIGS.strict);

  if (!rateLimitResult.allowed) {
    return rateLimitResponse(rateLimitResult);
  }

  // 3. Process request
  try {
    const { email, source = 'website', language = 'en' } = await request.json();

    if (!email) {
      return new Response(
        JSON.stringify({ error: 'Email is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    const result = await subscribeToNewsletter(email, source, language);

    if (result.success) {
      return new Response(
        JSON.stringify({ message: 'Successfully subscribed!' }),
        { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    } else {
      return new Response(
        JSON.stringify({ error: result.error }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
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

---

## 4. Common Patterns

### Newsletter Subscription

See the complete example above. Key features:
- Email validation
- Duplicate prevention
- Re-subscription support
- Language preference
- Single opt-in (no email confirmation)

### Event Registration with QR Codes

```typescript
// Generate cryptographically secure QR token
function generateQRToken(): string {
  return crypto.randomUUID();
}

// Registration with duplicate handling
export async function registerForEvent(
  eventSlug: string,
  email: string,
  name: string
): Promise<{ success: boolean; registration?: EventRegistration }> {
  const client = getSupabaseClient();
  if (!client) return { success: false };

  // Check for existing registration
  const { data: existing } = await client
    .from('event_registrations')
    .select('*')
    .eq('event_slug', eventSlug)
    .eq('email', email.toLowerCase())
    .single();

  if (existing) {
    // Return existing (good UX, prevents enumeration)
    return { success: true, registration: existing };
  }

  // New registration
  const { data, error } = await client
    .from('event_registrations')
    .insert({
      event_slug: eventSlug,
      email: email.toLowerCase(),
      name,
      qr_code_token: generateQRToken(),
      status: 'registered',
    })
    .select()
    .single();

  if (error) throw error;
  return { success: true, registration: data };
}

// Check-in with optimized single query
export async function checkInAttendee(token: string) {
  const client = getSupabaseClient();
  if (!client) return { success: false };

  // Atomic update (only if not already checked in)
  const { data, error } = await client
    .from('event_registrations')
    .update({
      status: 'attended',
      checked_in_at: new Date().toISOString(),
    })
    .eq('qr_code_token', token)
    .is('checked_in_at', null)  // Only update if not checked in
    .select()
    .single();

  if (data) return { success: true, registration: data };

  // Check why it failed
  const { data: existing } = await client
    .from('event_registrations')
    .select('*')
    .eq('qr_code_token', token)
    .single();

  if (!existing) return { success: false, error: 'Not found' };
  if (existing.checked_in_at) return { success: true, alreadyCheckedIn: true };

  return { success: false, error: 'Check-in failed' };
}
```

### Analytics Tracking

```sql
-- Analytics table with privacy-conscious design
CREATE TABLE analytics_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  event_type TEXT NOT NULL,
  event_data JSONB DEFAULT '{}',
  client_ip_hash TEXT,  -- Hashed, not raw IP
  user_agent TEXT,
  country TEXT DEFAULT 'unknown',  -- From CF-IPCountry header
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (tracking), deny reads
CREATE POLICY "Allow anonymous tracking" ON analytics_events
  FOR INSERT TO anon WITH CHECK (true);
```

```typescript
// Get country from Cloudflare header
function getCountry(request: Request): string {
  return request.headers.get('CF-IPCountry') || 'unknown';
}

// Hash IP for privacy
async function hashIP(ip: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(ip + 'your-salt');
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
}
```

---

## 5. Deployment

### Cloudflare Pages Setup

```bash
# 1. Install dependencies
pnpm install

# 2. Build
pnpm build

# 3. Preview locally (with Cloudflare environment)
pnpm preview  # or: wrangler pages dev ./dist

# 4. Deploy
# Option A: Connect GitHub repo in Cloudflare Dashboard
# Option B: Direct deploy
wrangler pages deploy ./dist
```

### Astro Configuration

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  output: 'hybrid',  // Static by default, SSR opt-in
  adapter: cloudflare({
    platformProxy: {
      enabled: true,
    },
  }),
  integrations: [react(), tailwind()],
});
```

### Production Checklist

- [ ] Set Supabase secrets via `wrangler secret put`
- [ ] Enable RLS on all tables
- [ ] Configure allowed origins in security.ts
- [ ] Set up Cloudflare Rate Limiting Rules (Dashboard)
- [ ] Enable Cloudflare WAF rules
- [ ] Configure custom domain with SSL

---

## Security Best Practices

1. **Row Level Security (RLS)**: Always enable on Supabase tables
2. **CSRF Protection**: Validate Origin/Referer headers
3. **Rate Limiting**: Protect signup/auth endpoints
4. **Input Validation**: Validate and sanitize all inputs
5. **Error Handling**: Don't leak internal errors to clients
6. **Secrets Management**: Use `wrangler secret` for production

---

## Troubleshooting

### "Supabase credentials not configured"

```bash
# Check if env vars are set
wrangler pages dev ./dist --local

# Set secrets for production
wrangler secret put PUBLIC_SUPABASE_URL
wrangler secret put PUBLIC_SUPABASE_ANON_KEY
```

### RLS Policy Blocking Queries

```sql
-- Debug: Check current policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Temporarily disable RLS (development only!)
ALTER TABLE your_table DISABLE ROW LEVEL SECURITY;
```

### Rate Limit Not Working in Production

The in-memory rate limiter works per-instance. For multi-instance deployments:

1. Use Cloudflare Rate Limiting Rules (Dashboard)
2. Or use Cloudflare KV for shared state
3. Or use Supabase for rate limit tracking

---

## Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Supabase Documentation](https://supabase.com/docs)
- [Astro Cloudflare Adapter](https://docs.astro.build/en/guides/integrations-guide/cloudflare/)
- [Claude World Examples](https://github.com/claude-world/claude-world-examples)

---

*This example is based on the actual implementation of [claude-world.com](https://claude-world.com), built from zero to production in 48 hours using Claude Code.*
