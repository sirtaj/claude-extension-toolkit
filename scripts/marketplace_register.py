#!/usr/bin/env python3
"""
Detect an ancestor marketplace.json and orchestrate one of three scaffolder flows:
  - Inside umbrella  -> register new plugin entry into the existing marketplace.json
  - Greenfield + --layout standalone -> scaffold plugin with its own marketplace.json
  - Greenfield + --layout umbrella   -> scaffold umbrella dir + first plugin entry

Upward-search detection is pure pathlib (no subprocess). Safe JSON append uses
Python json module (no shell jq). Reserved-name collisions and ../ path violations
are caught before any file is written.

Usage:
    python marketplace_register.py <plugin_name> [--plugin-path PATH] [--layout {standalone,umbrella,auto}]
                                   [--owner NAME] [--owner-email EMAIL]
                                   [--marketplace-name NAME] [--umbrella-path PATH]

Exit codes:
    0 - Success
    1 - Runtime error (reserved name, path violation, duplicate plugin, etc.)
    2 - Usage error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
TOOLKIT_ROOT = SCRIPT_DIR.parent
VERSION_MANIFEST = TOOLKIT_ROOT / "data" / "version-manifest.json"


def load_reserved_names() -> set:
    """Load reserved marketplace names from version-manifest. Empty set on failure."""
    try:
        with open(VERSION_MANIFEST) as f:
            return set(
                json.load(f)["schemas"]["marketplace_manifest"]["reserved_names"]
            )
    except (OSError, KeyError, json.JSONDecodeError):
        return set()


def find_ancestor_marketplace(start: Path) -> Optional[Path]:
    """Walk upward from start, return first dir containing .claude-plugin/marketplace.json."""
    current = start.resolve()
    while True:
        candidate = current / ".claude-plugin" / "marketplace.json"
        if candidate.is_file():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def read_manifest(marketplace_root: Path) -> dict:
    """Read the marketplace.json manifest."""
    with open(marketplace_root / ".claude-plugin" / "marketplace.json") as f:
        return json.load(f)


def write_manifest(marketplace_root: Path, manifest: dict) -> None:
    """Write the marketplace.json manifest, indent=2, trailing newline."""
    path = marketplace_root / ".claude-plugin" / "marketplace.json"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def validate_relative_path(plugin_path: Path, marketplace_root: Path) -> str:
    """Return './<rel>' if plugin_path is inside marketplace_root; else raise ValueError."""
    plug = plugin_path.resolve()
    root = marketplace_root.resolve()
    try:
        rel = plug.relative_to(root)
    except ValueError:
        raise ValueError(
            f"Plugin must be inside marketplace root; got {plug} not under {root}"
        )
    rel_str = rel.as_posix()
    if rel_str in ("", "."):
        return "./"
    return "./" + rel_str


def append_plugin_entry(marketplace_root: Path, entry: dict) -> None:
    """Append a plugin entry; raise ValueError if name already registered."""
    manifest = read_manifest(marketplace_root)
    names = {p.get("name") for p in manifest.get("plugins", [])}
    if entry["name"] in names:
        raise ValueError(f"Plugin '{entry['name']}' already registered")
    manifest.setdefault("plugins", []).append(entry)
    write_manifest(marketplace_root, manifest)


def check_reserved_name(name: str) -> None:
    """Raise ValueError if name collides with Anthropic's reserved names."""
    if name in load_reserved_names():
        raise ValueError(
            f"Marketplace name '{name}' is reserved by Anthropic. Choose a different name."
        )


