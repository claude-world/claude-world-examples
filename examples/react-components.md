# React Components for Claude Code Projects

> Production-ready React component patterns with TypeScript and Tailwind CSS - copy, paste, and adapt for your projects.

## Overview

This guide provides complete, copy-paste-ready React component patterns commonly used in Claude Code projects. Each component includes TypeScript types, Tailwind styling, and accessibility features.

## Component Categories

| Category | Components | Use Case |
|----------|------------|----------|
| [Forms](#forms) | Newsletter, Validation | User input collection |
| [Navigation](#navigation) | Language Switcher, Mobile Nav | Site navigation |
| [UI Controls](#ui-controls) | Dark Mode, Copy Button | User interactions |
| [Feedback](#feedback) | Toast, Loading States | Status communication |

---

## Forms

### 1. Newsletter Subscription Form

**Use case**: Email collection with validation and multi-language support

```tsx
// components/NewsletterForm.tsx
import { useState, useEffect } from 'react';

interface NewsletterFormProps {
  className?: string;
  source?: string;
  lang?: 'en' | 'zh-tw' | 'ja';
}

// i18n labels
const labels = {
  en: {
    placeholder: 'you@email.com',
    button: 'Subscribe',
    buttonLoading: 'Joining...',
    success: 'Welcome! Check your inbox for confirmation.',
    error: 'Something went wrong. Please try again.',
    invalidEmail: 'Please enter a valid email address.',
    help: 'Weekly insights delivered. No spam, unsubscribe anytime.',
  },
  'zh-tw': {
    placeholder: 'you@email.com',
    button: '訂閱',
    buttonLoading: '處理中...',
    success: '訂閱成功！請檢查您的收件匣確認。',
    error: '發生錯誤，請稍後再試。',
    invalidEmail: '請輸入有效的電子郵件地址。',
    help: '每週精選內容。無垃圾郵件，隨時取消訂閱。',
  },
  ja: {
    placeholder: 'you@email.com',
    button: '購読',
    buttonLoading: '処理中...',
    success: '購読完了！確認メールをご確認ください。',
    error: 'エラーが発生しました。もう一度お試しください。',
    invalidEmail: '有効なメールアドレスを入力してください。',
    help: '毎週配信。スパムなし、いつでも解除可能。',
  },
} as const;

// Loading spinner component
function LoadingSpinner() {
  return (
    <svg
      className="animate-spin -ml-1 mr-2 h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export default function NewsletterForm({
  className = '',
  source = 'website',
  lang = 'en',
}: NewsletterFormProps) {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const t = labels[lang];

  // Email validation
  const validateEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !validateEmail(email)) {
      setStatus('error');
      setMessage(t.invalidEmail);
      return;
    }

    setStatus('loading');

    try {
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source, language: lang }),
      });

      if (response.ok) {
        setStatus('success');
        setMessage(t.success);
        setEmail('');
      } else {
        const data = await response.json();
        setStatus('error');
        setMessage(data.error || t.error);
      }
    } catch {
      setStatus('error');
      setMessage(t.error);
    }
  };

  const hasError = status === 'error';

  return (
    <form onSubmit={handleSubmit} className={`w-full max-w-md ${className}`} noValidate>
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t.placeholder}
          className={`flex-1 px-4 py-3 bg-gray-800 rounded-lg border focus:outline-none text-white placeholder:text-gray-500 ${
            hasError
              ? 'border-red-500 focus:border-red-500'
              : 'border-gray-700 focus:border-orange-500'
          }`}
          disabled={status === 'loading'}
          aria-invalid={hasError}
          aria-describedby="newsletter-help"
          aria-required="true"
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className="px-6 py-3 bg-orange-500 text-white font-semibold rounded-lg hover:bg-orange-600 transition-all hover:shadow-lg hover:shadow-orange-500/30 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center min-w-[120px]"
          aria-busy={status === 'loading'}
        >
          {status === 'loading' ? (
            <>
              <LoadingSpinner />
              {t.buttonLoading}
            </>
          ) : (
            t.button
          )}
        </button>
      </div>

      {message && (
        <p
          className={`mt-3 text-sm ${status === 'success' ? 'text-green-400' : 'text-red-400'}`}
          role={hasError ? 'alert' : undefined}
          aria-live="polite"
        >
          {message}
        </p>
      )}

      <p id="newsletter-help" className="mt-3 text-sm text-gray-500">
        {t.help}
      </p>
    </form>
  );
}
```

**Key Features:**
- Form validation with email pattern matching
- Loading state with animated spinner
- Multi-language support (i18n)
- Accessible error messages with ARIA attributes
- Responsive layout (stacks on mobile)

---

## Navigation

### 2. Language Switcher Component

**Use case**: Multi-language site navigation with dropdown

```tsx
// components/LanguageSwitcher.tsx
import { useState, useRef, useEffect } from 'react';

interface Language {
  code: string;
  label: string;
  flag: string;
}

interface LanguageSwitcherProps {
  currentLang: string;
  languages?: Language[];
  onLanguageChange?: (lang: string) => void;
}

const DEFAULT_LANGUAGES: Language[] = [
  { code: 'en', label: 'English', flag: 'US' },
  { code: 'zh-tw', label: '繁體中文', flag: 'TW' },
  { code: 'ja', label: '日本語', flag: 'JP' },
];

export default function LanguageSwitcher({
  currentLang,
  languages = DEFAULT_LANGUAGES,
  onLanguageChange,
}: LanguageSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close on Escape key
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const currentLanguage = languages.find((l) => l.code === currentLang) || languages[0];

  const handleLanguageSelect = (lang: Language) => {
    if (onLanguageChange) {
      onLanguageChange(lang.code);
    } else {
      // Default behavior: navigate to localized path
      const currentPath = window.location.pathname;
      const pathWithoutLang = currentPath.replace(/^\/(en|zh-tw|ja)/, '');
      const newPath = lang.code === 'en' ? pathWithoutLang || '/' : `/${lang.code}${pathWithoutLang}`;
      window.location.href = newPath;
    }
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 hover:border-gray-600 transition-colors text-sm"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-label="Select language"
      >
        <span className="text-base">{currentLanguage.flag}</span>
        <span className="hidden sm:inline text-gray-300">{currentLanguage.label}</span>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-xl border border-gray-700 z-50 overflow-hidden"
          role="listbox"
          aria-label="Available languages"
        >
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleLanguageSelect(lang)}
              className={`w-full px-4 py-3 text-left flex items-center gap-3 hover:bg-gray-700 transition-colors ${
                lang.code === currentLang ? 'bg-gray-700/50' : ''
              }`}
              role="option"
              aria-selected={lang.code === currentLang}
            >
              <span className="text-lg">{lang.flag}</span>
              <span className="text-gray-200">{lang.label}</span>
              {lang.code === currentLang && (
                <svg className="w-4 h-4 ml-auto text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 3. Responsive Navigation

**Use case**: Mobile-friendly navigation with hamburger menu

```tsx
// components/Navigation.tsx
import { useState, useEffect } from 'react';

interface NavItem {
  label: string;
  href: string;
  isActive?: boolean;
}

interface NavigationProps {
  items: NavItem[];
  logo?: React.ReactNode;
  rightSlot?: React.ReactNode;
}

export default function Navigation({ items, logo, rightSlot }: NavigationProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Add scroll listener for header background
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close menu on resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Prevent scroll when menu is open
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMenuOpen]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all ${
        isScrolled ? 'bg-gray-900/95 backdrop-blur-sm shadow-lg' : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            {logo || (
              <a href="/" className="text-xl font-bold text-white">
                Logo
              </a>
            )}
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {items.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  item.isActive
                    ? 'bg-orange-500/20 text-orange-400'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* Right Slot (CTA, language switcher, etc.) */}
          <div className="hidden md:flex items-center gap-4">
            {rightSlot}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
            aria-expanded={isMenuOpen}
            aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
          >
            {isMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div
        className={`md:hidden fixed inset-0 top-16 bg-gray-900/98 backdrop-blur-sm transition-all ${
          isMenuOpen ? 'opacity-100 visible' : 'opacity-0 invisible'
        }`}
      >
        <nav className="flex flex-col p-4 space-y-2">
          {items.map((item) => (
            <a
              key={item.href}
              href={item.href}
              onClick={() => setIsMenuOpen(false)}
              className={`px-4 py-3 rounded-lg text-lg font-medium transition-colors ${
                item.isActive
                  ? 'bg-orange-500/20 text-orange-400'
                  : 'text-gray-300 hover:text-white hover:bg-gray-800'
              }`}
            >
              {item.label}
            </a>
          ))}
          <div className="pt-4 border-t border-gray-800">
            {rightSlot}
          </div>
        </nav>
      </div>
    </header>
  );
}
```

**Usage Example:**
```tsx
<Navigation
  items={[
    { label: 'Home', href: '/', isActive: true },
    { label: 'Articles', href: '/articles' },
    { label: 'Examples', href: '/examples' },
    { label: 'Community', href: '/community' },
  ]}
  logo={<img src="/logo.svg" alt="Site Logo" className="h-8" />}
  rightSlot={
    <>
      <LanguageSwitcher currentLang="en" />
      <a href="/subscribe" className="btn-primary">Subscribe</a>
    </>
  }
/>
```

---

## UI Controls

### 4. Dark Mode Toggle

**Use case**: Theme switching with system preference detection

```tsx
// components/DarkModeToggle.tsx
import { useState, useEffect } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface DarkModeToggleProps {
  className?: string;
}

export default function DarkModeToggle({ className = '' }: DarkModeToggleProps) {
  const [theme, setTheme] = useState<Theme>('system');
  const [mounted, setMounted] = useState(false);

  // Get initial theme from localStorage or system
  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem('theme') as Theme | null;
    if (stored) {
      setTheme(stored);
    }
  }, []);

  // Apply theme changes
  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (theme === 'dark' || (theme === 'system' && systemDark)) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    if (theme !== 'system') {
      localStorage.setItem('theme', theme);
    } else {
      localStorage.removeItem('theme');
    }
  }, [theme, mounted]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (theme === 'system') {
        const root = document.documentElement;
        if (mediaQuery.matches) {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const cycleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(theme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    setTheme(nextTheme);
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return <div className={`w-10 h-10 ${className}`} />;
  }

  const icons = {
    light: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>
    ),
    dark: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        />
      </svg>
    ),
    system: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        />
      </svg>
    ),
  };

  const labels = {
    light: 'Light mode',
    dark: 'Dark mode',
    system: 'System theme',
  };

  return (
    <button
      onClick={cycleTheme}
      className={`p-2 rounded-lg bg-gray-800 border border-gray-700 hover:border-gray-600 text-gray-300 hover:text-white transition-colors ${className}`}
      aria-label={labels[theme]}
      title={labels[theme]}
    >
      {icons[theme]}
    </button>
  );
}
```

### 5. Copy-to-Clipboard Button

**Use case**: Code block copy functionality with multiple formats

```tsx
// components/CopyButton.tsx
import { useState } from 'react';

