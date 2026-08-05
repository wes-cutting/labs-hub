#!/usr/bin/env python3
"""Docs gate — frontmatter, links, tables, heading sequence, README tree.

Carried as-is by the baseline kit and RUNNABLE FROM COMMIT ZERO: docs are the one thing
the kit ships, so this is the one gate step that never has to wait for a stack. Python 3
stdlib only, no dependencies, no package manifest.

    python3 scripts/check-docs.py          # from the repo root

Implements the policy in docs/00_WAYS_OF_WORKING.md §4:

  * doc -> doc  : STRICT EVERYWHERE. Every target must exist, ADRs and other append-only
                  records included — append-only protects the decision, not a wrong path.
  * doc -> code : strict in docs describing the current system; PERMITTED in dated records
                  (spikes, status reports, reviews), whose code references *should* rot.
                  Every permitted one is printed on each run, so the exception stays a
                  visible bounded list rather than a hole.
  * lexical     : fenced code blocks are skipped (sample text, not references); a trailing
                  `:227` is a line reference and is stripped before resolving.

Two things worth knowing about what this CANNOT do (§4):
  * A link check verifies that a path resolves, never that it resolves to what the author
    meant. Reusing a retired document's filename is its blind spot.
  * A gate's coverage is exactly the set of properties it checks, so this script prints
    what it scanned AND what it skipped. Read the coverage block; don't assume it.

Per-project configuration is the CONFIG section below and nothing else.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG — the only part a project edits.
# ---------------------------------------------------------------------------

#: Trees whose .md files must carry frontmatter (docs/00_WAYS_OF_WORKING.md §4).
FRONTMATTER_TREES = ("docs",)

#: Directories never walked at all.
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}

#: Trees that are link-checked but exempt from frontmatter, with the reason. Printed in
#: the coverage block so the exemption stays visible rather than silent.
FRONTMATTER_EXEMPT_TREES = {
    "examples": "illustrative walkthrough, not product docs",
    "templates": "stencils — their frontmatter is a pre-filled placeholder, checked separately",
}

#: Individual files exempt from frontmatter, with the reason.
FRONTMATTER_EXEMPT_FILES = {
    "templates/DISCOVERY-GUIDE.md": "read-only playbook, never copied into docs/",
    "templates/README-TEMPLATE.md": "destination is the repo root, where frontmatter renders as junk",
}

#: id prefix required for each frontmatter `type` (§4's prefix table). Anything not listed
#: must use DEFAULT_ID_PREFIX.
TYPE_ID_PREFIX = {
    "adr": "ADR-",
    "spike": "SPIKE-",
    "feature-spec": "FEAT-",
    "ux-spec": "UX-",
    "status-report": "SR-",
    "audit": "REV-",
    "initiative": "REV-",
    "working-note": "REV-",
    "generated": "REV-",
}
DEFAULT_ID_PREFIX = "DOC-"

#: Where each template is COPIED TO. Its links are written for that destination, so they
#: must be resolved from there — the relative prefix is a function of the file being
#: written, never a constant (§4). This mapping is what makes that checkable.
TEMPLATE_DEST = {
    "README-TEMPLATE.md": ".",
    "DISCOVERY-GUIDE.md": "templates",  # read in place, never copied
    "FEATURE-SPEC-TEMPLATE.md": "docs/features",
    "UX-SPEC-TEMPLATE.md": "docs/ux",
    "SPIKE-REPORT-TEMPLATE.md": "docs/spikes",
    "STATUS-REPORT-TEMPLATE.md": "docs/status-reports",
}
TEMPLATE_DEST_DEFAULT = "docs"

#: Dated records: doc -> code links here are permitted-but-printed, never failed.
DATED_RECORD_TREES = ("docs/spikes", "docs/status-reports", "docs/reviews")

#: Targets that exist in a PROJECT built from the kit but not in the kit itself. Only
#: consulted for links inside templates/; permitted-but-printed, never silent.
PROJECT_ONLY_TARGETS = (
    re.compile(r"^KIT-README\.md$"),
    re.compile(r"^docs/0\d_[A-Z_]+(-[A-Z]+)?\.md$"),
    re.compile(r"^docs/DEPLOY_CONTRACT\.md$"),
    re.compile(r"^docs/(features|ux|spikes|status-reports|reviews)(/|$)"),
    re.compile(r"^docs/adr/ADR-0*[1-9]"),
)

#: Check the README's file-tree block against the real tree. Self-disabling: skipped when
#: the README has no tree block.
CHECK_README_TREE = True

# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

FENCE = re.compile(r"^\s{0,3}(```|~~~)")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LINE_REF = re.compile(r":\d+$")
PLACEHOLDER = re.compile(r"[<>]")
NUMBERED_HEADING = re.compile(r"^##\s+(\d+)\.\s")

failures: list[str] = []
permitted: list[str] = []


def fail(path: Path, line: int, kind: str, msg: str) -> None:
    failures.append(f"  {path}:{line}  [{kind}] {msg}")


def permit(path: Path, line: int, kind: str, msg: str) -> None:
    permitted.append(f"  {path}:{line}  [{kind}] {msg}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def under(path: Path, trees) -> bool:
    s = path.as_posix()
    return any(s == t or s.startswith(t + "/") for t in trees)


def code_lines(text: str):
    """Yield (lineno, line) for lines outside fenced code blocks (§4 lexical rule)."""
    in_fence = False
    marker = ""
    for i, line in enumerate(text.split("\n"), 1):
        m = FENCE.match(line)
        if m:
            if not in_fence:
                in_fence, marker = True, m.group(1)
            elif line.strip().startswith(marker):
                in_fence = False
            continue
        if not in_fence:
            yield i, line


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    body = text[3:end]
    out = {}
    for line in body.split("\n"):
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*?)\s*(?:#.*)?$", line)
        if m and m.group(2):
            out[m.group(1)] = m.group(2).strip()
    return out


def is_template(rel: Path) -> bool:
    """A stencil, not a doc. Lives in templates/ OR is named *-TEMPLATE.md anywhere —
    docs/adr/ADR-TEMPLATE.md sits beside the ADRs it produces."""
    return rel.parts[0] == "templates" or rel.name.endswith("-TEMPLATE.md")


def resolve_base(path: Path, root: Path) -> Path:
    """The directory a file's links are written relative to.

    For a template that is its COPY DESTINATION, not its own location.
    """
    if path.parent.name == "templates" and path.parent.parent == root:
        return root / TEMPLATE_DEST.get(path.name, TEMPLATE_DEST_DEFAULT)
    return path.parent


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_frontmatter(path: Path, rel: Path, text: str, ids: dict[str, Path]) -> None:
    fm = parse_frontmatter(text)
    template = is_template(rel)

    if fm is None:
        fail(rel, 1, "frontmatter", "missing frontmatter block (id / type / status)")
        return

    for key in ("id", "type", "status"):
        if key not in fm:
            fail(rel, 1, "frontmatter", f"missing required key `{key}`")
    if "id" not in fm or "type" not in fm:
        return

    doc_id, doc_type = fm["id"], fm["type"]
    want = TYPE_ID_PREFIX.get(doc_type, DEFAULT_ID_PREFIX)
    if not doc_id.startswith(want):
        fail(rel, 1, "frontmatter", f"id `{doc_id}` does not match type `{doc_type}` (needs prefix `{want}`)")

    if PLACEHOLDER.search(doc_id):
        # A template's id is a stencil (`SPIKE-<NN>`); prefix is checked, shape is not,
        # and it never joins the uniqueness pool.
        if not template:
            fail(rel, 1, "frontmatter", f"id `{doc_id}` still contains a placeholder")
        return

    if not re.fullmatch(r"[A-Z]+-[A-Za-z0-9][A-Za-z0-9-]*", doc_id):
        fail(rel, 1, "frontmatter", f"id `{doc_id}` is not well-formed (PREFIX-slug)")

    if not template:
        if doc_id in ids:
            fail(rel, 1, "frontmatter", f"duplicate id `{doc_id}` (also in {ids[doc_id]})")
        else:
            ids[doc_id] = rel


def check_links(path: Path, rel: Path, text: str, root: Path) -> None:
    base = resolve_base(path, root)
    template = is_template(rel)
    dated = under(rel, DATED_RECORD_TREES)
    abs_root = root.resolve()

    for lineno, line in code_lines(text):
        for m in LINK.finditer(line):
            raw = m.group(1)
            if raw.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = raw.split("#")[0]
            if not target:
                continue
            if PLACEHOLDER.search(target):
                continue  # `<slug>` etc. — a stencil path, not a reference
            target = LINE_REF.sub("", target)

            resolved = (base / target).resolve()
            if resolved.exists():
                continue

            # Match the PROJECT_ONLY allowance against the RESOLVED repo-relative path, not
            # the raw target: `../docs/x.md` from docs/spikes/ resolves to `docs/docs/x.md`,
            # which must fail rather than pattern-match its way into the permitted list.
            try:
                repo_target = resolved.relative_to(abs_root).as_posix()
            except ValueError:
                repo_target = None

            shown = f"`{raw}` -> {repo_target or resolved}"

            if template and repo_target and any(p.match(repo_target) for p in PROJECT_ONLY_TARGETS):
                permit(rel, lineno, "link", f"{shown} (exists in a project, not in the kit)")
            elif dated and not target.endswith((".md", "/")):
                permit(rel, lineno, "link", f"{shown} (code ref in a dated record)")
            else:
                fail(rel, lineno, "link", f"{shown} (missing)")


def check_tables(rel: Path, text: str) -> None:
    block: list[tuple[int, str]] = []

    def flush() -> None:
        if len(block) < 2:
            return
        widths = {row.count("|") for _, row in block}
        if len(widths) > 1:
            fail(rel, block[0][0], "table", f"ragged rows — differing cell counts {sorted(widths)}")
        if not re.fullmatch(r"\|[\s:|-]+\|", block[1][1]):
            fail(rel, block[0][0], "table", "no header separator row — renders as garbage")

    for lineno, line in code_lines(text):
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and len(s) > 1:
            block.append((lineno, s))
        else:
            flush()
            block = []
    flush()


def check_headings(rel: Path, text: str) -> None:
    seen: list[tuple[int, int]] = []
    for lineno, line in code_lines(text):
        m = NUMBERED_HEADING.match(line)
        if m:
            seen.append((lineno, int(m.group(1))))
    for idx, (lineno, num) in enumerate(seen, 1):
        if num != idx:
            fail(rel, lineno, "headings", f"section numbered {num} but is #{idx} in order — renumbering drift")
            return


def check_readme_tree(root: Path) -> str | None:
    readme = root / "README.md"
    if not readme.exists():
        return "no README.md"
    text = readme.read_text()
    blocks = re.findall(r"```[^\n]*\n(.*?)```", text, re.S)
    tree = next((b for b in blocks if "├─" in b or "└─" in b), None)
    if tree is None:
        return "README has no file-tree block"

    listed = set(re.findall(r"([A-Za-z0-9_.\-]+\.(?:md|yml|yaml))", tree))
    actual = {
        p.name
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix in (".md", ".yml", ".yaml")
        and not set(p.relative_to(root).parts) & SKIP_DIRS
        and not under(p.relative_to(root), ("examples",))
    }
    for name in sorted(actual - listed):
        fail(Path("README.md"), 1, "readme-tree", f"`{name}` exists but is not in the layout block")
    for name in sorted(listed - actual):
        fail(Path("README.md"), 1, "readme-tree", f"`{name}` is in the layout block but does not exist")
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    files = sorted(
        p
        for p in root.rglob("*.md")
        if not set(p.relative_to(root).parts) & SKIP_DIRS
    )

    ids: dict[str, Path] = {}
    fm_checked = fm_skipped = 0

    for path in files:
        rel = path.relative_to(root)
        text = path.read_text()

        check_links(path, rel, text, root)
        check_tables(rel, text)
        check_headings(rel, text)

        exempt = rel.as_posix() in FRONTMATTER_EXEMPT_FILES or under(rel, FRONTMATTER_EXEMPT_TREES)
        if under(rel, FRONTMATTER_TREES) and not exempt:
            check_frontmatter(path, rel, text, ids)
            fm_checked += 1
        else:
            fm_skipped += 1

    readme_note = check_readme_tree(root) if CHECK_README_TREE else "disabled"

    # --- report -----------------------------------------------------------
    print("docs check\n")
    print("Coverage (a gate's coverage is exactly what it checks — §4):")
    print(f"  markdown files scanned         : {len(files)}")
    print(f"  links / tables / headings      : all {len(files)}")
    print(f"  frontmatter validated          : {fm_checked}  (unique ids: {len(ids)})")
    print(f"  frontmatter intentionally skipped: {fm_skipped}")
    for tree, why in FRONTMATTER_EXEMPT_TREES.items():
        print(f"      {tree}/ — {why}")
    for name, why in FRONTMATTER_EXEMPT_FILES.items():
        print(f"      {name} — {why}")
    print(f"  README tree check              : {readme_note or 'run'}")

    if permitted:
        print(f"\nPermitted, listed exceptions ({len(permitted)}) — bounded, not a hole:")
        for item in permitted:
            print(item)

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for item in failures:
            print(item)
        print("\ndocs check: FAIL")
        return 1

    print("\ndocs check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
