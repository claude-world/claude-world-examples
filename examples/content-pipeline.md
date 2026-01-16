# Content Pipeline Architecture

> Build an automated content pipeline that monitors sources, generates multi-language articles with Claude API, and publishes to social media.

This guide covers the content pipeline architecture used by [claude-world.com](https://claude-world.com), featuring automated blog monitoring, AI-powered content generation, and social media distribution.

---

## Overview

| Component | Purpose | Technology |
|-----------|---------|------------|
| Source Monitoring | Track blog updates, releases | GitHub Actions cron |
| Content Processing | Analyze and extract information | Claude API |
| Article Generation | Multi-language content creation | Claude API |
| Social Distribution | Auto-post to X, Threads | Platform APIs |
| Issue Tracking | Development opportunities | GitHub Issues |

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Content Pipeline Flow                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Sources    │    │   Process    │    │   Generate   │    │   Publish    │
│              │───▶│              │───▶│              │───▶│              │
│  - Blogs     │    │  - Fetch     │    │  - Articles  │    │  - Website   │
│  - Releases  │    │  - Analyze   │    │  - Multi-lang│    │  - Social    │
│  - RSS       │    │  - Filter    │    │  - AI-gen    │    │  - Discord   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                  GitHub Actions                      │
                    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
                    │  │ check-blog  │  │  generate   │  │ post-social │  │
                    │  └─────────────┘  └─────────────┘  └─────────────┘  │
                    └─────────────────────────────────────────────────────┘
                                           │
                                           ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                    Storage                           │
                    │  - processed-articles.json (tracking)                │
                    │  - src/content/articles/ (generated content)         │
                    │  - social-logs/posts.json (social posting log)       │
                    └─────────────────────────────────────────────────────┘
```

---

## 1. Content Source Monitoring

### GitHub Actions Workflow

The monitoring workflow runs on a schedule to check for new content.

```yaml
# .github/workflows/blog-monitor.yml
name: Anthropic Blog Monitor

on:
  # Check every 2 hours
  schedule:
    - cron: '0 */2 * * *'

  # Allow manual trigger
  workflow_dispatch:
    inputs:
      blog_url:
        description: 'Specific blog URL to process (leave empty to check for new)'
        required: false
        type: string
      force_process:
        description: 'Force process even if already tracked'
        required: false
        default: false
        type: boolean

env:
  BLOG_URL: https://claude.com/blog
  TRACKING_FILE: 00-upstream-tracking/claude-blog/processed-articles.json
  CLAUDE_MODEL: claude-sonnet-4-20250514

jobs:
  check-blog:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    outputs:
      has_new: ${{ steps.check.outputs.has_new }}
      articles_json: ${{ steps.check.outputs.articles_json }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Check for new blog articles
        id: check
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SPECIFIC_URL: ${{ github.event.inputs.blog_url }}
          FORCE_PROCESS: ${{ github.event.inputs.force_process }}
        run: |
          # Check script runs here (see next section)
          node /tmp/check-blog.js > /tmp/result.json

          HAS_NEW=$(cat /tmp/result.json | jq -r '.has_new')
          echo "has_new=$HAS_NEW" >> $GITHUB_OUTPUT

          if [ "$HAS_NEW" == "true" ]; then
            ARTICLES=$(cat /tmp/result.json | jq -c '.articles')
            echo "articles_json=$(echo "$ARTICLES" | base64 -w 0)" >> $GITHUB_OUTPUT
          fi
```

### Tracking File Structure

Track processed articles to avoid duplicate processing.

```json
{
  "articles": [
    "claude-code-best-practices",
    "introducing-claude-4",
    "model-context-protocol"
  ],
  "lastCheck": "2026-01-16T10:30:00Z"
}
```

---

## 2. Content Fetching and Analysis

### Blog Link Extraction (No AI)

Use regex to extract blog links - no API cost for initial filtering.

```javascript
// Extract blog links from HTML using regex (no AI needed)
function extractBlogLinks(html) {
  const links = [];
  const patterns = [
    /href=["'](?:https?:\/\/claude\.com)?\/blog\/([a-z0-9-]+)["']/gi,
    /href=["'](?:https?:\/\/www\.anthropic\.com)?\/research\/([a-z0-9-]+)["']/gi
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(html)) !== null) {
      const slug = match[1];
      if (slug && !links.includes(slug) && slug !== 'blog' && slug.length > 3) {
        links.push(slug);
      }
    }
  }
  return links;
}
```

### Content Analysis with Claude

Analyze article content to extract structured information.

```javascript
async function analyzeArticle(articleHtml, slug) {
  const prompt = `
    Analyze this blog article HTML and extract detailed information.

    HTML Content (truncated):
    ${articleHtml.substring(0, 15000)}

    Return JSON only (no markdown, no explanation):
    {
      "slug": "${slug}",
      "title": "Exact title from the article",
      "date": "YYYY-MM-DD",
      "summary": "2-3 sentence summary",
      "relevance": "high/medium/low based on Claude Code relevance",
      "key_topics": ["topic1", "topic2"],
      "key_features": ["feature1", "feature2"],
      "claude_world_angle": "How this relates to our site / methodology",
      "dev_opportunities": [
        {
          "type": "example|skill|template|docs",
          "title": "Short title for the dev task",
          "description": "What to implement and why valuable",
          "target_repo": "tools-repo or examples-repo",
          "priority": "high/medium/low"
        }
      ]
    }

    Only include high-value opportunities. Return empty array if none.
  `;

  return await callClaude(prompt);
}
```

### Claude API Helper with Retry

```javascript
// Retry wrapper with exponential backoff
async function withRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === maxRetries - 1) throw e;
      const delay = 1000 * Math.pow(2, i);
      console.error(`Retry ${i + 1}/${maxRetries} after ${delay}ms...`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}

function callClaudeOnce(prompt) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: process.env.CLAUDE_MODEL || 'claude-sonnet-4-20250514',
      max_tokens: 4000,
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
        try {
          const response = JSON.parse(data);
          if (response.error) reject(new Error(response.error.message));
          else resolve(response.content[0].text);
        } catch (e) {
          reject(e);
        }
      });
    });

    req.setTimeout(30000, () => {
      req.destroy(new Error('Request timeout'));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function callClaude(prompt) {
  return withRetry(() => callClaudeOnce(prompt));
}

// Extract JSON from Claude response
function extractJson(text) {
  const jsonMatch = text.match(/\[[\s\S]*\]|\{[\s\S]*\}/);
  if (jsonMatch) {
    return JSON.parse(jsonMatch[0]);
  }
  return JSON.parse(text);
}
```

---

## 3. Multi-Language Article Generation

### Article Generation Workflow

```yaml
# Continuation of blog-monitor.yml
generate-articles:
  needs: check-blog
  runs-on: ubuntu-latest
  if: needs.check-blog.outputs.has_new == 'true'
  permissions:
    contents: write

  steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'

    - name: Generate website articles
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        ARTICLES_B64: ${{ needs.check-blog.outputs.articles_json }}
      run: |
        ARTICLES=$(echo "$ARTICLES_B64" | base64 -d)
        ARTICLES="$ARTICLES" node /tmp/generate-articles.js

    - name: Commit and push articles
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"

        git add src/content/articles/
        git add 00-upstream-tracking/

        if git diff --staged --quiet; then
          echo "No changes to commit"
        else
          git commit -m "content: add blog articles from source"
          git pull --rebase origin main
          git push
          echo "Articles committed and pushed"
        fi
```

### Multi-Language Generation Script

```javascript
// scripts/generate-articles.js
const LANGUAGES = ['zh-TW', 'en', 'ja'];

const LANG_CONFIG = {
  'zh-TW': {
    instructions: 'Use Traditional Chinese. Professional but friendly tone.',
    sections: {
      announcement: '## 官方發布了什麼？',
      meaning: '## 這代表什麼？',
      impact: '## 對開發者的影響',
      perspective: '## 我們的觀點',
      nextSteps: '## 下一步'
    }
  },
  'en': {
    instructions: 'Write in English. Professional but approachable tone.',
    sections: {
      announcement: '## What Did They Announce?',
      meaning: '## What Does This Mean?',
      impact: '## Impact on Developers',
      perspective: '## Our Perspective',
      nextSteps: '## Next Steps'
    }
  },
  'ja': {
    instructions: 'Write in Japanese. Professional but friendly tone.',
    sections: {
      announcement: '## 公式発表の内容',
      meaning: '## これが意味すること',
      impact: '## 開発者への影響',
      perspective: '## 私たちの見解',
      nextSteps: '## 次のステップ'
    }
  }
};

async function generateArticle(article, lang) {
  const config = LANG_CONFIG[lang];

  const prompt = `
    Generate a blog article based on this source:

    Title: ${article.title}
    URL: https://source.com/blog/${article.slug}
    Summary: ${article.summary}
    Key Topics: ${article.key_topics?.join(', ')}
    Key Features: ${article.key_features?.join(', ')}
    Our Angle: ${article.claude_world_angle}

    ${config.instructions}

    IMPORTANT: This is NOT a translation. Add unique value:
    - Connect to practical use cases
    - Provide insights for developers
    - Add our perspective on implications

    Return the article in this exact format (no code blocks, just the content):

    ---
    title: "[Your title - NOT a direct translation]"
    description: "[SEO description, ~150 chars]"
    pubDate: "${article.date}"
    author: "Your Site"
    tags: ${JSON.stringify(article.key_topics || ['tech'])}
    heroImage: "/images/blog/default.png"
    lang: "${lang}"
    ---

    ${config.sections.announcement}

    [2-3 paragraphs summarizing the official announcement]

    ${config.sections.meaning}

    [2-3 paragraphs of deeper analysis]

    ${config.sections.impact}

    [Practical implications, what developers should do]

    ${config.sections.perspective}

    [Connect to your methodology, tools, insights]

    ${config.sections.nextSteps}

    [What readers can do, links to resources]

    ---

    *Original: [${article.title}](https://source.com/blog/${article.slug})*
  `;

  return await callClaude(prompt);
}

async function main() {
  const articles = JSON.parse(process.env.ARTICLES || '[]');

  for (const article of articles) {
    console.log(`\nProcessing: ${article.title}`);

    for (const lang of LANGUAGES) {
      console.log(`  Generating ${lang}...`);

      const content = await generateArticle(article, lang);

      // Each language has its own content directory
      const langDir = lang === 'en' ? 'articles' : `articles-${lang.toLowerCase()}`;
      const filePath = path.join('src/content', langDir, `${article.slug}.md`);

      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, content);

      console.log(`  Written: ${filePath}`);
    }
  }

  // Update tracking file
  updateTrackingFile(articles);
}
```

---

## 4. Content Storage and Organization

### Directory Structure

```
project/
├── src/
│   └── content/
│       ├── articles/              # English articles
│       │   └── new-feature.md
│       ├── articles-zh-tw/        # Traditional Chinese
│       │   └── new-feature.md
│       └── articles-ja/           # Japanese
│           └── new-feature.md
├── 00-upstream-tracking/
│   └── claude-blog/
│       └── processed-articles.json
├── content-pipeline/
│   └── social-logs/
│       └── posts.json
└── scripts/
    ├── generate-newsletter-from-release.js
    ├── post-to-social.js
    ├── x-post.js
    └── threads-post.js
```

### Astro Content Collections

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content';

const articleSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  author: z.string().optional(),
  tags: z.array(z.string()).optional(),
  heroImage: z.string().optional(),
  lang: z.enum(['en', 'zh-tw', 'ja']).optional(),
  version: z.string().optional(),
  releaseUrl: z.string().optional(),
  type: z.enum(['article', 'release', 'tutorial']).optional(),
});

// Define collection for each language
export const collections = {
  articles: defineCollection({ type: 'content', schema: articleSchema }),
  'articles-zh-tw': defineCollection({ type: 'content', schema: articleSchema }),
  'articles-ja': defineCollection({ type: 'content', schema: articleSchema }),
};
```

---

## 5. Social Media Distribution

### Social Posting Workflow

```yaml
# Continuation of blog-monitor.yml
post-social:
  needs: [check-blog, generate-articles]
  runs-on: ubuntu-latest
  if: needs.check-blog.outputs.has_new == 'true'
  permissions:
    issues: write
    contents: read

  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        ref: main  # Get latest with new articles

    - name: Post to X
      env:
        X_API_KEY: ${{ secrets.X_API_KEY }}
        X_API_SECRET: ${{ secrets.X_API_SECRET }}
        X_ACCESS_TOKEN: ${{ secrets.X_ACCESS_TOKEN }}
        X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        ARTICLES_B64: ${{ needs.check-blog.outputs.articles_json }}
      run: |
        if [ -z "$X_API_KEY" ]; then
          echo "X API not configured, skipping"
          exit 0
        fi

        echo "$ARTICLES_B64" | base64 -d > /tmp/articles.json
        node /tmp/generate-social.js > /tmp/posts.json
        node /tmp/post-x.js
```

### X (Twitter) Posting Script

```javascript
// scripts/x-post.js
const OAuth = require('oauth-1.0a');
const crypto = require('crypto');
const https = require('https');

const oauth = OAuth({
  consumer: { key: process.env.X_API_KEY, secret: process.env.X_API_SECRET },
  signature_method: 'HMAC-SHA1',
  hash_function(base_string, key) {
    return crypto.createHmac('sha1', key).update(base_string).digest('base64');
  }
});

const token = { key: process.env.X_ACCESS_TOKEN, secret: process.env.X_ACCESS_SECRET };

function postTweet(text, replyToId = null) {
  return new Promise((resolve, reject) => {
    const url = 'https://api.twitter.com/2/tweets';
    const body = { text };
    if (replyToId) body.reply = { in_reply_to_tweet_id: replyToId };

    const request_data = { url, method: 'POST' };
    const headers = oauth.toHeader(oauth.authorize(request_data, token));
    headers['Content-Type'] = 'application/json';

    const req = https.request(url, { method: 'POST', headers }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(data));
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });
    req.on('error', reject);
    req.write(JSON.stringify(body));
    req.end();
  });
}

// Thread support: post main tweet, then replies
async function postThread(posts) {
  let lastId = null;

  for (const { text, isReply } of posts) {
    const replyTo = isReply ? lastId : null;
    const result = await postTweet(text, replyTo);
    lastId = result.data.id;
    console.log(`Posted: https://twitter.com/i/status/${lastId}`);

    // Rate limit delay
    await new Promise(r => setTimeout(r, 2000));
  }
}
```

### Threads Posting Script

```javascript
// scripts/threads-post.js
const https = require('https');

