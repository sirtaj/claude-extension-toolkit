#!/usr/bin/env python3
"""
Manage symlinks between AI source directory and ~/.claude.

Syncs extensions from a source directory (e.g., ~/sirtaj-notes/3-Resources/AI)
to the Claude Code config directory (~/.claude) via symlinks.

Usage:
    python sync_symlinks.py --check              # Check symlink status
    python sync_symlinks.py --sync               # Create missing symlinks
    python sync_symlinks.py --source <path>      # Use custom source directory
    python sync_symlinks.py --dry-run            # Show what would be done

Exit codes:
    0 - All synced / success
    1 - Symlinks need attention
    2 - Usage error
"""

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

# Default paths
DEFAULT_SOURCE = Path.home() / "sirtaj-notes" / "3-Resources" / "AI"
CLAUDE_DIR = Path.home() / ".claude"

# Mapping from source subdirectory to ~/.claude subdirectory
SYMLINK_MAP = {
    "CLAUDE.md": "CLAUDE.md",
    "Agents": "agents",
    "Commands": "commands",
    "Skills": "skills",
}


@dataclass
class SymlinkStatus:
    """Status of a single symlink."""
    source: Path
    target: Path
    status: str  # "ok", "missing", "broken", "wrong_target", "is_file", "is_dir"
    message: str = ""


def check_symlink(source: Path, target: Path) -> SymlinkStatus:
    """Check the status of a symlink."""
    if not source.exists():
        return SymlinkStatus(source, target, "source_missing",
                             f"Source does not exist: {source}")

    if not target.exists() and not target.is_symlink():
        return SymlinkStatus(source, target, "missing",
                             f"Symlink does not exist: {target}")

    if target.is_symlink():
        actual_target = target.resolve()
        expected_target = source.resolve()

        if actual_target == expected_target:
            return SymlinkStatus(source, target, "ok", "Symlink is correct")
        else:
            return SymlinkStatus(source, target, "wrong_target",
                                 f"Symlink points to {actual_target}, expected {expected_target}")

    elif target.is_file():
        return SymlinkStatus(source, target, "is_file",
                             f"Target exists as regular file (not symlink): {target}")
    elif target.is_dir():
        return SymlinkStatus(source, target, "is_dir",
                             f"Target exists as directory (not symlink): {target}")
    else:
        return SymlinkStatus(source, target, "unknown",
                             f"Unknown state for {target}")


def create_symlink(source: Path, target: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Create a symlink from target -> source."""
    if dry_run:
        return True, f"Would create: {target} -> {source}"

    try:
        # Ensure parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing broken symlink
        if target.is_symlink():
            target.unlink()

        # Create symlink
        target.symlink_to(source)
        return True, f"Created: {target} -> {source}"
    except Exception as e:
        return False, f"Failed to create symlink: {e}"


def check_all_symlinks(source_dir: Path) -> List[SymlinkStatus]:
    """Check all expected symlinks."""
    results = []

    for source_name, target_name in SYMLINK_MAP.items():
        source = source_dir / source_name
        target = CLAUDE_DIR / target_name
        results.append(check_symlink(source, target))

    return results


def sync_symlinks(source_dir: Path, dry_run: bool = False) -> List[Tuple[SymlinkStatus, str]]:
    """Sync all symlinks, creating missing ones."""
    results = []

    for source_name, target_name in SYMLINK_MAP.items():
        source = source_dir / source_name
        target = CLAUDE_DIR / target_name

        status = check_symlink(source, target)

        if status.status == "ok":
            results.append((status, "Already synced"))
        elif status.status == "source_missing":
            results.append((status, "Skipped (source missing)"))
        elif status.status in ("missing", "wrong_target"):
            success, message = create_symlink(source, target, dry_run)
            if success:
                status.status = "synced"
                status.message = message
            results.append((status, message))
        elif status.status in ("is_file", "is_dir"):
            results.append((status, "Manual intervention needed - target exists as file/dir"))
        else:
            results.append((status, "Unknown state"))

    return results


def print_status(results: List[SymlinkStatus]) -> int:
    """Print status and return exit code."""
    print("Symlink Status:")
    print("="*60)

    issues = 0
    for status in results:
        icon = {
            "ok": "[OK]",
            "missing": "[MISSING]",
            "broken": "[BROKEN]",
            "wrong_target": "[WRONG]",
            "is_file": "[CONFLICT]",
            "is_dir": "[CONFLICT]",
            "source_missing": "[NO SRC]",
        }.get(status.status, "[?]")

        print(f"{icon:12} {status.target.name}")
        print(f"             Source: {status.source}")
        print(f"             Target: {status.target}")
        if status.message:
            print(f"             {status.message}")
        print()

        if status.status != "ok":
            issues += 1

    print("="*60)
    if issues == 0:
        print("All symlinks are correctly configured.")
    else:
        print(f"{issues} symlinks need attention.")
        print("Run with --sync to fix missing/broken symlinks.")

    return 1 if issues > 0 else 0


def print_sync_results(results: List[Tuple[SymlinkStatus, str]]) -> int:
    """Print sync results and return exit code."""
    print("Sync Results:")
    print("="*60)

    errors = 0
    for status, message in results:
        icon = {
            "ok": "[OK]",
            "synced": "[SYNCED]",
            "missing": "[CREATED]",
            "source_missing": "[SKIP]",
            "is_file": "[ERROR]",
            "is_dir": "[ERROR]",
        }.get(status.status, "[?]")

        print(f"{icon:12} {status.target.name}")
        print(f"             {message}")
        print()

        if status.status in ("is_file", "is_dir"):
            errors += 1

    print("="*60)
    if errors > 0:
        print(f"{errors} items need manual intervention.")
        return 1
    else:
        print("Sync complete.")
        return 0


def discover_additional_extensions(source_dir: Path) -> List[Tuple[Path, Path]]:
    """Discover extensions beyond the standard map."""
    additional = []

    # Check for additional skill directories
    skills_dir = source_dir / "Skills"
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                target = CLAUDE_DIR / "skills" / item.name
                if not target.exists():
                    additional.append((item, target))

    return additional


def main():
    parser = argparse.ArgumentParser(description="Manage Claude Code symlinks")
    parser.add_argument("--check", action="store_true", help="Check symlink status")
    parser.add_argument("--sync", action="store_true", help="Create missing symlinks")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                        help=f"Source directory (default: {DEFAULT_SOURCE})")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--discover", action="store_true",
                        help="Discover additional extensions not in standard map")

    args = parser.parse_args()

    source_dir = args.source

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}", file=sys.stderr)
        print("Use --source to specify a different source directory.")
        sys.exit(2)

    if args.discover:
        additional = discover_additional_extensions(source_dir)
        if additional:
            print("Additional extensions found:")
            for src, tgt in additional:
                print(f"  {src.name}: {src} -> {tgt}")
        else:
            print("No additional extensions found.")
        sys.exit(0)

    if args.sync:
        if args.dry_run:
            print("DRY RUN - no changes will be made\n")
        results = sync_symlinks(source_dir, args.dry_run)
        sys.exit(print_sync_results(results))
    elif args.check or (not args.sync):
        results = check_all_symlinks(source_dir)
        sys.exit(print_status(results))
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
