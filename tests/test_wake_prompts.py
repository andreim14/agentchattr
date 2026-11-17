"""One poll may hold triggers from several channels/jobs: none may be dropped."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wrapper import _wake_prompts  # noqa: E402


def q(**kw):
    return json.dumps(kw)


class WakePromptTests(unittest.TestCase):
    def test_single_channel_unchanged(self):
        extras, p = _wake_prompts([q(channel="reviews"), q(channel="reviews")])
        self.assertEqual(extras, [])
        self.assertEqual(p, "use mcp to read #reviews - you're mentioned, take appropriate action and respond")

    def test_two_channels_both_named(self):
        _, p = _wake_prompts([q(channel="general"), q(channel="incidents")])
        self.assertIn("#general", p)
        self.assertIn("#incidents", p)

    def test_channel_and_job_both_named(self):
        _, p = _wake_prompts([q(channel="general", job_id=7), q(channel="reviews")])
        self.assertIn("#reviews", p)
        self.assertIn("job_id=7", p)

    def test_single_job(self):
        _, p = _wake_prompts([q(channel="general", job_id=3)])
        self.assertTrue(p.startswith("use mcp to read job_id=3"))

    def test_slash_command_kept_alongside_mention(self):
        extras, p = _wake_prompts([q(channel="general", prompt="/compact"), q(channel="general")])
        self.assertEqual(extras, ["/compact"])
        self.assertIn("#general", p)

    def test_only_custom_prompts(self):
        extras, p = _wake_prompts([q(prompt="/compact"), q(prompt="/context")])
        self.assertEqual((extras, p), (["/compact"], "/context"))

    def test_garbage_lines_ignored(self):
        _, p = _wake_prompts(["not json", "", q(channel="ops")])
        self.assertIn("#ops", p)


if __name__ == "__main__":
    unittest.main()
