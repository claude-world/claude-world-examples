# Social Media Automation (X/Twitter and Threads)

> Build an automated social posting system using X API v2, Threads API, and Claude for content generation.

This guide covers building a complete social media automation pipeline that:
1. Generates platform-optimized posts using Claude API
2. Posts to X (Twitter) and Threads
3. Handles multi-language content
4. Automates via GitHub Actions

---

## Overview

| Component | Purpose | Technology |
|-----------|---------|------------|
| Content Generation | Platform-optimized posts | Claude API |
| X/Twitter Posting | 280-character posts | X API v2 (OAuth 1.0a) |
| Threads Posting | 500-character posts | Threads API (Graph API) |
| Scheduling | Automated posting | GitHub Actions |
| Logging | Track posted content | JSON logs |

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions Workflow                      │
│                   (Manual trigger / Scheduled)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Job 1: Generate Posts                                           │
│  ├── Read article metadata                                       │
│  ├── Call Claude API for platform-specific content               │
│  └── Output: x_post, threads_post, hashtags                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  Job 2: Post to X       │     │  Job 3: Post to Threads │
│  ├── OAuth 1.0a auth    │     │  ├── Create container   │
│  ├── POST /2/tweets     │     │  ├── Publish thread     │
│  └── Log result         │     │  └── Log result         │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 1. Platform Setup

### X (Twitter) API v2 Setup