const userId = process.env.THREADS_USER_ID;
const accessToken = process.env.THREADS_ACCESS_TOKEN;

function postThreads(text, replyToId = null) {
  return new Promise((resolve, reject) => {
    let createUrl = `https://graph.threads.net/v1.0/${userId}/threads?media_type=TEXT&text=${encodeURIComponent(text)}&access_token=${accessToken}`;

    if (replyToId) {
      createUrl += `&reply_to_id=${replyToId}`;
    }

    // Step 1: Create container
    https.request(createUrl, { method: 'POST' }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const container = JSON.parse(data);
          if (!container.id) {
            reject(new Error(`Create failed: ${data}`));
            return;
          }

          // Step 2: Wait for processing then publish
          setTimeout(() => {
            const publishUrl = `https://graph.threads.net/v1.0/${userId}/threads_publish?creation_id=${container.id}&access_token=${accessToken}`;

            https.request(publishUrl, { method: 'POST' }, (res2) => {
              let data2 = '';
              res2.on('data', chunk => data2 += chunk);
              res2.on('end', () => {
                try {
                  const result = JSON.parse(data2);
                  if (result.id) {
                    resolve(result);
                  } else {
                    reject(new Error(`Publish failed: ${data2}`));
                  }
                } catch (e) {
                  reject(new Error(`Parse error: ${data2}`));
                }
              });
            }).on('error', reject).end();
          }, 3000);  // Wait for Threads processing
        } catch (e) {
          reject(new Error(`Parse error: ${data}`));
        }
      });
    }).on('error', reject).end();
  });
}
```

### Social Post Generation

```javascript
// Generate platform-specific posts
async function generateSocialPosts(article) {
  const prompt = `
    Generate social media posts for this article:
    Title: ${article.title}
    Summary: ${article.summary}
    Article URL: https://your-site.com/articles/${article.slug}
    Original: https://source.com/blog/${article.slug}

    Return JSON only (no markdown, no explanation):
    {
      "x_en": "English tweet. Emoji + headline + key insight + article link. Under 280 chars. URL last.",
      "threads_zh": "Traditional Chinese post. Emoji + title + insight + link. Under 450 chars. Link last."
    }
  `;

  const result = await callClaude(prompt);
  return extractJson(result);
}
```

---

## 6. Development Issue Generation

### Auto-Create GitHub Issues

When articles are processed, automatically create development issues for opportunities identified by Claude.

```yaml
# In blog-monitor.yml
- name: Create development issues for opportunities
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ARTICLES_B64: ${{ needs.check-blog.outputs.articles_json }}
  run: |
    ARTICLES=$(echo "$ARTICLES_B64" | base64 -d)

    echo "$ARTICLES" | jq -c '.[]' | while read -r article; do
      ARTICLE_TITLE=$(echo "$article" | jq -r '.title')
      OPPORTUNITIES=$(echo "$article" | jq -c '.dev_opportunities // []')

      if [ "$OPPORTUNITIES" == "[]" ]; then
        continue
      fi

      echo "$OPPORTUNITIES" | jq -c '.[]' | while read -r opp; do
        OPP_TYPE=$(echo "$opp" | jq -r '.type // "unknown"')
        OPP_TITLE=$(echo "$opp" | jq -r '.title // "Untitled"')
        OPP_DESC=$(echo "$opp" | jq -r '.description // ""')
        OPP_REPO=$(echo "$opp" | jq -r '.target_repo // "examples"')
        OPP_PRIORITY=$(echo "$opp" | jq -r '.priority // "medium"')

        # Determine labels
        LABELS="enhancement,from-blog"
        if [ "$OPP_PRIORITY" == "high" ]; then
          LABELS="$LABELS,priority-high"
        fi

        gh issue create \
          --title "[$OPP_REPO] $OPP_TITLE" \
          --body "## Development Opportunity

    **Source**: $ARTICLE_TITLE
    **Type**: \`$OPP_TYPE\`
    **Target Repo**: $OPP_REPO
    **Priority**: $OPP_PRIORITY

    ## Description

    $OPP_DESC

    ## Acceptance Criteria

    - [ ] Implementation complete
    - [ ] Tests added (if applicable)
    - [ ] Documentation updated"

        sleep 1  # Rate limiting
      done
    done
```

