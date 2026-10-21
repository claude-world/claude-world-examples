# Extended Thinking Guide

> Unlock deeper reasoning for architecture decisions, security audits, and complex problem solving

## Quick Reference

| Model | Thinking | Default effort in Claude Code | Effort levels |
|-------|----------|-------------------------------|---------------|
| **Opus 5.5** | Always on (adaptive) | `medium` | low / medium / high / xhigh / max |
| **Sonnet 5.5** | Always on (adaptive) | `medium` | low / medium / high / xhigh / max |
| **Haiku 5.5** | Always on (adaptive) | `medium` | low / medium / high / xhigh / max |
| **Fable 5.1** | Always on (adaptive) | `high` | low / medium / high / xhigh / max |

On current models you don't switch thinking on or off. You set the **effort level**, and the model decides on each step whether and how much to think.

## What is Extended Thinking?

Extended thinking is the reasoning Claude does before it responds. Current models use **adaptive reasoning**: a simple step gets a quick answer, a hard one gets deeper reasoning, and the effort level shifts that balance.

```
Normal Mode:
┌────────┐       ┌──────────┐
│ Prompt │  ───► │ Response │
└────────┘       └──────────┘

Extended Thinking:
┌────────┐    ┌──────────────────┐    ┌──────────┐
│ Prompt │ ─► │ Internal Reason  │ ─► │ Response │
└────────┘    │ (deeper thinking)│    └──────────┘
              └──────────────────┘
```

## Controlling Thinking

### Method 1: /effort (the main control)

```
/effort          → open the effort slider
/effort high     → set a level for this model (saved as your default)
/effort auto     → clear your saved level
```

You can also adjust effort with the left/right arrows in the `/model` picker. The session header shows the active level, for example "with medium effort".

### Method 2: At Launch

```bash
claude --effort xhigh                  # this session only
CLAUDE_CODE_EFFORT_LEVEL=high claude   # overrides settings and frontmatter
```

### Method 3: Settings

`.claude/settings.json`:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "effortLevel": "high"
}
```

`effortLevel` accepts `low`, `medium`, `high`, or `xhigh`; `max` is never saved and applies to one session. When you pick a level with `/effort`, Claude Code stores it per model under `modelSettings` in your user settings.

### Method 4: `ultrathink` for One Turn

```
"ultrathink: why does this cache invalidation fail under concurrent writes?"
```

Including `ultrathink` anywhere in a prompt asks for deeper reasoning on that turn without changing your effort setting. Other phrases such as "think hard" or "think more" are ordinary text, not keywords.

### Method 5: Skill and Subagent Frontmatter

A skill or subagent can carry its own level, which applies while it runs:

```markdown
---
name: security-reviewer
description: Reviews authentication and payment code for vulnerabilities
model: opus
effort: max
---

Review the code you are given for security issues and report findings with severity levels.
```

### Turning Thinking Off (Older Models Only)

Opus 5.5, Sonnet 5.5, Haiku 5.5, and the Fable models always think. `Option+T` (macOS) / `Alt+T` (Windows/Linux), the thinking toggle in `/config` (`alwaysThinkingEnabled`), and `MAX_THINKING_TOKENS=0` only affect older models such as Opus 4.6 and Sonnet 4.6. To lower thinking on a current model, lower the effort.

Thinking is collapsed by default. Press `Ctrl+O` to open the transcript viewer and read it. Press `Option+P` (macOS) or `Alt+P` (Windows/Linux) to switch models without clearing your prompt.

## Effort Levels

| Effort | Use Case |
|--------|----------|
| `low` | Quick exchanges you review step by step: brainstorming, a first sketch, a rename |
| `medium` | Default on the 5.5 models: day-to-day work with a clear scope |
| `high` | Work where verification matters, such as fixing a bug in an existing codebase |
| `xhigh` | Deeper reasoning at higher token spend: architecture and trade-off analysis |
| `max` | Hard problems you want Claude to work through on its own, such as hunting for security vulnerabilities |

`max` can show diminishing returns and is prone to overthinking, so test it before adopting it broadly. **Ultracode** is a separate setting (`/effort ultracode`), not a level: it has Claude orchestrate a dynamic workflow for substantive tasks at the current effort.

### Setting Effort Level

**In prompts:** a prompt can't change the level, but Claude follows guidance within it:
```
"This one matters. Take the time to check edge cases before you answer."
```
Change the level itself with `/effort`, or use `ultrathink` for a single turn.

**For a subagent:**
```javascript
// Conceptual: Claude makes this call when you ask for a high-effort subagent
Agent({
  subagent_type: "general-purpose",
  description: "Design payment architecture",
  model: "opus",
  effort: "high",
  prompt: `
    Design the payment processing architecture.
    Consider all edge cases and failure modes.
  `
})
```

## When to Use Higher Effort

### High-Value Scenarios

| Scenario | Effort | Why |
|----------|--------|-----|
| Architecture decisions | xhigh | Avoid months of rework |
| Security reviews | max | Catch vulnerabilities early |
| Complex refactoring | high | Better design patterns |
| Bug investigation | high | Faster root cause analysis |
| Trade-off analysis | xhigh | Informed decision making |

### Keep Effort Low For

- File searches (use the Explore subagent)
- Pattern matching
- Simple code changes
- Documentation updates
- Routine tests

## Extended Thinking Patterns

### Pattern 1: Architecture Decision

```
/effort xhigh

