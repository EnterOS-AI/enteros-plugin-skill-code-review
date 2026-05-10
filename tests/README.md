# Test Rationale — molecule-skill-code-review

## What this plugin does

`molecule-skill-code-review` is a prose-only skill: its logic lives entirely in
`skills/code-review/SKILL.md`. The adapter (`adapters/claude_code.py`) is a thin
re-export of `AgentskillsAdaptor` from `plugins_registry.builtins` — no business
logic, no network calls, no side effects.

## What is tested

- `plugin.yaml` is valid YAML with required fields (name, version, runtimes, skills)
- `skills/code-review/SKILL.md` has valid YAML frontmatter and a body with headings
- `adapters/claude_code.py` exists and re-exports `AgentskillsAdaptor`
- `validate-plugin.py` (`.molecule-ci/scripts/`) exits zero

## What is NOT unit-tested (and why)

The multi-criteria review logic (best-practices checks, modularity scoring, etc.)
is prose guidance inside SKILL.md — there is no Python function to call. Testing
it would require a full workspace runtime with a real Claude session. Smoke tests
cover the artifact structure; full evaluation requires integration tests.

## Running tests

```bash
python -m pytest tests/ -v
```