1. **Create Developer Account**: Go to [developer.twitter.com](https://developer.twitter.com)
2. **Create Project and App**: Get "Free" or "Basic" tier access
3. **Configure OAuth 1.0a**: Enable "Read and Write" permissions
4. **Generate Keys**: You need 4 credentials

```
X_API_KEY           → API Key (Consumer Key)
X_API_SECRET        → API Secret (Consumer Secret)
X_ACCESS_TOKEN      → Access Token
X_ACCESS_SECRET     → Access Token Secret
```

**Important**: For posting tweets, you need OAuth 1.0a User Context (not App-only).

### Threads API Setup

1. **Create Meta Developer Account**: Go to [developers.facebook.com](https://developers.facebook.com)
2. **Create App**: Select "Consumer" app type
3. **Add Threads Product**: In your app dashboard
4. **Get Permissions**: Request `threads_basic` and `threads_content_publish`
5. **Generate Long-Lived Token**: Exchange short-lived token

```
THREADS_USER_ID       → Your Threads account ID (numeric)
THREADS_ACCESS_TOKEN  → Long-lived access token (60 days)
```

**Token Refresh**: Threads tokens expire. Set up a refresh workflow:

```bash
# Refresh token before expiry
curl -X GET \
  "https://graph.threads.net/refresh_access_token?grant_type=th_refresh_token&access_token=${THREADS_ACCESS_TOKEN}"
```

---

## 2. Platform Character Limits and Formatting

| Platform | Text Limit | URL Handling | Hashtag Best Practice |
|----------|------------|--------------|----------------------|
| X/Twitter | 280 chars | URLs count as 23 chars | 2-3 hashtags max |
| Threads | 500 chars | Full URL counted | 3-5 hashtags, more casual |

### Platform-Specific Formatting

```javascript
// Character limits
const LIMITS = {
  x: {
    maxChars: 280,
    urlChars: 23,  // All URLs count as 23 chars
    hashtagLimit: 3,
  },
  threads: {
    maxChars: 500,
    urlChars: 'actual',  // Full URL length counted
    hashtagLimit: 5,
  },
};

// Formatting rules
const FORMATS = {
  x: {
    // Concise, punchy
    style: 'brief',
    cta: 'short',
    example: 'Claude Code 2.2.0 is out!\n\nMajor improvements to agent mode.\n\nRead more: https://...\n\n#ClaudeCode #AI',
  },
  threads: {
    // Conversational, can be longer
    style: 'conversational',
    cta: 'descriptive',
    example: 'Excited to share the latest Claude Code update!\n\nVersion 2.2.0 brings significant improvements to agent mode, making complex tasks even smoother.\n\nCheck out the full details: https://...\n\n#ClaudeCode #AITools #DeveloperTools',
  },
};
```

---

## 3. Post Generation with Claude API

### Node.js Script

```javascript
// scripts/generate-social-posts.js
import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';

const anthropic = new Anthropic();

const PLATFORM_SPECS = {
  x: {
    maxChars: 280,
    urlReserved: 23,
    style: 'concise and impactful',
    hashtagCount: '2-3',
  },
  threads: {
    maxChars: 500,
    urlReserved: 0,
    style: 'conversational and engaging',
    hashtagCount: '3-5',
  },
};

const LANGUAGE_INSTRUCTIONS = {
  en: 'Write in English.',
  'zh-tw': 'Write in Traditional Chinese (Taiwan). Use natural Taiwanese expressions.',
  ja: 'Write in Japanese. Use appropriate keigo for social media.',
};

/**
 * Generate platform-optimized social posts using Claude
 */
async function generateSocialPosts(content, options = {}) {
  const {
    language = 'en',
    url = '',
    platforms = ['x', 'threads'],
    tone = 'professional',
  } = options;

  const urlLength = url.length || 30;

  // Build platform-specific instructions
  const platformInstructions = platforms.map(p => {
    const spec = PLATFORM_SPECS[p];
    const availableChars = p === 'x'
      ? spec.maxChars - spec.urlReserved - 5  // 5 for newlines
      : spec.maxChars - urlLength - 5;

    return `
## ${p.toUpperCase()} Post
- Maximum ${availableChars} characters (excluding URL)
- Style: ${spec.style}
- Include ${spec.hashtagCount} relevant hashtags
- ${p === 'x' ? 'Be punchy and direct' : 'Can be more descriptive and friendly'}
`;
  }).join('\n');

  const prompt = `You are a social media expert. Generate platform-optimized posts for the following content.

${LANGUAGE_INSTRUCTIONS[language]}

Content to promote:
"""
${content}
"""

${url ? `Link to include: ${url}` : 'No link to include.'}

Tone: ${tone}

${platformInstructions}

Return ONLY valid JSON in this exact format:
{
  "x": "Tweet text here (no URL, I will add it)",
  "threads": "Threads post text here (no URL, I will add it)",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
}`;

  try {
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }],
    });

    const text = response.content[0].text;
    const jsonMatch = text.match(/\{[\s\S]*\}/);

    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }

    return JSON.parse(jsonMatch[0]);
  } catch (error) {
    console.error('Claude API error:', error.message);
    throw error;
  }
}

/**
 * Format final post with URL and hashtags
 */
function formatPost(baseText, url, hashtags, platform) {
  const spec = PLATFORM_SPECS[platform];
  const hashtagText = hashtags
    .slice(0, platform === 'x' ? 3 : 5)
    .map(h => h.startsWith('#') ? h : `#${h}`)
    .join(' ');

  let post = baseText;

  // Add URL
  if (url) {
    post += `\n\n${url}`;
  }

  // Add hashtags
  if (hashtagText) {
    post += `\n\n${hashtagText}`;
  }

  // Validate length
  const maxChars = spec.maxChars;
  const effectiveLength = platform === 'x'
    ? post.replace(url, '').length + spec.urlReserved
    : post.length;

  if (effectiveLength > maxChars) {
    console.warn(`Warning: ${platform} post exceeds limit (${effectiveLength}/${maxChars})`);
  }

  return post;
}

// CLI usage
async function main() {
  const args = process.argv.slice(2);
  const contentArg = args.find(a => a.startsWith('--content='));
  const urlArg = args.find(a => a.startsWith('--url='));
  const langArg = args.find(a => a.startsWith('--lang='));

  if (!contentArg) {
    console.error('Usage: node generate-social-posts.js --content="Your content" [--url="..."] [--lang="en"]');
    process.exit(1);
  }

  const content = contentArg.split('=').slice(1).join('=');
  const url = urlArg ? urlArg.split('=').slice(1).join('=') : '';
  const language = langArg ? langArg.split('=')[1] : 'en';

  console.log('Generating social posts...\n');

  const generated = await generateSocialPosts(content, { language, url });

  console.log('Generated posts:\n');

  for (const platform of ['x', 'threads']) {
    const formatted = formatPost(generated[platform], url, generated.hashtags, platform);
    console.log(`--- ${platform.toUpperCase()} (${formatted.length} chars) ---`);
    console.log(formatted);
    console.log('');
  }

  // Save to file
  const output = {
    generated,
    formatted: {
      x: formatPost(generated.x, url, generated.hashtags, 'x'),
      threads: formatPost(generated.threads, url, generated.hashtags, 'threads'),
    },
    metadata: {
      language,
      url,
      generatedAt: new Date().toISOString(),
    },
  };

  fs.writeFileSync('/tmp/social-posts.json', JSON.stringify(output, null, 2));
  console.log('Saved to /tmp/social-posts.json');
}

main().catch(console.error);
```

---

## 4. Posting Scripts

### Post to X (Twitter)

```javascript
// scripts/post-to-x.js
import { TwitterApi } from 'twitter-api-v2';

/**
 * Post to X using Twitter API v2
 */
async function postToX(content) {
  // Validate credentials
  const requiredEnvVars = ['X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 'X_ACCESS_SECRET'];
  const missing = requiredEnvVars.filter(v => !process.env[v]);

  if (missing.length > 0) {
    throw new Error(`Missing environment variables: ${missing.join(', ')}`);
  }

  // Initialize client with OAuth 1.0a User Context
  const client = new TwitterApi({
    appKey: process.env.X_API_KEY,
    appSecret: process.env.X_API_SECRET,
    accessToken: process.env.X_ACCESS_TOKEN,
    accessSecret: process.env.X_ACCESS_SECRET,
  });

  try {
    // Post tweet
    const tweet = await client.v2.tweet(content);

    console.log('Posted to X successfully');
    console.log('Tweet ID:', tweet.data.id);
    console.log('URL:', `https://x.com/i/status/${tweet.data.id}`);

    return {
      success: true,
      id: tweet.data.id,
      url: `https://x.com/i/status/${tweet.data.id}`,
    };
  } catch (error) {
    console.error('X posting failed:', error.message);

    // Handle rate limiting
    if (error.code === 429) {
      const resetTime = error.rateLimit?.reset;
      console.error(`Rate limited. Reset at: ${new Date(resetTime * 1000).toISOString()}`);
    }

    return {
      success: false,
      error: error.message,
      code: error.code,
    };
  }
}

// CLI usage
const content = process.argv[2] || process.env.POST_CONTENT;
if (content) {
  postToX(content).then(result => {
    process.exit(result.success ? 0 : 1);
  });
}

export { postToX };
```

### Post to Threads

```javascript
// scripts/post-to-threads.js

/**
 * Post to Threads using Graph API
 * Threads API requires a two-step process: create container, then publish
 */
async function postToThreads(content) {
  const userId = process.env.THREADS_USER_ID;
  const accessToken = process.env.THREADS_ACCESS_TOKEN;

  if (!userId || !accessToken) {
    throw new Error('Missing THREADS_USER_ID or THREADS_ACCESS_TOKEN');
  }

  const baseUrl = 'https://graph.threads.net/v1.0';

  try {
    // Step 1: Create media container
    console.log('Creating Threads container...');

    const createResponse = await fetch(`${baseUrl}/${userId}/threads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        media_type: 'TEXT',
        text: content,
        access_token: accessToken,
      }),
    });

    const createData = await createResponse.json();

    if (createData.error) {
      throw new Error(createData.error.message || 'Failed to create container');
    }

    const containerId = createData.id;
    console.log('Container created:', containerId);

    // Wait for container to be ready (recommended by Meta)
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Step 2: Publish the container
    console.log('Publishing...');

    const publishResponse = await fetch(`${baseUrl}/${userId}/threads_publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        creation_id: containerId,
        access_token: accessToken,
      }),
    });

    const publishData = await publishResponse.json();

    if (publishData.error) {
      throw new Error(publishData.error.message || 'Failed to publish');
    }

    console.log('Posted to Threads successfully');
    console.log('Thread ID:', publishData.id);

    return {
      success: true,
      id: publishData.id,
    };
  } catch (error) {
    console.error('Threads posting failed:', error.message);

    return {
      success: false,
      error: error.message,
    };
  }
}

