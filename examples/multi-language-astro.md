# Multi-Language Website with Astro

> Complete guide to building a multi-language website with Astro, including i18n routing, content collections, and automatic language detection

## Overview

This example shows how to build a website supporting:
- **3 languages**: English (default), Traditional Chinese, Japanese
- **URL structure**: `/` (en), `/zh-tw/`, `/ja/`
- **Auto language detection**: Based on browser `Accept-Language`
- **Content collections**: Separate articles per language
- **SEO**: Proper hreflang tags

## Project Structure

```
src/
├── content/
│   └── articles/
│       ├── my-article.md           # English (default)
│       ├── zh-tw/
│       │   └── my-article.md       # Traditional Chinese
│       └── ja/
│           └── my-article.md       # Japanese
├── i18n/
│   ├── en.json
│   ├── zh-tw.json
│   └── ja.json
├── pages/
│   ├── index.astro                 # English homepage
│   ├── articles/
│   │   ├── index.astro
│   │   └── [slug].astro
│   ├── zh-tw/
│   │   ├── index.astro
│   │   └── articles/
│   │       ├── index.astro
│   │       └── [slug].astro
│   └── ja/
│       ├── index.astro
│       └── articles/
│           ├── index.astro
│           └── [slug].astro
├── middleware.ts                   # Language detection
└── components/
    └── LanguageSwitcher.astro
```

## Configuration

### `astro.config.mjs`

```javascript
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://your-site.com',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh-tw', 'ja'],
    routing: {
      prefixDefaultLocale: false,  // /about instead of /en/about
    },
  },
  integrations: [
    sitemap({
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

## Content Collections

### `src/content.config.ts`

```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const articleSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  author: z.string().optional(),
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

export const collections = {
  articles,
  'articles-zh-tw': articlesZhTw,
  'articles-ja': articlesJa,
};
```

## i18n Translations

### `src/i18n/en.json`

```json
{
  "site": {
    "title": "My Website",
    "description": "A multi-language website"
  },
  "nav": {
    "home": "Home",
    "articles": "Articles",
    "about": "About"
  },
  "common": {
    "readMore": "Read more",
    "publishedOn": "Published on"
  }
}
```

### `src/i18n/zh-tw.json`

```json
{
  "site": {
    "title": "我的網站",
    "description": "一個多語言網站"
  },
  "nav": {
    "home": "首頁",
    "articles": "文章",
    "about": "關於"
  },
  "common": {
    "readMore": "閱讀更多",
    "publishedOn": "發布於"
  }
}
```

### `src/i18n/ja.json`

```json
{
  "site": {
    "title": "私のウェブサイト",
    "description": "多言語ウェブサイト"
  },
  "nav": {
    "home": "ホーム",
    "articles": "記事",
    "about": "概要"
  },
  "common": {
    "readMore": "続きを読む",
    "publishedOn": "公開日"
  }
}
```

### `src/i18n/index.ts`

```typescript
import en from './en.json';
import zhTw from './zh-tw.json';
import ja from './ja.json';

export const translations = {
  en,
  'zh-tw': zhTw,
  ja,
} as const;

export type Locale = keyof typeof translations;

export function getLocaleFromPath(pathname: string): Locale {
  if (pathname.startsWith('/zh-tw')) return 'zh-tw';
  if (pathname.startsWith('/ja')) return 'ja';
  return 'en';
}

export function t(locale: Locale, key: string): string {
  const keys = key.split('.');
  let value: any = translations[locale];

  for (const k of keys) {
    value = value?.[k];
  }

  return value || key;
}

export function getLocalePath(locale: Locale, path: string): string {
  if (locale === 'en') return path;
  return `/${locale}${path}`;
}
```

## Language Detection Middleware

### `src/middleware.ts`

```typescript
import { defineMiddleware } from 'astro:middleware';

const SUPPORTED_LOCALES = ['en', 'zh-tw', 'ja'] as const;
const DEFAULT_LOCALE = 'en';
const LANG_COOKIE = 'preferred_lang';
const SKIP_PATHS = ['/api/', '/_', '/favicon', '/robots.txt', '/sitemap'];

