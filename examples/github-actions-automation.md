# GitHub Actions Automation with Claude API

> Build fully automated workflows that use Claude API for content generation, notifications, and more

## Overview

This example shows how to build a **Release Monitor** that:
1. Monitors a GitHub repository for new releases
2. Uses Claude API to generate content
3. Sends notifications to multiple platforms
4. Auto-generates articles and commits them

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   GitHub Actions Workflow                   │
│                      (Hourly trigger)                       │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│  Job 1: check-release                                       │
│  ├── Fetch latest release from target repo                  │
│  ├── Compare with last known version                        │
│  └── Output: new_release (true/false), version, body        │
└────────────────────────────────────────────────────────────┘
                              │
                    (if new_release == true)
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│  Job 2: generate-content                                    │
│  ├── Call Claude API with release notes                     │
│  └── Output: social posts, newsletter slug                  │
└────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Job 3: Discord   │ │ Job 4: X/Twitter │ │ Job 5: Email     │
│ Notification     │ │ Thread           │ │ Newsletter       │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│  Job 6: generate-newsletter                                 │
│  ├── Call Claude API to generate articles (3 languages)    │
│  ├── Write markdown files                                   │
│  ├── Git commit and push                                    │
│  └── Trigger deployment                                     │
└────────────────────────────────────────────────────────────┘
```

## Complete Workflow Example

### `.github/workflows/release-monitor.yml`

```yaml
name: Release Monitor

on:
  schedule:
    - cron: '0 * * * *'  # Every hour

  workflow_dispatch:
    inputs:
      force_notify:
        description: 'Force notification even if no new release'
        required: false
        default: false
        type: boolean

permissions:
  contents: read

env:
  REPO_TO_MONITOR: anthropics/claude-code
  VERSION_FILE: .github/last-known-version.txt
  CLAUDE_FAST_MODEL: claude-haiku-5-5  # Short social copy and JSON extraction
  CLAUDE_MODEL: claude-sonnet-5-5      # Long-form articles