"Design the real-time notification system.
Requirements:
- 100K concurrent users
- <100ms delivery latency
- Support mobile and web
- Handle offline users

Analyze options and recommend architecture."
```

### Pattern 2: Security Audit

```
/model opus
/effort max

"Review authentication.

Check for:
- OWASP Top 10 vulnerabilities
- JWT best practices
- Session management issues
- Rate limiting gaps

Report findings with severity levels."
```

### Pattern 3: Trade-off Analysis

```
"ultrathink about this decision.

Option A: Monolith with modular structure
Option B: Microservices from start

Context:
- 3-person team
- MVP stage
- Unknown scale requirements

Analyze both with pros, cons, and recommendation."
```

### Pattern 4: Complex Debug

```
"ultrathink: analyze this production issue.

Symptoms:
- Response time: 50ms → 2s at 500 RPS
- CPU: 30%, Memory: 60%
- Database connections spike
- No errors in logs

Identify potential causes and investigation steps."
```

### Pattern 5: Migration Planning

```
/effort high

"Create migration plan from MongoDB to PostgreSQL.

Current state:
- 50 collections
- 10M documents
- 5 dependent services
- Zero downtime requirement

Deliverables:
1. Migration strategy
2. Schema design
3. Service update plan
4. Rollback strategy
5. Testing approach"
```

## Extended Thinking with Agents

### Model and Effort by Task

```
Explore agents:     main model, or your own Explore with model: haiku - Speed
Implementation:     Sonnet, medium effort - Balance
Critical review:    Opus, high or max effort - Quality
```

Subagents inherit the main conversation's thinking configuration. Explore runs on the main conversation's model; to explore on Haiku, define a project subagent named `Explore` with `model: haiku`.

### Explore Agent

```javascript
Agent({
  subagent_type: "Explore",
  description: "Find authentication patterns",
  prompt: "Find authentication patterns (thoroughness: medium)"
})
```

**Little thinking needed** - pure search and discovery.

### Implementation Agent (Sonnet, Medium Effort)

```javascript
Agent({
  subagent_type: "general-purpose",
  description: "Implement OAuth PKCE flow",
  model: "sonnet",
  effort: "medium",
  prompt: `
    Implement OAuth 2.0 with PKCE flow.
    Consider:
    - State management
    - Token storage
    - Refresh handling
    - Error recovery
  `
})
```

### Review Agent (Opus, Max Effort)

```javascript
Agent({
  subagent_type: "security-auditor", // a custom agent in .claude/agents/, not built in
  description: "Review payment security",
  model: "opus",
  effort: "max",
  prompt: `
    Security review the payment integration.
    Check for:
    - PCI compliance issues
    - Data exposure risks
    - Authentication bypasses
  `
})
```

### Multi-Phase with Thinking

Combine deep reasoning for design with speed for execution:

```
Phase 1 (Opus, xhigh effort):
- Design migration strategy
- Plan architecture

Phase 2 (Sonnet, medium effort):
- Implement each migration step
- Write tests

Phase 3 (Haiku, low effort):
- Run tests in parallel
- Generate reports
```

## Context Impact

**Important:** Thinking tokens are billed as output, even when the thinking is collapsed.

```
Lower effort:
├── Fewer thinking tokens per step
├── Faster responses
└── Lower cost

