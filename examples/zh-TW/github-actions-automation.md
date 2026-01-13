# 使用 Claude API 的 GitHub Actions 自動化

> 建立完全自動化的工作流程，使用 Claude API 進行內容生成、通知等

## 概述

這個範例展示如何建立一個 **Release Monitor**：
1. 監控 GitHub repository 的新 releases
2. 使用 Claude API 生成內容
3. 發送通知到多個平台
4. 自動生成文章並提交

## 架構

```
┌────────────────────────────────────────────────────────────┐
│                   GitHub Actions Workflow                   │
│                      （每小時觸發）                          │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│  Job 1: check-release                                       │
│  ├── 從目標 repo 取得最新 release                           │
│  ├── 與上次已知版本比較                                      │
│  └── 輸出: new_release (true/false), version, body          │
└────────────────────────────────────────────────────────────┘
                              │
                    (如果 new_release == true)
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│  Job 2: generate-content                                    │
│  ├── 使用 release notes 呼叫 Claude API                     │
│  └── 輸出: social posts, newsletter slug                    │
└────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Job 3: Discord   │ │ Job 4: X/Twitter │ │ Job 5: Email     │
│ 通知             │ │ Thread           │ │ Newsletter       │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│  Job 6: generate-newsletter                                 │
│  ├── 呼叫 Claude API 生成文章（3 種語言）                    │
│  ├── 寫入 markdown 檔案                                     │
│  ├── Git commit 和 push                                     │
│  └── 觸發部署                                               │
└────────────────────────────────────────────────────────────┘
```

## 完整 Workflow 範例

### `.github/workflows/release-monitor.yml`

```yaml
name: Release Monitor

on:
  schedule:
    - cron: '0 * * * *'  # 每小時
  workflow_dispatch:
    inputs:
      force_notify:
        description: '即使沒有新 release 也強制通知'
        required: false
        default: false
        type: boolean

env:
  REPO_TO_MONITOR: anthropics/claude-code
  VERSION_FILE: .github/last-known-version.txt

jobs:
  # ============================================
  # Job 1: 檢查新 releases
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
            echo "🆕 偵測到新 release: $LATEST_VERSION"
          else
            echo "new_release=false" >> $GITHUB_OUTPUT
            echo "✓ 沒有新 release"
          fi

          echo "version=$LATEST_VERSION" >> $GITHUB_OUTPUT
          echo "release_name=${{ steps.fetch.outputs.release_name }}" >> $GITHUB_OUTPUT
          echo "release_url=${{ steps.fetch.outputs.release_url }}" >> $GITHUB_OUTPUT

          # Base64 編碼以安全輸出
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
  # Job 2: 使用 Claude API 生成內容
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
          # 解碼 release body
          RELEASE_BODY=$(echo "$RELEASE_BODY_B64" | base64 -d)

          # 建立 Claude 的 prompt
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

          # 呼叫 Claude API
          RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
            -H "Content-Type: application/json" \
            -H "x-api-key: $ANTHROPIC_API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -d "{
              \"model\": \"claude-sonnet-4-20250514\",
              \"max_tokens\": 2000,
              \"messages\": [{\"role\": \"user\", \"content\": $(echo "$PROMPT" | jq -Rs .)}]
            }")

          # 提取內容
          CONTENT=$(echo "$RESPONSE" | jq -r '.content[0].text')

          # 解析並設定輸出
          echo "main_post_en=$(echo "$CONTENT" | jq -r '.main_post_en' | base64 -w 0)" >> $GITHUB_OUTPUT
          echo "main_post_zh=$(echo "$CONTENT" | jq -r '.main_post_zh' | base64 -w 0)" >> $GITHUB_OUTPUT
          echo "newsletter_slug=$(echo "$CONTENT" | jq -r '.newsletter_slug')" >> $GITHUB_OUTPUT

          # 儲存 Discord 內容為 JSON
          echo "$CONTENT" | jq '{title: .discord_title, description: .discord_description, features: .discord_features}' > /tmp/discord.json
          echo "discord_content=$(cat /tmp/discord.json | base64 -w 0)" >> $GITHUB_OUTPUT

  # ============================================
  # Job 3: Discord 通知
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
  # Job 4: 生成並提交文章
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

          # 為每種語言生成文章內容
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

            # 決定輸出路徑
            if [ "$LANG" = "en" ]; then
              OUTPUT_PATH="src/content/articles/${NEWSLETTER_SLUG}.md"
            else
              OUTPUT_PATH="src/content/articles/${LANG}/${NEWSLETTER_SLUG}.md"
            fi

            mkdir -p $(dirname "$OUTPUT_PATH")
            echo "$CONTENT" > "$OUTPUT_PATH"
            echo "已建立: $OUTPUT_PATH"
          done

      - name: Commit and push
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add src/content/articles/

          if git diff --staged --quiet; then
            echo "沒有變更需要提交"
          else
            git commit -m "content: add newsletter for ${{ needs.check-release.outputs.version }}"
            git pull --rebase origin main  # 避免競態條件
            git push
          fi
```

## 關鍵模式

### 1. Job 相依性與資料傳遞

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

### 2. 多行內容的 Base64 編碼

```yaml
# 編碼
BODY_B64=$(echo "$MULTI_LINE_CONTENT" | base64 -w 0)
echo "body=$BODY_B64" >> $GITHUB_OUTPUT

# 解碼
CONTENT=$(echo "$BODY_B64" | base64 -d)
```

### 3. 條件式 Job 執行

```yaml
jobs:
  notify:
    needs: check-release
    if: needs.check-release.outputs.new_release == 'true'
```

### 4. 競態條件預防

```yaml
- name: Commit and push
  run: |
    git commit -m "message"
    git pull --rebase origin main  # push 前總是先 pull
    git push
```

## 所需 Secrets

| Secret | 用途 |
|--------|---------|
| `ANTHROPIC_API_KEY` | Claude API 認證 |
| `DISCORD_WEBHOOK_URL` | Discord 通知 |
| `X_API_KEY` | X/Twitter 發文 |
| `X_API_SECRET` | X/Twitter 發文 |
| `X_ACCESS_TOKEN` | X/Twitter 發文 |
| `X_ACCESS_SECRET` | X/Twitter 發文 |

## 測試

### 手動觸發

```bash
gh workflow run release-monitor.yml -f force_notify=true
```

### 查看 Logs

```bash
gh run list --workflow=release-monitor.yml
gh run view <run-id> --log
```

## 成本估算

| 元件 | 成本 |
|-----------|------|
| GitHub Actions | 免費（2,000 分鐘/月） |
| Claude API（~5 次呼叫/release） | ~$0.10/release |
| **每月（4 個 releases）** | **~$0.40** |

## 相關資源

- [48 小時網站案例研究](../case-studies/48-hour-website.md)
- [Release Monitor 範本](../templates/release-monitor-workflow.yml)
- [Claude API 文件](https://docs.anthropic.com/en/api)

---

*這個自動化 24/7 全天候運作，無需人工介入，展示了結合 Claude API 與 GitHub Actions 的威力。*
