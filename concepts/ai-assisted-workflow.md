# AI-Assisted Development Workflow

> How to leverage Claude Code as a force multiplier, not just a code assistant

## The Paradigm Shift

Traditional development:
```
Developer → Code → Test → Debug → Repeat
```

AI-assisted development:
```
Director → Define Goals → Claude Executes → Review Results → Ship
```

The key insight: **You're not writing code with AI help. You're directing a team of AI agents.**

## The Force Multiplier Effect

| Metric | Traditional | AI-Assisted | Multiplier |
|--------|-------------|-------------|------------|
| Lines of code/hour | 50-100 | 500-1000 | 10x |
| Files explored/session | 10-20 | 100-200 | 10x |
| Context switches | Many | Few | 0.2x |
| Decision fatigue | High | Low | 0.3x |

## Core Principles

### 1. Goals Over Instructions

**Instead of**:
```
"Create a file called UserService.ts with a class that has
methods getUserById, createUser, and updateUser..."
```

**Use**:
```
"Implement user CRUD operations following the existing service patterns"
```

Let Claude figure out the details. Your job is outcomes, not steps.

### 2. Parallel Exploration

**Instead of**:
```
"Search for authentication code"
[wait]
"Now search for user model"
[wait]
"Now check the middleware"
```

**Use**:
```
"Use subagents to explore the authentication system (thoroughness: medium)"
```

Claude delegates independent searches to Explore subagents that run in parallel, each in its own context window, and report back summaries, keeping your main conversation clean.

### 3. Autonomous Execution

**Instead of**:
```
Claude: "Should I create the file?"
You: "Yes"
Claude: "Should I add the import?"
You: "Yes"
Claude: "Should I run the tests?"
You: "Yes"
```

**Use permission rules** in `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test *)",
      "Bash(git add *)",
      "Bash(git commit *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(npm run migrate *)"
    ]
  }
}
```

Current Claude Code starts interactive sessions in auto mode by default, so routine edits and commands don't prompt, while explicit `ask` and `deny` rules still apply in every mode. Keep a matching "Autonomous Operations / Requires Confirmation" list in CLAUDE.md so Claude knows your intent, but CLAUDE.md alone doesn't enforce anything.

### 4. Review, Don't Supervise

**Instead of**: Watching every keystroke

**Use**: Review completed work
```
You: "Implement the feature"
[Claude works for 5 minutes]
Claude: "Done. Created 3 files, added tests, all passing."
You: [Reviews diff, approves or requests changes]
```

## The Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    AI-Assisted Workflow                      │
└─────────────────────────────────────────────────────────────┘

1. DEFINE
   ├── What outcome do you want?
   ├── What constraints exist?
   └── What's the acceptance criteria?

2. DELEGATE
   ├── Give Claude the goal
   ├── Let it explore and plan (plan mode: Shift+Tab)
   └── Trust the parallel execution

3. REVIEW
   ├── Check the results
   ├── Verify tests pass
   └── Approve, iterate, or /rewind

4. SHIP
   ├── Commit the changes
   ├── Push to remote
   └── Monitor deployment
```

## Practical Examples

### Example 1: Bug Fix

**Traditional approach** (~30 min):
```
1. Read error report
2. Search for related code
3. Add console.logs
4. Reproduce issue
5. Find root cause
6. Write fix
7. Test fix
8. Remove console.logs
9. Write test
10. Commit
```

**AI-assisted approach** (~5 min):
```
You: "Fix the login timeout bug. Error: 'Session expired after 5 minutes'"

Claude: [Launches parallel agents]
        → Agent 1: Search error message in codebase
        → Agent 2: Check session configuration
        → Agent 3: Review auth middleware
        → Agent 4: Check recent commits
        → Agent 5: Look for timeout settings

Claude: "Found issue: session.maxAge set to 300000ms (5 min) instead of
         3600000ms (1 hour). Fixed in auth/config.ts. Added test. Committed."
```

### Example 2: New Feature

**Traditional approach** (~4 hours):
```
1. Plan the feature
2. Design API
3. Create database schema
4. Implement backend
5. Write tests
6. Implement frontend
7. Integration test
8. Documentation
```

**AI-assisted approach** (~1 hour):
```
You: "Add user profile photo upload feature.
Requirements:
- Upload to S3
- Resize to 200x200
- Update user profile
- Show in navbar"

Claude: [Works autonomously]
        → Creates API endpoint
        → Adds S3 integration
        → Implements image processing
        → Updates frontend
        → Writes tests
        → Updates types

Claude: "Feature complete. 8 files modified, 2 new files created.
         Tests passing. Preview at /profile/settings."
