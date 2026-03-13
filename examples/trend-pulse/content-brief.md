# Trend Pulse: Content Brief from Trends

> Turn live trend data into a concrete brief for a blog post, newsletter item, or social thread.

## The Goal

Use `trend-pulse` to choose a topic with real momentum, validate it, and have Claude produce a brief that is specific enough to hand directly to a writer or implementer.

## Recommended Flow

1. Use `get_trending` to collect current topics.
2. Pick one topic that fits your audience.
3. Use `search_trends` to confirm the topic is not a one-hour spike.
4. Ask Claude to produce a brief with angle, outline, keywords, and risks.

## Example Prompt for Claude Code

```text
Use the trend-pulse MCP server to create a content brief for Claude World.

1. Call `get_trending` for US developer and AI topics from the last 7 days.
2. Choose one topic that is both rising and practical for Claude Code users.
3. Call `search_trends` on the chosen topic plus two related keywords to validate sustained interest.
4. Produce a content brief with:
   - working title
   - target audience
   - why this topic matters now
   - 3 key questions the article should answer
   - recommended outline
   - related keywords to include naturally
   - hype or misinformation risks to avoid
   - suggested CTA
```

## Example Brief Template

Ask Claude to return the result in a structure like this:

```markdown
# Content Brief

## Topic
[Chosen trend]

## Working Title
[Specific title]

## Audience
[Who this is for]

## Why Now
[Trend signal plus practical reason to publish]

## Core Angle
[What unique point of view to take]

## Outline
1. [Section]
2. [Section]
3. [Section]
4. [Section]

## Supporting Keywords
- [keyword]
- [keyword]
- [keyword]

## Risks to Avoid
- [overclaim]
- [missing context]

## CTA
[What the reader should do next]
```

## Variant Prompts

### Newsletter brief

```text
Take the same validated trend topic and rewrite the brief for a 250-word newsletter section with one strong takeaway and one link recommendation.
```

### Social thread brief

```text
Take the same validated trend topic and turn it into a 6-post social thread brief with a hook, three proof points, one caution, and a closing CTA.
```

## Best Practices

- Keep the audience explicit. A trend that is strong for marketers may still be weak for developers.
- Ask Claude to validate with `search_trends` before generating the brief.
- Require a "risks to avoid" section so the brief does not read like hype.
- Prefer one strong trend-based brief over five shallow ones.

---

See also: [Trend Pulse: Basic Trending Queries](./basic-trending.md)
