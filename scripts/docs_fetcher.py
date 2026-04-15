#!/usr/bin/env python3
"""
Fetch and parse official Claude Code documentation.

Syncs canonical documentation sources and extracts schema definitions.

Usage:
    python docs_fetcher.py sync              # Fetch all docs and update schemas
    python docs_fetcher.py check             # Check if sync is needed
    python docs_fetcher.py show <source_id>  # Show cached content for source

Exit codes:
    0 - Success
    1 - Error during fetch
    2 - Usage error
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
TOOLKIT_ROOT = SCRIPT_DIR.parent
DATA_DIR = TOOLKIT_ROOT / "data"
REFERENCES_DIR = TOOLKIT_ROOT / "references"

MANIFEST_PATH = DATA_DIR / "version-manifest.json"
SOURCES_PATH = DATA_DIR / "canonical-sources.json"
CACHE_DIR = DATA_DIR / "cache"


def load_manifest() -> dict:
    """Load version manifest."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {}


def save_manifest(manifest: dict):
    """Save version manifest."""
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def load_sources() -> dict:
    """Load canonical sources config."""
    if SOURCES_PATH.exists():
        with open(SOURCES_PATH) as f:
            return json.load(f)
    return {"sources": [], "sync_config": {"max_age_days": 7}}


def needs_sync(manifest: dict, sources: dict) -> bool:
    """Check if sync is needed based on age."""
    last_sync = manifest.get("last_docs_sync")
    if not last_sync:
        return True

    try:
        last_sync_dt = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
        max_age = sources.get("sync_config", {}).get("max_age_days", 7)
        return datetime.now(last_sync_dt.tzinfo) - last_sync_dt > timedelta(days=max_age)
    except (ValueError, TypeError):
        return True


def fetch_url(url: str, timeout: int = 30) -> Optional[str]:
    """Fetch content from URL."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "claude-extension-toolkit/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error fetching {url}: {e}", file=sys.stderr)
        return None


def cache_content(source_id: str, content: str):
    """Cache fetched content."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{source_id}.txt"
    cache_file.write_text(content)

    # Also save metadata
    meta_file = CACHE_DIR / f"{source_id}.meta.json"
    meta_file.write_text(json.dumps({
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "size": len(content)
    }))


def get_cached(source_id: str) -> Optional[str]:
    """Get cached content."""
    cache_file = CACHE_DIR / f"{source_id}.txt"
    if cache_file.exists():
        return cache_file.read_text()
    return None


def extract_schemas_from_docs(cached_docs: dict) -> dict:
    """Extract schema information from cached docs."""
    schemas = {}

    # This is a placeholder - actual extraction would parse the markdown
    # and extract structured information about frontmatter fields, etc.
    # For now, we rely on the manually-maintained version-manifest.json

    return schemas


def sync_docs(sources: dict) -> bool:
    """Sync all documentation sources."""
    success = True
    timeout = sources.get("sync_config", {}).get("timeout_seconds", 30)

    for source in sources.get("sources", []):
        source_id = source["id"]
        url = source["url"]

        print(f"Fetching {source_id}...")
        content = fetch_url(url, timeout=timeout)

        if content:
            cache_content(source_id, content)
            print(f"  Cached {len(content)} bytes")
        else:
            print(f"  Failed to fetch {source_id}")
            success = False

    return success


def update_schema_definitions():
    """Update the schema-definitions.md reference file."""
    manifest = load_manifest()

    content = """# Schema Definitions

Auto-generated from version manifest. Last updated: {timestamp}

## Skill Frontmatter

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | Yes | string | Skill identifier |
| description | Yes | string | Third-person trigger description |
| allowed-tools | No | list | Tool restrictions |
| model | No | enum | sonnet, opus, haiku |
| context | No | string | Additional context file |
| agent | No | string | Execute as subagent |
| hooks | No | object | Skill-scoped hooks |
| argument-hint | No | string | Argument prompt |
| disable-model-invocation | No | bool | Require explicit invocation |
| user-invocable | No | bool | Allow /skill-name |

## Agent Frontmatter

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | Yes | string | Agent identifier (used with Task tool) |
| description | Yes | string | When to use, with <example> blocks |
| tools | No | list | Allowed tools (default: all) |
| disallowedTools | No | list | Explicitly denied tools |
| model | No | enum | sonnet, opus, haiku |
| color | No | enum | blue, cyan, green, yellow, magenta, red |
| hooks | No | object | Agent-scoped hooks |
| permissionMode | No | enum | Permission handling mode |
| skills | No | list | Preloaded skills |

## Hook Events

| Event | When | Can Block | Has Matcher |
|-------|------|-----------|-------------|
{events_table}

## Plugin Manifest (plugin.json)

| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Plugin identifier |
| description | Yes | What the plugin provides |
| version | No | Semantic version |
| author | No | Author object with name/email |
| keywords | No | Discovery tags |
| repository | No | Source repository URL |
| license | No | License identifier |

## Valid Values

- **Models**: sonnet, opus, haiku
- **Colors**: blue, cyan, green, yellow, magenta, red
- **Permission modes**: (see docs for current options)
"""

    # Build events table
    events = manifest.get("schemas", {}).get("hooks", {}).get("events", [])
    events_table = ""
    blocking_events = {"PreToolUse", "PermissionRequest", "Stop", "UserPromptSubmit"}
    matcher_events = {"PreToolUse", "PostToolUse", "PostToolUseFailure"}

    for event in events:
        can_block = "Yes" if event in blocking_events else "No"
        has_matcher = "Yes" if event in matcher_events else "No"
        events_table += f"| {event} | See docs | {can_block} | {has_matcher} |\n"

    content = content.format(
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        events_table=events_table
    )

    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    schema_file = REFERENCES_DIR / "schema-definitions.md"
    schema_file.write_text(content)
    print(f"Updated {schema_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and parse official Claude Code documentation"
    )
    parser.add_argument(
        "command",
        choices=["sync", "check", "show", "update-schemas"],
        help="Command to run"
    )
    parser.add_argument(
        "source_id",
        nargs="?",
        help="Source ID for show command"
    )

    args = parser.parse_args()

    manifest = load_manifest()
    sources = load_sources()

    if args.command == "check":
        if needs_sync(manifest, sources):
            last = manifest.get("last_docs_sync", "never")
            print(f"Sync needed. Last sync: {last}")
            sys.exit(1)
        else:
            print(f"Docs are current. Last sync: {manifest['last_docs_sync']}")
            sys.exit(0)

    elif args.command == "sync":
        print("Syncing documentation sources...")
        if sync_docs(sources):
            manifest["last_docs_sync"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            save_manifest(manifest)
            print("\nSync complete. Updating schema definitions...")
            update_schema_definitions()
            sys.exit(0)
        else:
            print("\nSync completed with errors.")
            sys.exit(1)

    elif args.command == "show":
        if not args.source_id:
            print("Error: source_id required for show command", file=sys.stderr)
            sys.exit(2)

        content = get_cached(args.source_id)
        if content:
            print(content)
        else:
            print(f"No cached content for {args.source_id}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "update-schemas":
        update_schema_definitions()
        sys.exit(0)


if __name__ == "__main__":
    main()
