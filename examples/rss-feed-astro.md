# RSS Feed Generation with Astro

> Complete guide to implementing RSS feeds in Astro, including multi-language support, custom stylesheets, and various feed types

## Overview

This example shows how to build a comprehensive RSS system with:
- **Multiple feed types**: Articles, newsletters, releases
- **Multi-language support**: Separate feeds per language
- **Custom styling**: XSL stylesheet for browser viewing
- **Sitemap integration**: Automatic discovery
- **Validation**: Testing and compliance

## Why RSS Matters

RSS feeds provide:
1. **User control**: Readers choose when to read, no algorithm
2. **No tracking**: Privacy-friendly content distribution
3. **Aggregation**: Users can follow multiple sources in one app
4. **Automation**: Integrate with workflows (IFTTT, Zapier, etc.)
5. **SEO benefit**: Search engines use feeds for content discovery

## Project Structure

```
src/
├── pages/
│   ├── rss.xml.ts              # Main articles feed (English)
│   ├── newsletter/
│   │   └── rss.xml.ts          # Newsletter-specific feed
│   ├── zh-tw/
│   │   └── rss.xml.ts          # Chinese articles feed
│   └── ja/
│       └── rss.xml.ts          # Japanese articles feed
├── content/
│   ├── articles/               # English articles
│   │   ├── article-1.md
│   │   ├── zh-tw/              # Chinese articles
│   │   └── ja/                 # Japanese articles
│   └── newsletters/            # Newsletter content
└── public/
    └── rss/
        └── styles.xsl          # RSS stylesheet
```

## Installation

```bash
# Install the Astro RSS package
pnpm add @astrojs/rss

# For sitemap integration
pnpm add @astrojs/sitemap
```

## Basic RSS Feed

### `src/pages/rss.xml.ts`

```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const articles = await getCollection('articles');

  // Sort articles by date (newest first)
  const sortedArticles = articles.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    // Channel metadata
    title: 'My Website - Articles',
    description: 'Latest articles and tutorials',
    site: context.site?.toString() ?? 'https://example.com',

    // Feed items
    items: sortedArticles.map((article) => ({
      title: article.data.title,
      pubDate: article.data.pubDate,
      description: article.data.description,
      link: `/articles/${article.id}/`,
      author: article.data.author,
      categories: article.data.tags,
    })),

    // Additional feed metadata
    customData: `<language>en-us</language>`,

    // Optional: Custom stylesheet for browser viewing
    stylesheet: '/rss/styles.xsl',
  });
}
```

## Multi-Language RSS Feeds

### English Feed (Default): `src/pages/rss.xml.ts`

```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const articles = await getCollection('articles');

  const sortedArticles = articles.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    title: 'My Website - Articles',
    description: 'Latest articles and tutorials',
    site: context.site?.toString() ?? 'https://example.com',
    items: sortedArticles.map((article) => ({
      title: article.data.title,
      pubDate: article.data.pubDate,
      description: article.data.description,
      link: `/articles/${article.id}/`,
      author: article.data.author,
      categories: article.data.tags,
    })),
    customData: `<language>en-us</language>`,
    stylesheet: '/rss/styles.xsl',
  });
}
```

### Chinese Feed: `src/pages/zh-tw/rss.xml.ts`

```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  // Use the Chinese articles collection
  const articles = await getCollection('articles-zh-tw');

  const sortedArticles = articles.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    title: 'My Website - Articles (Traditional Chinese)',
    description: 'Latest articles and tutorials in Traditional Chinese',
    site: context.site?.toString() ?? 'https://example.com',
    items: sortedArticles.map((article) => ({
      title: article.data.title,
      pubDate: article.data.pubDate,
      description: article.data.description,
      link: `/zh-tw/articles/${article.id}/`,
      author: article.data.author,
      categories: article.data.tags,
    })),
    customData: `<language>zh-tw</language>`,
    stylesheet: '/rss/styles.xsl',
  });
}
```

### Japanese Feed: `src/pages/ja/rss.xml.ts`

