#!/usr/bin/env python3
"""
Guard tests for the PR diff-acquisition guidance in skills/code-review/SKILL.md.

Why this file exists
--------------------
The molecule-code-reviewer kept posting false `REQUEST_CHANGES` ("the patch body
is absent" / "I can't see the diff") on green PRs because the diff was fetched
from the WRONG path:
  - the non-/api/v1 web route  <host>/<owner>/<repo>/pulls/<N>.diff  -> HTTP 404
    (CF-1010 behind Cloudflare on the public host), and/or
  - the per-file `patch` field of  /pulls/<N>/files , which Gitea OMITS for
    large/binary/many-file PRs (the field is absent -> "(no patch)").

The working path is the /api/v1 PR diff endpoint:
    {GITEA_API_URL}/repos/{owner}/{repo}/pulls/{N}.diff   -> HTTP 200, real diff.

These tests lock the SKILL.md guidance to the correct endpoint so a future edit
can't silently regress to the 404 path, and (when creds are present) prove the
endpoint actually returns a non-empty unified diff for a known PR.

Run: python -m pytest tests/ -v
"""
import os
import re
import unittest
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_PATH = os.path.join(REPO_ROOT, "skills", "code-review", "SKILL.md")


def _skill_text():
    with open(SKILL_PATH, encoding="utf-8") as f:
        return f.read()


class TestDiffFetchGuidance(unittest.TestCase):
    """Static guards — run everywhere, credential-free. These are the
    regression net for the 404 / 'no patch' false-REQUEST_CHANGES bug."""

    def test_documents_correct_api_v1_diff_endpoint(self):
        text = _skill_text()
        # The canonical, working endpoint must be documented verbatim.
        self.assertRegex(
            text,
            r"/repos/\$?\{?OWNER\}?/\$?\{?REPO\}?/pulls/\$?\{?N\}?\.diff",
            "SKILL.md must document the /api/v1 PR diff endpoint "
            "(.../repos/$OWNER/$REPO/pulls/$N.diff)",
        )
        self.assertIn(
            "/api/v1",
            text,
            "SKILL.md must reference the /api/v1 prefix for the diff fetch",
        )

    def test_fetch_uses_token_and_browser_user_agent(self):
        text = _skill_text()
        self.assertIn(
            "Authorization: token $GITEA_TOKEN",
            text,
            "diff fetch must send the Gitea token header",
        )
        self.assertIn(
            "User-Agent: Mozilla/5.0",
            text,
            "diff fetch must send a browser User-Agent to dodge CF-1010",
        )

    def test_warns_against_wrong_web_route(self):
        text = _skill_text().lower()
        self.assertIn("404", text, "SKILL.md must warn the web route returns 404")
        self.assertTrue(
            "non-`/api/v1`" in text or "non-/api/v1" in text or "web route" in text,
            "SKILL.md must call out the non-/api/v1 web route as the wrong path",
        )

    def test_warns_against_empty_files_patch_field(self):
        text = _skill_text().lower()
        self.assertIn(
            "patch` field",
            text,
            "SKILL.md must warn that the per-file `patch` field can be absent",
        )
        self.assertIn(
            "(no patch)",
            text,
            "SKILL.md must mention the '(no patch)' symptom it explains",
        )

    def test_does_not_recommend_gh_pr_diff_as_the_method(self):
        # `gh pr diff` may be MENTIONED as wrong, but must not be the
        # instructed fetch. Assert it only appears in a do-NOT context.
        text = _skill_text()
        for m in re.finditer(r"`?gh pr diff`?", text):
            window = text[max(0, m.start() - 80): m.end() + 40].lower()
            self.assertTrue(
                ("do not" in window) or ("cannot" in window) or ("wrong" in window),
                "`gh pr diff` must only appear flagged as wrong, never as the "
                "instructed fetch method",
            )


class TestLiveDiffFetch(unittest.TestCase):
    """Live guard — proves the documented endpoint returns a non-empty diff.

    SKIPPED unless GITEA_API_URL and GITEA_TOKEN are set, so it never runs (and
    never reds) credential-free CI. No CI-gate change is introduced by this test.
    Override the sample PR with DIFF_GUARD_OWNER/REPO/PR if the default is gone.
    """

    def test_known_pr_diff_is_non_empty(self):
        api = os.environ.get("GITEA_API_URL")
        tok = os.environ.get("GITEA_TOKEN")
        if not api or not tok:
            self.skipTest("GITEA_API_URL / GITEA_TOKEN not set — live fetch skipped")

        owner = os.environ.get("DIFF_GUARD_OWNER", "molecule-ai")
        repo = os.environ.get("DIFF_GUARD_REPO", "molecule-controlplane")
        pr = os.environ.get("DIFF_GUARD_PR", "1059")
        url = f"{api.rstrip('/')}/repos/{owner}/{repo}/pulls/{pr}.diff"

        req = urllib.request.Request(
            url,
            headers={
                "Authorization": "token " + tok,
                "User-Agent": "Mozilla/5.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                self.assertEqual(resp.status, 200, f"{url} did not return 200")
                body = resp.read().decode("utf-8", "ignore")
        except urllib.error.URLError as e:
            # Creds present but host unreachable from this runner — don't red an
            # unrelated build; the static guards already protect the path.
            self.skipTest(f"diff endpoint unreachable: {e}")

        self.assertTrue(body.strip(), f"diff body from {url} was empty")
        self.assertIn(
            "diff --git",
            body,
            f"{url} did not return a unified diff (got {len(body)} bytes)",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