jobs:
  # ============================================
  # Job 1: Check for new releases
  # ============================================
  check-release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    outputs:
      new_release: ${{ steps.check.outputs.new_release }}
      version: ${{ steps.fetch.outputs.version }}
      release_name: ${{ steps.fetch.outputs.release_name }}
      release_url: ${{ steps.fetch.outputs.release_url }}
      release_body: ${{ steps.fetch.outputs.release_body }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Get latest release
        id: fetch
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          RELEASE_JSON=$(gh api "repos/$REPO_TO_MONITOR/releases/latest")

          {
            echo "version=$(jq -r '.tag_name' <<<"$RELEASE_JSON")"
            echo "release_name=$(jq -r '(.name // .tag_name) | gsub("[\r\n]"; " ")' <<<"$RELEASE_JSON")"
            echo "release_url=$(jq -r '.html_url' <<<"$RELEASE_JSON")"
            # Base64 encode for safe multi-line output
            echo "release_body=$(jq -r '.body // "No release notes"' <<<"$RELEASE_JSON" | head -c 3000 | base64 -w 0)"
          } >> "$GITHUB_OUTPUT"

      - name: Check if new release
        id: check
        env:
          LATEST_VERSION: ${{ steps.fetch.outputs.version }}
          FORCE_NOTIFY: ${{ inputs.force_notify }}
        run: |
          LAST_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "none")

          if [ "$LATEST_VERSION" != "$LAST_VERSION" ] || [ "$FORCE_NOTIFY" = "true" ]; then
            echo "new_release=true" >> "$GITHUB_OUTPUT"
            echo "🆕 New release detected: $LATEST_VERSION"
          else
            echo "new_release=false" >> "$GITHUB_OUTPUT"
            echo "✓ No new release"
          fi

      - name: Update last known version
        if: steps.check.outputs.new_release == 'true'
        env:
          LATEST_VERSION: ${{ steps.fetch.outputs.version }}
        run: |
          mkdir -p "$(dirname "$VERSION_FILE")"
          echo "$LATEST_VERSION" > "$VERSION_FILE"

          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add "$VERSION_FILE"
          git diff --staged --quiet || git commit -m "chore: update last known version to $LATEST_VERSION"
          git push

  # ============================================
  # Job 2: Generate content with Claude API
  # ============================================
  generate-content:
    needs: check-release
    runs-on: ubuntu-latest
    if: needs.check-release.outputs.new_release == 'true'
    outputs:
      main_post_en: ${{ steps.generate.outputs.main_post_en }}
      main_post_zh: ${{ steps.generate.outputs.main_post_zh }}
      discord_content: ${{ steps.generate.outputs.discord_content }}
      newsletter_slug: ${{ steps.generate.outputs.newsletter_slug }}

    steps:
      - name: Generate content with Claude API
        id: generate
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          VERSION: ${{ needs.check-release.outputs.version }}
          RELEASE_NAME: ${{ needs.check-release.outputs.release_name }}
          RELEASE_URL: ${{ needs.check-release.outputs.release_url }}
          RELEASE_BODY_B64: ${{ needs.check-release.outputs.release_body }}
        run: |
          # Decode release body
          RELEASE_BODY=$(base64 -d <<<"$RELEASE_BODY_B64")

          # Create prompt for Claude (variables expand; their contents are never executed)
          PROMPT=$(cat <<EOF
          You are a developer advocate creating social media posts.

          Release Info:
          - Version: $VERSION
          - Name: $RELEASE_NAME
          - URL: $RELEASE_URL
          - Notes: $RELEASE_BODY

          Generate JSON with:
          {
            "main_post_en": "English post (280 chars max)",
            "main_post_zh": "繁中貼文 (450 chars max)",
            "discord_title": "Discord embed title",
            "discord_description": "2-3 sentences",
            "discord_features": "• Feature 1\n• Feature 2",
            "newsletter_slug": "version-slug-release"
          }

          Output ONLY valid JSON, without markdown fences.
          EOF
          )

          # Build the request with jq so the prompt is escaped correctly
          REQUEST=$(jq -n --arg model "$CLAUDE_FAST_MODEL" --arg prompt "$PROMPT" '{
            model: $model,
            max_tokens: 4096,
            output_config: {effort: "low"},
            messages: [{role: "user", content: $prompt}]
          }')

          # Call Claude API
          RESPONSE=$(curl -sS https://api.anthropic.com/v1/messages \
            -H "content-type: application/json" \
            -H "x-api-key: $ANTHROPIC_API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -d "$REQUEST")

          if jq -e '.error' <<<"$RESPONSE" > /dev/null; then
            echo "API error: $(jq -r '.error.message' <<<"$RESPONSE")"
            exit 1
          fi

          # Extract content. Current models can return a thinking block before
          # the text, so join the text blocks instead of reading .content[0].
          CONTENT=$(jq -r '[.content[] | select(.type == "text") | .text] | join("")' <<<"$RESPONSE" | sed '/^```/d')

          # Parse and set outputs
          {
            echo "main_post_en=$(jq -r '.main_post_en' <<<"$CONTENT" | base64 -w 0)"
            echo "main_post_zh=$(jq -r '.main_post_zh' <<<"$CONTENT" | base64 -w 0)"
            echo "newsletter_slug=$(jq -r '.newsletter_slug' <<<"$CONTENT")"
            # Save Discord content as JSON
            echo "discord_content=$(jq -c '{title: .discord_title, description: .discord_description, features: .discord_features}' <<<"$CONTENT" | base64 -w 0)"
          } >> "$GITHUB_OUTPUT"

  # ============================================
  # Job 3: Discord notification
  # ============================================
  notify-discord:
    needs: [check-release, generate-content]
    runs-on: ubuntu-latest

    steps:
      - name: Send Discord notification
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          RELEASE_URL: ${{ needs.check-release.outputs.release_url }}
          DISCORD_CONTENT_B64: ${{ needs.generate-content.outputs.discord_content }}
        run: |
          # jq builds the payload, so quotes and newlines in the content are escaped
          base64 -d <<<"$DISCORD_CONTENT_B64" |
            jq --arg url "$RELEASE_URL" '{embeds: [{
              title: .title,
              description: .description,
              url: $url,
              color: 5763719,
              fields: [{name: "✨ Features", value: (.features | .[0:1024])}]
            }]}' |
            curl -sS --fail-with-body -X POST "$DISCORD_WEBHOOK_URL" \
              -H "Content-Type: application/json" \
              -d @-

  # ============================================
  # Job 4: Generate and commit articles
  # ============================================
  generate-newsletter:
    needs: [check-release, generate-content]
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Generate articles with Claude API
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          VERSION: ${{ needs.check-release.outputs.version }}
          RELEASE_BODY_B64: ${{ needs.check-release.outputs.release_body }}
          NEWSLETTER_SLUG: ${{ needs.generate-content.outputs.newsletter_slug }}
        run: |
          RELEASE_BODY=$(base64 -d <<<"$RELEASE_BODY_B64")
          PUB_DATE=$(date +%Y-%m-%d)
          # The slug comes from the model, so keep only safe filename characters
          SLUG=$(printf '%s' "$NEWSLETTER_SLUG" | tr -cd 'a-z0-9-')

          # Generate article content for each language
          for LANG in en zh-tw ja; do
            PROMPT=$(cat <<EOF
          Generate a release notes article in $LANG for version $VERSION.
          Release notes: $RELEASE_BODY

          Output markdown with frontmatter, without wrapping it in a code fence:
          ---
          title: "..."
          description: "..."
          pubDate: "$PUB_DATE"
          version: "$VERSION"
          ---

          [Article content...]
          EOF
            )

            REQUEST=$(jq -n --arg model "$CLAUDE_MODEL" --arg prompt "$PROMPT" '{
              model: $model,
              max_tokens: 8192,
              messages: [{role: "user", content: $prompt}]
            }')

            RESPONSE=$(curl -sS https://api.anthropic.com/v1/messages \
              -H "content-type: application/json" \
              -H "x-api-key: $ANTHROPIC_API_KEY" \
              -H "anthropic-version: 2023-06-01" \
              -d "$REQUEST")

            CONTENT=$(jq -r '[.content[] | select(.type == "text") | .text] | join("")' <<<"$RESPONSE")

            # Determine output path
            if [ "$LANG" = "en" ]; then
              OUTPUT_PATH="src/content/articles/${SLUG}.md"
            else
              OUTPUT_PATH="src/content/articles/${LANG}/${SLUG}.md"
            fi

            mkdir -p "$(dirname "$OUTPUT_PATH")"
            printf '%s\n' "$CONTENT" > "$OUTPUT_PATH"
            echo "Created: $OUTPUT_PATH"
          done

      - name: Commit and push
        env:
          VERSION: ${{ needs.check-release.outputs.version }}
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add src/content/articles/

          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "content: add newsletter for $VERSION"
            git pull --rebase origin main  # Avoid race condition
            git push
          fi