```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const articles = await getCollection('articles-ja');

  const sortedArticles = articles.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    title: 'My Website - Articles (Japanese)',
    description: 'Latest articles and tutorials in Japanese',
    site: context.site?.toString() ?? 'https://example.com',
    items: sortedArticles.map((article) => ({
      title: article.data.title,
      pubDate: article.data.pubDate,
      description: article.data.description,
      link: `/ja/articles/${article.id}/`,
      author: article.data.author,
      categories: article.data.tags,
    })),
    customData: `<language>ja-jp</language>`,
    stylesheet: '/rss/styles.xsl',
  });
}
```

## Newsletter-Specific Feed

### `src/pages/newsletter/rss.xml.ts`

```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const newsletters = await getCollection('newsletters');

  const sortedNewsletters = newsletters.sort(
    (a, b) => new Date(b.data.pubDate).getTime() - new Date(a.data.pubDate).getTime()
  );

  return rss({
    title: 'My Website Weekly - Newsletter',
    description: 'Weekly tips, release notes, and community insights.',
    site: context.site?.toString() ?? 'https://example.com',
    items: sortedNewsletters.map((newsletter) => ({
      title: newsletter.data.title,
      pubDate: new Date(newsletter.data.pubDate),
      description: newsletter.data.description,
      link: `/newsletter/${newsletter.id}/`,
      author: newsletter.data.author,
      // Custom categories based on content type
      categories: newsletter.data.highlight
        ? [newsletter.data.highlight.type || 'newsletter']
        : ['newsletter'],
    })),
    customData: `<language>en-us</language>`,
    stylesheet: '/rss/styles.xsl',
  });
}
```

## Custom RSS Stylesheet

Create a visual stylesheet for browsers viewing the RSS feed directly.

### `public/rss/styles.xsl`

```xml
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
      <head>
        <title><xsl:value-of select="/rss/channel/title"/> - RSS Feed</title>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style type="text/css">
          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            line-height: 1.6;
          }
          .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1rem;
          }
          .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
          }
          .rss-icon {
            width: 48px;
            height: 48px;
            margin-bottom: 1rem;
          }
          h1 {
            font-size: 1.75rem;
            color: #ff6b35;
            margin-bottom: 0.5rem;
          }
          .description {
            color: #a0a0a0;
            font-size: 0.95rem;
          }
          .subscribe-box {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: #fff;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
          }
          .subscribe-box h2 {
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
          }
          .subscribe-box p {
            font-size: 0.9rem;
            opacity: 0.9;
          }
          .subscribe-box code {
            display: block;
            background: rgba(0, 0, 0, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            margin-top: 0.75rem;
            font-size: 0.85rem;
            word-break: break-all;
          }
          .items-header {
            font-size: 1.1rem;
            color: #888;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          }
          .item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
          }
          .item:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 107, 53, 0.3);
          }
          .item-title {
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
          }
          .item-title a {
            color: #fff;
            text-decoration: none;
          }
          .item-title a:hover {
            color: #ff6b35;
          }
          .item-meta {
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 0.5rem;
          }
          .item-description {
            color: #b0b0b0;
            font-size: 0.95rem;
          }
          .category {
            display: inline-block;
            background: rgba(255, 107, 53, 0.2);
            color: #ff6b35;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-left: 0.5rem;
          }
          .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.85rem;
          }
          .footer a {
            color: #ff6b35;
            text-decoration: none;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <svg class="rss-icon" viewBox="0 0 24 24" fill="#ff6b35">
              <path d="M6.18 15.64a2.18 2.18 0 0 1 2.18 2.18C8.36 19 7.38 20 6.18 20C5 20 4 19 4 17.82a2.18 2.18 0 0 1 2.18-2.18M4 4.44A15.56 15.56 0 0 1 19.56 20h-2.83A12.73 12.73 0 0 0 4 7.27V4.44m0 5.66a9.9 9.9 0 0 1 9.9 9.9h-2.83A7.07 7.07 0 0 0 4 12.93V10.1Z"/>
            </svg>
            <h1><xsl:value-of select="/rss/channel/title"/></h1>
            <p class="description"><xsl:value-of select="/rss/channel/description"/></p>
          </div>

          <div class="subscribe-box">
            <h2>Subscribe to this RSS Feed</h2>
            <p>Copy this URL and add it to your favorite RSS reader:</p>
            <code><xsl:value-of select="/rss/channel/link"/>rss.xml</code>
          </div>

          <div class="items-header">Recent Posts</div>

          <xsl:for-each select="/rss/channel/item">
            <div class="item">
              <div class="item-title">
                <a>
                  <xsl:attribute name="href">
                    <xsl:value-of select="link"/>
                  </xsl:attribute>
                  <xsl:value-of select="title"/>
                </a>
                <xsl:if test="category">
                  <span class="category"><xsl:value-of select="category"/></span>
                </xsl:if>
              </div>
              <div class="item-meta">
                <xsl:value-of select="pubDate"/>
              </div>
              <div class="item-description">
                <xsl:value-of select="description"/>
              </div>
            </div>
          </xsl:for-each>

          <div class="footer">
            <p>
              <a href="/">Back to Website</a>
            </p>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
```

