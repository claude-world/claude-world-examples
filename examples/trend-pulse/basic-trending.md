# Trend Pulse: Basic Trending Queries

> Use `get_trending` and `search_trends` to spot what is accelerating before you decide what to write, build, or investigate.

## What This Solves

When you ask Claude for topic ideas without live signals, the answer is usually generic. `trend-pulse` gives Claude current trend data so it can rank ideas by momentum instead of guessing.

## Project MCP Configuration

[`trend-pulse`](https://github.com/claude-world/trend-pulse) is free and needs no API key. Add it as a project-scoped server with [uv](https://docs.astral.sh/uv/) installed:

```bash
claude mcp add --scope project trend-pulse -- uvx --from "trend-pulse[mcp]" trend-pulse-server
```

That writes this entry to `.mcp.json`:

```json
{
  "mcpServers": {
    "trend-pulse": {
      "command": "uvx",
      "args": ["--from", "trend-pulse[mcp]", "trend-pulse-server"]
    }
  }
}
```

`get_trending` takes optional `sources` (comma-separated, such as `hackernews,github,reddit`), `geo` (a country code such as `US` or `TW`), and `count`. `search_trends` takes a `query` plus the same `sources` and `geo`. Both report what is trending now; for momentum over days, save snapshots (`save: true` or `take_snapshot`) and query `get_trend_history` or `compare_trends`.

## Basic Workflow

1. Call `get_trending` to get the broad signal.
2. Call `search_trends` for the terms you are already considering.
3. Ask Claude to cluster overlap, remove noise, and recommend one direction.

## Example Prompts for Claude Code

### 1. Discover fast-moving topics

```text
Use the trend-pulse MCP server.

1. Call `get_trending` with geo `US` and sources `hackernews,github,devto,reddit,producthunt`.
2. Keep only AI, developer tools, browser automation, and Cloudflare-related topics.
3. Group near-duplicate topics together.
4. Return the top 8 opportunities with:
   - topic
   - why it is trending
   - who would care
   - whether it looks durable or short-lived
```

### 2. Compare candidate ideas before writing

```text
Use `search_trends` with geo `US` to compare current signals for these topics:
- Claude Code
- Model Context Protocol
- Browser automation
- Cloudflare Browser Rendering

Show which topic has:
- the strongest current momentum
- the steadiest interest
- the weakest signal

If saved snapshots exist, add `compare_trends` for the top two to see 30-day momentum.

Then recommend one topic for a tutorial and explain why.
```

### 3. Turn broad trends into a short action list

```text
Use `get_trending` with geo `US` and `save: true`, then use `search_trends` to validate the three most relevant developer-tool topics.

Return a table with:
- topic
- momentum summary
- best format (blog post, social thread, short demo, or docs update)
- why now
```

## Practical Pattern

Use `get_trending` first when you do not know what to explore. Use `search_trends` after that when you need evidence for a specific topic choice. That keeps Claude from over-indexing on a single keyword too early.

## Best Practices

- Be explicit about region (`geo`) and sources. "Trending" without scope is too vague.
- Save snapshots regularly if you want trends over time; `get_trend_history` only sees what was saved.
- Ask Claude to merge near-duplicate terms before ranking them.
- Compare at least 3 candidate terms with `search_trends` before committing to a content plan.
- Ask for "durable vs. short-lived" so hype spikes do not dominate the recommendation.

---

See also: [Trend Pulse: Content Brief](./content-brief.md), [MCP Setup](../mcp-setup.md)
