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

這個 workflow 實作了架構圖中的 Discord 與文章 jobs。X/Twitter 發文與 Email 電子報的做法相同，請參考 GitHub Actions 套件中的 [`social-post.yml`](../../templates/github-actions-suite/social-post.yml) 與 [`newsletter-trigger.yml`](../../templates/github-actions-suite/newsletter-trigger.yml)。

### 在 workflow 中呼叫 Claude API

- **依任務選擇模型。** `claude-haiku-5-5` 快速又便宜，適合短社群貼文與 JSON 擷取；`claude-sonnet-5-5` 負責撰寫長篇文章。`claude-sonnet-4-20250514` 等舊 ID 已退役，呼叫會失敗。
- **讀取 text 區塊，而不是 `content[0]`。** 目前的模型會先思考再回答，回應可能以 `thinking` 區塊開頭。請合併所有 `type` 為 `text` 的區塊。
- **為 `max_tokens` 預留空間。** 思考也會計入上限，短輸出至少設為 4096。簡單任務可加上 `output_config: {effort: "low"}` 縮短思考。
- **不要傳送取樣參數。** 目前的模型遇到非預設的 `temperature`、`top_p`、`top_k` 會回傳 400 錯誤。
- **用 `jq` 組 JSON。** `jq -n --arg` 會正確跳脫 prompt 與 payload 中的引號和換行，手刻 JSON 字串很容易出錯。

## Claude Code GitHub Action

上面的 workflow 只送出單次 Messages API 請求，生成文字已經足夠。如果你希望在 CI 中執行 Claude Code agent 本身，讓它讀取 repository、使用工具、回應 `@claude`、審查 pull request 或推送修正，請使用官方的 [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action)：

- **快速設定：** 在 Claude Code 中執行 `/install-github-app`。它會安裝 Claude GitHub App、把 API key 存成 secret，並開一個包含 workflow 的 pull request。
- **互動模式：** 沒有 `prompt` 輸入時，有寫入權限的人在 issue、pull request 或 review 中提到 `@claude`，Claude 就會回應。
- **自動化模式：** 提供 `prompt` 輸入（純文字或像 `/code-review:code-review` 這樣的 skill）時，Claude 可以在任何觸發條件下執行，包括 `schedule`。
- **CLI 參數：** 透過 `claude_args` 傳入 `--model`、`--max-turns`、`--allowedTools`、`--append-system-prompt` 或 `--mcp-config`。
- **認證：** 使用 `anthropic_api_key`，或用 `claude_code_oauth_token`（以 `claude setup-token` 建立）改用 Claude 訂閱。
- **v0 輸入已移除：** `direct_prompt`、`custom_instructions`、`model`、`max_turns`、`allowed_tools`、`claude_env`、`mcp_config` 已改為 `prompt`、`claude_args` 與 `settings`。

以下取自官方文件的排程 workflow 會把每日報告寫進執行紀錄。Claude 透過 action 提供的 GitHub 工具讀取 commits 與 issues，因此不需要 checkout：

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

現成範本：[`claude.yml`](../../templates/github-actions-suite/claude.yml) 回應 `@claude`，[`claude-code-review.yml`](../../templates/github-actions-suite/claude-code-review.yml) 會審查每個 pull request。只有具寫入權限的使用者能觸發這個 action；不要把 issue 標題這類不受信任的文字放進 `run:` 腳本或 `prompt` 輸入。

## 關鍵模式

### 1. Job 相依性與資料傳遞

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

請透過 `env:` 把值傳進腳本；直接把 `${{ }}` 運算式貼進 `run:`，可能讓精心構造的內容被當成 shell 程式碼執行。

### 2. 多行內容的 Base64 編碼

```bash
# Encode
BODY_B64=$(printf '%s' "$MULTI_LINE_CONTENT" | base64 -w 0)
echo "body=$BODY_B64" >> "$GITHUB_OUTPUT"

# Decode
CONTENT=$(base64 -d <<<"$BODY_B64")
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
    git pull --rebase origin main  # Always pull before push
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
| GitHub Actions | 公開 repo 免費（私有 repo 在 Free 方案每月 2,000 分鐘） |
| Claude API（每個 release 1 次 Haiku 呼叫 + 3 篇 Sonnet 文章） | ~$0.15/release |
| **每月（4 個 releases）** | **~$0.60** |

估算以定價計算（Haiku 5.5 每百萬 input/output tokens 起價 $0.10/$0.50，Sonnet 5.5 為 $2/$10），並包含思考 tokens。請查看[最新定價](https://platform.claude.com/docs/en/about-claude/pricing)。

## 相關資源

- [48 小時網站案例研究](../../case-studies/zh-TW/48-hour-website.md)
- [Release Monitor 範本](../../templates/release-monitor-workflow.yml)
- [GitHub Actions 套件](../../templates/github-actions-suite/)
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Claude API 文件](https://platform.claude.com/docs)

---

*這個自動化 24/7 全天候運作，無需人工介入，展示了結合 Claude API 與 GitHub Actions 的威力。*