## Content Collection Schema

### `src/content.config.ts`

```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const articleSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  author: z.string().optional(),
  tags: z.array(z.string()).optional(),
  image: z.string().optional(),
});

const newsletterSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  author: z.string().optional(),
  highlight: z.object({
    type: z.string().optional(),
  }).optional(),
});

// English articles (default)
const articles = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/articles' }),
  schema: articleSchema,
});

// Chinese articles
const articlesZhTw = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/articles/zh-tw' }),
  schema: articleSchema,
});

// Japanese articles
const articlesJa = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/articles/ja' }),
  schema: articleSchema,
});

// Newsletters
const newsletters = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/newsletters' }),
  schema: newsletterSchema,
});

export const collections = {
  articles,
  'articles-zh-tw': articlesZhTw,
  'articles-ja': articlesJa,
  newsletters,
};
```

## Sitemap Integration

### `astro.config.mjs`

```javascript
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh-tw', 'ja'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/api/'),
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
      i18n: {
        defaultLocale: 'en',
        locales: {
          en: 'en-US',
          'zh-tw': 'zh-TW',
          ja: 'ja-JP',
        },
      },
    }),
  ],
});
```

## RSS Discovery Tags

Add RSS auto-discovery to your layout so browsers and feed readers can find your feeds.

### `src/layouts/Layout.astro`

```astro
---
interface Props {
  title: string;
  description?: string;
  locale?: string;
}

const { title, description, locale = 'en' } = Astro.props;

// Determine RSS feed URL based on locale
function getRssFeed(loc: string): string {
  if (loc === 'zh-tw') return '/zh-tw/rss.xml';
  if (loc === 'ja') return '/ja/rss.xml';
  return '/rss.xml';
}
---

<!DOCTYPE html>
<html lang={locale}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {description && <meta name="description" content={description} />}

  <!-- RSS Auto-discovery -->
  <link
    rel="alternate"
    type="application/rss+xml"
    title={`${title} - RSS Feed`}
    href={getRssFeed(locale)}
  />

  <!-- Newsletter RSS (optional) -->
  <link
    rel="alternate"
    type="application/rss+xml"
    title="Newsletter RSS"
    href="/newsletter/rss.xml"
  />
</head>
<body>
  <slot />
</body>
</html>
```

## Advanced: Full Content in Feed

Include the full article content in your RSS feed for readers who prefer reading in their feed reader.

### `src/pages/rss-full.xml.ts`

```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';
import sanitizeHtml from 'sanitize-html';
import MarkdownIt from 'markdown-it';

const parser = new MarkdownIt();

export async function GET(context: APIContext) {
  const articles = await getCollection('articles');

  const sortedArticles = articles.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    title: 'My Website - Full Articles',
    description: 'Full content RSS feed',
    site: context.site?.toString() ?? 'https://example.com',
    items: sortedArticles.map((article) => ({
      title: article.data.title,
      pubDate: article.data.pubDate,
      description: article.data.description,
      link: `/articles/${article.id}/`,
      // Include full HTML content
      content: sanitizeHtml(parser.render(article.body || ''), {
        allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img']),
      }),
    })),
    customData: `<language>en-us</language>`,
  });
}
```

Install dependencies for full content:

```bash
pnpm add sanitize-html markdown-it
pnpm add -D @types/sanitize-html @types/markdown-it
```

## Advanced: Releases Feed

Track software releases with a dedicated feed.

### `src/pages/releases/rss.xml.ts`

