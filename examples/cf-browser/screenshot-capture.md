# CF Browser: Screenshot Capture with Claude Code

> Use `browser_screenshot` and `browser_scrape` together to inspect a rendered page the way a user actually sees it.

## What This Solves

Static HTTP fetching misses client-rendered content, layout regressions, and hydration failures. `cf-browser` lets Claude capture the rendered page and extract visible content from the same session.

## Project MCP Configuration

Add a project-scoped server to `.mcp.json`:

```json
{
  "mcpServers": {
    "cf-browser": {
      "command": "<cf-browser-mcp-command>",
      "args": ["<provider-arg-1>", "<provider-arg-2>"],
      "env": {
        "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}",
        "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}"
      }
    }
  }
}
```

Replace the command and args with the launcher from your `cf-browser` provider. The prompts below assume the server exposes `browser_screenshot` and `browser_scrape`.

## Basic Workflow

1. Use `browser_screenshot` to capture the rendered state.
2. Use `browser_scrape` on the same page to extract headings, CTAs, or structured content.
3. Ask Claude to compare what is visible with what is present in the rendered DOM.

## Example Prompts for Claude Code

### 1. Landing page QA

```text
Use the cf-browser MCP server on https://example.com/pricing.

1. Call `browser_screenshot` on the page.
2. Call `browser_scrape` on the same page.
3. List the visible page title, main headings, CTA buttons, and pricing card names.
4. Flag anything that looks broken, duplicated, missing, or inconsistent between the screenshot and the scraped content.
```

### 2. Pre-release visual smoke test

```text
Use `browser_screenshot` and `browser_scrape` on https://staging.example.com/.

Check:
- whether the hero section rendered correctly
- whether the primary CTA is visible
- whether navigation labels match the rendered content
- whether there are signs of hydration or loading-state failures

Return a short QA report with blockers first.
```

### 3. Marketing asset review

```text
Use the cf-browser MCP tools on https://example.com/product-launch.

Take a screenshot, scrape the rendered page, and tell me:
- the headline and subheadline
- the first three proof points
- the CTA copy
- whether the page is visually ready for a social screenshot
```

## Best Practices

- Start with a screenshot so Claude can detect obvious layout failures.
- Ask for specific fields when scraping. "Summarize the page" is usually too loose.
- Use the screenshot and scrape together. Either one alone can hide problems.
- Prefer staging or preview URLs for release checks.

---

See also: [CF Browser: Scraping JS-Rendered Pages](./page-scraping.md), [MCP Setup](../mcp-setup.md)
