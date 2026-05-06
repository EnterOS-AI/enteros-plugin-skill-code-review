# Local Development Setup

This runbook covers setting up a local development environment for
`molecule-skill-code-review`.

---

## Prerequisites

- Python 3.11+
- `gh` CLI authenticated
- Write access to `Molecule-AI/molecule-ai-plugin-molecule-skill-code-review`

---

## Clone & Bootstrap

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-skill-code-review.git
cd molecule-ai-plugin-molecule-skill-code-review
```

---

## Validating Plugin Structure

```bash
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
echo "plugin.yaml OK"

python3 -c "
import yaml, os
with open('plugin.yaml') as f:
    data = yaml.safe_load(f)
for skill in data.get('skills', []):
    path = f'skills/{skill}/SKILL.md'
    exists = os.path.exists(path)
    print(f'[{\"OK\" if exists else \"MISSING\"}] {path}')
"
```

---

## Testing the Code Review Skill

The harness wrapper is provided by the Molecule AI platform at runtime.
To test:

1. Install the plugin in a test workspace
2. Open a PR in a test repo
3. Run the `code-review` skill against the PR diff
4. Verify findings appear in each relevant category

---

## Troubleshooting

### No findings on a deliberately buggy PR

- The skill uses heuristics — it may miss subtle bugs
- Run against a PR with known issues and verify at least some are caught
- Check the skill's criteria are correctly loaded

### Review times out on large PRs

- Break large PRs into smaller chunks for review
- The skill may need a token or time limit for very large diffs

---

## Related

- `skills/code-review/SKILL.md` — full review criteria and usage