```

The workflow implements the Discord and article jobs from the diagram. X/Twitter posting and email newsletters follow the same pattern; see [`social-post.yml`](../templates/github-actions-suite/social-post.yml) and [`newsletter-trigger.yml`](../templates/github-actions-suite/newsletter-trigger.yml) in the GitHub Actions suite.

### Calling the Claude API from a workflow

- **Pick the model per task.** `claude-haiku-5-5` handles short social copy and JSON extraction quickly and cheaply; `claude-sonnet-5-5` writes the long-form articles. Older IDs such as `claude-sonnet-4-20250514` are retired and now fail.
- **Read the text blocks, not `content[0]`.** Current models think before answering, and the response can start with a `thinking` block. Join the blocks whose `type` is `text`.
- **Leave room in `max_tokens`.** Thinking counts toward the limit, so use at least 4096 for short outputs. For simple tasks, `output_config: {effort: "low"}` keeps thinking short.
- **Don't send sampling parameters.** Current models reject non-default `temperature`, `top_p`, and `top_k` with a 400 error.
- **Build JSON with `jq`.** `jq -n --arg` escapes quotes and newlines in prompts and payloads, which hand-built JSON strings get wrong.

## Claude Code GitHub Action

The workflow above sends single Messages API requests, which is enough for text generation. When you want the Claude Code agent itself in CI, so it can read the repository, run tools, answer `@claude` requests, review pull requests, or push a fix, use the official [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action):

- **Quick setup:** run `/install-github-app` in Claude Code. It installs the Claude GitHub App, stores the API key as a secret, and opens a pull request with the workflow.
- **Interactive mode:** without a `prompt` input, Claude responds when someone with write access mentions `@claude` in an issue, pull request, or review.
- **Automation mode:** with a `prompt` input (plain text or a skill such as `/code-review:code-review`), Claude runs on any trigger, including `schedule`.
- **CLI flags:** pass `--model`, `--max-turns`, `--allowedTools`, `--append-system-prompt`, or `--mcp-config` through `claude_args`.
- **Authentication:** `anthropic_api_key`, or `claude_code_oauth_token` (created with `claude setup-token`) to use a Claude subscription.
- **v0 inputs were removed:** `direct_prompt`, `custom_instructions`, `model`, `max_turns`, `allowed_tools`, `claude_env`, and `mcp_config` became `prompt`, `claude_args`, and `settings`.

This scheduled workflow, from the official docs, writes a daily report to the run log. Claude reads commits and issues through the GitHub tools the action provides, so no checkout is needed:

```yaml
name: Daily Report

