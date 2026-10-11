#!/usr/bin/env python3
"""Regression coverage for the Cloudflare-compatible SOP gate client."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest
from unittest import mock


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "sop-checklist-gate.py"
SPEC = importlib.util.spec_from_file_location("sop_checklist_gate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return b"{}"

    def getcode(self) -> int:
        return 200


class GiteaClientUserAgentTest(unittest.TestCase):
    def test_request_uses_cloudflare_compatible_user_agent(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return _Response()

        client = MODULE.GiteaClient("git.moleculesai.app", "test-token")
        with mock.patch.object(
            MODULE.urllib.request, "urlopen", side_effect=fake_urlopen
        ):
            code, body = client._req("GET", "/version")

        self.assertEqual((code, body), (200, {}))
        self.assertEqual(captured["timeout"], 20)
        self.assertEqual(
            captured["request"].get_header("User-agent"), "curl/8.4.0"
        )


if __name__ == "__main__":
    unittest.main()