---

## 7. Release-Based Content Generation

### Newsletter from Releases

```javascript
// scripts/generate-newsletter-from-release.js
const VERSION = process.env.VERSION;
const RELEASE_NAME = process.env.RELEASE_NAME;
const RELEASE_URL = process.env.RELEASE_URL;
const RELEASE_BODY = Buffer.from(process.env.RELEASE_BODY_B64 || '', 'base64').toString('utf-8');
const NEWSLETTER_SLUG = process.env.NEWSLETTER_SLUG;
const TODAY = new Date().toISOString().split('T')[0];

const prompt = `You are a technical writer creating newsletter articles.

Release Info:
- Version: ${VERSION}
- Name: ${RELEASE_NAME}
- URL: ${RELEASE_URL}
- Release Notes:
${RELEASE_BODY}

Generate newsletter articles in 3 languages. Output JSON with this structure:
{
  "en": {
    "title": "Product ${VERSION} Release Notes",
    "description": "Short meta description for SEO, 1-2 sentences",
    "content": "Full markdown article content. Include:
    - Introduction paragraph
    - ## What's New section with feature details
    - ## How to Update section
    - ## Links section with release URL"
  },
  "zh-tw": {
    "title": "Product ${VERSION} 發布說明",
    "description": "SEO 簡短描述，1-2 句",
    "content": "完整的繁體中文 Markdown 文章內容..."
  },
  "ja": {
    "title": "Product ${VERSION} リリースノート",
    "description": "SEO用の短い説明、1-2文",
    "content": "完全な日本語Markdownコンテンツ..."
  }
}

