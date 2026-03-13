# Trend Pulse: Basic Trending Queries

> Use `get_trending` and `search_trends` to spot what is accelerating before you decide what to write, build, or investigate.

## What This Solves

When you ask Claude for topic ideas without live signals, the answer is usually generic. `trend-pulse` gives Claude current trend data so it can rank ideas by momentum instead of guessing.

## Project MCP Configuration

Add a project-scoped server to `.mcp.json`:

```json
{
  "mcpServers": {
    "trend-pulse": {
      "command": "<trend-pulse-mcp-command>",
      "args": ["<provider-arg-1>", "<provider-arg-2>"],
      "env": {
        "TREND_PULSE_API_KEY": "${TREND_PULSE_API_KEY}",
        "TREND_PULSE_DEFAULT_REGION": "US",
        "TREND_PULSE_DEFAULT_LANGUAGE": "en"
      }
    }
  }
}
```

Replace the command and args with the launcher from your `trend-pulse` provider. The prompts below assume the server exposes `get_trending` and `search_trends`.

## Basic Workflow

1. Call `get_trending` to get the broad signal.
2. Call `search_trends` for the terms you are already considering.
3. Ask Claude to cluster overlap, remove noise, and recommend one direction.

## Example Prompts for Claude Code

### 1. Discover fast-moving topics

```text
Use the trend-pulse MCP server.

1. Call `get_trending` for the United States over the last 24 hours.
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
Use `search_trends` to compare these topics in the US over the last 30 days:
- Claude Code
- Model Context Protocol
- Browser automation
- Cloudflare Browser Rendering

Show which topic has:
- the strongest current momentum
- the steadiest interest
- the weakest signal

Then recommend one topic for a tutorial and explain why.
```

### 3. Turn broad trends into a short action list

```text
Use `get_trending` for the last 7 days, then use `search_trends` to validate the three most relevant developer-tool topics.

Return a table with:
- topic
- momentum summary
- best format (blog post, social thread, short demo, or docs update)
- why now
```

## Practical Pattern

Use `get_trending` first when you do not know what to explore. Use `search_trends` after that when you need evidence for a specific topic choice. That keeps Claude from over-indexing on a single keyword too early.

## Best Practices

- Be explicit about region and time window. "Trending" without scope is too vague.
- Ask Claude to merge near-duplicate terms before ranking them.
- Compare at least 3 candidate terms with `search_trends` before committing to a content plan.
- Ask for "durable vs. short-lived" so hype spikes do not dominate the recommendation.

---

See also: [Trend Pulse: Content Brief](./content-brief.md), [MCP Setup](../mcp-setup.md)