def scaffold_marketplace_manifest(
    marketplace_root: Path,
    marketplace_name: str,
    owner_name: str,
    owner_email: Optional[str] = None,
    first_entry: Optional[dict] = None,
) -> None:
    """Create .claude-plugin/marketplace.json at marketplace_root."""
    check_reserved_name(marketplace_name)
    manifest = {
        "name": marketplace_name,
        "owner": {"name": owner_name},
        "plugins": [] if first_entry is None else [first_entry],
    }
    if owner_email:
        manifest["owner"]["email"] = owner_email
    (marketplace_root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    write_manifest(marketplace_root, manifest)


def build_plugin_entry(
    plugin_name: str, source: str, plugin_manifest: Optional[dict] = None
) -> dict:
    """Build a minimal plugin entry, optionally pulling description/version from plugin.json."""
    entry = {"name": plugin_name, "source": source}
    if plugin_manifest:
        if "description" in plugin_manifest:
            entry["description"] = plugin_manifest["description"]
        if "version" in plugin_manifest:
            entry["version"] = plugin_manifest["version"]
    return entry


def register_in_existing(
    plugin_name: str, plugin_path: Path, marketplace_root: Path
) -> str:
    """Register an existing plugin directory into an ancestor marketplace.json."""
    source = validate_relative_path(plugin_path, marketplace_root)
    plugin_manifest = None
    plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
    if plugin_json.is_file():
        try:
            with open(plugin_json) as f:
                plugin_manifest = json.load(f)
        except (OSError, json.JSONDecodeError):
            plugin_manifest = None
    entry = build_plugin_entry(plugin_name, source, plugin_manifest)
    append_plugin_entry(marketplace_root, entry)
    return (
        f"Registered '{plugin_name}' into {marketplace_root.name}"
        f"/.claude-plugin/marketplace.json as {source}"
    )


def scaffold_standalone(
    plugin_name: str,
    plugin_path: Path,
    owner_name: str,
    owner_email: Optional[str],
    marketplace_name: Optional[str],
) -> str:
    """Greenfield standalone: plugin root IS marketplace root."""
    mk_name = marketplace_name or plugin_name
    check_reserved_name(mk_name)
    entry = build_plugin_entry(plugin_name, "./")
    plugin_path.mkdir(parents=True, exist_ok=True)
    scaffold_marketplace_manifest(
        plugin_path, mk_name, owner_name, owner_email, first_entry=entry
    )
    return f"Scaffolded standalone marketplace at {plugin_path}/.claude-plugin/marketplace.json"


def scaffold_umbrella(
    plugin_name: str,
    umbrella_path: Path,
    plugin_subdir_path: Path,
    owner_name: str,
    owner_email: Optional[str],
    marketplace_name: str,
) -> str:
    """Greenfield umbrella: umbrella dir + first plugin entry."""
    check_reserved_name(marketplace_name)
    umbrella_path.mkdir(parents=True, exist_ok=True)
    source = validate_relative_path(plugin_subdir_path, umbrella_path)
    entry = build_plugin_entry(plugin_name, source)
    scaffold_marketplace_manifest(
        umbrella_path, marketplace_name, owner_name, owner_email, first_entry=entry
    )
    return (
        f"Scaffolded umbrella marketplace at {umbrella_path}"
        f"/.claude-plugin/marketplace.json with first plugin '{plugin_name}'"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Detect ancestor marketplace.json and orchestrate scaffolder flows."
    )
    parser.add_argument("plugin_name", help="Plugin identifier to register")
    parser.add_argument(
        "--plugin-path", default=".", help="Plugin dir (existing or to-be-created)"
    )
    parser.add_argument(
        "--layout",
        choices=["standalone", "umbrella", "auto"],
        default="auto",
        help="auto uses detection; explicit overrides",
    )
    parser.add_argument(
        "--owner", default="", help="Owner name (required for scaffolding)"
    )
    parser.add_argument("--owner-email", default="", help="Owner email (optional)")
    parser.add_argument(
        "--marketplace-name",
        default="",
        help="Marketplace name; required for umbrella, defaults to plugin name for standalone",
    )
    parser.add_argument(
        "--umbrella-path",
        default="",
        help="Umbrella root path (required for greenfield umbrella)",
    )

    args = parser.parse_args()

    plugin_path = Path(args.plugin_path).resolve()
    layout = args.layout

    search_start = plugin_path if plugin_path.exists() else plugin_path.parent
    detected = find_ancestor_marketplace(search_start)

    try:
        if detected and layout in ("auto", "umbrella"):
            msg = register_in_existing(args.plugin_name, plugin_path, detected)
        elif layout == "auto":
            print(
                "Error: no ancestor marketplace.json found; specify --layout standalone "
                "or --layout umbrella",
                file=sys.stderr,
            )
            sys.exit(2)
        elif layout == "standalone":
            if not args.owner:
                print(
                    "Error: --owner is required for standalone layout", file=sys.stderr
                )
                sys.exit(2)
            msg = scaffold_standalone(
                args.plugin_name,
                plugin_path,
                args.owner,
                args.owner_email or None,
                args.marketplace_name or None,
            )
        elif layout == "umbrella":
            if not args.umbrella_path or not args.owner or not args.marketplace_name:
                print(
                    "Error: --umbrella-path, --owner, and --marketplace-name are required for umbrella layout",
                    file=sys.stderr,
                )
                sys.exit(2)
            umbrella = Path(args.umbrella_path).resolve()
            msg = scaffold_umbrella(
                args.plugin_name,
                umbrella,
                plugin_path,
                args.owner,
                args.owner_email or None,
                args.marketplace_name,
            )
        else:
            print(f"Error: unknown layout {layout}", file=sys.stderr)
            sys.exit(2)
        print(msg)
        sys.exit(0)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