on:
  schedule:
    - cron: '0 9 * * *'  # 09:00 UTC every day

permissions:
  contents: read

jobs:
  report:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      issues: read
      id-token: write
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: |
            --model claude-sonnet-5-5
            --max-turns 10
            --allowedTools "mcp__github__list_commits,mcp__github__list_issues"
```

Ready-made templates: [`claude.yml`](../templates/github-actions-suite/claude.yml) answers `@claude` mentions, and [`claude-code-review.yml`](../templates/github-actions-suite/claude-code-review.yml) reviews every pull request. Only users with write access can trigger the action; keep untrusted text such as issue titles out of `run:` scripts and `prompt` inputs.

## Key Patterns

### 1. Job Dependencies & Data Passing

```yaml
jobs:
  job-a:
    runs-on: ubuntu-latest
    outputs:
      data: ${{ steps.step1.outputs.data }}
    steps:
      - id: step1
        run: echo "data=value" >> "$GITHUB_OUTPUT"

  job-b:
    needs: job-a
    runs-on: ubuntu-latest
    steps:
      - env:
          DATA: ${{ needs.job-a.outputs.data }}
        run: echo "$DATA"
```

Pass values into scripts through `env:`; pasting `${{ }}` expressions straight into `run:` lets crafted content run as shell code.

### 2. Base64 Encoding for Multi-line Content

```bash
# Encode
BODY_B64=$(printf '%s' "$MULTI_LINE_CONTENT" | base64 -w 0)
echo "body=$BODY_B64" >> "$GITHUB_OUTPUT"

# Decode
CONTENT=$(base64 -d <<<"$BODY_B64")
```

### 3. Conditional Job Execution

```yaml
jobs:
  notify:
    needs: check-release
    if: needs.check-release.outputs.new_release == 'true'
```

### 4. Race Condition Prevention

```yaml
- name: Commit and push
  run: |
    git commit -m "message"
    git pull --rebase origin main  # Always pull before push
    git push
```

## Secrets Required

| Secret | Purpose |
|--------|---------|
| `ANTHROPIC_API_KEY` | Claude API authentication |
| `DISCORD_WEBHOOK_URL` | Discord notifications |
| `X_API_KEY` | X/Twitter posting |
| `X_API_SECRET` | X/Twitter posting |
| `X_ACCESS_TOKEN` | X/Twitter posting |
| `X_ACCESS_SECRET` | X/Twitter posting |

## Testing

### Manual Trigger

```bash
gh workflow run release-monitor.yml -f force_notify=true
```

### View Logs

```bash
gh run list --workflow=release-monitor.yml
gh run view <run-id> --log
```

## Cost Estimation

| Component | Cost |
|-----------|------|
| GitHub Actions | Free for public repos (2,000 min/month for private repos on the Free plan) |
| Claude API (1 Haiku call + 3 Sonnet articles per release) | ~$0.15/release |
| **Monthly (4 releases)** | **~$0.60** |

Estimates use list prices (Haiku 5.5 from $0.10/$0.50 and Sonnet 5.5 $2/$10 per million input/output tokens) and include thinking tokens. Check [current pricing](https://platform.claude.com/docs/en/about-claude/pricing).

## Related Resources

- [48-Hour Website Case Study](../case-studies/48-hour-website.md)
- [Release Monitor Template](../templates/release-monitor-workflow.yml)
- [GitHub Actions Suite](../templates/github-actions-suite/)
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Claude API Documentation](https://platform.claude.com/docs)

---

*This automation runs 24/7 without human intervention, demonstrating the power of combining Claude API with GitHub Actions.*
