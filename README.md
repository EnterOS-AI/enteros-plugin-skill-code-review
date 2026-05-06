# molecule-skill-code-review — Multi-Axis Code Review

Plugin for Claude Code. Invokes a 16-criteria code review across code quality
dimensions: best practices, modularity, scalability, abstraction, test coverage,
redundancy, hardcoded values, type safety, performance, naming, API design,
async patterns, config/env sync, template consistency, and documentation alignment.

## When to use

Install on workspaces that review code changes (PRs, diffs, generated code).
The skill is invoked on-demand via the `Skill` tool.

## What it reviews

| Dimension | What to check |
|-----------|---------------|
| Best practices | idiomatic language use, error handling, resource cleanup |
| Modularity | single responsibility, low coupling, cohesive modules |
| Scalability | algorithmic complexity, N+1 queries, pagination |
| Type safety | strict types, no `any`, null checks |
| Test coverage | edge cases, happy path, error conditions |
| Security | injection vectors, secrets in code, input validation |
| Performance | unnecessary work, caching opportunities, DB efficiency |

## Installation

### In org template (org.yaml)
```yaml
plugins:
  - molecule-skill-code-review
```

### From URL
```
github://Molecule-AI/molecule-ai-plugin-molecule-skill-code-review
```

## License
Business Source License 1.1 — © Molecule AI.
