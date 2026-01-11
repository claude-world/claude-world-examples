# Simple CLAUDE.md Template

A minimal but effective CLAUDE.md that you can adapt for any project.

## The Template

```markdown
# [Your Project Name]

> Brief description of what this project does

## Tech Stack

- **Framework**: [e.g., Next.js 14, Express, Django]
- **Database**: [e.g., PostgreSQL, MongoDB, SQLite]
- **Language**: [e.g., TypeScript, Python, Go]

## Project Structure

```
/src
  /components   - UI components
  /lib          - Utilities and helpers
  /api          - API routes/handlers
  /types        - TypeScript types
/tests          - Test files
/docs           - Documentation
```

## Quick Commands

```bash
npm run dev     # Start development server
npm run test    # Run tests
npm run build   # Build for production
npm run lint    # Check code style
```

## Development Guidelines

### Do
- Write tests for new features
- Use TypeScript strict mode
- Follow existing code patterns
- Keep functions small and focused

### Don't
- Add dependencies without good reason
- Skip error handling
- Use `any` type
- Leave console.logs in production code

## Common Patterns

### API Response Format
```typescript
{
  success: boolean;
  data?: T;
  error?: string;
}
```

### Component Structure
```typescript
// components/FeatureName/index.tsx - Main export
// components/FeatureName/FeatureName.tsx - Component
// components/FeatureName/FeatureName.test.tsx - Tests
```
```

## Customization Tips

### For a React/Next.js Project

Add:
```markdown
## State Management
- Use React Query for server state
- Use Zustand for client state
- Avoid prop drilling - use context

## Styling
- Tailwind CSS for all styling
- Use cn() helper for conditional classes
- Design tokens in tailwind.config.ts
```

### For an API/Backend Project

Add:
```markdown
## API Design
- RESTful endpoints
- Versioning: /api/v1/...
- Auth: Bearer token in Authorization header

## Error Handling
- Use custom error classes
- Log all errors to monitoring
- Return consistent error format
```

### For a CLI Tool

Add:
```markdown
## CLI Structure
- Commands in /src/commands
- Use Commander.js for parsing
- All output through logger utility

## Testing
- Unit tests for each command
- Integration tests in /tests/integration
- Mock filesystem in tests
```

## Why This Works

1. **Context** - Claude knows your tech stack immediately
2. **Structure** - Claude can navigate your codebase
3. **Commands** - Claude can run your scripts
4. **Guidelines** - Claude follows your conventions
5. **Patterns** - Claude produces consistent code

## Next Steps

Start with this template and expand as you notice:
- Questions Claude keeps asking → Add to CLAUDE.md
- Patterns Claude should follow → Document them
- Decisions Claude should know → Write them down

---

See also: [CLAUDE.md Principles](../concepts/claude-md-principles.md)
