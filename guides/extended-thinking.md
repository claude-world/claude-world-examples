# Extended Thinking Guide

> Unlock deeper reasoning for architecture decisions, security audits, and complex problem solving

## Quick Reference

| Model | Extended Thinking | Default | Effort Levels |
|-------|-------------------|---------|---------------|
| **Opus 4.5** | Yes | ON (v2.0.67+) | low / medium / high |
| **Sonnet 4.5** | Yes | OFF | N/A |
| **Haiku 4.5** | Yes | OFF | N/A |

## What is Extended Thinking?

Extended Thinking (also called "Thinking Mode") gives Claude more time to reason through complex problems before responding.

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

## Enabling Extended Thinking

### Method 1: Via /config

```
Thinking Mode: ON
```

### Method 2: Via Settings

> **Note:** The settings below show the conceptual configuration. Actual Claude Code settings may use different property names. Check `/config` in Claude Code for current options.

`.claude/settings.json`:
```json
{
  "model": "opus"
}
```

Thinking mode is typically controlled via `/config` interactively rather than settings files.

### Method 3: In Prompt

```
"Enable extended thinking for this security analysis."
```

### Method 4: Quick Model Switch

Press `Option+P` (macOS) or `Alt+P` (Windows/Linux) during prompting.

## Effort Levels (Opus 4.5 Only)

| Effort | Thinking Depth | Use Case |
|--------|----------------|----------|
| `low` | Minimal | Quick tasks, batch operations |
| `medium` | Balanced | Default, most development tasks |
| `high` | Maximum | Architecture, security, critical decisions |

### Setting Effort Level

**In prompts:**
```
"Analyze this authentication system with high effort.
I need thorough security analysis."
```

**In Task tool:**
```javascript
Task({
  subagent_type: "general-purpose",
  model: "opus",
  prompt: `
    Effort: high

    Design the payment processing architecture.
    Consider all edge cases and failure modes.
  `
})
```

## When to Use Extended Thinking

### High-Value Scenarios

| Scenario | Effort | Why |
|----------|--------|-----|
| Architecture decisions | High | Avoid months of rework |
| Security reviews | High | Catch vulnerabilities early |
| Complex refactoring | Medium | Better design patterns |
| Bug investigation | Medium | Faster root cause analysis |
| Trade-off analysis | High | Informed decision making |

### Skip Thinking For

- File searches (use Explore agent)
- Pattern matching
- Simple code changes
- Documentation updates
- Routine tests

## Extended Thinking Patterns

### Pattern 1: Architecture Decision

```
"Enable high-effort thinking.

Design the real-time notification system.
Requirements:
- 100K concurrent users
- <100ms delivery latency
- Support mobile and web
- Handle offline users

Analyze options and recommend architecture."
```

### Pattern 2: Security Audit

```
"Using Opus with high effort, review authentication.

Check for:
- OWASP Top 10 vulnerabilities
- JWT best practices
- Session management issues
- Rate limiting gaps

Report findings with severity levels."
```

### Pattern 3: Trade-off Analysis

```
"Think deeply about this decision.

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
"Use extended thinking to analyze this production issue.

Symptoms:
- Response time: 50ms → 2s at 500 RPS
- CPU: 30%, Memory: 60%
- Database connections spike
- No errors in logs

Identify potential causes and investigation steps."
```

### Pattern 5: Migration Planning

```
"Effort: high

Create migration plan from MongoDB to PostgreSQL.

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

### Model Selection by Task

```
Explore agents:     Haiku (no thinking)  - Speed
Implementation:     Sonnet (thinking optional) - Balance
Critical review:    Opus (thinking default) - Quality
```

### Explore Agent (No Thinking)

```javascript
Task({
  subagent_type: "Explore",
  model: "haiku",
  prompt: "Find authentication patterns (thoroughness: medium)"
})
```

**No thinking needed** - pure search and discovery.

### Implementation Agent (Sonnet + Thinking)

```javascript
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Enable thinking mode.

    Implement OAuth 2.0 with PKCE flow.
    Consider:
    - State management
    - Token storage
    - Refresh handling
    - Error recovery
  `
})
```

### Review Agent (Opus + High Effort)

