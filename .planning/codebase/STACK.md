# Technology Stack

**Analysis Date:** 2026-04-16

## Languages

**Primary:**
- Python 3 — all utility scripts under `scripts/` (shebang `#!/usr/bin/env python3`, stdlib only)
- Markdown — all skill/reference content (SKILL.md, references/*.md)
- JSON — plugin manifest, version manifest, canonical sources, doc cache metadata

**Secondary:**
- Bash — `scripts/quick_update_check.sh` (SessionStart-hook helper); uses `set -euo pipefail`, `jq`, `find`, `grep`

## Runtime

**Environment:**
- Claude Code v2.1.77 (target runtime; recorded in `data/version-manifest.json` `claude_code_version`)
- Python 3 (system interpreter via `/usr/bin/env python3`) — no virtualenv, no `pyproject.toml`, no `requirements.txt`
- Bash (POSIX shell with `jq`)

**Package Manager:**
- None. Scripts depend only on Python 3 standard library. No `package.json`, `pyproject.toml`, `requirements.txt`, or lockfile present.

## Frameworks

**Core:**
- Not applicable. This is a Claude Code plugin (content + scripts), not a compiled/served application.

**Testing:**
- None detected. No `pytest`, `unittest`, or test files present.

**Build/Dev:**
- None. Scripts are directly executable; plugin is consumed by Claude Code at load time.

## Key Dependencies

**Critical (Python stdlib only):**
- `argparse`, `json`, `pathlib`, `dataclasses`, `typing` — used across all scripts
- `urllib.request`, `urllib.error`, `urllib.parse` — `scripts/docs_fetcher.py`, `scripts/lint_references.py` (fetch canonical docs, validate links)
- `re` — `scripts/pattern_detector.py`, `scripts/token_counter.py`, `scripts/lint_references.py`
- `datetime` — `scripts/docs_fetcher.py`, `scripts/extension_report.py` (sync-age tracking)

**External CLI tools (runtime-assumed):**
- `jq` — required by `scripts/quick_update_check.sh` for JSON parsing of manifest and hook stdin
- `find`, `grep` — used by `scripts/quick_update_check.sh`

**No third-party Python packages.** Deliberate zero-dependency design.

## Configuration

**Plugin manifest:**
- `.claude-plugin/plugin.json` — name, version (3.0.0), author, keywords

**Runtime data (not user config):**
- `data/version-manifest.json` — schema versions, deprecations, valid model/color values, last-sync timestamp
- `data/canonical-sources.json` — documentation URLs, sync settings (`max_age_days: 7`, `timeout_seconds: 30`, `retry_count: 3`)
- `data/cache/*.txt` + `data/cache/*.meta.json` — fetched doc cache (8 source pages)

**Environment:**
- No `.env` files. No secrets. Scripts read only local JSON manifests and optionally fetch over HTTPS.

## Platform Requirements

**Development:**
- Python 3 on PATH
- `jq`, `find`, `grep`, `bash` for hook helper script
- Git (repo is a submodule; `.git` is a gitlink file)

**Production (plugin consumption):**
- Claude Code >= 2.1.77 (per version manifest)
- Plugin installed via local marketplace at `/home/sirtaj/proj/claude-stuff/.claude-plugin/marketplace.json`

---

*Stack analysis: 2026-04-16*