function getBestLocale(acceptLanguage: string | null): string {
  if (!acceptLanguage) return DEFAULT_LOCALE;

  const languages = acceptLanguage
    .split(',')
    .map(lang => {
      const [code, qValue] = lang.trim().split(';q=');
      return {
        code: code.toLowerCase(),
        quality: qValue ? parseFloat(qValue) : 1.0,
      };
    })
    .sort((a, b) => b.quality - a.quality);

  for (const { code } of languages) {
    // Exact match
    if (SUPPORTED_LOCALES.includes(code as any)) {
      return code;
    }
    // Language family match
    if (code === 'zh' || code.startsWith('zh-')) return 'zh-tw';
    if (code === 'ja' || code.startsWith('ja-')) return 'ja';
    if (code === 'en' || code.startsWith('en-')) return 'en';
  }

  return DEFAULT_LOCALE;
}

function getLocaleFromPath(pathname: string): string | null {
  if (pathname.startsWith('/zh-tw')) return 'zh-tw';
  if (pathname.startsWith('/ja')) return 'ja';
  return null;  // Root paths are English
}

export const onRequest = defineMiddleware((context, next) => {
  const { pathname } = context.url;
  const { cookies, request } = context;

  // Skip non-page routes
  if (SKIP_PATHS.some(path => pathname.startsWith(path))) {
    return next();
  }

  // Already on localized path
  const currentLocale = getLocaleFromPath(pathname);
  if (currentLocale !== null) {
    return next();
  }

  // Check stored preference
  const preferredLang = cookies.get(LANG_COOKIE)?.value;
  if (preferredLang && preferredLang !== 'en') {
    const newUrl = new URL(`/${preferredLang}${pathname}`, context.url);
    return context.redirect(newUrl.toString(), 302);
  }

  // Detect from Accept-Language header
  if (!preferredLang) {
    const acceptLanguage = request.headers?.get?.('Accept-Language') ?? null;
    const detectedLocale = getBestLocale(acceptLanguage);

    // Store preference
    cookies.set(LANG_COOKIE, detectedLocale, {
      path: '/',
      maxAge: 60 * 60 * 24 * 365,
      httpOnly: false,
      sameSite: 'lax',
    });

    // Redirect if not English
    if (detectedLocale !== 'en') {
      const newUrl = new URL(`/${detectedLocale}${pathname}`, context.url);
      return context.redirect(newUrl.toString(), 302);
    }
  }

  return next();
});
```

## Page Templates

### `src/pages/index.astro` (English)

```astro
---
import Layout from '../layouts/Layout.astro';
import { t } from '../i18n';

const locale = 'en';
---

<Layout title={t(locale, 'site.title')} locale={locale}>
  <h1>{t(locale, 'nav.home')}</h1>
  <!-- Content -->
</Layout>
```

### `src/pages/zh-tw/index.astro` (Chinese)

```astro
---
import Layout from '../../layouts/Layout.astro';
import { t } from '../../i18n';

const locale = 'zh-tw';
---

<Layout title={t(locale, 'site.title')} locale={locale}>
  <h1>{t(locale, 'nav.home')}</h1>
  <!-- Content -->
</Layout>
```

### `src/pages/articles/[slug].astro`

```astro
---
import { getCollection } from 'astro:content';
import Layout from '../../layouts/Layout.astro';

export async function getStaticPaths() {
  const articles = await getCollection('articles');
  return articles.map(article => ({
    params: { slug: article.id },
    props: { article },
  }));
}

const { article } = Astro.props;
const { Content } = await article.render();
---

<Layout title={article.data.title} locale="en">
  <article>
    <h1>{article.data.title}</h1>
    <time>{article.data.pubDate.toLocaleDateString('en-US')}</time>
    <Content />
  </article>
</Layout>
```

### `src/pages/zh-tw/articles/[slug].astro`

```astro
---
import { getCollection } from 'astro:content';
import Layout from '../../../layouts/Layout.astro';

export async function getStaticPaths() {
  const articles = await getCollection('articles-zh-tw');
  return articles.map(article => ({
    params: { slug: article.id },
    props: { article },
  }));
}

const { article } = Astro.props;
const { Content } = await article.render();
---

<Layout title={article.data.title} locale="zh-tw">
  <article>
    <h1>{article.data.title}</h1>
    <time>{article.data.pubDate.toLocaleDateString('zh-TW')}</time>
    <Content />
  </article>