// CLI usage
const content = process.argv[2] || process.env.POST_CONTENT;
if (content) {
  postToThreads(content).then(result => {
    process.exit(result.success ? 0 : 1);
  });
}

export { postToThreads };
```

---

## 5. Combined Posting Script

```javascript
// scripts/post-to-social.js
#!/usr/bin/env node

/**
 * Social Media Auto-Posting Script
 *
 * Usage:
 *   node scripts/post-to-social.js --article="slug" --lang="en"
 *   node scripts/post-to-social.js --article="slug" --lang="zh-tw" --platforms="x,threads"
 *   node scripts/post-to-social.js --article="slug" --dry-run="true"
 */

import { TwitterApi } from 'twitter-api-v2';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const SITE_URL = 'https://your-domain.com';
const MAX_TWEET_LENGTH = 280;
const MAX_THREADS_LENGTH = 500;

// Language-specific CTAs
const CTA_TEXT = {
  en: 'Read more',
  'zh-tw': '閱讀更多',
  ja: '続きを読む',
};

// Parse command line arguments
function parseArgs() {
  const args = {};
  process.argv.slice(2).forEach(arg => {
    const [key, ...valueParts] = arg.replace('--', '').split('=');
    args[key] = valueParts.join('=');
  });
  return args;
}

// Read article metadata from markdown frontmatter
function getArticleMetadata(slug, lang = 'en') {
  const basePath = path.join(__dirname, '../src/content/articles');
  const filePath = lang === 'en'
    ? path.join(basePath, `${slug}.md`)
    : path.join(basePath, lang, `${slug}.md`);

  if (!fs.existsSync(filePath)) {
    throw new Error(`Article not found: ${filePath}`);
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);

  if (!frontmatterMatch) {
    throw new Error('No frontmatter found in article');
  }

  const metadata = {};
  frontmatterMatch[1].split('\n').forEach(line => {
    const match = line.match(/^(\w+):\s*(.+)$/);
    if (match) {
      let value = match[2].trim().replace(/^["']|["']$/g, '');
      if (value.startsWith('[') && value.endsWith(']')) {
        value = value.slice(1, -1).split(',').map(v => v.trim().replace(/"/g, ''));
      }
      metadata[match[1]] = value;
    }
  });

  return metadata;
}

// Generate post content for each platform
function generatePostContent(metadata, lang, platform) {
  const { title, description, tags } = metadata;
  const url = `${SITE_URL}${lang === 'en' ? '' : `/${lang}`}/articles/${metadata.slug}`;

  const maxLength = platform === 'x' ? MAX_TWEET_LENGTH : MAX_THREADS_LENGTH;

  // Format hashtags
  const hashtags = (tags || [])
    .slice(0, platform === 'x' ? 3 : 5)
    .map(tag => `#${tag.replace(/\s+/g, '')}`)
    .join(' ');

  const cta = CTA_TEXT[lang] || CTA_TEXT.en;

  let post = '';

  if (platform === 'x') {
    // Twitter: Concise format
    post = `${title}\n\n${cta}: ${url}\n\n${hashtags}`;

    // Truncate if needed (account for 23-char URL)
    if (post.length > maxLength) {
      const availableForTitle = maxLength - 23 - hashtags.length - cta.length - 10;
      post = `${title.slice(0, availableForTitle)}...\n\n${cta}: ${url}\n\n${hashtags}`;
    }
  } else if (platform === 'threads') {
    // Threads: Can be more descriptive
    post = `${title}\n\n${description}\n\n${cta}: ${url}\n\n${hashtags}`;

    if (post.length > maxLength) {
      const availableForDesc = maxLength - title.length - url.length - hashtags.length - 30;
      post = `${title}\n\n${description.slice(0, availableForDesc)}...\n\n${cta}: ${url}\n\n${hashtags}`;
    }
  }

  return post.trim();
}

// Post to X (Twitter)
async function postToX(content) {
  const client = new TwitterApi({
    appKey: process.env.X_API_KEY,
    appSecret: process.env.X_API_SECRET,
    accessToken: process.env.X_ACCESS_TOKEN,
    accessSecret: process.env.X_ACCESS_SECRET,
  });

  try {
    const tweet = await client.v2.tweet(content);
    console.log('Posted to X:', tweet.data.id);
    return { success: true, id: tweet.data.id };
  } catch (error) {
    console.error('X posting failed:', error.message);
    return { success: false, error: error.message };
  }
}

// Post to Threads
async function postToThreads(content) {
  const userId = process.env.THREADS_USER_ID;
  const accessToken = process.env.THREADS_ACCESS_TOKEN;

  if (!userId || !accessToken) {
    return { success: false, error: 'Missing Threads credentials' };
  }

  try {
    // Create container
    const createResponse = await fetch(
      `https://graph.threads.net/v1.0/${userId}/threads`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_type: 'TEXT',
          text: content,
          access_token: accessToken,
        }),
      }
    );

    const createData = await createResponse.json();
    if (createData.error) throw new Error(createData.error.message);

    await new Promise(r => setTimeout(r, 2000));

    // Publish
    const publishResponse = await fetch(
      `https://graph.threads.net/v1.0/${userId}/threads_publish`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          creation_id: createData.id,
          access_token: accessToken,
        }),
      }
    );

    const publishData = await publishResponse.json();
    if (publishData.error) throw new Error(publishData.error.message);

    console.log('Posted to Threads:', publishData.id);
    return { success: true, id: publishData.id };
  } catch (error) {
    console.error('Threads posting failed:', error.message);
    return { success: false, error: error.message };
  }
}