```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const releases = await getCollection('releases');

  const sortedReleases = releases.sort(
    (a, b) => b.data.releaseDate.valueOf() - a.data.releaseDate.valueOf()
  );

  return rss({
    title: 'My App - Release Notes',
    description: 'Latest releases and changelogs',
    site: context.site?.toString() ?? 'https://example.com',
    items: sortedReleases.map((release) => ({
      title: `v${release.data.version} - ${release.data.title}`,
      pubDate: release.data.releaseDate,
      description: release.data.summary,
      link: `/releases/${release.id}/`,
      categories: [
        release.data.type, // 'major', 'minor', 'patch'
        ...(release.data.breaking ? ['breaking-changes'] : []),
      ],
    })),
    customData: `
      <language>en-us</language>
      <docs>https://example.com/releases</docs>
    `,
    stylesheet: '/rss/styles.xsl',
  });
}
```

## Testing and Validation

### 1. Local Testing

```bash
# Build and preview
pnpm build
pnpm preview

# Check feed in browser
open http://localhost:4321/rss.xml
```

### 2. Feed Validators

| Validator | URL |
|-----------|-----|
| W3C Feed Validator | https://validator.w3.org/feed/ |
| Feed Validator | https://www.feedvalidator.org/ |
| RSS Advisory Board | https://rss.scripting.com/validator/ |

### 3. Common Validation Errors

| Error | Solution |
|-------|----------|
| Invalid date format | Use `Date` object, not string |
| Missing required fields | Include `title`, `link`, `description` |
| Invalid characters | Sanitize HTML content |
| Missing site URL | Set `site` in `astro.config.mjs` |

### 4. Test with Feed Readers

Popular RSS readers for testing:
- **Feedly** - Web-based, most popular
- **NetNewsWire** - macOS/iOS, free
- **Inoreader** - Web-based, advanced features
- **Reeder** - macOS/iOS, premium

## RSS Feed URLs Summary

| Feed | URL | Purpose |
|------|-----|---------|
| Articles (EN) | `/rss.xml` | Main English articles |
| Articles (ZH-TW) | `/zh-tw/rss.xml` | Chinese articles |
| Articles (JA) | `/ja/rss.xml` | Japanese articles |
| Newsletter | `/newsletter/rss.xml` | Weekly newsletter |
| Releases | `/releases/rss.xml` | Software releases |
| Full Content | `/rss-full.xml` | Articles with full content |

## Best Practices

### 1. Keep Feeds Focused

One feed per content type:
- Articles feed for blog posts
- Newsletter feed for newsletters
- Releases feed for changelogs

### 2. Use Consistent Dates

Always use `Date` objects:

```typescript
// Good
pubDate: article.data.pubDate,  // Already a Date from schema

// Also good
pubDate: new Date(article.data.pubDate),

// Bad - string dates may cause issues
pubDate: '2024-01-15',
```

### 3. Sanitize Content

Always sanitize HTML in feed content:

```typescript
import sanitizeHtml from 'sanitize-html';

content: sanitizeHtml(htmlContent, {
  allowedTags: ['p', 'a', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre'],
  allowedAttributes: {
    a: ['href'],
  },
});
```

### 4. Add Categories

Categories improve feed reader organization:

```typescript
categories: article.data.tags || ['general'],
```

### 5. Set Reasonable Limits

For large sites, limit feed items:

```typescript
const recentArticles = sortedArticles.slice(0, 20);  // Last 20 articles
```

## Troubleshooting

### Feed Not Updating

1. Check that `site` is set in `astro.config.mjs`
2. Verify `pubDate` is a valid `Date` object
3. Rebuild the site after content changes

### XSL Stylesheet Not Loading

1. Ensure `styles.xsl` is in `public/rss/`
2. Check the stylesheet path in feed options
3. Some browsers block XSL - test in a feed reader

### Characters Breaking Feed

1. Use `sanitize-html` for content
2. Escape special XML characters
3. Validate with W3C Feed Validator

## Related Resources

- [Astro RSS Documentation](https://docs.astro.build/en/guides/rss/)
- [Multi-Language Website Example](./multi-language-astro.md)
- [RSS 2.0 Specification](https://www.rssboard.org/rss-specification)
- [Atom Feed Specification](https://www.rfc-editor.org/rfc/rfc4287)

---

*RSS feeds remain one of the most user-friendly ways to distribute content. They respect user privacy, work offline, and integrate with countless tools and workflows.*