interface CopyButtonProps {
  text: string;
  className?: string;
  label?: string;
  successLabel?: string;
}

export default function CopyButton({
  text,
  className = '',
  label = 'Copy',
  successLabel = 'Copied!',
}: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className={`inline-flex items-center gap-2 px-3 py-1.5 text-sm rounded-md transition-colors ${
        copied
          ? 'bg-green-500/20 text-green-400'
          : 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white'
      } ${className}`}
      aria-label={copied ? successLabel : label}
    >
      {copied ? (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {successLabel}
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          {label}
        </>
      )}
    </button>
  );
}
```

**Advanced: Copy with Format Options**

```tsx
// components/CopyWithFormats.tsx
import { useState, useRef, useEffect } from 'react';

type CopyFormat = 'text' | 'markdown' | 'html';

interface CopyWithFormatsProps {
  content: {
    text: string;
    markdown?: string;
    html?: string;
  };
  className?: string;
}

const formatLabels: Record<CopyFormat, { label: string; desc: string }> = {
  text: { label: 'Plain Text', desc: 'Basic text without formatting' },
  markdown: { label: 'Markdown', desc: 'Preserves headings, lists, code' },
  html: { label: 'HTML', desc: 'Full HTML markup' },
};

export default function CopyWithFormats({ content, className = '' }: CopyWithFormatsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState<CopyFormat | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleCopy = async (format: CopyFormat) => {
    const textToCopy = format === 'text'
      ? content.text
      : format === 'markdown'
        ? content.markdown || content.text
        : content.html || content.text;

    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(format);
      setTimeout(() => {
        setCopied(null);
        setIsOpen(false);
      }, 1500);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const availableFormats = (['text', 'markdown', 'html'] as CopyFormat[]).filter(
    (f) => f === 'text' || content[f]
  );

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-800 text-gray-300 rounded-lg text-sm hover:bg-gray-700 hover:text-white transition-colors border border-gray-700"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
        Copy
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-gray-800 rounded-xl shadow-xl border border-gray-700 z-50 overflow-hidden">
          {availableFormats.map((format) => (
            <button
              key={format}
              onClick={() => handleCopy(format)}
              className="w-full px-4 py-3 text-left hover:bg-gray-700 transition-colors border-b border-gray-700 last:border-b-0"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-200">
                  {copied === format ? 'Copied!' : formatLabels[format].label}
                </span>
                {copied === format && (
                  <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-0.5">{formatLabels[format].desc}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Feedback

### 6. Toast Notifications

**Use case**: Non-intrusive status messages

```tsx
// components/Toast.tsx
import { useState, useEffect, useCallback } from 'react';

interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToastProps {
  toast: ToastMessage;
  onDismiss: (id: string) => void;
}

function Toast({ toast, onDismiss }: ToastProps) {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const duration = toast.duration || 4000;
    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(() => onDismiss(toast.id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [toast, onDismiss]);

  const icons = {
    success: (
      <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    ),
    error: (
      <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    ),
    warning: (
      <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
    ),
    info: (
      <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  };

  const bgColors = {
    success: 'bg-green-900/90 border-green-700',
    error: 'bg-red-900/90 border-red-700',
    warning: 'bg-yellow-900/90 border-yellow-700',
    info: 'bg-blue-900/90 border-blue-700',
  };

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-sm shadow-lg transition-all duration-300 ${
        bgColors[toast.type]
      } ${isExiting ? 'opacity-0 translate-x-4' : 'opacity-100 translate-x-0'}`}
      role="alert"
    >
      {icons[toast.type]}
      <p className="text-sm text-white flex-1">{toast.message}</p>
      <button
        onClick={() => {
          setIsExiting(true);
          setTimeout(() => onDismiss(toast.id), 300);
        }}
        className="text-gray-400 hover:text-white transition-colors"
        aria-label="Dismiss"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

// Toast Container and Hook
export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback((toast: Omit<ToastMessage, 'id'>) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { ...toast, id }]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Expose addToast globally
  useEffect(() => {
    (window as any).showToast = addToast;
    return () => {
      delete (window as any).showToast;
    };
  }, [addToast]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={removeToast} />
      ))}
    </div>
  );
}

// Usage hook
export function useToast() {
  const showToast = useCallback((options: Omit<ToastMessage, 'id'>) => {
    if (typeof window !== 'undefined' && (window as any).showToast) {
      (window as any).showToast(options);
    }
  }, []);

  return { showToast };
}
```

**Usage:**
```tsx
// In your app root
import { ToastContainer } from './components/Toast';

function App() {
  return (
    <>
      <MainContent />
      <ToastContainer />
    </>
  );
}

// In any component
import { useToast } from './components/Toast';

function MyComponent() {
  const { showToast } = useToast();

  const handleAction = () => {
    showToast({ message: 'Action completed!', type: 'success' });
  };

  return <button onClick={handleAction}>Do Something</button>;
}
```

### 7. Loading States and Skeletons

**Use case**: Visual feedback during data fetching

```tsx
// components/Loading.tsx

// Simple Spinner
export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div
      className={`${sizes[size]} border-orange-500 border-t-transparent rounded-full animate-spin`}
      role="status"
      aria-label="Loading"
    />
  );
}