// Track posted articles
function hasBeenPosted(slug, lang, platform) {
  const logFile = path.join(__dirname, '../logs/social-posts.json');
  if (!fs.existsSync(logFile)) return false;

  const logs = JSON.parse(fs.readFileSync(logFile, 'utf-8'));
  return logs.some(log =>
    log.article === slug &&
    log.lang === lang &&
    log.platform === platform &&
    log.success
  );
}

function logResult(slug, lang, platform, result) {
  const logDir = path.join(__dirname, '../logs');
  if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });

  const logFile = path.join(logDir, 'social-posts.json');
  const logs = fs.existsSync(logFile)
    ? JSON.parse(fs.readFileSync(logFile, 'utf-8'))
    : [];

  logs.push({
    timestamp: new Date().toISOString(),
    article: slug,
    lang,
    platform,
    success: result.success,
    postId: result.id || null,
    error: result.error || null,
  });

  fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
}

// Main
async function main() {
  const args = parseArgs();

  if (!args.article) {
    console.error('Usage: node post-to-social.js --article="slug" [--lang="en"] [--platforms="x,threads"]');
    process.exit(1);
  }

  const slug = args.article;
  const lang = args.lang || 'en';
  const platforms = (args.platforms || 'x,threads').split(',').map(p => p.trim());
  const dryRun = args['dry-run'] === 'true';

  console.log(`\nSocial Media Posting`);
  console.log(`  Article: ${slug}`);
  console.log(`  Language: ${lang}`);
  console.log(`  Platforms: ${platforms.join(', ')}`);
  console.log(`  Dry Run: ${dryRun}\n`);

  // Get article metadata
  let metadata;
  try {
    metadata = getArticleMetadata(slug, lang);
    metadata.slug = slug;
    console.log(`Found article: ${metadata.title}\n`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }

  const results = {};

  for (const platform of platforms) {
    if (hasBeenPosted(slug, lang, platform)) {
      console.log(`Skipping ${platform}: Already posted`);
      continue;
    }

    const content = generatePostContent(metadata, lang, platform);

    console.log(`--- ${platform.toUpperCase()} (${content.length} chars) ---`);
    console.log(content);
    console.log('---\n');

    if (dryRun) {
      console.log('Dry run: Skipping actual post');
      results[platform] = { success: true, dryRun: true };
      continue;
    }

    let result;
    if (platform === 'x') {
      result = await postToX(content);
    } else if (platform === 'threads') {
      result = await postToThreads(content);
    }

    results[platform] = result;
    logResult(slug, lang, platform, result);
  }

  console.log('\nSummary:');
  for (const [platform, result] of Object.entries(results)) {
    const status = result.success ? 'OK' : 'FAILED';
    console.log(`  ${platform}: ${status} ${result.id || result.error || ''}`);
  }
}

main().catch(console.error);
```

---

## 6. GitHub Actions Workflow

### Manual/Scheduled Posting

```yaml
# .github/workflows/social-post.yml
name: Post to Social Media

on:
  workflow_dispatch:
    inputs:
      article:
        description: 'Article slug (e.g., claude-code-220-release)'
        required: true
        type: string
      lang:
        description: 'Language'
        required: true
        type: choice
        options:
          - en
          - zh-tw
          - ja
        default: en
      platforms:
        description: 'Platforms (comma-separated)'
        required: true
        type: string
        default: 'x,threads'
      dry_run:
        description: 'Dry run (no actual posting)'
        required: false
        type: boolean
        default: false

jobs:
  post-to-social:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Post to Social Media
        env:
          # X (Twitter) credentials
          X_API_KEY: ${{ secrets.X_API_KEY }}
          X_API_SECRET: ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN: ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          # Threads credentials
          THREADS_USER_ID: ${{ secrets.THREADS_USER_ID }}
          THREADS_ACCESS_TOKEN: ${{ secrets.THREADS_ACCESS_TOKEN }}
        run: |
          node scripts/post-to-social.js \
            --article="${{ inputs.article }}" \
            --lang="${{ inputs.lang }}" \
            --platforms="${{ inputs.platforms }}" \
            --dry-run="${{ inputs.dry_run }}"

      - name: Upload posting logs
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: social-posting-logs
          path: logs/
          retention-days: 30
```

### AI-Generated Posts with Claude

```yaml
# .github/workflows/ai-social-post.yml
name: AI-Generated Social Posts

on:
  workflow_dispatch:
    inputs:
      content:
        description: 'Content to promote (or article slug)'
        required: true
        type: string
      platforms:
        description: 'Platforms (x,threads)'
        required: true
        type: string
        default: 'x,threads'
      language:
        description: 'Language'
        required: true
        type: choice
        options:
          - en
          - zh-tw
          - ja
        default: en
      dry_run:
        description: 'Dry run'
        required: false
        type: boolean
        default: false

jobs:
  generate-posts:
    runs-on: ubuntu-latest
    outputs:
      posts_json: ${{ steps.generate.outputs.posts_json }}

    steps:
      - name: Generate platform-specific posts with Claude
        id: generate
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          CONTENT: ${{ github.event.inputs.content }}
          LANGUAGE: ${{ github.event.inputs.language }}
        run: |
          cat > /tmp/generate.js << 'EOF'
          const https = require('https');

          async function callClaude(prompt) {
            return new Promise((resolve, reject) => {
              const body = JSON.stringify({
                model: 'claude-sonnet-4-20250514',
                max_tokens: 1000,
                messages: [{ role: 'user', content: prompt }]
              });

              const req = https.request({
                hostname: 'api.anthropic.com',
                path: '/v1/messages',
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'x-api-key': process.env.ANTHROPIC_API_KEY,
                  'anthropic-version': '2023-06-01'
                }
              }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                  const response = JSON.parse(data);
                  if (response.error) reject(new Error(response.error.message));
                  else resolve(response.content[0].text);
                });
              });
              req.on('error', reject);
              req.write(body);
              req.end();
            });
          }

          async function main() {
            const content = process.env.CONTENT;
            const lang = process.env.LANGUAGE;

            const langInstructions = {
              en: 'Write in English.',
              'zh-tw': 'Write in Traditional Chinese (Taiwan).',
              ja: 'Write in Japanese.'
            };

            const prompt = `
              Generate social media posts for this content:
              "${content}"

              ${langInstructions[lang]}

              Return JSON only:
              {
                "x": "Tweet under 280 chars. Include relevant hashtags.",
                "threads": "Threads post under 500 chars. More conversational tone."
              }
            `;

            const result = await callClaude(prompt);
            const posts = JSON.parse(result.match(/\{[\s\S]*\}/)[0]);
            console.log(JSON.stringify(posts));
          }

          main().catch(err => {
            console.error('Error:', err.message);
            process.exit(1);
          });
          EOF

          node /tmp/generate.js > /tmp/posts.json
          echo "Generated posts:"
          cat /tmp/posts.json

          echo "posts_json=$(cat /tmp/posts.json | base64 -w 0)" >> $GITHUB_OUTPUT

  post-to-x:
    needs: generate-posts
    runs-on: ubuntu-latest
    if: contains(github.event.inputs.platforms, 'x')

    steps:
      - name: Post to X
        env:
          X_API_KEY: ${{ secrets.X_API_KEY }}
          X_API_SECRET: ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN: ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          POSTS_B64: ${{ needs.generate-posts.outputs.posts_json }}
          DRY_RUN: ${{ github.event.inputs.dry_run }}
        run: |
          if [ -z "$X_API_KEY" ]; then
            echo "X API not configured, skipping"
            exit 0
          fi

          POSTS=$(echo "$POSTS_B64" | base64 -d)
          TWEET=$(echo "$POSTS" | jq -r '.x')

          echo "Tweet: $TWEET"

          if [ "$DRY_RUN" == "true" ]; then
            echo "DRY RUN - Would post: $TWEET"
            exit 0
          fi

          npm init -y && npm install twitter-api-v2

          cat > /tmp/post-x.js << 'EOF'
          const { TwitterApi } = require('twitter-api-v2');

          const client = new TwitterApi({
            appKey: process.env.X_API_KEY,
            appSecret: process.env.X_API_SECRET,
            accessToken: process.env.X_ACCESS_TOKEN,
            accessSecret: process.env.X_ACCESS_SECRET,
          });

          async function post() {
            const tweet = process.env.TWEET;
            const result = await client.v2.tweet(tweet);
            console.log('Posted:', result.data.id);
          }

          post().catch(err => {
            console.error('Failed:', err.message);
            process.exit(1);
          });
          EOF

          TWEET="$TWEET" node /tmp/post-x.js

  post-to-threads:
    needs: generate-posts
    runs-on: ubuntu-latest
    if: contains(github.event.inputs.platforms, 'threads')

    steps:
      - name: Post to Threads
        env:
          THREADS_USER_ID: ${{ secrets.THREADS_USER_ID }}
          THREADS_ACCESS_TOKEN: ${{ secrets.THREADS_ACCESS_TOKEN }}
          POSTS_B64: ${{ needs.generate-posts.outputs.posts_json }}
          DRY_RUN: ${{ github.event.inputs.dry_run }}
        run: |
          if [ -z "$THREADS_ACCESS_TOKEN" ]; then
            echo "Threads API not configured, skipping"
            exit 0
          fi

          POSTS=$(echo "$POSTS_B64" | base64 -d)
          TEXT=$(echo "$POSTS" | jq -r '.threads')

          echo "Threads post: $TEXT"

          if [ "$DRY_RUN" == "true" ]; then
            echo "DRY RUN - Would post: $TEXT"
            exit 0
          fi

          # URL encode the text
          ENCODED_TEXT=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$TEXT'''))")

          # Create container
          CONTAINER=$(curl -s -X POST \
            "https://graph.threads.net/v1.0/${THREADS_USER_ID}/threads?media_type=TEXT&text=${ENCODED_TEXT}&access_token=${THREADS_ACCESS_TOKEN}")

          CONTAINER_ID=$(echo "$CONTAINER" | jq -r '.id')

          if [ "$CONTAINER_ID" == "null" ]; then
            echo "Failed to create container: $CONTAINER"
            exit 1
          fi

          echo "Container created: $CONTAINER_ID"
          sleep 2

          # Publish
          RESULT=$(curl -s -X POST \
            "https://graph.threads.net/v1.0/${THREADS_USER_ID}/threads_publish?creation_id=${CONTAINER_ID}&access_token=${THREADS_ACCESS_TOKEN}")

          echo "Published: $RESULT"
```

---

## 7. Rate Limiting and Error Handling

### Rate Limits

| Platform | Rate Limit | Window |
|----------|------------|--------|
| X Free Tier | 50 tweets/day | 24 hours |
| X Basic | 100 tweets/day | 24 hours |
| Threads | 250 posts/day | 24 hours |

### Error Handling Patterns

```javascript
// Retry with exponential backoff
async function postWithRetry(postFn, content, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await postFn(content);
    } catch (error) {
      const isRateLimit = error.code === 429 || error.message.includes('rate');
      const isTemporary = error.code >= 500 || isRateLimit;

      if (!isTemporary || attempt === maxRetries) {
        throw error;
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt - 1) * 1000;
      console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}

// Handle platform-specific errors
function handleError(error, platform) {
  const errorMap = {
    x: {
      187: 'Duplicate tweet',
      403: 'Authentication failed',
      429: 'Rate limit exceeded',
    },
    threads: {
      'OAuthException': 'Token expired - refresh needed',
      'Invalid parameter': 'Check content format',
    },
  };

  console.error(`[${platform}] Error:`, error.message);

  // Log for debugging
  return {
    success: false,
    error: error.message,
    code: error.code,
    timestamp: new Date().toISOString(),
  };
}
```

---

## 8. Multi-Language Posts

### Language-Aware Content Generation

```javascript
const LANGUAGE_CONFIG = {
  en: {
    label: 'English',
    cta: 'Read more',
    hashtags: ['ClaudeCode', 'AI', 'DevTools'],
    tone: 'professional',
  },
  'zh-tw': {
    label: 'Traditional Chinese',
    cta: '閱讀更多',
    hashtags: ['ClaudeCode', 'AI工具', '開發者'],
    tone: 'friendly',
  },
  ja: {
    label: 'Japanese',
    cta: '続きを読む',
    hashtags: ['ClaudeCode', 'AI', '開発ツール'],
    tone: 'polite',
  },
};

// Generate posts for all languages
async function generateMultilingualPosts(content, url) {
  const results = {};

  for (const [lang, config] of Object.entries(LANGUAGE_CONFIG)) {
    console.log(`Generating ${config.label} posts...`);

    const posts = await generateSocialPosts(content, {
      language: lang,
      url,
      tone: config.tone,
    });

    results[lang] = posts;
  }

  return results;
}
```

---

## 9. Secrets Configuration

Add these secrets to your GitHub repository (Settings > Secrets and variables > Actions):

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key for content generation |
| `X_API_KEY` | X/Twitter Consumer Key |
| `X_API_SECRET` | X/Twitter Consumer Secret |
| `X_ACCESS_TOKEN` | X/Twitter Access Token |
| `X_ACCESS_SECRET` | X/Twitter Access Token Secret |
| `THREADS_USER_ID` | Threads numeric user ID |
| `THREADS_ACCESS_TOKEN` | Threads long-lived access token |

---

## 10. Directory Structure

```
project/
├── scripts/
│   ├── generate-social-posts.js   # Claude-powered generation
│   ├── post-to-x.js               # X/Twitter posting
│   ├── post-to-threads.js         # Threads posting
│   └── post-to-social.js          # Combined script
├── logs/
│   └── social-posts.json          # Posting history
├── .github/
│   └── workflows/
│       ├── social-post.yml        # Manual posting
│       └── ai-social-post.yml     # AI-generated posts
└── src/
    └── content/
        └── articles/              # Article source files
```

---

## Testing

### Dry Run

```bash
# Test without posting
node scripts/post-to-social.js --article="my-article" --dry-run="true"
```

### Manual Trigger

```bash
# Via GitHub CLI
gh workflow run social-post.yml \
  -f article="claude-code-220" \
  -f lang="en" \
  -f platforms="x,threads" \
  -f dry_run="true"
```

### View Logs

```bash
gh run list --workflow=social-post.yml
gh run view <run-id> --log
```

---

## Cost Estimation

| Component | Cost |
|-----------|------|
| X Free Tier | Free (50 tweets/day) |
| Threads API | Free |
| Claude API (~3 calls/post) | ~$0.03/post |
| GitHub Actions | Free (2,000 min/month) |
| **Monthly (30 posts)** | **~$1.00** |

---

## Related Resources

- [X API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Threads API Documentation](https://developers.facebook.com/docs/threads)
- [Claude API Documentation](https://docs.anthropic.com/en/api)
- [GitHub Actions Automation](./github-actions-automation.md)

---

*This example demonstrates automating social media presence across X and Threads with AI-powered content generation.*
