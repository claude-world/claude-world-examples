#!/usr/bin/env python3
"""Validate the fenced code blocks in this repository's Markdown files.

Rules:
- ```json blocks must be strict JSON: no comments, trailing commas, `...`
  placeholders or duplicate keys. Use ```jsonc for a snippet that is
  intentionally partial or annotated; those blocks are not parsed.
- ```yaml / ```yml blocks must parse as YAML without duplicate keys.
- With --actionlint, YAML blocks that are complete GitHub Actions workflows
  (top-level `on` and `jobs`) are also linted with actionlint, and findings
  are reported against the Markdown file and line.

Usage: check_code_blocks.py [--actionlint] [FILE.md ...]
With no files, every Markdown file tracked by git is checked.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"


class UniqueKeyLoader(yaml.SafeLoader):
    """A SafeLoader that rejects duplicate mapping keys."""


def _construct_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key {key!r}", key_node.start_mark
            )
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def _reject_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise ValueError(f"duplicate key(s): {', '.join(duplicates)}")
    return dict(pairs)


def iter_blocks(path: Path):
    """Yield (language, first content line number, text) for each fenced block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        opening = FENCE.match(lines[i])
        if not opening:
            i += 1
            continue
        indent, fence = opening["indent"], opening["fence"]
        info = opening["info"].strip()
        language = info.split()[0].lower() if info else ""
        first_line = i + 2
        body = []
        i += 1
        while i < len(lines):
            closing = FENCE.match(lines[i])
            if (
                closing
                and closing["fence"][0] == fence[0]
                and len(closing["fence"]) >= len(fence)
                and not closing["info"].strip()
            ):
                break
            line = lines[i]
            body.append(line[len(indent):] if line.startswith(indent) else line.lstrip())
            i += 1
        yield language, first_line, "\n".join(body) + "\n"
        i += 1


def is_workflow(document) -> bool:
    # YAML 1.1 reads a bare `on` key as the boolean True.
    return isinstance(document, dict) and "jobs" in document and (
        "on" in document or True in document
    )


def report(path: str, line: int, message: str) -> None:
    print(f"{path}:{line}: {message}")
    if IN_CI:
        print(f"::error file={path},line={line}::{message}")


def check_file(path: Path, workflows: list[tuple[str, int, str]]) -> int:
    errors = 0
    for language, first_line, text in iter_blocks(path):
        if language == "json":
            try:
                json.loads(text, object_pairs_hook=_reject_duplicate_keys)
            except (json.JSONDecodeError, ValueError) as exc:
                line = first_line + getattr(exc, "lineno", 1) - 1
                report(str(path), line, f"invalid JSON block: {exc}")
                errors += 1
        elif language in ("yaml", "yml"):
            try:
                documents = list(yaml.load_all(text, Loader=UniqueKeyLoader))
            except yaml.YAMLError as exc:
                mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
                line = first_line + (mark.line if mark else 0)
                report(str(path), line, f"invalid YAML block: {exc}".replace("\n", " "))
                errors += 1
                continue
            if len(documents) == 1 and is_workflow(documents[0]):
                workflows.append((str(path), first_line, text))
    return errors


def lint_workflows(workflows: list[tuple[str, int, str]]) -> int:
    if not workflows:
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        sources = {}
        for index, (path, first_line, text) in enumerate(workflows):
            target = Path(tmp, f"block-{index}.yml")
            target.write_text(text, encoding="utf-8")
            sources[target.resolve()] = (path, first_line)
        result = subprocess.run(
            ["actionlint", "-format", "{{json .}}", *map(str, sources)],
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode not in (0, 1):
        print(result.stderr or result.stdout, file=sys.stderr)
        return 1
    findings = json.loads(result.stdout or "[]")
    for finding in findings:
        path, first_line = sources[Path(finding["filepath"]).resolve()]
        report(path, first_line + finding["line"] - 1, f"actionlint: {finding['message']}")
    return len(findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument(
        "--actionlint",
        action="store_true",
        help="lint embedded GitHub Actions workflows with actionlint",
    )
    args = parser.parse_args()

    files = args.files or [
        Path(name)
        for name in subprocess.run(
            ["git", "ls-files", "*.md"], capture_output=True, text=True, check=True
        ).stdout.splitlines()
    ]
    workflows: list[tuple[str, int, str]] = []
    errors = sum(check_file(path, workflows) for path in files)
    if args.actionlint:
        errors += lint_workflows(workflows)
    print(
        f"Checked {len(files)} Markdown files and {len(workflows)} embedded workflows: "
        f"{errors} problem(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