// Loading Overlay
export function LoadingOverlay({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="text-center">
        <Spinner size="lg" />
        <p className="text-gray-400 mt-4">{message}</p>
      </div>
    </div>
  );
}

// Skeleton primitives
export function SkeletonLine({ className = '' }: { className?: string }) {
  return (
    <div
      className={`bg-gray-700 rounded animate-pulse ${className}`}
      aria-hidden="true"
    />
  );
}

export function SkeletonCircle({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div
      className={`${sizes[size]} bg-gray-700 rounded-full animate-pulse`}
      aria-hidden="true"
    />
  );
}

// Card Skeleton
export function CardSkeleton() {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700" aria-hidden="true">
      <div className="flex items-start gap-4">
        <SkeletonCircle size="md" />
        <div className="flex-1 space-y-3">
          <SkeletonLine className="h-4 w-3/4" />
          <SkeletonLine className="h-3 w-1/2" />
        </div>
      </div>
      <div className="mt-6 space-y-3">
        <SkeletonLine className="h-3 w-full" />
        <SkeletonLine className="h-3 w-full" />
        <SkeletonLine className="h-3 w-2/3" />
      </div>
    </div>
  );
}

// Article List Skeleton
export function ArticleListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-6" role="status" aria-label="Loading articles">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex gap-4 p-4 rounded-lg bg-gray-800/50" aria-hidden="true">
          <SkeletonLine className="w-24 h-24 rounded-lg flex-shrink-0" />
          <div className="flex-1 space-y-3">
            <SkeletonLine className="h-5 w-3/4" />
            <SkeletonLine className="h-3 w-full" />
            <SkeletonLine className="h-3 w-2/3" />
            <div className="flex gap-2 pt-2">
              <SkeletonLine className="h-5 w-16 rounded-full" />
              <SkeletonLine className="h-5 w-20 rounded-full" />
            </div>
          </div>
        </div>
      ))}
      <span className="sr-only">Loading content...</span>
    </div>
  );
}

