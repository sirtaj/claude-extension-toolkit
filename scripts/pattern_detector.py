#!/usr/bin/env python3
"""
Detect deprecated patterns in Claude Code extensions.

Checks extensions against known deprecated patterns from the version manifest.

Usage:
    python pattern_detector.py <path>           # Check single file/directory
    python pattern_detector.py --all            # Check all extensions
    python pattern_detector.py --severity error # Only show errors

Exit codes:
    0 - No deprecated patterns found
    1 - Deprecated patterns found
    2 - Usage error
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = Path(__file__).parent
TOOLKIT_ROOT = SCRIPT_DIR.parent
CLAUDE_DIR = Path.home() / ".claude"

MANIFEST_PATH = TOOLKIT_ROOT / "data" / "version-manifest.json"


@dataclass
class PatternMatch:
    """A deprecated pattern match."""
    file_path: str
    line_number: int
    line_content: str
    pattern: str
    replacement: str
    severity: str
    since: str


@dataclass
class DetectionResult:
    """Result of pattern detection for a file."""
    file_path: str
    matches: List[PatternMatch] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(m.severity == "error" for m in self.matches)

    @property
    def has_warnings(self) -> bool:
        return any(m.severity == "warning" for m in self.matches)


def load_deprecations() -> List[dict]:
    """Load deprecation patterns from version manifest."""
    if not MANIFEST_PATH.exists():
        print(f"Warning: Manifest not found at {MANIFEST_PATH}", file=sys.stderr)
        return []

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    return manifest.get("deprecations", [])


def check_file(path: Path, deprecations: List[dict]) -> DetectionResult:
    """Check a file for deprecated patterns."""
    result = DetectionResult(str(path))

    try:
        content = path.read_text()
    except Exception as e:
        print(f"Warning: Cannot read {path}: {e}", file=sys.stderr)
        return result

    lines = content.split("\n")

    for deprecation in deprecations:
        pattern = deprecation["pattern"]
        replacement = deprecation.get("replacement", "see documentation")
        severity = deprecation.get("severity", "warning")
        since = deprecation.get("since", "unknown")

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            # Treat as literal string match
            regex = re.compile(re.escape(pattern), re.IGNORECASE)

        for line_num, line in enumerate(lines, 1):
            if regex.search(line):
                match = PatternMatch(
                    file_path=str(path),
                    line_number=line_num,
                    line_content=line.strip()[:80],
                    pattern=pattern,
                    replacement=replacement,
                    severity=severity,
                    since=since,
                )
                result.matches.append(match)

    return result


def find_extension_files(base_dir: Path) -> List[Path]:
    """Find all extension files to check."""
    files = []

    # Markdown files (skills, agents, commands)
    for md_file in base_dir.rglob("*.md"):
        files.append(md_file)

    # Shell scripts (hooks)
    for sh_file in base_dir.rglob("*.sh"):
        files.append(sh_file)

    # JSON files (settings, hooks config)
    for json_file in base_dir.rglob("*.json"):
        # Skip manifest and package files
        if json_file.name not in ["package.json", "package-lock.json"]:
            files.append(json_file)

    return files


def print_results(
    results: List[DetectionResult],
    severity_filter: Optional[str] = None
) -> int:
    """Print detection results and return exit code."""
    has_issues = False

    for result in results:
        matches = result.matches
        if severity_filter:
            matches = [m for m in matches if m.severity == severity_filter]

        if not matches:
            continue

        has_issues = True
        print(f"\n{result.file_path}")

        for match in matches:
            severity_marker = "ERROR" if match.severity == "error" else "WARN"
            print(f"  [{severity_marker}] Line {match.line_number}: {match.pattern}")
            print(f"    Found: {match.line_content}")
            print(f"    Replace with: {match.replacement}")
            print(f"    Deprecated since: v{match.since}")

    if has_issues:
        error_count = sum(
            1 for r in results for m in r.matches if m.severity == "error"
        )
        warning_count = sum(
            1 for r in results for m in r.matches if m.severity == "warning"
        )
        print(f"\n{'='*50}")
        print(f"Found {error_count} errors and {warning_count} warnings")
        return 1 if error_count > 0 else 0

    print("No deprecated patterns found.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Detect deprecated patterns in Claude Code extensions"
    )
    parser.add_argument("path", nargs="?", help="Path to check")
    parser.add_argument(
        "--all", action="store_true",
        help="Check all extensions in ~/.claude"
    )
    parser.add_argument(
        "--severity", choices=["error", "warning"],
        help="Only show matches of this severity"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    deprecations = load_deprecations()
    if not deprecations:
        print("No deprecation patterns loaded. Check version-manifest.json.")
        sys.exit(0)

    results = []

    if args.all:
        files = find_extension_files(CLAUDE_DIR)
        for f in files:
            results.append(check_file(f, deprecations))
    elif args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            sys.exit(2)

        if path.is_file():
            results.append(check_file(path, deprecations))
        else:
            files = find_extension_files(path)
            for f in files:
                results.append(check_file(f, deprecations))
    else:
        parser.print_help()
        sys.exit(2)

    if args.json:
        output = []
        for r in results:
            if r.matches:
                output.append({
                    "file": r.file_path,
                    "matches": [
                        {
                            "line": m.line_number,
                            "content": m.line_content,
                            "pattern": m.pattern,
                            "replacement": m.replacement,
                            "severity": m.severity,
                            "since": m.since,
                        }
                        for m in r.matches
                    ]
                })
        print(json.dumps(output, indent=2))
        sys.exit(1 if any(r.has_errors for r in results) else 0)
    else:
        sys.exit(print_results(results, args.severity))


if __name__ == "__main__":
    main()
