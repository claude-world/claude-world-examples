# GitHub Actions Automation Suite

> Complete set of GitHub Actions workflows for automated community and project management.

This template collection provides production-ready workflows for monitoring upstream repos, generating content, posting to social media, and automating CI/CD.

---

## Workflows Included

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| [release-monitor.yml](./release-monitor.yml) | Monitor upstream repos for new releases | Scheduled (hourly) |
| [blog-monitor.yml](./blog-monitor.yml) | Monitor RSS/websites for new content | Scheduled (2 hours) |
| [social-post.yml](./social-post.yml) | Post to X/Threads | Manual |
| [newsletter-trigger.yml](./newsletter-trigger.yml) | Generate and send newsletters | Manual + Release |
| [sync-upstream.yml](./sync-upstream.yml) | Keep submodules updated | Scheduled (daily) |
| [ci.yml](./ci.yml) | Build, lint, and validate | Push/PR |

---

## Quick Start

```bash
# 1. Copy all workflows to your repo
cp -r templates/github-actions-suite/*.yml .github/workflows/

# 2. Add required secrets in GitHub Settings > Secrets
# See "Required Secrets" section below

# 3. Customize the workflows for your use case
# See comments in each file
```

---

## Required Secrets

### Core (Required)

| Secret | Purpose | Where to get |
|--------|---------|--------------|
| `ANTHROPIC_API_KEY` | Claude API for content generation | [Anthropic Console](https://console.anthropic.com) |

### Social Media (Optional)

| Secret | Purpose | Where to get |
|--------|---------|--------------|
| `X_API_KEY` | X/Twitter posting | [X Developer Portal](https://developer.twitter.com) |
| `X_API_SECRET` | X/Twitter posting | X Developer Portal |
| `X_ACCESS_TOKEN` | X/Twitter posting | X Developer Portal |
| `X_ACCESS_SECRET` | X/Twitter posting | X Developer Portal |
| `THREADS_USER_ID` | Threads posting | [Meta Developer](https://developers.facebook.com) |
| `THREADS_ACCESS_TOKEN` | Threads posting | Meta Developer Portal |

### Newsletter (Optional)

| Secret | Purpose | Where to get |
|--------|---------|--------------|
| `RESEND_API_KEY` | Send emails | [Resend](https://resend.com) |
| `SUPABASE_URL` | Database | [Supabase](https://supabase.com) |
| `SUPABASE_SERVICE_KEY` | Database (admin) | Supabase Dashboard |

### Notifications (Optional)

| Secret | Purpose | Where to get |
|--------|---------|--------------|
| `DISCORD_WEBHOOK_URL` | Discord notifications | Server Settings > Integrations |
| `SLACK_WEBHOOK_URL` | Slack notifications | Slack App Settings |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Scheduled Triggers                          │
├─────────────────────────────────────────────────────────────────┤
│   release-monitor     blog-monitor        sync-upstream         │
│   (hourly)           (every 2h)          (daily)                │
│       │                   │                  │                  │
│       ▼                   ▼                  ▼                  │
│   ┌───────┐           ┌───────┐          ┌───────┐              │
│   │Detect │           │Fetch  │          │Update │              │
│   │Release│           │Content│          │Submod │              │
│   └───┬───┘           └───┬───┘          └───┬───┘              │
│       │                   │                  │                  │
│       ▼                   ▼                  ▼                  │
│   ┌───────────────────────────────────────────────┐             │
│   │              Claude API (Content Gen)          │             │
│   └───────────────────────────────────────────────┘             │
│       │                   │                  │                  │
│       ▼                   ▼                  ▼                  │
│   ┌───────┐           ┌───────┐          ┌───────┐              │
│   │Notify │           │Create │          │Create │              │
│   │Discord│           │Article│          │Issue  │              │
│   └───────┘           └───────┘          └───────┘              │
│                           │                                      │
│                           ▼                                      │
│                      ┌───────────┐                               │
│                      │social-post│ (manual trigger)              │
│                      └─────┬─────┘                               │
│                            │                                     │
│                      ┌─────┴─────┐                               │
│                      ▼           ▼                               │
│                   ┌─────┐     ┌───────┐                          │
│                   │  X  │     │Threads│                          │
│                   └─────┘     └───────┘                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD Pipeline                              │
├─────────────────────────────────────────────────────────────────┤
│   Push/PR to main                                                │
│       │                                                          │
│       ▼                                                          │
│   ┌──────────────────────────────────────────────┐               │
│   │                   ci.yml                      │               │
│   │  ┌─────────┬─────────┬─────────┬─────────┐   │               │
│   │  │validate │  build  │  lint   │validate │   │               │
│   │  │ config  │ website │  check  │  hooks  │   │               │
│   │  └─────────┴─────────┴─────────┴─────────┘   │               │
│   └──────────────────────────────────────────────┘               │
│       │                                                          │
│       ▼                                                          │
│   Auto-deploy (Cloudflare/Vercel/Netlify)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Customization

### Changing Monitored Repository

In `release-monitor.yml`:

```yaml
env:
  REPO_TO_MONITOR: owner/repo  # Change this
```

### Adjusting Schedule

```yaml
on:
  schedule:
    - cron: '0 * * * *'    # Hourly
    - cron: '0 */2 * * *'  # Every 2 hours
    - cron: '0 0 * * *'    # Daily at midnight
    - cron: '0 0 * * 0'    # Weekly on Sunday
```

### Adding Notification Channels

See individual workflow files for examples of:
- Discord webhooks
- Slack webhooks
- Email via Resend
- GitHub Issues

---

## Best Practices

1. **Use Secrets for Sensitive Data**
   - Never hardcode API keys
   - Use `${{ secrets.NAME }}` syntax

2. **Rate Limiting**
   - Add delays between API calls
   - Use scheduled triggers wisely

3. **Error Handling**
   - Use `continue-on-error: true` for non-critical steps
   - Always check API responses

4. **Caching**
   - Cache npm/pnpm dependencies
   - Cache build artifacts

5. **Permissions**
   - Use minimal required permissions
   - Specify explicitly in each job

---

## Files

- [release-monitor.yml](./release-monitor.yml) - Monitor GitHub releases
- [blog-monitor.yml](./blog-monitor.yml) - Monitor blog/RSS feeds
- [social-post.yml](./social-post.yml) - Post to social media
- [newsletter-trigger.yml](./newsletter-trigger.yml) - Newsletter automation
- [sync-upstream.yml](./sync-upstream.yml) - Submodule sync
- [ci.yml](./ci.yml) - CI/CD pipeline

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Syntax Generator](https://crontab.guru)
- [Claude API Documentation](https://docs.anthropic.com)
- [Newsletter System Example](../../examples/newsletter-system.md)

---

*Based on production workflows from [claude-world.com](https://claude-world.com)*
