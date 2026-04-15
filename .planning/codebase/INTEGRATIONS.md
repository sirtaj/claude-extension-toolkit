# External Integrations

**Analysis Date:** 2026-04-16

## APIs & External Services

**Claude Code documentation sites (read-only HTTPS fetch via `urllib.request`):**

Configured in `data/canonical-sources.json`, fetched by `scripts/docs_fetcher.py sync`:

- `https://code.claude.com/docs/en/skills` — skill frontmatter schema
- `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` — skill best practices
- `https://code.claude.com/docs/en/sub-agents` — agent frontmatter
- `https://code.claude.com/docs/en/hooks` — hook events & schemas
- `https://code.claude.com/docs/en/hooks-guide` — hook patterns
- `https://code.claude.com/docs/en/plugins` — plugin structure
- `https://code.claude.com/docs/en/plugins-reference` — plugin technical specs
- `https://code.claude.com/docs/en/plugin-marketplaces` — marketplace schema
- `https://code.claude.com/docs/en/agent-teams` — multi-agent coordination
- `https://code.claude.com/docs/en/scheduled-tasks` — cron task specs
- `https://code.claude.com/docs/llms.txt` — doc index

**Community sources (reference only):**
- `https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably`
- `https://claude-plugins.dev`

**Sync policy:** `max_age_days: 7`, `timeout_seconds: 30`, `retry_count: 3`. No authentication required — all sources are public HTTPS GET.

## Claude Code Host Integration

The toolkit integrates with the Claude Code host via several documented extension surfaces (all produced by this plugin, not consumed):

- **Skills** — `skills/*/SKILL.md` auto-loaded by Claude Code when matched by description triggers
- **Hooks** — `scripts/quick_update_check.sh` designed for `SessionStart` hook (reads JSON via stdin, emits status message on stdout)
- **Plugin marketplace** — consumed by Claude Code via parent `/home/sirtaj/proj/claude-stuff/.claude-plugin/marketplace.json`

## Data Storage

**Databases:** None.

**File storage (local only):**
- `data/cache/*.txt` — fetched documentation bodies (8 pages)
- `data/cache/*.meta.json` — per-source fetch metadata (timestamp, URL)
- `data/version-manifest.json` — mutated by `scripts/docs_fetcher.py` (updates `last_docs_sync`)

**Caching:** Local filesystem cache in `data/cache/`; invalidation by `max_age_days` in `canonical-sources.json`.

## Authentication & Identity

None. All network fetches are unauthenticated public HTTPS. No user identity, tokens, or secrets handled anywhere in the codebase.

## Monitoring & Observability

**Error Tracking:** None.

**Logs:** Stdout/stderr only. Scripts use exit codes (0 = success, 1 = errors, 2 = usage). `quick_update_check.sh` emits bracketed status lines (`[extension-toolkit] ...`).

## CI/CD & Deployment

**Hosting:** None (distributed as plugin directory).

**CI Pipeline:** None detected. No `.github/workflows/`, no CI config.

**Distribution:** Consumed as a git submodule under `/home/sirtaj/proj/claude-stuff/` (parent marketplace repo). `.git` is a gitlink.

## Environment Configuration

**Required env vars:** None.

**Secrets location:** Not applicable — no secrets used.

## External CLI Tools

Invoked at runtime (not bundled):

- `jq` — `scripts/quick_update_check.sh` parses `version-manifest.json` and hook stdin
- `find`, `grep` — `scripts/quick_update_check.sh` scans `~/.claude` for deprecated patterns in recently-modified shell scripts (last 24h)
- `python3` — used by `quick_update_check.sh` to compute sync-age in days

## Filesystem Touchpoints Outside Repo

- `~/.claude/` — read by `scripts/validate_extension.py` (`CLAUDE_DIR = Path.home() / ".claude"`), `scripts/extension_report.py`, and `scripts/quick_update_check.sh` (scans for `*.sh` modified in last 24h)

## Webhooks & Callbacks

None.

---

*Integration audit: 2026-04-16*