IMPORTANT: Output ONLY valid JSON, no markdown code blocks.`;

// Generate and save articles for each language
const articles = await callClaude(prompt);
const parsed = JSON.parse(articles);

for (const [lang, article] of Object.entries(parsed)) {
  const frontmatter = [
    '---',
    `title: "${article.title}"`,
    `description: "${article.description}"`,
    `pubDate: "${TODAY}"`,
    `version: "${VERSION}"`,
    `releaseUrl: "${RELEASE_URL}"`,
    'type: "release"',
    '---',
    '',
    article.content
  ].join('\n');

  const langDir = lang === 'en' ? 'articles' : `articles-${lang}`;
  const targetDir = path.join('src/content', langDir);
  fs.mkdirSync(targetDir, { recursive: true });

  const filePath = path.join(targetDir, `${NEWSLETTER_SLUG}.md`);
  fs.writeFileSync(filePath, frontmatter);
  console.log('Created:', filePath);
}
```

### Release Trigger Workflow

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

---

## 8. Complete GitHub Actions Workflow

### Full Blog Monitor Workflow

```yaml
# .github/workflows/blog-monitor.yml
name: Blog Monitor

on:
  schedule:
    - cron: '0 */2 * * *'
  workflow_dispatch:
    inputs:
      blog_url:
        description: 'Specific blog URL to process'
        required: false
        type: string
      force_process:
        description: 'Force process even if already tracked'
        required: false
        default: false
        type: boolean

env:
  TRACKING_FILE: tracking/processed-articles.json
  CLAUDE_MODEL: claude-sonnet-4-20250514

jobs:
  check-blog:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    outputs:
      has_new: ${{ steps.check.outputs.has_new }}
      articles_json: ${{ steps.check.outputs.articles_json }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Check for new articles
        id: check
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: node scripts/check-blog.js

  generate-articles:
    needs: check-blog
    runs-on: ubuntu-latest
    if: needs.check-blog.outputs.has_new == 'true'
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Generate articles
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ARTICLES_B64: ${{ needs.check-blog.outputs.articles_json }}
        run: node scripts/generate-articles.js
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .
          git diff --staged --quiet || git commit -m "content: add new articles"
          git push

  post-social:
    needs: [check-blog, generate-articles]
    runs-on: ubuntu-latest
    if: needs.check-blog.outputs.has_new == 'true'
    permissions:
      issues: write
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Post to X
        env:
          X_API_KEY: ${{ secrets.X_API_KEY }}
          X_API_SECRET: ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN: ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ARTICLES_B64: ${{ needs.check-blog.outputs.articles_json }}
        run: |
          [ -z "$X_API_KEY" ] && exit 0
          node scripts/post-to-x.js
      - name: Post to Threads
        env:
          THREADS_USER_ID: ${{ secrets.THREADS_USER_ID }}
          THREADS_ACCESS_TOKEN: ${{ secrets.THREADS_ACCESS_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ARTICLES_B64: ${{ needs.check-blog.outputs.articles_json }}
        run: |
          [ -z "$THREADS_ACCESS_TOKEN" ] && exit 0
          node scripts/post-to-threads.js
      - name: Create dev issues
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ARTICLES_B64: ${{ needs.check-blog.outputs.articles_json }}
        run: node scripts/create-dev-issues.js
```

