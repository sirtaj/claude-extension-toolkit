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
        return datetime.now(last_sync_dt.tzinfo) - last_sync_dt > timedelta(
            days=max_age
        )
    except (ValueError, TypeError):
        return True


def markdown_url(url: str) -> str:
    """Return the plain-markdown variant of a docs URL.

    The Claude Code docs site serves clean markdown for any page when the path
    ends in `.md`. Fetching the HTML page instead yields megabytes of app shell
    that is useless for schema extraction.
    """
    if url.endswith((".md", ".txt", ".json")):
        return url
    return url + ".md"


def fetch_url(url: str, timeout: int = 30) -> Optional[str]:
    """Fetch content from URL."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "claude-extension-toolkit/1.0"}
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
    meta_file.write_text(
        json.dumps(
            {
                "fetched_at": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "size": len(content),
            }
        )
    )


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
        url = markdown_url(source["url"])

        print(f"Fetching {source_id}...")
        content = fetch_url(url, timeout=timeout)

        if content:
            cache_content(source_id, content)
            print(f"  Cached {len(content)} bytes")
        else:
            print(f"  Failed to fetch {source_id}")
            success = False

    return success


def _field_table(schema: dict) -> str:
    """Render a required/recommended/optional field list as a markdown table."""
    rows = []
    for requiredness, key in (
        ("Yes", "required"),
        ("Recommended", "recommended"),
        ("No", "optional"),
    ):
        for field in schema.get(key, []):
            # A field can appear in both `recommended` and `optional`; keep the
            # stronger signal only.
            if any(field == existing for existing, _ in rows):
                continue
            rows.append((field, requiredness))

    if not rows:
        return "_No fields recorded in the version manifest._\n"

    table = "| Field | Required |\n|-------|----------|\n"
    for field, requiredness in rows:
        table += f"| `{field}` | {requiredness} |\n"
    return table


def _events_table(events) -> str:
    """Render the hook event table."""
    table = "| Event | Can Block | Has Matcher |\n|-------|-----------|-------------|\n"
    if isinstance(events, dict):
        for event, details in events.items():
            if isinstance(details, dict):
                can_block = "Yes" if details.get("can_block") else "No"
                has_matcher = "Yes" if details.get("has_matcher") else "No"
            else:
                can_block = has_matcher = "See docs"
            table += f"| `{event}` | {can_block} | {has_matcher} |\n"
    elif isinstance(events, list):
        for event in events:
            table += f"| `{event}` | See docs | See docs |\n"
    return table


def _value_list(values) -> str:
    """Render a list of literal values as inline code, comma separated."""
    if not values:
        return "see docs"
    return ", ".join(f"`{v}`" for v in values)


def update_schema_definitions():
    """Regenerate references/schema-definitions.md from the version manifest.

    Every table here is derived from data/version-manifest.json so the reference
    can never drift from the manifest that validate_extension.py checks against.
    """
    manifest = load_manifest()
    schemas = manifest.get("schemas", {})
    hooks = schemas.get("hooks", {})

    sections = [
        "# Schema Definitions",
        "",
        "Auto-generated from `data/version-manifest.json` by "
        "`scripts/docs_fetcher.py update-schemas`. Do not edit by hand.",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
        f"- Claude Code version: {manifest.get('claude_code_version', 'unknown')}",
        f"- Last docs sync: {manifest.get('last_docs_sync', 'never')}",
        "",
        "## Skill Frontmatter",
        "",
        _field_table(schemas.get("skill_frontmatter", {})),
        "## Agent Frontmatter",
        "",
        _field_table(schemas.get("agent_frontmatter", {})),
        "## Command Frontmatter",
        "",
        _field_table(schemas.get("command_frontmatter", {})),
        "## Plugin Manifest (plugin.json)",
        "",
        _field_table(schemas.get("plugin_manifest", {})),
        "## Marketplace Manifest (marketplace.json)",
        "",
        _field_table(schemas.get("marketplace_manifest", {})),
        "## Marketplace Plugin Entry",
        "",
        _field_table(schemas.get("marketplace_plugin_entry", {})),
        "## Hook Events",
        "",
        _events_table(hooks.get("events", {})),
        "## Valid Values",
        "",
        f"- **Model aliases**: {_value_list(schemas.get('model_values', {}).get('short'))}",
        f"- **Model IDs**: {_value_list(schemas.get('model_values', {}).get('full_ids'))}",
        f"- **Model special**: {_value_list(schemas.get('model_values', {}).get('special'))}",
        f"- **Agent colors**: {_value_list(hooks.get('valid_colors'))}",
        f"- **Permission modes**: {_value_list(schemas.get('permission_modes', {}).get('values'))}",
        f"- **Hook handler types**: "
        f"{_value_list(hooks.get('handler_fields', {}).get('type', {}).get('values'))}",
        "",
    ]

    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    schema_file = REFERENCES_DIR / "schema-definitions.md"
    schema_file.write_text("\n".join(sections))
    print(f"Updated {schema_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and parse official Claude Code documentation"
    )
    parser.add_argument(
        "command",
        choices=["sync", "check", "show", "update-schemas"],
        help="Command to run",
    )
    parser.add_argument("source_id", nargs="?", help="Source ID for show command")

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
            manifest["last_docs_sync"] = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
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
