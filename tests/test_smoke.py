#!/usr/bin/env python3
"""
Smoke tests for molecule-skill-code-review.

See tests/README.md for rationale on limited test coverage.

Run: python -m pytest tests/ -v
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPluginManifest(unittest.TestCase):
    """Verify plugin.yaml is well-formed."""

    @classmethod
    def setUpClass(cls):
        import yaml
        manifest_path = os.path.join(REPO_ROOT, 'plugin.yaml')
        with open(manifest_path) as f:
            cls.manifest = yaml.safe_load(f)

    def test_plugin_yaml_loads(self):
        self.assertIsInstance(self.manifest, dict)

    def test_name(self):
        self.assertEqual(self.manifest['name'], 'molecule-skill-code-review')

    def test_version_semver(self):
        v = self.manifest['version']
        self.assertRegex(v, r'^\d+\.\d+\.\d+$')

    def test_description_present(self):
        self.assertGreater(len(self.manifest.get('description', '')), 20)

    def test_runtime_claude_code(self):
        self.assertIn('claude_code', self.manifest.get('runtimes', []))

    def test_skill_declared(self):
        self.assertIn('code-review', self.manifest.get('skills', []))


class TestCodeReviewSkill(unittest.TestCase):
    """Verify skills/code-review/SKILL.md is well-formed."""

    SKILL_PATH = os.path.join(REPO_ROOT, 'skills', 'code-review', 'SKILL.md')

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.SKILL_PATH))

    def test_has_frontmatter(self):
        import yaml
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertTrue(content.startswith('---'))
        parts = content.split('---', 2)
        self.assertEqual(len(parts), 3)
        _, frontmatter, _ = parts
        data = yaml.safe_load(frontmatter)
        self.assertIsInstance(data, dict)

    def test_frontmatter_name(self):
        import yaml
        with open(self.SKILL_PATH) as f:
            content = f.read()
        parts = content.split('---', 2)
        _, frontmatter, _ = parts
        data = yaml.safe_load(frontmatter)
        self.assertEqual(data['name'], 'code-review')

    def test_body_has_heading(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        parts = content.split('---', 2)
        _, _, body = parts
        self.assertRegex(body.lstrip(), r'^# ', "SKILL.md body must start with a # heading")

    def test_body_has_review_criteria(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('Best Practices', content)
        self.assertIn('Modularity', content)


class TestAdapter(unittest.TestCase):
    """Verify Claude Code adapter is a valid re-export of AgentskillsAdaptor."""

    ADAPTER_PATH = os.path.join(REPO_ROOT, 'adapters', 'claude_code.py')

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.ADAPTER_PATH))

    def test_re_exports_agentskills_adaptor(self):
        with open(self.ADAPTER_PATH) as f:
            content = f.read()
        self.assertIn('AgentskillsAdaptor', content)


class TestValidatePlugin(unittest.TestCase):
    """Smoke-test validate-plugin.py if present."""

    def test_validate_plugin_exits_zero(self):
        import subprocess
        val_path = os.path.join(REPO_ROOT, '.molecule-ci', 'scripts', 'validate-plugin.py')
        if not os.path.isfile(val_path):
            self.skipTest("validate-plugin.py not found")
        result = subprocess.run(
            [sys.executable, val_path],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(
            result.returncode, 0,
            f"validate-plugin.py failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        self.assertIn('molecule-skill-code-review', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