---

## Required Secrets

Configure these secrets in your GitHub repository:

| Secret | Required | Description |
|--------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key for content generation |
| `X_API_KEY` | No | X (Twitter) API key |
| `X_API_SECRET` | No | X API secret |
| `X_ACCESS_TOKEN` | No | X access token |
| `X_ACCESS_SECRET` | No | X access token secret |
| `THREADS_USER_ID` | No | Threads user ID |
| `THREADS_ACCESS_TOKEN` | No | Threads access token |

---

## Cost Optimization Tips

1. **Use regex for initial filtering** - Extract links without API calls
2. **Filter by relevance** - Only generate content for high/medium relevance articles
3. **Batch processing** - Process multiple articles in single API calls when possible
4. **Cache tracking** - Avoid reprocessing already-handled content
5. **Selective generation** - Only generate for languages with subscribers

---

## Monitoring and Debugging

### Logging

```javascript
// Log all API calls
console.log(`[${new Date().toISOString()}] API call: ${prompt.substring(0, 100)}...`);

// Log results
console.log(`[${new Date().toISOString()}] Generated ${lang} article for ${slug}`);

// Log errors with context
console.error(`[${new Date().toISOString()}] Error processing ${slug}:`, error.message);
```

### Health Checks

```javascript
// Check API connectivity
async function healthCheck() {
  try {
    await callClaude('Say "OK" only.');
    console.log('Claude API: OK');
  } catch (e) {
    console.error('Claude API: FAILED -', e.message);
  }
}
```

---

## Resources

- [Claude API Documentation](https://docs.anthropic.com/claude/reference)
- [X API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Threads API Documentation](https://developers.facebook.com/docs/threads)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Newsletter System Architecture](./newsletter-system.md)

---

*This example is based on the actual content pipeline of [claude-world.com](https://claude-world.com), processing content across 3 languages with automated social distribution.*