// Stats Card Skeleton
export function StatsCardSkeleton() {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700" aria-hidden="true">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <SkeletonLine className="h-3 w-20" />
          <SkeletonLine className="h-8 w-16" />
          <SkeletonLine className="h-3 w-24" />
        </div>
        <SkeletonCircle size="sm" />
      </div>
      <div className="mt-4">
        <SkeletonLine className="h-10 w-full" />
      </div>
    </div>
  );
}
```

**Usage Example:**
```tsx
function ArticleList() {
  const [articles, setArticles] = useState<Article[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchArticles()
      .then(setArticles)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <ArticleListSkeleton count={5} />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="space-y-6">
      {articles?.map((article) => (
        <ArticleCard key={article.id} article={article} />
      ))}
    </div>
  );
}
```

---

## Complete Component Library Setup

Here's how to organize these components in a project:

```
src/
  components/
    ui/
      Button.tsx
      CopyButton.tsx
      DarkModeToggle.tsx
      Loading.tsx        # Spinner, Skeletons
      Toast.tsx
    forms/
      NewsletterForm.tsx
      Input.tsx
      Select.tsx
    navigation/
      Navigation.tsx
      LanguageSwitcher.tsx
      Breadcrumb.tsx
    index.ts            # Barrel exports
```

**Barrel Export (components/index.ts):**
```tsx
// UI Components
export { default as CopyButton } from './ui/CopyButton';
export { default as DarkModeToggle } from './ui/DarkModeToggle';
export { Spinner, LoadingOverlay, CardSkeleton } from './ui/Loading';
export { ToastContainer, useToast } from './ui/Toast';

