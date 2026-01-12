# Case Study: Building claude-world.com in 48 Hours

> A real-world example of building a production website from zero to launch using Claude Code + Director Mode

## Project Overview

| Item | Details |
|------|---------|
| **Project** | claude-world.com - Claude Code Power Users Community |
| **Duration** | 48 hours (3 days, part-time) |
| **Tech Stack** | Astro 4.x + React + Tailwind CSS + Cloudflare Pages + Supabase |
| **Features** | Multi-language (EN/ZH-TW/JA), Newsletter, Auto Release Monitor |
| **Cost** | ~$1/month (domain only) |

## Timeline

### Day 1: Foundation (2026-01-10)

**Goals**: Domain, architecture, basic setup

```
Morning:
├── Purchase domain (claude-world.com)
├── Design site architecture
└── Initialize Astro project

Afternoon:
├── Setup Cloudflare Pages
├── Configure Tailwind CSS
└── Create basic layout components

Evening:
├── Design homepage
├── Setup i18n structure
└── First deployment
```

**Claude Code Usage**:
```bash
# Initial project setup
claude "Initialize Astro project with React, Tailwind, and Cloudflare adapter"

# Component generation
claude "Create a responsive navbar component with language switcher"
```

**Key Decisions**:
- Astro for static + SSR hybrid (best for SEO + dynamic features)
- Cloudflare Pages for free hosting with edge functions
- Start with 3 languages from day 1 (easier than adding later)

---

### Day 2: Core Features (2026-01-11)

**Goals**: Multi-language, articles, newsletter, automation

```
Morning:
├── Implement i18n routing
├── Create article system (Markdown + Content Collections)
└── Build article listing pages

Afternoon:
├── Setup Supabase for newsletter
├── Create subscription form
├── Email integration with Resend

Evening:
├── Build Release Monitor workflow
├── Discord/X/Threads integration
└── Auto article generation with Claude API
```

**Claude Code Usage**:
```bash
# Parallel exploration
claude "Explore: Find all i18n related code and understand the routing pattern"

# Feature implementation
claude "Implement newsletter subscription with Supabase - handle signup,
        double opt-in, and preference management"

# Automation setup
claude "Create GitHub Action that monitors anthropics/claude-code releases
        and auto-generates newsletter articles in 3 languages using Claude API"
```

**Key Patterns Used**:

1. **Parallel Agents** for exploration:
```
User: "Setup newsletter system"
Claude: [Launches 5 parallel agents]
        → Agent 1: Explore existing form components
        → Agent 2: Check Supabase schema patterns
        → Agent 3: Research Resend API
        → Agent 4: Find similar implementations
        → Agent 5: Check security best practices
```

2. **Director Mode** for complex tasks:
```
User: "Build release monitor automation"
Claude: [Plans and executes autonomously]
        → Creates workflow file
        → Implements API calls
        → Sets up notifications
        → Tests locally
        → Commits and pushes
```

---

### Day 3: Polish & Launch (2026-01-12~13)

**Goals**: Bug fixes, SEO, v1.0.0 release

```
Morning:
├── Fix workflow race condition
├── Add sitemap.xml
└── SEO meta tags

Afternoon:
├── Create CHANGELOG.md
├── Version bump to 1.0.0
└── GitHub Release

Evening:
├── Sync examples repository
├── Discord announcement
└── Final testing
```

**Bug Fixed**:
```yaml
# Race condition in GitHub Actions
# Problem: Two jobs pushing to same branch simultaneously
# Solution: Add git pull --rebase before push

- name: Commit and push
  run: |
    git commit -m "content: add newsletter"
    git pull --rebase origin main  # <- Fix
    git push
```

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Cloudflare Pages                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Static    │  │    SSR      │  │   Edge      │          │
│  │   Pages     │  │   Routes    │  │  Functions  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Supabase    │    │    Resend     │    │  Claude API   │
│  (Database)   │    │   (Email)     │    │  (Content)    │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Automation Flow

