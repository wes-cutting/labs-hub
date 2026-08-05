#!/usr/bin/env python3
"""Self-test for the docs gate. Python 3 stdlib only.

    python3 scripts/test-check-docs.py

A gate nobody has watched FAIL is not a gate — it is an assertion about itself. Each case
below injects one defect and asserts the check fires, plus negative controls for the things
that must NOT fire (fenced sample links, `:227` line refs, template placeholders, code
references inside dated records).
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("check_docs", Path(__file__).parent / "check-docs.py")
cd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cd)


class Case(unittest.TestCase):
    def setUp(self) -> None:
        cd.failures.clear()
        cd.permitted.clear()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "real.md").write_text("# real\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def links(self, rel: str, text: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        cd.check_links(p, Path(rel), text, self.root)

    # --- links ----------------------------------------------------------
    def test_broken_doc_link_fails(self) -> None:
        self.links("docs/a.md", "see [x](gone.md)")
        self.assertEqual(len(cd.failures), 1)
        self.assertIn("missing", cd.failures[0])

    def test_existing_doc_link_passes(self) -> None:
        self.links("docs/a.md", "see [x](real.md)")
        self.assertEqual(cd.failures, [])

    def test_link_inside_fenced_block_is_ignored(self) -> None:
        self.links("docs/a.md", "```\n[x](totally-made-up.md)\n```\n")
        self.assertEqual(cd.failures, [])

    def test_line_reference_is_stripped(self) -> None:
        self.links("docs/a.md", "see [x](real.md:227)")
        self.assertEqual(cd.failures, [])

    def test_placeholder_target_is_ignored(self) -> None:
        self.links("docs/a.md", "see [x](docs/spikes/SPIKE-<NN>-<slug>.md)")
        self.assertEqual(cd.failures, [])

    def test_code_ref_in_dated_record_is_permitted_not_failed(self) -> None:
        self.links("docs/spikes/s.md", "see [code](../../src/gone.ts)")
        self.assertEqual(cd.failures, [])
        self.assertEqual(len(cd.permitted), 1)

    def test_code_ref_in_current_system_doc_fails(self) -> None:
        self.links("docs/a.md", "see [code](../src/gone.ts)")
        self.assertEqual(len(cd.failures), 1)

    def test_template_link_resolves_from_its_destination(self) -> None:
        # A template copied to docs/spikes/ must reach the spine as ../, not ../docs/ —
        # this is the exact defect the gate was built after finding.
        (self.root / "templates").mkdir()
        self.links("templates/SPIKE-REPORT-TEMPLATE.md", "see [w](../docs/real.md)")
        self.assertEqual(len(cd.failures), 1, "wrong prefix from copy destination must fail")

        cd.failures.clear()
        self.links("templates/SPIKE-REPORT-TEMPLATE.md", "see [w](../real.md)")
        self.assertEqual(cd.failures, [], "correct prefix from copy destination must pass")

    # --- frontmatter ----------------------------------------------------
    def fm(self, rel: str, text: str, ids: dict | None = None) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        cd.check_frontmatter(p, Path(rel), text, ids if ids is not None else {})

    def test_missing_frontmatter_fails(self) -> None:
        self.fm("docs/a.md", "# no frontmatter\n")
        self.assertEqual(len(cd.failures), 1)

    def test_id_type_mismatch_fails(self) -> None:
        self.fm("docs/a.md", "---\nid: DOC-THING\ntype: spike\nstatus: Open\n---\n")
        self.assertIn("does not match type", cd.failures[0])

    def test_duplicate_id_fails(self) -> None:
        self.fm("docs/a.md", "---\nid: DOC-X\ntype: standard\nstatus: Accepted\n---\n",
                ids={"DOC-X": Path("docs/other.md")})
        self.assertIn("duplicate id", cd.failures[0])

    def test_placeholder_id_fails_in_a_real_doc(self) -> None:
        self.fm("docs/a.md", "---\nid: DOC-<slug>\ntype: standard\nstatus: Accepted\n---\n")
        self.assertIn("placeholder", cd.failures[0])

    def test_placeholder_id_passes_in_a_template(self) -> None:
        self.fm("docs/adr/ADR-TEMPLATE.md", "---\nid: ADR-<NNNN>\ntype: adr\nstatus: Proposed\n---\n")
        self.assertEqual(cd.failures, [])

    # --- tables & headings ----------------------------------------------
    def test_ragged_table_fails(self) -> None:
        cd.check_tables(Path("docs/a.md"), "| a | b |\n| - | - |\n| 1 | 2 | 3 |\n")
        self.assertIn("ragged", cd.failures[0])

    def test_table_without_header_separator_fails(self) -> None:
        cd.check_tables(Path("docs/a.md"), "| a | b |\n| 1 | 2 |\n")
        self.assertIn("no header separator", cd.failures[0])

    def test_well_formed_table_passes(self) -> None:
        cd.check_tables(Path("docs/a.md"), "| a | b |\n| - | - |\n| 1 | 2 |\n")
        self.assertEqual(cd.failures, [])

    def test_heading_gap_fails(self) -> None:
        cd.check_headings(Path("docs/a.md"), "## 1. one\n## 2. two\n## 4. four\n")
        self.assertIn("renumbering drift", cd.failures[0])

    def test_contiguous_headings_pass(self) -> None:
        cd.check_headings(Path("docs/a.md"), "## 1. one\n## 2. two\n## 3. three\n")
        self.assertEqual(cd.failures, [])

    # --- README tree ----------------------------------------------------
    def test_readme_tree_detects_both_directions(self) -> None:
        (self.root / "README.md").write_text(
            "# r\n\n```\nrepo/\n├─ listed-but-absent.md\n└─ docs/\n```\n"
        )
        cd.check_readme_tree(self.root)
        joined = "\n".join(cd.failures)
        self.assertIn("listed-but-absent.md", joined)  # listed, does not exist
        self.assertIn("real.md", joined)               # exists, not listed

    def test_readme_tree_check_self_disables_without_a_tree_block(self) -> None:
        (self.root / "README.md").write_text("# r\n\nNo tree here.\n")
        note = cd.check_readme_tree(self.root)
        self.assertEqual(cd.failures, [])
        self.assertIsNotNone(note)


if __name__ == "__main__":
    unittest.main(verbosity=2)