// Forms
export { default as NewsletterForm } from './forms/NewsletterForm';

// Navigation
export { default as Navigation } from './navigation/Navigation';
export { default as LanguageSwitcher } from './navigation/LanguageSwitcher';
```

---

## Tips for Claude Code Projects

### 1. Use Custom CSS Variables

Define your theme in Tailwind config and CSS:

```css
/* globals.css */
:root {
  --color-primary: #f97316;
  --color-surface: #1f1f1f;
  --color-border: rgba(255, 255, 255, 0.1);
  --color-text-primary: #ffffff;
  --color-text-secondary: #9ca3af;
  --color-text-muted: #6b7280;
}
```

```tsx
// Use in components
<div className="bg-[--color-surface] border-[--color-border]">
```

### 2. Handle SSR/Hydration

For components that use browser APIs:

```tsx
const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);
}, []);

if (!mounted) {
  return <div className="skeleton-placeholder" />;
}
```

### 3. Accessibility Checklist

- [ ] Use semantic HTML elements
- [ ] Add ARIA labels for icon-only buttons
- [ ] Include `role` and `aria-live` for dynamic content
- [ ] Support keyboard navigation (Escape to close, Tab order)
- [ ] Provide visible focus states

### 4. Performance

- Use `useCallback` for event handlers passed to children
- Lazy load heavy components with `React.lazy`
- Debounce input handlers for API calls
- Use CSS transitions instead of JS animations when possible

---

## Related Resources

- [Feature Development Pattern](./feature-development.md) - Complete feature implementation workflow
- [Multi-Language Astro](./multi-language-astro.md) - i18n patterns for Astro sites
- [Newsletter System](./newsletter-system.md) - Full backend integration

---

*These components are production-tested from Claude World. Customize styling and functionality for your specific needs.*
