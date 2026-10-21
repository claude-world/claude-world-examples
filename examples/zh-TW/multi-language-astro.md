# 使用 Astro 建立多語言網站

> 使用 Astro 建立多語言網站的完整指南，包括 i18n 路由、內容集合和自動語言偵測

## 概述

這個範例展示如何建立支援以下功能的網站：
- **3 種語言**：英文（預設）、繁體中文、日文
- **URL 結構**：`/`（en）、`/zh-tw/`、`/ja/`
- **自動語言偵測**：基於瀏覽器 `Accept-Language`
- **內容集合**：每種語言獨立的文章
- **SEO**：正確的 hreflang 標籤

## 專案結構

```
src/
├── content/
│   └── articles/
│       ├── my-article.md           # 英文（預設）
│       ├── zh-tw/
│       │   └── my-article.md       # 繁體中文
│       └── ja/
│           └── my-article.md       # 日文
├── i18n/
│   ├── en.json
│   ├── zh-tw.json
│   └── ja.json
├── pages/
│   ├── index.astro                 # 英文首頁
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
├── middleware.ts                   # 語言偵測
└── components/
    └── LanguageSwitcher.astro
```

## 設定

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
      prefixDefaultLocale: false,  // /about 而不是 /en/about
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

## 內容集合

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

// 英文文章（預設）
const articles = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/articles' }),
  schema: articleSchema,
});

// 中文文章
const articlesZhTw = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/articles/zh-tw' }),
  schema: articleSchema,
});

// 日文文章
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

## i18n 翻譯

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

## 語言偵測 Middleware

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
    // 完全匹配
    if (SUPPORTED_LOCALES.includes(code as any)) {
      return code;
    }
    // 語系匹配
    if (code === 'zh' || code.startsWith('zh-')) return 'zh-tw';
    if (code === 'ja' || code.startsWith('ja-')) return 'ja';
    if (code === 'en' || code.startsWith('en-')) return 'en';
  }

  return DEFAULT_LOCALE;
}

function getLocaleFromPath(pathname: string): string | null {
  if (pathname.startsWith('/zh-tw')) return 'zh-tw';
  if (pathname.startsWith('/ja')) return 'ja';
  return null;  // 根路徑是英文
}

export const onRequest = defineMiddleware((context, next) => {
  const { pathname } = context.url;
  const { cookies, request } = context;

  // 跳過非頁面路由
  if (SKIP_PATHS.some(path => pathname.startsWith(path))) {
    return next();
  }

  // 已經在本地化路徑
  const currentLocale = getLocaleFromPath(pathname);
  if (currentLocale !== null) {
    return next();
  }

  // 檢查儲存的偏好
  const preferredLang = cookies.get(LANG_COOKIE)?.value;
  if (preferredLang && preferredLang !== 'en') {
    const newUrl = new URL(`/${preferredLang}${pathname}`, context.url);
    return context.redirect(newUrl.toString(), 302);
  }

  // 從 Accept-Language header 偵測
  if (!preferredLang) {
    const acceptLanguage = request.headers?.get?.('Accept-Language') ?? null;
    const detectedLocale = getBestLocale(acceptLanguage);

    // 儲存偏好
    cookies.set(LANG_COOKIE, detectedLocale, {
      path: '/',
      maxAge: 60 * 60 * 24 * 365,
      httpOnly: false,
      sameSite: 'lax',
    });

    // 如果不是英文則重新導向
    if (detectedLocale !== 'en') {
      const newUrl = new URL(`/${detectedLocale}${pathname}`, context.url);
      return context.redirect(newUrl.toString(), 302);
    }
  }

  return next();
});
```

## 頁面範本

### `src/pages/index.astro`（英文）

```astro
---
import Layout from '../layouts/Layout.astro';
import { t } from '../i18n';

const locale = 'en';
---

<Layout title={t(locale, 'site.title')} locale={locale}>
  <h1>{t(locale, 'nav.home')}</h1>
  <!-- 內容 -->
</Layout>
```

### `src/pages/zh-tw/index.astro`（中文）

```astro
---
import Layout from '../../layouts/Layout.astro';
import { t } from '../../i18n';

const locale = 'zh-tw';
---

<Layout title={t(locale, 'site.title')} locale={locale}>
  <h1>{t(locale, 'nav.home')}</h1>
  <!-- 內容 -->
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

## 語言切換元件

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
  // 移除當前語言前綴
  let cleanPath = path
    .replace(/^\/(zh-tw|ja)/, '')
    .replace(/^\/+/, '/');

  if (cleanPath === '') cleanPath = '/';

  // 添加新語言前綴（英文除外）
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
  // 使用者點擊時儲存偏好
  document.querySelectorAll('.locale-link').forEach(link => {
    link.addEventListener('click', () => {
      const locale = link.getAttribute('data-locale');
      document.cookie = `preferred_lang=${locale};path=/;max-age=${60*60*24*365}`;
    });
  });
</script>
```

## SEO: Hreflang 標籤

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

// 為所有語言生成替代 URLs
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

  <!-- SEO 的 Hreflang 標籤 -->
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

## 技巧與最佳實踐

### 1. 從第一天就加入 i18n

之後添加 i18n 很痛苦。即使只有佔位翻譯，也先設定好結構。

### 2. 使用內容集合

不要重複頁面範本。使用集合處理內容，範本處理結構。

### 3. Cookie + Header 偵測

```
1. 先檢查 cookie（使用者偏好）
2. 退而求其次用 Accept-Language header
3. 預設為英文
```

### 4. 一致的 URL 結構

```
英文:    /articles/my-post
中文:    /zh-tw/articles/my-post
日文:    /ja/articles/my-post
```

### 5. 帶有 Hreflang 的 Sitemap

Astro 的 sitemap 整合在設定後會自動添加 hreflang。

## 相關資源

- [Astro i18n 文件](https://docs.astro.build/en/guides/internationalization/)
- [48 小時網站案例研究](../../case-studies/zh-TW/48-hour-website.md)
- [Astro 內容集合](https://docs.astro.build/en/guides/content-collections/)

---

*從一開始就做好多語言支援，可以節省之後數小時的重構時間。*
