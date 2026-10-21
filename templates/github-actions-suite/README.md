# GitHub Actions Automation Suite

> Complete set of GitHub Actions workflows for automated community and project management.

This template collection provides production-ready workflows for monitoring upstream repos, generating content, posting to social media, running Claude Code in your repository, and automating CI/CD.

Two kinds of Claude integration are used:

- **Claude Code GitHub Action** (`claude.yml`, `claude-code-review.yml`): runs the full Claude Code agent with access to your repository, through [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action). Use it when Claude should read code, answer `@claude` requests, review PRs, or push changes.
- **Claude API calls** (the monitoring, social, and newsletter workflows): one Messages API request per item for simple text generation. They use `claude-haiku-5-5` for short, high-volume tasks and `claude-sonnet-5-5` for long-form writing; change `CLAUDE_MODEL` in each file to switch.

---

## Workflows Included

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| [claude.yml](./claude.yml) | Claude Code answers `@claude` in issues and PRs | Comments, reviews, issues |
| [claude-code-review.yml](./claude-code-review.yml) | Automated Claude Code review on every PR | Pull request |
| [release-monitor.yml](./release-monitor.yml) | Monitor upstream repos for new releases | Scheduled (hourly) |
| [blog-monitor.yml](./blog-monitor.yml) | Monitor RSS/websites for new content | Scheduled (2 hours) |
| [social-post.yml](./social-post.yml) | Post to X | Manual |
| [newsletter-trigger.yml](./newsletter-trigger.yml) | Generate and send newsletters | Manual + Release |
| [sync-upstream.yml](./sync-upstream.yml) | Keep submodules updated | Scheduled (daily) |
| [ci.yml](./ci.yml) | Build, lint, and validate | Push/PR |

---

## Quick Start

```bash
# 1. Copy the workflows you need to your repo
mkdir -p .github/workflows
cp templates/github-actions-suite/claude.yml .github/workflows/
cp templates/github-actions-suite/release-monitor.yml .github/workflows/

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
| `ANTHROPIC_API_KEY` | Claude API for content generation and the Claude Code GitHub Action | [Claude Console](https://platform.claude.com) |

### Claude Code GitHub Action

`claude.yml` and `claude-code-review.yml` also need the [Claude GitHub App](https://github.com/apps/claude) installed on the repository. The fastest setup is to run `/install-github-app` inside Claude Code: it installs the app, stores the secret, and opens a pull request with the workflow. To bill a Claude subscription instead of the API, store a token from `claude setup-token` as `CLAUDE_CODE_OAUTH_TOKEN` and pass it as `claude_code_oauth_token`.

### Social Media (Optional)

| Secret | Purpose | Where to get |
|--------|---------|--------------|
| `X_API_KEY` | X/Twitter posting | [X Developer Portal](https://developer.x.com) |
| `X_API_SECRET` | X/Twitter posting | X Developer Portal |
| `X_ACCESS_TOKEN` | X/Twitter posting | X Developer Portal |
| `X_ACCESS_SECRET` | X/Twitter posting | X Developer Portal |

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
│                            ▼                                     │
│                         ┌─────┐                                  │
│                         │  X  │                                  │
│                         └─────┘                                  │
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

### Choosing the Claude Model

The API-based workflows read the model from `CLAUDE_MODEL`:

```yaml
env:
  CLAUDE_MODEL: claude-haiku-5-5   # or claude-sonnet-5-5, claude-opus-5-5
```

For the Claude Code GitHub Action, pass CLI flags through `claude_args`:

```yaml
claude_args: |
  --model claude-sonnet-5-5
  --max-turns 30
```

Current models think before answering, and the thinking is returned as its own content block. The templates therefore read the text blocks of each response instead of `content[0]`, and leave `max_tokens` headroom for thinking.

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

2. **Keep Untrusted Input Out of Scripts**
   - Pass `${{ github.event.* }}` and `${{ inputs.* }}` values through `env:` and quote them (`"$VAR"`); never paste them directly into a `run:` script
   - Only users with write access can trigger the Claude Code GitHub Action; keep it that way on public repositories

3. **Rate Limiting**
   - Add delays between API calls
   - Use scheduled triggers wisely

4. **Error Handling**
   - Use `continue-on-error: true` for non-critical steps
   - Always check API responses

5. **Caching**
   - Cache npm/pnpm dependencies
   - Cache build artifacts

6. **Permissions**
   - Use minimal required permissions
   - Set `permissions: contents: read` at the top and grant more per job

---

## Files

- [claude.yml](./claude.yml) - Claude Code `@claude` assistant
- [claude-code-review.yml](./claude-code-review.yml) - Automated PR review
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
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [claude-code-action](https://github.com/anthropics/claude-code-action)
- [Claude API Documentation](https://platform.claude.com/docs)
- [Newsletter System Example](../../examples/newsletter-system.md)

---

*Based on production workflows from [claude-world.com](https://claude-world.com)*
