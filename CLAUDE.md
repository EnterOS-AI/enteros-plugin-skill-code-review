# molecule-skill-code-review — Multi-Criteria Code Review Skill

`molecule-skill-code-review` provides a multi-criteria code review skill
that checks PRs against best practices, modularity, scalability, abstraction,
test coverage, redundancy, hardcoded values, type safety, performance, naming,
API design, async patterns, config/env sync, template consistency, and
documentation alignment.

**Version:** 1.0.0
**Runtime:** `claude_code`

---

## Repository Layout

```
molecule-skill-code-review/
├── plugin.yaml              — Plugin manifest
├── skills/
│   └── code-review/
│       └── SKILL.md         — Full review criteria and process
└── adapters/               — Harness adaptors
```

---

## Review Criteria

The skill evaluates PRs across these dimensions:

| Category | Checks |
|---|---|
| Best practices | Language idioms, error handling, resource cleanup |
| Modularity | Single responsibility, low coupling |
| Scalability | Algorithm complexity, pagination, streaming |
| Abstraction | Correct use of interfaces/types |
| Test coverage | Tests for new logic, edge cases |
| Redundancy | DRY violations, copy-paste |
| Hardcoded values | Secrets, URLs, magic numbers |
| Type safety | Explicit types, no `any` |
| Performance | N+1 queries, missing indexes |
| Naming | Descriptive, consistent |
| API design | REST conventions, idempotency |
| Async patterns | Correct use of async/await |
| Config/env sync | Config changes reflected in env |
| Template consistency | Follows repo conventions |

---

## Development

### Prerequisites

- Python 3.11+
- `gh` CLI authenticated
- Write access to `Molecule-AI/molecule-ai-plugin-molecule-skill-code-review`

### Setup

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-skill-code-review.git
cd molecule-ai-plugin-molecule-skill-code-review
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
```

### Pre-Commit Checklist

```bash
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"

python3 -c "
import re, sys
with open('plugin.yaml') as f:
    content = f.read()
patterns = [r'sk.ant', r'ghp.', r'AKIA[A-Z0-9]']
if any(re.search(p, content) for p in patterns):
    print('FAIL: possible credentials found')
    sys.exit(1)
print('No credentials: OK')
"
```

---

## Release Process

1. Review changes: `git log origin/main..HEAD --oneline`
2. Bump `version` in `plugin.yaml` (semver)
3. Commit: `chore: bump version to X.Y.Z`
4. Tag and push: `git tag vX.Y.Z && git push origin main --tags`
5. Create GitHub Release with changelog

---

## Known Issues

See `known-issues.md` at the repo root.
