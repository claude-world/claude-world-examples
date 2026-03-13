# CF Browser: Scraping JS-Rendered Pages

> Use `browser_scrape` when the page content only appears after JavaScript runs.

## The Problem

Many modern pages render the useful content after hydration. A normal fetch may only show a shell, placeholder markup, or empty containers. `cf-browser` gives Claude access to the rendered page instead of the initial HTML.

## Recommended Workflow

1. Capture a screenshot first to confirm the page actually rendered.
2. Use `browser_scrape` to extract the rendered text or structured elements.
3. Ask Claude for a structured result instead of a loose summary.

## Example Prompts for Claude Code

### 1. Scrape a JS-rendered search page

```text
Use the cf-browser MCP server on https://example.com/search?q=mcp.

1. Call `browser_screenshot` first so we can verify the page hydrated.
2. Call `browser_scrape` after the page is rendered.
3. Extract:
   - page title
   - visible H1 and H2 text
   - the first 5 result titles
   - any filters, sort controls, or pagination
4. Return the result as structured markdown.
```

### 2. Extract cards from a single-page app

```text
Use `browser_scrape` on https://example.com/jobs.

I only care about rendered content. Extract the first 10 visible job cards with:
- title
- location
- team
- link text or destination

If the page looks broken in the screenshot, report that before scraping details.
```

### 3. Pull content from a docs page with client-side navigation

```text
Use the cf-browser MCP tools on https://example.com/docs/browser-rendering.

Take a screenshot, then scrape the rendered page and return:
- page title
- section headings
- callout text
- code block titles or labels
- links in the "next steps" area
```

## Practical Tips

- Tell Claude exactly which fields you want back.
- Ask for "rendered content only" if the page mixes server HTML with client updates.
- Use the screenshot as a guardrail for login walls, captchas, or empty-state failures.
- If you need repeatable extraction, have Claude return a table or JSON-shaped markdown.

---

See also: [CF Browser: Screenshot Capture with Claude Code](./screenshot-capture.md)