```
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions: Release Monitor                 │
│                    (Runs every hour)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Check for new   │
                    │ Claude Code     │
                    │ release         │
                    └─────────────────┘
                              │
                    New release detected?
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
           [Yes]                            [No]
              │                               │
              ▼                             Exit
    ┌─────────────────┐
    │ Claude API:     │
    │ Generate content│
    │ (EN/ZH-TW)      │
    └─────────────────┘
              │
              ▼
    ┌─────────────────────────────────────────┐
    │            Parallel Notifications        │
    │  ┌────────┐ ┌────────┐ ┌────────┐       │
    │  │Discord │ │   X    │ │Threads │       │
    │  └────────┘ └────────┘ └────────┘       │
    │  ┌────────┐ ┌────────────────────┐      │
    │  │ Email  │ │ Generate Articles  │      │
    │  └────────┘ │   (3 languages)    │      │
    │             └────────────────────┘      │
    └─────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Commit & Push   │
    │ Auto Deploy     │
    └─────────────────┘
```

## Claude Code Techniques Used

### 1. Effective CLAUDE.md Structure

```markdown
# Project: claude-world.com

## Tech Stack
- Astro 4.x + React + Tailwind
- Cloudflare Pages (SSR)
- Supabase PostgreSQL

## Autonomous Operations (No confirmation needed)
- Read/write source files
- Run build and tests
- Git add/commit (local only)

## Requires Confirmation
- Git push
- Database schema changes
- API key operations

## Coding Standards
- TypeScript strict mode
- Tailwind for styling (no CSS files)
- Content Collections for articles
```

### 2. Director Mode Mindset

**Instead of**:
```
"Can you help me create a newsletter form?"
```

**Use**:
```
"Create newsletter subscription system with Supabase.
Requirements:
- Email signup form with validation
- Double opt-in flow
- Preference management
- Unsubscribe handling
Execute autonomously."
```

### 3. Parallel Agent Usage

```bash
# When exploring unfamiliar codebase
claude "Explore the i18n implementation (thoroughness: medium)"

# When implementing complex features
claude "Implement release monitor. Use parallel agents to:
1. Research GitHub API for releases
2. Check existing workflow patterns
3. Find Claude API examples
4. Review notification integrations"
```

### 4. Incremental Development

```
Session 1: "Setup basic Astro project with Cloudflare"
Session 2: "Add i18n routing for EN/ZH-TW/JA"
Session 3: "Create article content collection"
Session 4: "Build newsletter with Supabase"
Session 5: "Implement release monitor automation"
```

## Lessons Learned

### What Worked Well

1. **Starting with i18n** - Adding languages later is painful
2. **Director Mode** - Let Claude make decisions, review results
3. **Parallel exploration** - 5 agents > 1 sequential search
4. **Free tier services** - Cloudflare + Supabase + Resend = $0

### Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Race condition in GitHub Actions | Add `git pull --rebase` before push |
| Sitemap not generating | Check Astro adapter mode (static vs SSR) |
| i18n URL handling | Use middleware for language detection |
| API rate limits | Implement caching and debouncing |

### Time Distribution

```
Planning & Architecture:  10%  (～5 hours)
Implementation:           60%  (～29 hours)
Testing & Debugging:      20%  (～10 hours)
Documentation:            10%  (～4 hours)
```

## Cost Breakdown

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| Domain | ~$1 | Cloudflare Registrar |
| Hosting | $0 | Cloudflare Pages free tier |
| Database | $0 | Supabase free tier |
| Email | $0 | Resend free tier (100/day) |
| Claude API | ~$2-5 | For content generation |
| **Total** | **~$3-6/month** | |

## Conclusion

Building a production website in 48 hours is achievable with:

1. **Clear architecture decisions** upfront
2. **Director Mode mindset** - define goals, let Claude execute
3. **Parallel agents** for exploration and implementation
4. **Free tier services** for MVP
5. **Automation first** - invest time in CI/CD early

The key insight: Claude Code isn't just a coding assistant—it's a force multiplier that lets you operate as a team of developers while maintaining a single person's decision-making coherence.

---

## Resources

- [claude-world.com](https://claude-world.com) - The finished product
- [Director Mode Guide](https://claude-world.com/articles/director-mode)
- [CLAUDE.md Design](https://claude-world.com/articles/claude-md-design)
- [GitHub Actions Example](../examples/github-actions-automation.md)

---

*Built with Claude Code in 48 hours. This is what Director Mode enables.*