Higher effort:
├── More reasoning and self-checking per step
├── Slower responses, more tokens
└── Switching level or model mid-session re-sends context without the prompt cache
```

**Recommendation:** Pick the level per task, and avoid flipping effort back and forth within one session.

### Monitor Context Usage

- `/context` shows what fills the context window
- `/usage` shows plan usage and limits
- The session header shows the effort level, and a custom status line can show it too (`/statusline`)

For long sessions with routine work, lower the effort:
```
/effort low
```

## Configuration

### Via /effort and /model

`/effort` sets the level; `/model` picks the model and has its own effort slider. Both apply immediately and save your choice for that model.

### Project Settings

```json
{
  "model": "sonnet",
  "effortLevel": "medium"
}
```

### Automatic Effort for Sensitive Code

Claude Code has no keyword triggers for thinking, but a skill gets close: give it `paths` so Claude loads it when working on matching files, and an `effort` that applies while the skill is active.

```markdown
---
name: sensitive-code-review
description: Deep review for authentication, payment, and admin code. Use when changing files in these areas.
paths:
  - "src/auth/**"
  - "src/payment/**"
  - "src/admin/**"
effort: max
---

Before finishing a change in these directories, check it for OWASP Top 10 issues,
authorization gaps, and secrets in code. Report findings with severity levels.
```

## Cost-Benefit Matrix

| Scenario | Suggested Effort | Quality Gain | ROI |
|----------|------------------|--------------|-----|
| Architecture decision | xhigh | Avoid months of rework | Very High |
| Security review | max | Catch vulnerabilities | Very High |
| Complex refactor | high | Better design | High |
| Bug investigation | high | Faster root cause | High |
| Routine coding | low or medium | Marginal improvement | Low |

## Best Practices

### 1. Be Explicit

**Good:**
```
"ultrathink: review this authorization middleware for privilege escalation."
```

**Vague:**
```
"Analyze this code."
```

### 2. Provide Rich Context

```
"Design the caching layer.

Context:
- Current: No caching, 200ms average response
- Goal: <50ms for 80% of requests
- Constraints: Redis available, 5GB memory budget
- Traffic: 10K RPM, 80% reads

Consider cache invalidation and stampede prevention."
```

### 3. Request Structured Output

```
"Think through this architecture decision.

Output format:
1. Options considered (3-5)
2. Evaluation criteria
3. Analysis matrix
4. Recommendation with rationale
5. Risk assessment"
```

### 4. Match Model and Effort to Task

| Task Type | Model | Effort |
|-----------|-------|--------|
| Quick search | Haiku (custom Explore) | low |
| Standard code | Sonnet | medium |
| Complex logic | Sonnet | high |
| Critical review | Opus | high or max |
| Architecture | Opus | xhigh |

### 5. Phase Your Work

```
High-stakes decisions → Opus, xhigh effort
Implementation → Sonnet, medium effort
Verification → Haiku parallel agents, low effort
```

## Common Mistakes

### Mistake 1: Maximum Effort for Everything

```
❌ max effort for file search
❌ max effort for simple edits
❌ max effort for test runs

✅ Use low effort and Explore for speed tasks
✅ Reserve high, xhigh, and max for decisions that matter
```

### Mistake 2: Not Providing Context

```
❌ "Design authentication."

✅ "Design authentication for:
   - 100K users
   - Mobile + web
   - OAuth + email/password
   - HIPAA compliance required"
```

### Mistake 3: Ignoring Effort Levels

```
❌ Always using default effort

✅ Low effort: Batch operations
✅ Medium effort: Development tasks
✅ High or xhigh effort: Architecture, tricky bugs
✅ Max effort: Security audits
```

## Summary

| Principle | Action |
|-----------|--------|
| Use selectively | Raise effort for high-value decisions only |
| Match model to task | Haiku → Sonnet → Opus |
| Provide context | More context = better thinking |
| Request structure | Ask for formatted output |
| Monitor context | Watch usage in long sessions |

---

**Related:**
- [Agents Guide](./agents-guide.md) - Using agents with thinking
- [Extended Thinking Article](https://claude-world.com/articles/extended-thinking-guide) - Full deep dive
- [Model configuration](https://code.claude.com/docs/en/model-config) - Official effort and thinking reference

Back to [README](../README.md)