```javascript
Task({
  subagent_type: "security-auditor",
  model: "opus",
  prompt: `
    Effort: high

    Security review the payment integration.
    Check for:
    - PCI compliance issues
    - Data exposure risks
    - Authentication bypasses
  `
})
```

### Multi-Phase with Thinking

Combine thinking for design, speed for execution:

```
Phase 1 (Opus, high effort):
- Design migration strategy
- Plan architecture

Phase 2 (Sonnet, no thinking):
- Implement each migration step
- Write tests

Phase 3 (Haiku, no thinking):
- Run tests in parallel
- Generate reports
```

## Context Impact

**Important:** Extended Thinking uses additional tokens internally.

```
Normal Mode:
├── Prompt Cache: Highly effective
├── Context usage: Predictable
└── Token efficiency: High

Extended Thinking:
├── Prompt Cache: Less effective
├── Context usage: Variable
└── Token efficiency: Lower (but higher quality)
```

**Recommendation:** Use thinking selectively for high-value decisions.

### Monitor Context Usage

Status line (v2.0.65+):
```
Context: 45% used | Thinking: enabled | Model: opus
```

For long sessions, disable thinking for routine tasks:
```
"Disable thinking for these routine file updates."
```

## Configuration

### Via /config Command

The recommended way to configure thinking mode is through the `/config` interactive menu:

```
Thinking Mode: ON / OFF
Model: opus / sonnet / haiku
```

### Project Settings

> **Note:** The configurations below are conceptual examples showing possible automation patterns. As of Claude Code 2.1.x, thinking mode is primarily controlled via `/config`. These advanced configurations may be supported in future versions or custom setups.

```json
{
  "model": "sonnet"
}
```

### Conceptual: Auto-Enable Triggers

This pattern is not currently supported in standard Claude Code settings, but illustrates how automated thinking triggers might work:

```json
{
  "thinkingTriggers": {
    "keywords": ["security", "architecture", "design"],
    "paths": ["auth/", "payment/", "admin/"],
    "operations": ["create-file", "refactor"]
  }
}
```

> **Current approach:** Use verbal instructions like "enable extended thinking for this security analysis" to activate thinking mode for specific tasks.

## Cost-Benefit Matrix

| Scenario | Time Cost | Quality Gain | ROI |
|----------|-----------|--------------|-----|
| Architecture decision | +30s | Avoid months of rework | Very High |
| Security review | +45s | Catch vulnerabilities | Very High |
| Complex refactor | +20s | Better design | High |
| Bug investigation | +15s | Faster root cause | High |
| Routine coding | +10s | Marginal improvement | Low |

## Best Practices

### 1. Be Explicit

**Good:**
```
"Enable extended thinking for this security analysis."
```

**Vague:**
```
"Analyze this code."
```

### 2. Provide Rich Context

```
"Using high-effort thinking, design the caching layer.

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

### 4. Match Model to Task

| Task Type | Model | Thinking |
|-----------|-------|----------|
| Quick search | Haiku | OFF |
| Standard code | Sonnet | OFF |
| Complex logic | Sonnet | ON |
| Critical review | Opus | ON (default) |
| Architecture | Opus | ON + High effort |

### 5. Phase Your Work

```
High-stakes decisions → Opus with thinking
Implementation → Sonnet
Verification → Haiku parallel agents
```

## Common Mistakes

### Mistake 1: Using Thinking for Everything

```
❌ Enable thinking for file search
❌ Enable thinking for simple edits
❌ Enable thinking for test runs

✅ Use Haiku/Explore for speed tasks
✅ Reserve thinking for decisions that matter
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
✅ High effort: Architecture, security
```

## Summary

| Principle | Action |
|-----------|--------|
| Use selectively | High-value decisions only |
| Match model to task | Haiku → Sonnet → Opus |
| Provide context | More context = better thinking |
| Request structure | Ask for formatted output |
| Monitor context | Watch usage in long sessions |

---

**Related:**
- [Agents Guide](./agents-guide.md) - Using agents with thinking
- [Extended Thinking Article](https://claude-world.com/articles/extended-thinking-guide) - Full deep dive

Back to [README](../README.md)
