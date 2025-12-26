#!/usr/bin/env python3
"""
Check for broken internal links and references in Claude Code extensions.

Validates:
- Markdown links: [text](path)
- Reference mentions: `references/file.md`
- Skill references in descriptions
- Plugin component references

Usage:
    python lint_references.py <path>       # Check single file/directory
    python lint_references.py --all        # Check all extensions
    python lint_references.py --fix        # Suggest fixes for broken links

Exit codes:
    0 - All links valid
    1 - Broken links found
    2 - Usage error
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple
from urllib.parse import urlparse

CLAUDE_DIR = Path.home() / ".claude"

# Patterns for finding references
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
REFERENCE_MENTION_PATTERN = re.compile(r'`(references/[^`]+)`')
SKILL_REFERENCE_PATTERN = re.compile(r'/([a-z0-9_-]+)')  # Slash command references


@dataclass
class LinkResult:
    """Result of checking a single link."""
    source_file: str
    link_text: str
    link_target: str
    line_number: int
    is_valid: bool
    error: str = ""
    suggestion: str = ""


@dataclass
class LintResult:
    """Result of linting a file."""
    path: str
    links: List[LinkResult] = field(default_factory=list)

    @property
    def broken_count(self) -> int:
        return sum(1 for link in self.links if not link.is_valid)

    @property
    def is_valid(self) -> bool:
        return self.broken_count == 0


def is_url(target: str) -> bool:
    """Check if target is a URL (http/https)."""
    try:
        result = urlparse(target)
        return result.scheme in ("http", "https")
    except Exception:
        return False


def resolve_link(source_file: Path, target: str) -> Tuple[bool, str, str]:
    """
    Resolve a link target relative to the source file.
    Returns (is_valid, error_message, suggestion).
    """
    # Skip URLs
    if is_url(target):
        return True, "", ""

    # Skip anchor-only links
    if target.startswith("#"):
        return True, "", ""

    # Handle fragment (anchor) in path
    if "#" in target:
        target = target.split("#")[0]

    # Skip empty after fragment removal
    if not target:
        return True, "", ""

    # Resolve relative to source file's directory
    source_dir = source_file.parent
    target_path = (source_dir / target).resolve()

    if target_path.exists():
        return True, "", ""

    # Try some common fixes
    suggestion = ""

    # Check if file exists with different extension
    if not target_path.suffix:
        md_path = target_path.with_suffix(".md")
        if md_path.exists():
            suggestion = f"Try: {target}.md"

    # Check if in references/ directory
    if "references" not in target:
        ref_path = source_dir / "references" / target
        if ref_path.exists():
            suggestion = f"Try: references/{target}"
        ref_md_path = source_dir / "references" / (target + ".md")
        if ref_md_path.exists():
            suggestion = f"Try: references/{target}.md"

    return False, f"File not found: {target_path}", suggestion


def lint_markdown_file(path: Path) -> LintResult:
    """Lint a markdown file for broken links."""
    result = LintResult(str(path))

    try:
        content = path.read_text()
    except Exception as e:
        result.links.append(LinkResult(
            source_file=str(path),
            link_text="",
            link_target="",
            line_number=0,
            is_valid=False,
            error=f"Cannot read file: {e}"
        ))
        return result

    lines = content.split("\n")
    in_code_block = False

    for line_num, line in enumerate(lines, 1):
        # Track fenced code blocks (``` or ~~~)
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        # Skip lines inside code blocks (template examples, not real links)
        if in_code_block:
            continue

        # Check markdown links
        for match in MARKDOWN_LINK_PATTERN.finditer(line):
            link_text, link_target = match.groups()

            # Skip special links
            if link_target.startswith("mailto:"):
                continue

            is_valid, error, suggestion = resolve_link(path, link_target)

            result.links.append(LinkResult(
                source_file=str(path),
                link_text=link_text,
                link_target=link_target,
                line_number=line_num,
                is_valid=is_valid,
                error=error,
                suggestion=suggestion
            ))

        # Check reference mentions in backticks
        for match in REFERENCE_MENTION_PATTERN.finditer(line):
            ref_path = match.group(1)
            match_start = match.start()

            # Skip if this is inside a quoted string (syntax example)
            # Check for quotes before the match
            prefix = line[:match_start]
            if prefix.count('"') % 2 == 1 or prefix.count("'") % 2 == 1:
                continue  # Inside a quoted string - this is a syntax example

            is_valid, error, suggestion = resolve_link(path, ref_path)

            result.links.append(LinkResult(
                source_file=str(path),
                link_text=f"`{ref_path}`",
                link_target=ref_path,
                line_number=line_num,
                is_valid=is_valid,
                error=error,
                suggestion=suggestion
            ))

    return result


def lint_skill(path: Path) -> List[LintResult]:
    """Lint a skill and its references directory."""
    results = [lint_markdown_file(path)]

    references_dir = path.parent / "references"
    if references_dir.exists():
        for ref_file in references_dir.glob("*.md"):
            results.append(lint_markdown_file(ref_file))

    return results


def lint_plugin(path: Path) -> List[LintResult]:
    """Lint all markdown files in a plugin."""
    results = []

    for md_file in path.rglob("*.md"):
        results.append(lint_markdown_file(md_file))

    return results


def find_and_lint_all(base_dir: Path) -> List[LintResult]:
    """Find and lint all extensions."""
    results = []

    # Skills
    for skill_md in base_dir.rglob("SKILL.md"):
        results.extend(lint_skill(skill_md))

    # Agents
    agents_dir = base_dir / "agents"
    if agents_dir.exists():
        for agent in agents_dir.glob("*.md"):
            results.append(lint_markdown_file(agent))

    # Commands
    commands_dir = base_dir / "commands"
    if commands_dir.exists():
        for cmd in commands_dir.glob("*.md"):
            results.append(lint_markdown_file(cmd))

    # Plugins
    plugins_dir = base_dir / "plugins"
    if plugins_dir.exists():
        for item in plugins_dir.iterdir():
            if item.is_dir() and (item / ".claude-plugin").exists():
                results.extend(lint_plugin(item))

    # CLAUDE.md files
    for claude_md in base_dir.rglob("CLAUDE.md"):
        results.append(lint_markdown_file(claude_md))

    return results


def print_results(results: List[LintResult], show_valid: bool = False) -> int:
    """Print lint results and return exit code."""
    total_broken = 0
    total_links = 0

    for result in results:
        broken = [link for link in result.links if not link.is_valid]
        total_broken += len(broken)
        total_links += len(result.links)

        if broken:
            print(f"\n{result.path}:")
            for link in broken:
                print(f"  Line {link.line_number}: {link.link_text}")
                print(f"    Target: {link.link_target}")
                print(f"    Error: {link.error}")
                if link.suggestion:
                    print(f"    Suggestion: {link.suggestion}")

        elif show_valid and result.links:
            print(f"\n{result.path}: {len(result.links)} links OK")

    print(f"\n{'='*50}")
    print(f"Checked {total_links} links in {len(results)} files")
    print(f"Found {total_broken} broken links")

    return 1 if total_broken > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="Lint Claude Code extension references")
    parser.add_argument("path", nargs="?", help="Path to lint")
    parser.add_argument("--all", action="store_true", help="Lint all extensions in ~/.claude")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show valid links too")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    results = []

    if args.all:
        results = find_and_lint_all(CLAUDE_DIR)
    elif args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            sys.exit(2)

        if path.is_file():
            if path.name == "SKILL.md":
                results = lint_skill(path)
            else:
                results = [lint_markdown_file(path)]
        else:
            results = find_and_lint_all(path)
    else:
        parser.print_help()
        sys.exit(2)

    if args.json:
        output = []
        for result in results:
            output.append({
                "path": result.path,
                "broken_count": result.broken_count,
                "links": [
                    {
                        "text": link.link_text,
                        "target": link.link_target,
                        "line": link.line_number,
                        "valid": link.is_valid,
                        "error": link.error,
                        "suggestion": link.suggestion,
                    }
                    for link in result.links
                    if not link.is_valid or args.verbose
                ]
            })
        print(json.dumps(output, indent=2))
        sys.exit(0 if all(r.is_valid for r in results) else 1)
    else:
        sys.exit(print_results(results, args.verbose))


if __name__ == "__main__":
    main()