</Layout>
```

## Language Switcher Component

### `src/components/LanguageSwitcher.astro`

```astro
---
interface Props {
  currentLocale: string;
  currentPath: string;
}

const { currentLocale, currentPath } = Astro.props;

const locales = [
  { code: 'en', label: 'EN', flag: '🇺🇸' },
  { code: 'zh-tw', label: '繁中', flag: '🇹🇼' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
];

function getLocalizedPath(locale: string, path: string): string {
  // Remove current locale prefix
  let cleanPath = path
    .replace(/^\/(zh-tw|ja)/, '')
    .replace(/^\/+/, '/');

  if (cleanPath === '') cleanPath = '/';

  // Add new locale prefix (except for English)
  return locale === 'en' ? cleanPath : `/${locale}${cleanPath}`;
}
---

<div class="language-switcher">
  {locales.map(locale => (
    <a
      href={getLocalizedPath(locale.code, currentPath)}
      class:list={[
        'locale-link',
        { active: locale.code === currentLocale }
      ]}
      data-locale={locale.code}
    >
      <span class="flag">{locale.flag}</span>
      <span class="label">{locale.label}</span>
    </a>
  ))}
</div>

<style>
  .language-switcher {
    display: flex;
    gap: 0.5rem;
  }

  .locale-link {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    text-decoration: none;
    opacity: 0.7;
    transition: opacity 0.2s;
  }

  .locale-link:hover,
  .locale-link.active {
    opacity: 1;
  }

  .locale-link.active {
    background: rgba(0, 0, 0, 0.1);
  }
</style>

<script>
  // Store preference when user clicks
  document.querySelectorAll('.locale-link').forEach(link => {
    link.addEventListener('click', () => {
      const locale = link.getAttribute('data-locale');
      document.cookie = `preferred_lang=${locale};path=/;max-age=${60*60*24*365}`;
    });
  });
</script>
```

## SEO: Hreflang Tags

### `src/layouts/Layout.astro`

```astro
---
interface Props {
  title: string;
  description?: string;
  locale: string;
}

const { title, description, locale } = Astro.props;
const currentPath = Astro.url.pathname;

// Generate alternate URLs for all locales
function getAlternateUrl(targetLocale: string): string {
  const cleanPath = currentPath.replace(/^\/(zh-tw|ja)/, '') || '/';
  const base = Astro.site?.toString().replace(/\/$/, '') || '';

  if (targetLocale === 'en') {
    return `${base}${cleanPath}`;
  }
  return `${base}/${targetLocale}${cleanPath}`;
}
---

<!DOCTYPE html>
<html lang={locale === 'zh-tw' ? 'zh-TW' : locale}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {description && <meta name="description" content={description} />}

  <!-- Hreflang tags for SEO -->
  <link rel="alternate" hreflang="en" href={getAlternateUrl('en')} />
  <link rel="alternate" hreflang="zh-TW" href={getAlternateUrl('zh-tw')} />
  <link rel="alternate" hreflang="ja" href={getAlternateUrl('ja')} />
  <link rel="alternate" hreflang="x-default" href={getAlternateUrl('en')} />
</head>
<body>
  <slot />
</body>
</html>
```

## Tips & Best Practices

### 1. Start with i18n from Day 1

Adding i18n later is painful. Set up the structure first, even with placeholder translations.

### 2. Use Content Collections

Don't duplicate page templates. Use collections for content, templates for structure.

### 3. Cookie + Header Detection

```
1. Check cookie first (user preference)
2. Fall back to Accept-Language header
3. Default to English
```

### 4. Consistent URL Structure

```
English:  /articles/my-post
Chinese:  /zh-tw/articles/my-post
Japanese: /ja/articles/my-post
```

### 5. Sitemap with Hreflang

Astro's sitemap integration automatically adds hreflang when configured.

## Related Resources

- [Astro i18n Documentation](https://docs.astro.build/en/guides/internationalization/)
- [48-Hour Website Case Study](../case-studies/48-hour-website.md)
- [Astro Content Collections](https://docs.astro.build/en/guides/content-collections/)

---

*Multi-language support done right from the start saves hours of refactoring later.*
