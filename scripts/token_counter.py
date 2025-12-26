#!/usr/bin/env python3
"""
Estimate token usage for Claude Code extensions.

Uses a simple chars/4 approximation as mentioned in the skill-optimizer.
Provides breakdowns by section and identifies optimization opportunities.

Usage:
    python token_counter.py <path>           # Count tokens in file/directory
    python token_counter.py --all            # Count all extensions
    python token_counter.py --type skills    # Count specific type
    python token_counter.py --top 10         # Show top N by token count

Exit codes:
    0 - Success
    1 - Error
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CLAUDE_DIR = Path.home() / ".claude"

# Token estimation: ~4 chars per token (conservative estimate for English text)
CHARS_PER_TOKEN = 4

# Recommended token ranges by extension type
TOKEN_RANGES = {
    "skill": (500, 1500),      # 500-1500 words ≈ 125-375 tokens base
    "agent": (800, 2000),      # 800-2000 words
    "command": (50, 500),      # Commands should be concise
    "plugin": (0, 5000),       # Plugins can be larger (bundled)
    "claude_md": (200, 2000),  # Project instructions
}


@dataclass
class TokenCount:
    """Token count result for an extension."""
    path: str
    extension_type: str
    total_tokens: int
    total_chars: int
    sections: Dict[str, int] = field(default_factory=dict)
    references_tokens: int = 0
    frontmatter_tokens: int = 0
    body_tokens: int = 0
    recommendation: str = ""


def estimate_tokens(text: str) -> int:
    """Estimate token count from text."""
    return len(text) // CHARS_PER_TOKEN


def parse_frontmatter(content: str) -> Tuple[str, str]:
    """Split content into frontmatter and body."""
    if not content.startswith("---"):
        return "", content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", content

    return parts[1], parts[2]


def extract_sections(content: str) -> Dict[str, int]:
    """Extract markdown sections and their token counts."""
    sections = {}
    current_section = "_intro"
    current_text = []

    for line in content.split("\n"):
        if line.startswith("#"):
            # Save previous section
            if current_text:
                text = "\n".join(current_text)
                sections[current_section] = estimate_tokens(text)
            # Start new section
            current_section = line.lstrip("#").strip()
            current_text = []
        else:
            current_text.append(line)

    # Save last section
    if current_text:
        text = "\n".join(current_text)
        sections[current_section] = estimate_tokens(text)

    return sections


def count_skill_tokens(path: Path) -> TokenCount:
    """Count tokens for a skill and its references."""
    result = TokenCount(str(path), "skill", 0, 0)

    try:
        content = path.read_text()
    except Exception as e:
        result.recommendation = f"Cannot read file: {e}"
        return result

    result.total_chars = len(content)

    # Parse frontmatter vs body
    frontmatter, body = parse_frontmatter(content)
    result.frontmatter_tokens = estimate_tokens(frontmatter)
    result.body_tokens = estimate_tokens(body)
    result.sections = extract_sections(body)

    # Check for references
    references_dir = path.parent / "references"
    if references_dir.exists():
        for ref_file in references_dir.glob("*.md"):
            try:
                ref_content = ref_file.read_text()
                ref_tokens = estimate_tokens(ref_content)
                result.references_tokens += ref_tokens
                result.sections[f"ref:{ref_file.name}"] = ref_tokens
            except Exception:
                pass

    result.total_tokens = result.frontmatter_tokens + result.body_tokens + result.references_tokens

    # Generate recommendation
    min_tokens, max_tokens = TOKEN_RANGES["skill"]
    if result.total_tokens < min_tokens:
        result.recommendation = f"Skill may be too sparse ({result.total_tokens} tokens, recommend {min_tokens}-{max_tokens})"
    elif result.total_tokens > max_tokens:
        result.recommendation = f"Consider reducing tokens ({result.total_tokens} > {max_tokens} max)"
    else:
        result.recommendation = "Token count within recommended range"

    return result


def count_agent_tokens(path: Path) -> TokenCount:
    """Count tokens for an agent definition."""
    result = TokenCount(str(path), "agent", 0, 0)

    try:
        content = path.read_text()
    except Exception as e:
        result.recommendation = f"Cannot read file: {e}"
        return result

    result.total_chars = len(content)

    frontmatter, body = parse_frontmatter(content)
    result.frontmatter_tokens = estimate_tokens(frontmatter)
    result.body_tokens = estimate_tokens(body)
    result.sections = extract_sections(body)
    result.total_tokens = result.frontmatter_tokens + result.body_tokens

    min_tokens, max_tokens = TOKEN_RANGES["agent"]
    if result.total_tokens < min_tokens:
        result.recommendation = f"Agent may be too sparse ({result.total_tokens} tokens)"
    elif result.total_tokens > max_tokens:
        result.recommendation = f"Consider reducing tokens ({result.total_tokens} > {max_tokens} max)"
    else:
        result.recommendation = "Token count within recommended range"

    return result


def count_command_tokens(path: Path) -> TokenCount:
    """Count tokens for a command."""
    result = TokenCount(str(path), "command", 0, 0)

    try:
        content = path.read_text()
    except Exception as e:
        result.recommendation = f"Cannot read file: {e}"
        return result

    result.total_chars = len(content)

    frontmatter, body = parse_frontmatter(content)
    result.frontmatter_tokens = estimate_tokens(frontmatter)
    result.body_tokens = estimate_tokens(body)
    result.total_tokens = result.frontmatter_tokens + result.body_tokens

    min_tokens, max_tokens = TOKEN_RANGES["command"]
    if result.total_tokens > max_tokens:
        result.recommendation = f"Command is verbose ({result.total_tokens} tokens), consider simplifying"
    else:
        result.recommendation = "Token count acceptable"

    return result


def count_plugin_tokens(path: Path) -> TokenCount:
    """Count total tokens for a plugin and all its components."""
    result = TokenCount(str(path), "plugin", 0, 0)

    total = 0

    # Count all markdown files in plugin
    for md_file in path.rglob("*.md"):
        try:
            content = md_file.read_text()
            tokens = estimate_tokens(content)
            total += tokens
            rel_path = md_file.relative_to(path)
            result.sections[str(rel_path)] = tokens
        except Exception:
            pass

    # Count JSON files
    for json_file in path.rglob("*.json"):
        try:
            content = json_file.read_text()
            tokens = estimate_tokens(content)
            total += tokens
            rel_path = json_file.relative_to(path)
            result.sections[str(rel_path)] = tokens
        except Exception:
            pass

    result.total_tokens = total
    result.recommendation = f"Plugin total: {total} tokens across {len(result.sections)} files"

    return result


def find_and_count_all(base_dir: Path, ext_type: Optional[str] = None) -> List[TokenCount]:
    """Find and count all extensions."""
    results = []

    if ext_type is None or ext_type == "skills":
        for skill_md in base_dir.rglob("SKILL.md"):
            results.append(count_skill_tokens(skill_md))

    if ext_type is None or ext_type == "agents":
        agents_dir = base_dir / "agents"
        if agents_dir.exists():
            for agent in agents_dir.glob("*.md"):
                results.append(count_agent_tokens(agent))

    if ext_type is None or ext_type == "commands":
        commands_dir = base_dir / "commands"
        if commands_dir.exists():
            for cmd in commands_dir.glob("*.md"):
                results.append(count_command_tokens(cmd))

    if ext_type is None or ext_type == "plugins":
        plugins_dir = base_dir / "plugins"
        if plugins_dir.exists():
            for item in plugins_dir.iterdir():
                if item.is_dir() and (item / ".claude-plugin").exists():
                    results.append(count_plugin_tokens(item))

    return results


def print_results(results: List[TokenCount], top_n: Optional[int] = None, verbose: bool = False):
    """Print token count results."""
    if top_n:
        results = sorted(results, key=lambda r: r.total_tokens, reverse=True)[:top_n]

    total_all = 0

    for result in results:
        print(f"\n{result.extension_type.upper()}: {result.path}")
        print(f"  Total: {result.total_tokens:,} tokens ({result.total_chars:,} chars)")

        if result.frontmatter_tokens:
            print(f"  Frontmatter: {result.frontmatter_tokens:,} tokens")
        if result.body_tokens:
            print(f"  Body: {result.body_tokens:,} tokens")
        if result.references_tokens:
            print(f"  References: {result.references_tokens:,} tokens")

        if verbose and result.sections:
            print("  Sections:")
            for section, tokens in sorted(result.sections.items(), key=lambda x: -x[1]):
                print(f"    {section}: {tokens:,} tokens")

        if result.recommendation:
            print(f"  -> {result.recommendation}")

        total_all += result.total_tokens

    print(f"\n{'='*50}")
    print(f"Total: {len(results)} extensions, {total_all:,} tokens")


def main():
    parser = argparse.ArgumentParser(description="Count tokens in Claude Code extensions")
    parser.add_argument("path", nargs="?", help="Path to count")
    parser.add_argument("--all", action="store_true", help="Count all extensions in ~/.claude")
    parser.add_argument("--type", choices=["skills", "agents", "commands", "plugins"],
                        help="Count only specific extension type")
    parser.add_argument("--top", type=int, help="Show top N by token count")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show section breakdown")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    results = []

    if args.all:
        results = find_and_count_all(CLAUDE_DIR, args.type)
    elif args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            sys.exit(1)

        if path.is_file():
            if path.name == "SKILL.md":
                results = [count_skill_tokens(path)]
            elif path.suffix == ".md":
                parent = path.parent.name
                if parent == "agents" or "agents" in str(path):
                    results = [count_agent_tokens(path)]
                elif parent == "commands" or "commands" in str(path):
                    results = [count_command_tokens(path)]
                else:
                    results = [count_skill_tokens(path)]
        else:
            results = find_and_count_all(path, args.type)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        output = [
            {
                "path": r.path,
                "type": r.extension_type,
                "total_tokens": r.total_tokens,
                "total_chars": r.total_chars,
                "frontmatter_tokens": r.frontmatter_tokens,
                "body_tokens": r.body_tokens,
                "references_tokens": r.references_tokens,
                "sections": r.sections,
                "recommendation": r.recommendation,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
    else:
        print_results(results, args.top, args.verbose)


if __name__ == "__main__":
    main()