```

### Example 3: Code Review

**Traditional approach** (~20 min):
```
1. Read through PR
2. Check each file
3. Run tests locally
4. Write comments
5. Request changes
```

**AI-assisted approach** (~3 min):
```
You: "Review PR #123"   (or run /review 123)

Claude: [Parallel analysis]
        → Code quality check
        → Security scan
        → Test coverage analysis
        → Architecture review
        → Documentation check

Claude: "PR Review Summary:
         ✅ Tests passing
         ✅ No security issues
         ⚠️ Missing null check in UserService.ts:42
         ⚠️ Consider adding rate limiting to new endpoint
         📝 Add JSDoc to exported function"
```

## Setting Up Your Workflow

### 1. Create Effective CLAUDE.md

```markdown
# Project: [Name]

## Tech Stack
[List your technologies]

## Autonomous Operations
- Read/write source files
- Run tests and builds
- Git operations (local)
- Install dependencies

## Requires Confirmation
- Git push
- Database migrations
- API key changes
- Production deployments

## Coding Standards
[Your conventions]

## Testing Requirements
[Your test policy]
```

Run `/init` to generate a starter, keep it under ~200 lines, and back the "Requires Confirmation" list with the permission rules shown above.

### 2. Use Session-Based Development

```
Session 1: "Setup project structure"
Session 2: "Implement core data models"
Session 3: "Build API endpoints"
Session 4: "Create frontend components"
Session 5: "Integration and testing"
```

Each session = clear goal + autonomous execution + review. Run `/clear` between unrelated tasks; `claude --continue` or `/resume` picks a session back up.

### 3. Leverage Model Selection

| Task Type | Model | Why |
|-----------|-------|-----|
| Quick lookups, simple edits | Haiku 5.5 | Fast and low-cost, for high-volume, latency-sensitive tasks |
| Implementation | Sonnet 5.5 | The best combination of speed and intelligence |
| Architecture | Opus 5.5 | Long-running agentic coding and knowledge work |
| Security review | Opus 5.5 at `high` or `max` effort | Thorough analysis |

Quick switch: `/model haiku|sonnet|opus`, or `Option+P` (macOS) / `Alt+P` (Windows/Linux). Tune depth with `/effort` (the 5.5 models default to `medium`), or add `ultrathink` to a single prompt. Opus 5.5 is the `default` model on Pro, Max, Team, Enterprise and API accounts. Fable 5.1 (`/model fable`), "for demanding reasoning and long-horizon agentic work", is never the default and bills to usage credits on some plans.

The built-in Explore subagent runs on your main conversation's model. To explore on Haiku, define your own `Explore` subagent with `model: haiku`.

### 4. Trust the Process

The hardest part is **letting go of control**.

```
❌ "Let me see what you're doing..."
❌ "Wait, I want to do that part myself..."
❌ "Are you sure about that approach?"

✅ "Here's the goal. Execute."
✅ [Reviews completed work]
✅ "Ship it" or "Try a different approach"
```

## Measuring Success

### Time Metrics

Track these for your projects:

| Metric | Before AI | After AI |
|--------|-----------|----------|
| Feature implementation | X hours | Y hours |
| Bug investigation | X min | Y min |
| Code review | X min | Y min |
| Documentation | X hours | Y hours |

### Quality Metrics

AI-assisted development often improves:
- Test coverage (Claude writes tests when your CLAUDE.md asks for them)
- Documentation (Claude documents as it codes)
- Consistency (Claude follows patterns exactly)
- Security (Claude checks for common issues; run `/security-review` on your branch)

## Common Pitfalls

### 1. Micro-managing

**Problem**: Giving step-by-step instructions
**Solution**: Give goals, not steps

### 2. Not Trusting Parallel Agents

**Problem**: Running searches one at a time
**Solution**: Ask Claude to use subagents (such as Explore) or let it parallelize

### 3. Skipping CLAUDE.md

**Problem**: Re-explaining context every session
**Solution**: Invest time in good CLAUDE.md

### 4. Wrong Model for Task

**Problem**: Using Opus at high effort for simple searches
**Solution**: Haiku 5.5 or `/effort low` for quick lookups, Sonnet 5.5 or Opus 5.5 for coding

## The 48-Hour Mindset

This workflow enabled building [claude-world.com](https://claude-world.com) in 48 hours:

- **Day 1**: Architecture + basic setup
- **Day 2**: All features implemented
- **Day 3**: Polish + launch

The secret: **Director Mode thinking from minute one.**

You're not coding faster. You're operating at a different level entirely.

---

## Related Resources

- [Director Mode Basics](./director-mode-basics.md)
- [Parallel Agents](./parallel-agents.md)
- [48-Hour Website Case Study](../case-studies/48-hour-website.md)
- [CLAUDE.md Principles](./claude-md-principles.md)

---

*Stop writing code. Start directing outcomes.*
