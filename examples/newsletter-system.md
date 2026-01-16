# Newsletter System Architecture

> Build a complete newsletter system with subscription, multi-language sending, and GDPR-compliant unsubscription.

This guide covers the newsletter architecture used by [claude-world.com](https://claude-world.com), featuring multi-language support, batch sending via Resend, and automation with GitHub Actions.

---

## Overview

| Component | Purpose | Technology |
|-----------|---------|------------|
| Subscription | User signup with language preference | Supabase + API Routes |
| Sending | Batch email delivery | Resend API |
| Unsubscription | One-click + preference center | API + confirmation page |
| Automation | Auto-generate from releases | GitHub Actions + Claude API |

**Architecture:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Subscription  │    │     Sending     │    │  Unsubscription │
│      Form       │───▶│     Script      │◀───│    Handler      │
│   (React/Astro) │    │   (Node.js)     │    │   (API Route)   │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Supabase (PostgreSQL)                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  newsletter_subscribers (id, email, language, status)   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Database Schema

### Subscribers Table

```sql
-- supabase/migrations/001_newsletter_subscribers.sql

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  source TEXT DEFAULT 'website',
  preferred_language VARCHAR(10) DEFAULT 'en'
    CHECK (preferred_language IN ('en', 'zh-tw', 'ja')),
  subscribed_at TIMESTAMPTZ DEFAULT NOW(),
  confirmed BOOLEAN DEFAULT FALSE,
  unsubscribed_at TIMESTAMPTZ
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_newsletter_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_newsletter_source ON newsletter_subscribers(source);
CREATE INDEX IF NOT EXISTS idx_newsletter_language ON newsletter_subscribers(preferred_language);
CREATE INDEX IF NOT EXISTS idx_newsletter_active ON newsletter_subscribers(confirmed, unsubscribed_at)
  WHERE confirmed = true AND unsubscribed_at IS NULL;

-- Row Level Security
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (for signup)
CREATE POLICY "Allow anonymous inserts" ON newsletter_subscribers
  FOR INSERT TO anon
  WITH CHECK (true);

-- Deny reads to anonymous (protect email list)
CREATE POLICY "Deny anonymous reads" ON newsletter_subscribers
  FOR SELECT TO anon
  USING (false);

-- Allow updates for unsubscribe/preferences (application-layer validation)
CREATE POLICY "Allow anonymous updates" ON newsletter_subscribers
  FOR UPDATE TO anon
  USING (true);

-- Comments
COMMENT ON TABLE newsletter_subscribers IS 'Newsletter subscriber list';
COMMENT ON COLUMN newsletter_subscribers.preferred_language IS 'Newsletter content language preference';
COMMENT ON COLUMN newsletter_subscribers.source IS 'Where the user signed up (website, event, etc.)';
```

### Audit Table (Optional)

```sql
-- Track all subscription events for compliance
CREATE TABLE IF NOT EXISTS newsletter_audit (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  subscriber_id UUID REFERENCES newsletter_subscribers(id),
  action TEXT NOT NULL CHECK (action IN ('subscribe', 'unsubscribe', 'update_language', 'resubscribe')),
  ip_hash TEXT,  -- Hashed for privacy
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_subscriber ON newsletter_audit(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON newsletter_audit(created_at);

ALTER TABLE newsletter_audit ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous inserts" ON newsletter_audit
  FOR INSERT TO anon WITH CHECK (true);
```

---

## 2. Subscription Flow

### Supabase Client

```typescript
// src/lib/supabase.ts
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY || '';

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

export type SupportedLanguage = 'en' | 'zh-tw' | 'ja';

export interface NewsletterSubscriber {
  id?: string;
  email: string;
  source: string;
  preferred_language: SupportedLanguage;
  subscribed_at?: string;
  confirmed?: boolean;
  unsubscribed_at?: string | null;
}

/**
 * Subscribe to newsletter with language preference
 * Uses Single Opt-in (confirmed immediately)
 */
export async function subscribeToNewsletter(
  email: string,
  source: string = 'website',
  language: SupportedLanguage = 'en'
): Promise<{ success: boolean; error?: string; subscriberId?: string }> {
  // Validate email
  if (!email || !email.includes('@')) {
    return { success: false, error: 'Invalid email address' };
  }

  const client = getSupabaseClient();
  if (!client) {
    console.log('Newsletter subscription (no Supabase):', { email, source, language });
    return { success: true };
  }

  try {
    // Check if already subscribed
    const { data: existing } = await client
      .from('newsletter_subscribers')
      .select('id, unsubscribed_at, preferred_language')
      .eq('email', email.toLowerCase())
      .single();

    if (existing) {
      if (existing.unsubscribed_at) {
        // Re-subscribe: clear unsubscribed status
        const { error } = await client
          .from('newsletter_subscribers')
          .update({
            unsubscribed_at: null,
            source,
            preferred_language: language,
            confirmed: true,
          })
          .eq('id', existing.id);

        if (error) throw error;
        return { success: true, subscriberId: existing.id };
      }
      // Already subscribed - return success (prevents email enumeration)
      return { success: true };
    }

    // New subscription
    const { data, error } = await client
      .from('newsletter_subscribers')
      .insert({
        email: email.toLowerCase(),
        source,
        preferred_language: language,
        confirmed: true,  // Single opt-in
      })
      .select('id')
      .single();

    if (error) throw error;
    return { success: true, subscriberId: data?.id };
  } catch (err) {
    console.error('Newsletter subscription error:', err);
    return { success: false, error: 'Failed to subscribe. Please try again.' };
  }
}

/**
 * Unsubscribe from newsletter
 */
export async function unsubscribeFromNewsletter(
  email?: string,
  subscriberId?: string
): Promise<{ success: boolean; error?: string }> {
  const client = getSupabaseClient();
  if (!client) {
    return { success: false, error: 'Service unavailable' };
  }

  try {
    let query = client
      .from('newsletter_subscribers')
      .update({ unsubscribed_at: new Date().toISOString() });

    if (subscriberId) {
      query = query.eq('id', subscriberId);
    } else if (email) {
      query = query.eq('email', email.toLowerCase());
    } else {
      return { success: false, error: 'Email or subscriber ID required' };
    }

    const { error } = await query;
    if (error) throw error;
    return { success: true };
  } catch (err) {
    console.error('Unsubscribe error:', err);
    return { success: false, error: 'Failed to unsubscribe. Please try again.' };
  }
}

/**
 * Update subscriber language preference
 */
export async function updateSubscriberLanguage(
  email: string,
  language: SupportedLanguage,
  subscriberId?: string
): Promise<{ success: boolean; error?: string }> {
  const client = getSupabaseClient();
  if (!client) {
    return { success: false, error: 'Service unavailable' };
  }

  try {
    let query = client
      .from('newsletter_subscribers')
      .update({ preferred_language: language });

    if (subscriberId) {
      query = query.eq('id', subscriberId);
    } else {
      query = query.eq('email', email.toLowerCase());
    }

    const { error } = await query;
    if (error) throw error;
    return { success: true };
  } catch (err) {
    console.error('Update language error:', err);
    return { success: false, error: 'Failed to update language.' };
  }
}
```

### API Route

```typescript
// src/pages/api/newsletter.ts
import type { APIRoute } from 'astro';
import { subscribeToNewsletter, type SupportedLanguage } from '../../lib/supabase';
import { checkRateLimit, getClientId, rateLimitResponse, RATE_LIMIT_CONFIGS } from '../../lib/rate-limit';
import { validateOrigin, csrfForbiddenResponse, SECURITY_HEADERS } from '../../lib/security';

export const prerender = false;

const SUPPORTED_LANGUAGES: SupportedLanguage[] = ['en', 'zh-tw', 'ja'];

export const POST: APIRoute = async ({ request }) => {
  // CSRF protection
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  // Rate limiting (5 requests/minute)
  const clientId = getClientId(request);
  const rateLimitResult = checkRateLimit(clientId, 'newsletter', RATE_LIMIT_CONFIGS.strict);

  if (!rateLimitResult.allowed) {
    return rateLimitResponse(rateLimitResult);
  }

  try {
    const { email, source = 'website', language = 'en' } = await request.json();

    if (!email) {
      return new Response(
        JSON.stringify({ error: 'Email is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    const validLanguage: SupportedLanguage = SUPPORTED_LANGUAGES.includes(language)
      ? language
      : 'en';

    const result = await subscribeToNewsletter(email, source, validLanguage);

    if (result.success) {
      return new Response(
        JSON.stringify({ message: 'Successfully subscribed!', subscriberId: result.subscriberId }),
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

### React Form Component

```tsx
// src/components/NewsletterForm.tsx
import { useState, useEffect } from 'react';

interface NewsletterFormProps {
  source?: string;
  defaultLanguage?: string;
  showLanguageSelector?: boolean;
  lang?: 'en' | 'zh-tw' | 'ja';
}

const LANGUAGES = [
  { code: 'zh-tw', label: '繁體中文', flag: '🇹🇼' },
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
] as const;

const i18nLabels = {
  en: {
    placeholder: 'you@email.com',
    button: 'Subscribe',
    buttonLoading: 'Joining...',
    success: 'Welcome aboard! Check your inbox for confirmation.',
    error: 'Something went wrong. Please try again.',
    help: 'Weekly insights on Claude Code mastery. No spam, unsubscribe anytime.',
  },
  'zh-tw': {
    placeholder: 'you@email.com',
    button: '訂閱',
    buttonLoading: '處理中...',
    success: '訂閱成功！請檢查您的收件匣確認。',
    error: '發生錯誤，請稍後再試。',
    help: '每週 Claude Code 進階技巧。無垃圾郵件，隨時取消訂閱。',
  },
  ja: {
    placeholder: 'you@email.com',
    button: '購読',
    buttonLoading: '処理中...',
    success: '購読完了！確認メールをご確認ください。',
    error: 'エラーが発生しました。もう一度お試しください。',
    help: '毎週 Claude Code の上級テクニックをお届け。スパムなし、いつでも解除可能。',
  },
};

export default function NewsletterForm({
  source = 'website',
  defaultLanguage,
  showLanguageSelector = true,
  lang = 'en',
}: NewsletterFormProps) {
  const [email, setEmail] = useState('');
  const [language, setLanguage] = useState(defaultLanguage || 'en');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const labels = i18nLabels[lang] || i18nLabels.en;

  // Auto-detect language from page URL
  useEffect(() => {
    if (!defaultLanguage && typeof window !== 'undefined') {
      const path = window.location.pathname;
      if (path.startsWith('/zh-tw')) setLanguage('zh-tw');
      else if (path.startsWith('/ja')) setLanguage('ja');
    }
  }, [defaultLanguage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setStatus('error');
      setMessage('Please enter a valid email address.');
      return;
    }

    setStatus('loading');

    try {
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source, language }),
      });

      if (response.ok) {
        setStatus('success');
        setMessage(labels.success);
        setEmail('');
      } else {
        const data = await response.json();
        setStatus('error');
        setMessage(data.error || labels.error);
      }
    } catch {
      setStatus('error');
      setMessage('Network error. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md">
      {showLanguageSelector && (
        <div className="mb-4">
          <div className="flex gap-2">
            {LANGUAGES.map((l) => (
              <button
                key={l.code}
                type="button"
                onClick={() => setLanguage(l.code)}
                className={`px-3 py-2 rounded-lg border ${
                  language === l.code
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-300'
                }`}
              >
                {l.flag} {l.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={labels.placeholder}
          className="flex-1 px-4 py-3 border rounded-lg"
          disabled={status === 'loading'}
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg disabled:opacity-50"
        >
          {status === 'loading' ? labels.buttonLoading : labels.button}
        </button>
      </div>

      {message && (
        <p className={`mt-3 text-sm ${status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
          {message}
        </p>
      )}

      <p className="mt-3 text-sm text-gray-500">{labels.help}</p>
    </form>
  );
}
```

---

## 3. Newsletter Sending

### Sending Script

```javascript
// scripts/send-newsletter.js
import { Resend } from 'resend';
import { createClient } from '@supabase/supabase-js';
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Language configuration
const LANGUAGES = {
  'zh-tw': {
    label: '繁體中文',
    defaultSubject: (date) => `[Newsletter] 本週精選 - ${date}`,
  },
  'en': {
    label: 'English',
    defaultSubject: (date) => `[Newsletter] Weekly Highlights - ${date}`,
  },
  'ja': {
    label: '日本語',
    defaultSubject: (date) => `[Newsletter] 今週のハイライト - ${date}`,
  },
};

// Initialize clients
const resend = new Resend(process.env.RESEND_API_KEY);
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY  // Use service key for reading all subscribers
);

async function sendNewsletter(targetDate, filterLang = null) {
  console.log('📬 Newsletter Sender (Multi-Language)\n');

  // Validate environment
  if (!process.env.RESEND_API_KEY || !process.env.SUPABASE_SERVICE_KEY) {
    console.error('❌ Missing required environment variables');
    process.exit(1);
  }

  // Find newsletter directory
  const draftsDir = join(projectRoot, 'newsletters/drafts');
  if (!targetDate) {
    const dirs = readdirSync(draftsDir)
      .filter(d => /^\d{4}-\d{2}-\d{2}/.test(d))
      .sort()
      .reverse();
    targetDate = dirs[0];
    console.log(`📅 Using most recent: ${targetDate}`);
  }

  const newsletterDir = join(draftsDir, targetDate);
  if (!existsSync(newsletterDir)) {
    console.error(`❌ Newsletter not found: ${targetDate}`);
    process.exit(1);
  }

  // Check if already sent
  const sentLogPath = join(projectRoot, 'newsletters/sent', targetDate, 'send-log.json');
  if (existsSync(sentLogPath) && !filterLang) {
    console.warn(`⚠️  Already sent for ${targetDate}`);
    process.exit(1);
  }

  // Load newsletter files
  const newsletters = {};
  const subjects = {};
  const subjectFile = join(newsletterDir, 'subject-lines.txt');
  let subjectLines = existsSync(subjectFile) ? readFileSync(subjectFile, 'utf-8') : '';

  for (const [lang, config] of Object.entries(LANGUAGES)) {
    if (filterLang && filterLang !== lang) continue;

    const filePath = join(newsletterDir, `newsletter-${lang}.html`);
    if (existsSync(filePath)) {
      newsletters[lang] = readFileSync(filePath, 'utf-8');
      const match = subjectLines.match(new RegExp(`${lang}:\\s*(.+)`));
      subjects[lang] = match ? match[1].trim() : config.defaultSubject(targetDate);
      console.log(`✓ Loaded ${config.label}`);
    }
  }

  // Get subscribers grouped by language
  let query = supabase
    .from('newsletter_subscribers')
    .select('id, email, preferred_language')
    .eq('confirmed', true)
    .is('unsubscribed_at', null);

  if (filterLang) {
    query = query.eq('preferred_language', filterLang);
  }

  const { data: subscribers, error } = await query;
  if (error || !subscribers?.length) {
    console.log('ℹ️  No subscribers to send to');
    process.exit(0);
  }

  // Group by language
  const subscribersByLang = {};
  for (const sub of subscribers) {
    const lang = newsletters[sub.preferred_language] ? sub.preferred_language : 'en';
    if (!subscribersByLang[lang]) subscribersByLang[lang] = [];
    subscribersByLang[lang].push(sub);
  }

  console.log(`\n👥 ${subscribers.length} subscriber(s):`);
  for (const [lang, subs] of Object.entries(subscribersByLang)) {
    console.log(`   ${LANGUAGES[lang]?.label}: ${subs.length}`);
  }

  // Send in batches
  const results = { successful: 0, failed: 0, byLanguage: {} };
  const batchSize = 100;

  for (const [lang, langSubscribers] of Object.entries(subscribersByLang)) {
    if (!newsletters[lang]) continue;

    console.log(`\n🌐 Sending ${LANGUAGES[lang]?.label}...`);
    results.byLanguage[lang] = { successful: 0, failed: 0 };

    for (let i = 0; i < langSubscribers.length; i += batchSize) {
      const batch = langSubscribers.slice(i, i + batchSize);

      try {
        const emailPayloads = batch.map(sub => {
          const unsubscribeUrl = `https://your-domain.com/unsubscribe?id=${sub.id}&email=${encodeURIComponent(sub.email)}`;

          return {
            from: 'Newsletter <newsletter@your-domain.com>',
            to: sub.email,
            subject: subjects[lang],
            html: newsletters[lang].replace(/\{\{unsubscribe_url\}\}/g, unsubscribeUrl),
          };
        });

        await resend.batch.send(emailPayloads);
        results.successful += batch.length;
        results.byLanguage[lang].successful += batch.length;
        console.log(`  ✅ Batch: ${batch.length} sent`);
      } catch (err) {
        results.failed += batch.length;
        results.byLanguage[lang].failed += batch.length;
        console.error(`  ❌ Batch failed: ${err.message}`);
      }

      // Rate limiting
      if (i + batchSize < langSubscribers.length) {
        await new Promise(r => setTimeout(r, 1000));
      }
    }
  }

  // Save log
  const sentDir = join(projectRoot, 'newsletters/sent', targetDate);
  mkdirSync(sentDir, { recursive: true });

  const log = {
    sentAt: new Date().toISOString(),
    newsletterDate: targetDate,
    subjects,
    totalSent: subscribers.length,
    successful: results.successful,
    failed: results.failed,
    byLanguage: results.byLanguage,
  };

  writeFileSync(join(sentDir, 'send-log.json'), JSON.stringify(log, null, 2));

  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📬 Send Complete
✅ Successful: ${results.successful}
❌ Failed: ${results.failed}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
}

// Run
const args = process.argv.slice(2);
let dateArg = args.find(a => /^\d{4}-\d{2}-\d{2}$/.test(a));
let langArg = args.includes('--lang') ? args[args.indexOf('--lang') + 1] : null;

sendNewsletter(dateArg, langArg);
```

### Newsletter HTML Template

```html
<!-- newsletters/templates/base.html -->
<!DOCTYPE html>
<html lang="{{lang}}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{subject}}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { text-align: center; padding: 20px 0; }
    .content { padding: 20px 0; }
    .footer { text-align: center; padding: 20px 0; color: #666; font-size: 12px; }
    .button { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
    .unsubscribe { color: #999; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Newsletter</h1>
    </div>

    <div class="content">
      {{content}}
    </div>

    <div class="footer">
      <p>
        <a href="{{unsubscribe_url}}" class="unsubscribe">Unsubscribe</a> |
        <a href="https://your-domain.com/preferences?id={{subscriber_id}}">Manage Preferences</a>
      </p>
      <p>&copy; 2026 Your Company. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
```

---

## 4. Unsubscription

### Unsubscribe API

```typescript
// src/pages/api/unsubscribe.ts
import type { APIRoute } from 'astro';
import { unsubscribeFromNewsletter } from '../../lib/supabase';
import { validateOrigin, csrfForbiddenResponse, SECURITY_HEADERS } from '../../lib/security';

export const prerender = false;

// POST: Actual unsubscribe (requires CSRF check)
export const POST: APIRoute = async ({ request }) => {
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  try {
    const { email, id } = await request.json();

    if (!email && !id) {
      return new Response(
        JSON.stringify({ error: 'Email or subscriber ID is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    const result = await unsubscribeFromNewsletter(email, id);

    if (result.success) {
      return new Response(
        JSON.stringify({ message: 'Successfully unsubscribed' }),
        { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    } else {
      return new Response(
        JSON.stringify({ error: result.error }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }
  } catch (error) {
    console.error('Unsubscribe API error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }
};

// GET: Redirect from email link to confirmation page (CSRF-safe)
export const GET: APIRoute = async ({ url }) => {
  const email = url.searchParams.get('email');
  const id = url.searchParams.get('id');

  if (!email && !id) {
    return new Response(null, {
      status: 302,
      headers: { Location: '/unsubscribe?error=missing' },
    });
  }

  // Redirect to confirmation page (actual unsubscribe via POST)
  return new Response(null, {
    status: 302,
    headers: {
      Location: `/unsubscribe?email=${encodeURIComponent(email || '')}&id=${id || ''}`,
    },
  });
};
```

### Preference Center API

```typescript
// src/pages/api/preferences.ts
import type { APIRoute } from 'astro';
import { updateSubscriberLanguage, getSubscriber, type SupportedLanguage } from '../../lib/supabase';
import { validateOrigin, csrfForbiddenResponse, SECURITY_HEADERS } from '../../lib/security';

export const prerender = false;

const SUPPORTED_LANGUAGES: SupportedLanguage[] = ['en', 'zh-tw', 'ja'];

// GET: Get current preferences
export const GET: APIRoute = async ({ url }) => {
  const email = url.searchParams.get('email');
  const id = url.searchParams.get('id');

  if (!email && !id) {
    return new Response(
      JSON.stringify({ error: 'Email or subscriber ID required' }),
      { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }

  const result = await getSubscriber(email || undefined, id || undefined);

  if (result.success && result.subscriber) {
    return new Response(
      JSON.stringify({
        email: result.subscriber.email,
        language: result.subscriber.preferred_language,
        subscribed: !result.subscriber.unsubscribed_at,
      }),
      { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }

  return new Response(
    JSON.stringify({ error: 'Subscriber not found' }),
    { status: 404, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
  );
};

// POST: Update preferences
export const POST: APIRoute = async ({ request }) => {
  if (!validateOrigin(request)) {
    return csrfForbiddenResponse();
  }

  try {
    const { email, id, language } = await request.json();

    if (!email && !id) {
      return new Response(
        JSON.stringify({ error: 'Email or subscriber ID required' }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    if (!SUPPORTED_LANGUAGES.includes(language)) {
      return new Response(
        JSON.stringify({ error: `Invalid language. Supported: ${SUPPORTED_LANGUAGES.join(', ')}` }),
        { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    const result = await updateSubscriberLanguage(email || '', language, id || undefined);

    if (result.success) {
      return new Response(
        JSON.stringify({ message: 'Preferences updated' }),
        { status: 200, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
      );
    }

    return new Response(
      JSON.stringify({ error: result.error }),
      { status: 400, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  } catch (error) {
    console.error('Preferences API error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json', ...SECURITY_HEADERS } }
    );
  }
};
```

---

## 5. Automation

### GitHub Actions: Auto-Generate Newsletter

```yaml
# .github/workflows/generate-newsletter.yml
name: Generate Newsletter from Release

on:
  release:
    types: [published]

jobs:
  generate:
    runs-on: ubuntu-latest
    if: github.repository == 'owner/repo'

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Generate Newsletter Articles
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          VERSION: ${{ github.event.release.tag_name }}
          RELEASE_NAME: ${{ github.event.release.name }}
          RELEASE_URL: ${{ github.event.release.html_url }}
          RELEASE_BODY_B64: ${{ github.event.release.body && toBase64(github.event.release.body) || '' }}
          NEWSLETTER_SLUG: release-${{ github.event.release.tag_name }}
        run: node scripts/generate-newsletter-from-release.js

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: "Newsletter: ${{ github.event.release.tag_name }}"
          body: "Auto-generated newsletter for release ${{ github.event.release.tag_name }}"
          branch: newsletter/${{ github.event.release.tag_name }}
          commit-message: "feat(newsletter): add ${{ github.event.release.tag_name }} newsletter"
```

### GitHub Actions: Send Newsletter

```yaml
# .github/workflows/send-newsletter.yml
name: Send Newsletter

on:
  workflow_dispatch:
    inputs:
      date:
        description: 'Newsletter date (YYYY-MM-DD)'
        required: false
      language:
        description: 'Filter by language (optional)'
        required: false

jobs:
  send:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Send Newsletter
        env:
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: |
          node scripts/send-newsletter.js \
            ${{ github.event.inputs.date && format('--date {0}', github.event.inputs.date) || '' }} \
            ${{ github.event.inputs.language && format('--lang {0}', github.event.inputs.language) || '' }}

      - name: Commit send log
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add newsletters/sent/
          git commit -m "chore: newsletter sent log" || exit 0
          git push
```

---

## Directory Structure

```
project/
├── src/
│   ├── lib/
│   │   └── supabase.ts         # Database functions
│   ├── pages/
│   │   └── api/
│   │       ├── newsletter.ts   # Subscribe API
│   │       ├── unsubscribe.ts  # Unsubscribe API
│   │       └── preferences.ts  # Preference center API
│   └── components/
│       └── NewsletterForm.tsx  # Signup form
├── scripts/
│   ├── send-newsletter.js      # Send script
│   └── generate-newsletter.js  # Generation script
├── newsletters/
│   ├── templates/              # Email templates
│   ├── drafts/                 # Generated drafts
│   │   └── 2026-01-15/
│   │       ├── newsletter-en.html
│   │       ├── newsletter-zh-tw.html
│   │       ├── newsletter-ja.html
│   │       └── subject-lines.txt
│   └── sent/                   # Send logs
│       └── 2026-01-15/
│           └── send-log.json
└── supabase/
    └── migrations/
        └── 001_newsletter.sql
```

---

## Security Checklist

- [x] Rate limiting on signup endpoint (5 req/min)
- [x] CSRF protection on all POST endpoints
- [x] RLS enabled on database tables
- [x] Service key only in backend scripts (never in client)
- [x] Email enumeration prevention (generic success response)
- [x] Unsubscribe requires confirmation page (CSRF-safe)
- [x] IP hashing for audit logs (privacy)

## GDPR Compliance

- [x] Clear consent at signup (no pre-checked boxes)
- [x] Easy one-click unsubscribe in every email
- [x] Preference center for language updates
- [x] Audit trail for all subscription actions
- [x] Data export capability (via Supabase)

---

## Resources

- [Resend Documentation](https://resend.com/docs)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [GDPR Email Marketing](https://gdpr.eu/email-marketing/)
- [Supabase + Cloudflare Integration](./supabase-cloudflare-integration.md)

---

*This example is based on the actual newsletter system of [claude-world.com](https://claude-world.com), serving subscribers in 3 languages.*
