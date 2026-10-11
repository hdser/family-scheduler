#!/usr/bin/env python3
"""Fail if any personal value from private/family.json appears in a file git would commit.

    python3 scripts/check_private.py          # run by hand, or as the git pre-commit hook

What counts as personal: every text value in private/family.json (names, ids, emails,
calendar id, board link, prompt paragraphs…) plus the extra words listed under
"private_terms" (surname, school, clubs, town…). Values that are the same as in
config/family.example.json, and generic words like "his" or "handball", are skipped.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRIVATE = ROOT / "private/family.json"
EXAMPLE = ROOT / "config/family.example.json"
GENERIC = {"he", "his", "him", "himself", "she", "her", "hers", "herself", "they", "their", "them",
           "themselves", "handball", "basketball", "volleyball", "swimming", "school", "both", "family"}
SKIP_KEYS = {"match", "_readme"}  # regex patterns are covered by private_terms
SKIP_DIRS = {".git", "private", "dist", "node_modules", "__pycache__"}


def leaves(v, key=""):
    if isinstance(v, dict):
        for k, x in v.items():
            if k not in SKIP_KEYS:
                yield from leaves(x, k)
    elif isinstance(v, list):
        for x in v:
            yield from leaves(x, key)
    elif isinstance(v, str):
        yield v


def tracked_files():
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                             cwd=ROOT, capture_output=True, check=True).stdout.decode()
        files = [ROOT / f for f in out.split("\0") if f]
    except Exception:
        files = [p for p in ROOT.rglob("*") if p.is_file()]
    return [f for f in files if f.exists() and not (set(f.relative_to(ROOT).parts) & SKIP_DIRS)]


def main():
    if not PRIVATE.exists():
        print("check_private: no private/family.json, nothing to check")
        return 0
    cfg = json.loads(PRIVATE.read_text())
    example = set(leaves(json.loads(EXAMPLE.read_text()))) if EXAMPLE.exists() else set()
    terms = set()
    for v in leaves(cfg):
        v = v.strip()
        if v.startswith(("basketball:", "volleyball:", "swimming:", "handball:")):
            v = v.split(":", 1)[1]
        if len(v) < 3 or v in example or v.lower() in GENERIC:
            continue
        terms.add(v)
    pats = []
    for t in sorted(terms, key=len, reverse=True):
        left = r"(?<![\w])" if t[0].isalnum() else ""
        # short values (4 letters or fewer) must be whole words; longer ones also match as the start of a word ("Lindqvist" in "Lindqvists")
        right = r"(?![\w])" if t[-1].isalnum() and len(t) <= 4 else ""
        pats.append((t, re.compile(left + re.escape(t) + right, re.I)))
    hits = 0
    for f in tracked_files():
        try:
            text = f.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.split("\n"), 1):
            for t, p in pats:
                if p.search(line):
                    hits += 1
                    shown = t if len(t) <= 40 else t[:37] + "..."
                    print(f"{f.relative_to(ROOT)}:{n}: contains private value {shown!r}")
                    break
    if hits:
        print(f"check_private: {hits} line(s) with personal values. Move them to private/family.json and use a {{{{placeholder}}}}.")
        return 1
    print(f"check_private: OK ({len(terms)} private values, {len(tracked_files())} files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
