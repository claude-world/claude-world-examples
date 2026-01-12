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

env:
  REPO_TO_MONITOR: anthropics/claude-code
  VERSION_FILE: .github/last-known-version.txt

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
      version: ${{ steps.check.outputs.version }}
      release_name: ${{ steps.check.outputs.release_name }}
      release_url: ${{ steps.check.outputs.release_url }}
      release_body: ${{ steps.check.outputs.release_body }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Get latest release
        id: fetch
        run: |
          RELEASE_JSON=$(curl -s "https://api.github.com/repos/${{ env.REPO_TO_MONITOR }}/releases/latest")

          VERSION=$(echo "$RELEASE_JSON" | jq -r '.tag_name')
          RELEASE_NAME=$(echo "$RELEASE_JSON" | jq -r '.name')
          RELEASE_URL=$(echo "$RELEASE_JSON" | jq -r '.html_url')
          RELEASE_BODY=$(echo "$RELEASE_JSON" | jq -r '.body // "No release notes"' | head -c 3000)

          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "release_name=$RELEASE_NAME" >> $GITHUB_OUTPUT
          echo "release_url=$RELEASE_URL" >> $GITHUB_OUTPUT
          echo "$RELEASE_BODY" > /tmp/release_body.txt

      - name: Check if new release
        id: check
        run: |
          LATEST_VERSION="${{ steps.fetch.outputs.version }}"

          if [ -f "${{ env.VERSION_FILE }}" ]; then
            LAST_VERSION=$(cat "${{ env.VERSION_FILE }}")
          else
            LAST_VERSION="none"
          fi

          if [ "$LATEST_VERSION" != "$LAST_VERSION" ] || [ "${{ github.event.inputs.force_notify }}" == "true" ]; then
            echo "new_release=true" >> $GITHUB_OUTPUT
            echo "🆕 New release detected: $LATEST_VERSION"
          else
            echo "new_release=false" >> $GITHUB_OUTPUT
            echo "✓ No new release"
          fi

          echo "version=$LATEST_VERSION" >> $GITHUB_OUTPUT
          echo "release_name=${{ steps.fetch.outputs.release_name }}" >> $GITHUB_OUTPUT
          echo "release_url=${{ steps.fetch.outputs.release_url }}" >> $GITHUB_OUTPUT

          # Base64 encode for safe output
          BODY_B64=$(base64 -w 0 /tmp/release_body.txt)
          echo "release_body=$BODY_B64" >> $GITHUB_OUTPUT

      - name: Update last known version
        if: steps.check.outputs.new_release == 'true'
        run: |
          echo "${{ steps.check.outputs.version }}" > "${{ env.VERSION_FILE }}"

          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add "${{ env.VERSION_FILE }}"
          git diff --staged --quiet || git commit -m "chore: update last known version to ${{ steps.check.outputs.version }}"
          git push || echo "Push failed"

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
          RELEASE_BODY=$(echo "$RELEASE_BODY_B64" | base64 -d)

          # Create prompt for Claude
          PROMPT="You are a developer advocate creating social media posts.

          Release Info:
          - Version: $VERSION
          - Name: $RELEASE_NAME
          - URL: $RELEASE_URL
          - Notes: $RELEASE_BODY

          Generate JSON with:
          {
            \"main_post_en\": \"English post (280 chars max)\",
            \"main_post_zh\": \"繁中貼文 (450 chars max)\",
            \"discord_title\": \"Discord embed title\",
            \"discord_description\": \"2-3 sentences\",
            \"discord_features\": \"• Feature 1\\n• Feature 2\",
            \"newsletter_slug\": \"version-slug-release\"
          }

          Output ONLY valid JSON."

          # Call Claude API
          RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
            -H "Content-Type: application/json" \
            -H "x-api-key: $ANTHROPIC_API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -d "{
              \"model\": \"claude-sonnet-4-20250514\",
              \"max_tokens\": 2000,
              \"messages\": [{\"role\": \"user\", \"content\": $(echo "$PROMPT" | jq -Rs .)}]
            }")

          # Extract content
          CONTENT=$(echo "$RESPONSE" | jq -r '.content[0].text')

          # Parse and set outputs
          echo "main_post_en=$(echo "$CONTENT" | jq -r '.main_post_en' | base64 -w 0)" >> $GITHUB_OUTPUT
          echo "main_post_zh=$(echo "$CONTENT" | jq -r '.main_post_zh' | base64 -w 0)" >> $GITHUB_OUTPUT
          echo "newsletter_slug=$(echo "$CONTENT" | jq -r '.newsletter_slug')" >> $GITHUB_OUTPUT

          # Save Discord content as JSON
          echo "$CONTENT" | jq '{title: .discord_title, description: .discord_description, features: .discord_features}' > /tmp/discord.json
          echo "discord_content=$(cat /tmp/discord.json | base64 -w 0)" >> $GITHUB_OUTPUT

  # ============================================
  # Job 3: Discord notification
  # ============================================
  notify-discord:
    needs: [check-release, generate-content]
    runs-on: ubuntu-latest
    if: needs.check-release.outputs.new_release == 'true'

    steps:
      - name: Send Discord notification
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          VERSION: ${{ needs.check-release.outputs.version }}
          RELEASE_URL: ${{ needs.check-release.outputs.release_url }}
          DISCORD_CONTENT_B64: ${{ needs.generate-content.outputs.discord_content }}
        run: |
          DISCORD_JSON=$(echo "$DISCORD_CONTENT_B64" | base64 -d)
          TITLE=$(echo "$DISCORD_JSON" | jq -r '.title')
          DESC=$(echo "$DISCORD_JSON" | jq -r '.description')
          FEATURES=$(echo "$DISCORD_JSON" | jq -r '.features')

          curl -X POST "$DISCORD_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{
              \"embeds\": [{
                \"title\": \"$TITLE\",
                \"description\": \"$DESC\",
                \"url\": \"$RELEASE_URL\",
                \"color\": 5763719,
                \"fields\": [
                  {\"name\": \"✨ Features\", \"value\": \"$FEATURES\"}
                ]
              }]
            }"

  # ============================================
  # Job 4: Generate and commit articles
  # ============================================
  generate-newsletter:
    needs: [check-release, generate-content]
    runs-on: ubuntu-latest
    if: needs.check-release.outputs.new_release == 'true'
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Generate articles with Claude API
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          VERSION: ${{ needs.check-release.outputs.version }}
          RELEASE_BODY_B64: ${{ needs.check-release.outputs.release_body }}
          NEWSLETTER_SLUG: ${{ needs.generate-content.outputs.newsletter_slug }}
        run: |
          RELEASE_BODY=$(echo "$RELEASE_BODY_B64" | base64 -d)

          # Generate article content for each language
          for LANG in en zh-tw ja; do
            PROMPT="Generate a release notes article in $LANG for version $VERSION.
            Release notes: $RELEASE_BODY

            Output markdown with frontmatter:
            ---
            title: \"...\"
            description: \"...\"
            pubDate: \"$(date +%Y-%m-%d)\"
            version: \"$VERSION\"
            ---

            [Article content...]"

            RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
              -H "Content-Type: application/json" \
              -H "x-api-key: $ANTHROPIC_API_KEY" \
              -H "anthropic-version: 2023-06-01" \
              -d "{
                \"model\": \"claude-sonnet-4-20250514\",
                \"max_tokens\": 4000,
                \"messages\": [{\"role\": \"user\", \"content\": $(echo "$PROMPT" | jq -Rs .)}]
              }")

            CONTENT=$(echo "$RESPONSE" | jq -r '.content[0].text')

            # Determine output path
            if [ "$LANG" = "en" ]; then
              OUTPUT_PATH="src/content/articles/${NEWSLETTER_SLUG}.md"
            else
              OUTPUT_PATH="src/content/articles/${LANG}/${NEWSLETTER_SLUG}.md"
            fi

            mkdir -p $(dirname "$OUTPUT_PATH")
            echo "$CONTENT" > "$OUTPUT_PATH"
            echo "Created: $OUTPUT_PATH"
          done

      - name: Commit and push
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add src/content/articles/

          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "content: add newsletter for ${{ needs.check-release.outputs.version }}"
            git pull --rebase origin main  # Avoid race condition
            git push
          fi
```

## Key Patterns

### 1. Job Dependencies & Data Passing

```yaml
jobs:
  job-a:
    outputs:
      data: ${{ steps.step1.outputs.data }}
    steps:
      - id: step1
        run: echo "data=value" >> $GITHUB_OUTPUT

  job-b:
    needs: job-a
    steps:
      - run: echo "${{ needs.job-a.outputs.data }}"
```

### 2. Base64 Encoding for Multi-line Content

```yaml
# Encode
BODY_B64=$(echo "$MULTI_LINE_CONTENT" | base64 -w 0)
echo "body=$BODY_B64" >> $GITHUB_OUTPUT

# Decode
CONTENT=$(echo "$BODY_B64" | base64 -d)
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
| GitHub Actions | Free (2,000 min/month) |
| Claude API (~5 calls/release) | ~$0.10/release |
| **Monthly (4 releases)** | **~$0.40** |

## Related Resources

- [48-Hour Website Case Study](../case-studies/48-hour-website.md)
- [Release Monitor Template](../templates/release-monitor-workflow.yml)
- [Claude API Documentation](https://docs.anthropic.com/en/api)

---

*This automation runs 24/7 without human intervention, demonstrating the power of combining Claude API with GitHub Actions.*
