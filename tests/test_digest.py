import unittest
from pathlib import Path

from codex_maintainer_kit.digest import load_items, render_digest


class DigestTest(unittest.TestCase):
    def test_load_items_reads_labels(self) -> None:
        issues = load_items(Path("examples/issues.json"), "issue")

        self.assertEqual(issues[0].number, 12)
        self.assertIn("regression", issues[0].labels)

    def test_render_digest_prioritizes_blockers(self) -> None:
        issues = load_items(Path("examples/issues.json"), "issue")
        prs = load_items(Path("examples/prs.json"), "pr")

        markdown = render_digest("demo/project", issues, prs)

        self.assertIn("# Maintainer Digest: demo/project", markdown)
        self.assertIn("Regression in release checklist parser", markdown)
        self.assertIn("Security hardening for file loader", markdown)
        self.assertIn("Do not cut a release", markdown)


if __name__ == "__main__":
    unittest.main()
