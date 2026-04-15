---
phase: 01-marketplace-support
plan: 05
type: execute
wave: 3
depends_on: [02, 03, 04]
files_modified:
  - skills/extension-starter/SKILL.md
  - skills/extension-builder/SKILL.md
  - skills/extension-optimizer/SKILL.md
autonomous: true
requirements: []
must_haves:
  truths:
    - "extension-starter surfaces the layout choice (standalone vs umbrella) in its decision flow with a primer pointer"
    - "extension-starter does NOT perform detection or scaffolding (clean separation of concerns)"
    - "extension-builder instructs Claude to run marketplace_register.py for three-flow orchestration"
    - "extension-builder documents the upward-search detection behavior and the default (standalone auto-creates marketplace.json)"
    - "extension-optimizer audit instructs running marketplace_manager.py validate and interpreting tiered severity"
    - "All three skills link to references/marketplace-schema.md and references/marketplaces.md"
  artifacts:
    - path: "skills/extension-starter/SKILL.md"
      provides: "Layout-choice framing at entry point"
      contains: "Marketplace layout section with standalone vs umbrella decision, link to schema reference"
    - path: "skills/extension-builder/SKILL.md"
      provides: "Marketplace-aware scaffolding workflow"
      contains: "Three flows table, marketplace_register.py invocation, plugin_scaffolder.py --marketplace flag"
    - path: "skills/extension-optimizer/SKILL.md"
      provides: "Marketplace validation in audit checklist"
      contains: "marketplace_manager.py validate invocation, tier-aware interpretation (errors block, warnings guide)"
  key_links:
    - from: "skills/extension-builder/SKILL.md"
      to: "scripts/marketplace_register.py"
      via: "skill instructs Claude to run this script"
      pattern: "marketplace_register.py"
    - from: "skills/extension-optimizer/SKILL.md"
      to: "scripts/marketplace_manager.py"
      via: "skill instructs Claude to run validate subcommand"
      pattern: "marketplace_manager.py validate"
    - from: "skills/extension-starter/SKILL.md"
      to: "references/marketplace-schema.md"
      via: "markdown link for primer"
      pattern: "marketplace-schema"
---

<objective>
Surface the new marketplace tooling through the three user-facing skills. Preserve clean separation:
- `extension-starter` = decision framing (layout choice up front, primer link)
- `extension-builder` = execution (detection + three flows + scaffolder)
- `extension-optimizer` = validation (tier-aware audit)

This is the final wave. It integrates the knowledgebase (Plan 02), scaffolder (Plan 03), and validator (Plan 04) into the user-invoked skill surface.

Purpose: Without skill integration, the new scripts and docs exist but Claude won't discover/use them when users ask for help. This plan wires the surfaces.

Output: Updated SKILL.md for starter, builder, and optimizer skills.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/phases/01-marketplace-support/01-CONTEXT.md
@.planning/phases/01-marketplace-support/01-02-SUMMARY.md
@.planning/phases/01-marketplace-support/01-03-SUMMARY.md
@.planning/phases/01-marketplace-support/01-04-SUMMARY.md
@skills/extension-starter/SKILL.md
@skills/extension-builder/SKILL.md
@skills/extension-optimizer/SKILL.md
@references/marketplace-schema.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add layout-choice framing to extension-starter SKILL.md</name>
  <files>skills/extension-starter/SKILL.md</files>
  <read_first>
    - skills/extension-starter/SKILL.md (entire current file, 123 lines — understand decision-flow structure)
    - references/marketplace-schema.md (just created in Plan 02)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (extension-starter integration section — "surfaces the layout choice as part of its existing quick-start decision flow, plus a short primer pointing at the new marketplace reference"; "does NOT perform detection or scaffolding")
  </read_first>
  <action>
    Edit `skills/extension-starter/SKILL.md`. Add a new section titled `## Choose a marketplace layout` placed within the existing quick-start decision flow (after the user has decided to build a plugin; before handing off to extension-builder).

    Use this exact content (preserve headings, tables, and phrasing):

    ```markdown
    ## Choose a marketplace layout

    Plugins are consumed via Claude Code's marketplace layer. Before scaffolding, pick one of two layouts:

    | Layout | Best when | Structure |
    |--------|-----------|-----------|
    | **Standalone (flat)** | Shipping one plugin; fastest path to installable | Plugin directory contains its own `.claude-plugin/marketplace.json` |
    | **Umbrella (aggregating)** | Shipping multiple related plugins under one owner | Parent directory holds `.claude-plugin/marketplace.json` aggregating N plugin subdirs |

    **Default recommendation:** standalone. The toolkit auto-creates marketplace.json at the plugin root, so the new plugin is installable immediately with `/plugin marketplace add <plugin-dir>`.

    **Pick umbrella when:** you already maintain ≥2 plugins with shared ownership and discovery, or you're adding a new plugin to an existing umbrella (in which case detection handles it automatically — see below).

    The one invariant: `marketplace.json` lives at exactly one level per tree — never both at the plugin root and an ancestor umbrella root.

    Full schema, source types, reserved names: [`references/marketplace-schema.md`](../../references/marketplace-schema.md)
    CLI, auth, caching: [`references/marketplaces.md`](../../references/marketplaces.md)

    This skill captures your layout choice and hands off to `extension-builder` for actual scaffolding. Detection (upward-search for an ancestor marketplace.json) and file writes happen there, not here.
    ```

    Placement: insert after the existing plugin-related decision content, before any "next step" / "go to extension-builder" hand-off text. If unclear where, insert near the end as a penultimate section before the final hand-off summary.

    Do NOT add detection logic. Do NOT add commands that invoke marketplace_register.py. Starter is framing only.
  </action>
  <verify>
    <automated>
      grep -q "^## Choose a marketplace layout" skills/extension-starter/SKILL.md &&
      grep -q "Standalone (flat)" skills/extension-starter/SKILL.md &&
      grep -q "Umbrella (aggregating)" skills/extension-starter/SKILL.md &&
      grep -q "exactly one level" skills/extension-starter/SKILL.md &&
      grep -q "references/marketplace-schema.md" skills/extension-starter/SKILL.md &&
      grep -q "extension-builder" skills/extension-starter/SKILL.md &&
      ! grep -q "marketplace_register.py" skills/extension-starter/SKILL.md &&
      ! grep -q "find_ancestor_marketplace" skills/extension-starter/SKILL.md
    </automated>
  </verify>
  <acceptance_criteria>
    - Section `## Choose a marketplace layout` added to starter SKILL.md.
    - Contains comparison table with standalone and umbrella rows.
    - States "exactly one level" invariant.
    - Links to `references/marketplace-schema.md` and `references/marketplaces.md`.
    - References handoff to `extension-builder`.
    - Does NOT reference `marketplace_register.py` or detection logic (separation preserved).
  </acceptance_criteria>
  <done>Starter surfaces the choice; separation from builder preserved.</done>
</task>

<task type="auto">
  <name>Task 2: Add marketplace-aware scaffolding workflow to extension-builder SKILL.md</name>
  <files>skills/extension-builder/SKILL.md</files>
  <read_first>
    - skills/extension-builder/SKILL.md (entire current file, 250 lines — find the plugin-creation section)
    - scripts/marketplace_register.py (created in Plan 03 — CLI surface)
    - scripts/plugin_scaffolder.py (extended in Plan 03 — new --marketplace flag)
    - .planning/phases/01-marketplace-support/01-03-SUMMARY.md (CLI surface of both scripts)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (Scaffolder behavior section)
  </read_first>
  <action>
    Edit `skills/extension-builder/SKILL.md`. Add a new top-level section titled `## Marketplace-aware plugin scaffolding` placed within or after the existing plugin-creation workflow content.

    Use this exact content (preserve code blocks, tables, and command syntax verbatim):

    ```markdown
    ## Marketplace-aware plugin scaffolding

    When creating a plugin, choose the right flow based on where the user is invoking from. Run `scripts/marketplace_register.py` for three-flow orchestration; it handles detection and writes marketplace.json correctly for each case.

    ### Detection: is the user inside an existing umbrella?

    `marketplace_register.py` walks upward from `--plugin-path` looking for an ancestor `.claude-plugin/marketplace.json`. If found, it uses the register-into-existing flow automatically.

    ### Three flows

    | Detected state | User choice | Action |
    |----------------|-------------|--------|
    | Ancestor marketplace found | n/a | Register new plugin entry into the existing marketplace.json (safe JSON append, idempotent) |
    | Greenfield | standalone (default) | Scaffold plugin with its own `.claude-plugin/marketplace.json` at the plugin root; immediately installable |
    | Greenfield | umbrella | Scaffold umbrella dir + first plugin entry |

    ### Invocation

    **Standalone (default, greenfield):**
    ```bash
    # Create the plugin skeleton (auto-creates marketplace.json at plugin root)
    python3 scripts/plugin_scaffolder.py my-plugin \
        --output ./ \
        --author "Author Name" \
        --email "author@example.com"

    # Result: ./my-plugin/.claude-plugin/{plugin.json,marketplace.json}
    # Install with: /plugin marketplace add ./my-plugin
    ```

    **Umbrella (greenfield, scaffolding a new umbrella and first plugin):**
    ```bash
    # First create the plugin dir with no marketplace.json
    python3 scripts/plugin_scaffolder.py my-plugin --output ./my-umbrella --marketplace none

    # Then register it into a new umbrella marketplace.json
    python3 scripts/marketplace_register.py my-plugin \
        --plugin-path ./my-umbrella/my-plugin \
        --layout umbrella \
        --owner "Owner Name" \
        --marketplace-name my-umbrella \
        --umbrella-path ./my-umbrella
    ```

    **Register into existing umbrella (detection):**
    ```bash
    # CWD is inside an existing umbrella; scaffolder skips marketplace.json creation
    python3 scripts/plugin_scaffolder.py new-plugin --output . --marketplace none

    # Register into the ancestor marketplace (upward-search finds it automatically)
    python3 scripts/marketplace_register.py new-plugin \
        --plugin-path ./new-plugin \
        --layout auto \
        --owner "Owner Name"
    ```

    ### Safety guarantees

    - Reserved marketplace names (per `data/version-manifest.json` `schemas.marketplace_manifest.reserved_names`) are rejected before any file is written.
    - Plugin paths containing `../` or outside the marketplace root are rejected with a clear error.
    - Duplicate plugin names within a marketplace raise `Plugin '<name>' already registered`.
    - The one-level invariant is preserved: standalone writes marketplace.json at plugin root; register-into-existing writes nothing new at plugin root.

    ### References

    - Schema: [`references/marketplace-schema.md`](../../references/marketplace-schema.md)
    - CLI / auth / caching: [`references/marketplaces.md`](../../references/marketplaces.md)
    - Validator: `scripts/marketplace_manager.py validate <marketplace-root>` (see `extension-optimizer` skill)
    ```

    Placement: near or after the existing "creating a plugin" section. If the skill has an existing "Marketplace" mention, replace/consolidate — don't duplicate.

    Do NOT remove existing content. Do NOT change frontmatter.
  </action>
  <verify>
    <automated>
      grep -q "^## Marketplace-aware plugin scaffolding" skills/extension-builder/SKILL.md &&
      grep -q "marketplace_register.py" skills/extension-builder/SKILL.md &&
      grep -q "plugin_scaffolder.py" skills/extension-builder/SKILL.md &&
      grep -q "\-\-layout auto" skills/extension-builder/SKILL.md &&
      grep -q "\-\-layout umbrella" skills/extension-builder/SKILL.md &&
      grep -q "\-\-marketplace none" skills/extension-builder/SKILL.md &&
      grep -q "one-level invariant" skills/extension-builder/SKILL.md &&
      grep -q "/plugin marketplace add ./my-plugin" skills/extension-builder/SKILL.md
    </automated>
  </verify>
  <acceptance_criteria>
    - Section `## Marketplace-aware plugin scaffolding` present.
    - Documents all three flows in a table: ancestor-found, greenfield+standalone, greenfield+umbrella.
    - Includes working bash invocations for each flow.
    - References `marketplace_register.py`, `plugin_scaffolder.py --marketplace none`, `--layout auto/standalone/umbrella`.
    - States the one-level invariant.
    - Links to `references/marketplace-schema.md`, `references/marketplaces.md`, and cross-references `extension-optimizer` for validation.
  </acceptance_criteria>
  <done>Builder skill documents the three flows with copy-paste-ready commands.</done>
</task>

<task type="auto">
  <name>Task 3: Add tier-aware marketplace audit to extension-optimizer SKILL.md</name>
  <files>skills/extension-optimizer/SKILL.md</files>
  <read_first>
    - skills/extension-optimizer/SKILL.md (entire current file, 181 lines — find the audit/validation section)
    - skills/extension-optimizer/references/checklist.md (existing audit checklist — may need a marketplace addition)
    - scripts/marketplace_manager.py (extended in Plan 04 — new (errors, warnings) contract and --json output shape)
    - .planning/phases/01-marketplace-support/01-04-SUMMARY.md (tier table)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (Validator severity section)
  </read_first>
  <action>
    Edit `skills/extension-optimizer/SKILL.md`. Add a new section titled `## Marketplace audit` in the validation/audit portion of the skill.

    Use this exact content:

    ```markdown
    ## Marketplace audit

    When auditing a plugin or marketplace directory, validate its `marketplace.json` using the tiered-severity checker.

    ### Run

    ```bash
    python3 scripts/marketplace_manager.py validate <marketplace-root> --json
    ```

    Output shape:
    ```json
    {
      "valid": true,
      "errors": [],
      "warnings": ["Plugin 'x' missing optional field 'homepage'", "..."]
    }
    ```

    ### Severity tiers

    | Tier | Examples | Exit | Action |
    |------|----------|------|--------|
    | **Error** (exit 1) | Malformed JSON; missing required top-level fields; missing plugin-entry `name`/`source`; reserved name collision; unknown source type; `author` not `{name, email}` object; `metadata` not an object wrapper; source path outside marketplace root | blocks | Fix before shipping — plugin won't install |
    | **Warning** (exit 0) | Missing optional `homepage`/`repository`/`license`/`keywords`/`description`; legacy `path` field; unknown metadata keys; duplicate plugin names within marketplace; schema drift | guides | Address when polishing; not install-blocking |

    ### Interpreting output

    - `valid: true` with warnings: plugin installs; warnings are polish tasks (metadata completeness, duplicate-name hygiene).
    - `valid: false`: do not ship. Each error maps to a concrete fix — see `references/marketplace-schema.md` for the correct shape.
    - Reserved name errors: pick a different marketplace name. The authoritative reserved list is in `data/version-manifest.json` `schemas.marketplace_manifest.reserved_names`.
    - `author` shape errors: convert string authors to object `{name, email?}`.
    - `metadata` shape errors: wrap flat top-level `description`/`version`/`pluginRoot` into `metadata: {...}`.

    ### Built-in validator (complementary)

    Run Claude Code's built-in validator as well for syntax-level checks:
    ```bash
    claude plugin validate <marketplace-root>
    ```

    The toolkit's `marketplace_manager.py` handles semantic checks the built-in doesn't (reserved names, path-exists, author/metadata shape).

    Reference: [`references/marketplace-schema.md`](../../references/marketplace-schema.md)
    ```

    Placement: after or within the existing audit/checklist section. If the skill has an existing marketplace mention, replace/consolidate.

    Additionally, if `skills/extension-optimizer/references/checklist.md` exists, append a short marketplace entry to its checklist (one line each):
    - Run `scripts/marketplace_manager.py validate <root> --json`; no errors in output
    - All plugin entries have `description`, `homepage`, `license`, `keywords` (warnings clean)
    - Marketplace name not in reserved list
    - `author` field (if present) is an object `{name, email?}`, not a string

    Only append to checklist.md if it exists; if not, skip that sub-step (don't create the file here).
  </action>
  <verify>
    <automated>
      grep -q "^## Marketplace audit" skills/extension-optimizer/SKILL.md &&
      grep -q "marketplace_manager.py validate" skills/extension-optimizer/SKILL.md &&
      grep -q "Severity tiers" skills/extension-optimizer/SKILL.md &&
      grep -q "reserved name collision" skills/extension-optimizer/SKILL.md &&
      grep -q "references/marketplace-schema.md" skills/extension-optimizer/SKILL.md &&
      grep -q "claude plugin validate" skills/extension-optimizer/SKILL.md
    </automated>
  </verify>
  <acceptance_criteria>
    - Section `## Marketplace audit` added to optimizer SKILL.md.
    - Documents the validate CLI invocation with `--json`.
    - Documents the severity tier table (error vs warning, exit codes).
    - References `references/marketplace-schema.md` for canonical shape.
    - Complementary reference to built-in `claude plugin validate`.
    - If `skills/extension-optimizer/references/checklist.md` exists, it contains ≥1 new marketplace-related bullet.
  </acceptance_criteria>
  <done>Optimizer skill documents tiered validation workflow.</done>
</task>

</tasks>

<verification>
Run each task's automated checks. Then sanity-check the three-skill handoff narrative:
- starter surfaces choice → links to builder
- builder executes via scripts → links to optimizer for validation
- optimizer validates → links back to schema reference
Grep for cross-links between the three skill files.
</verification>

<success_criteria>
- extension-starter surfaces layout choice (framing only, no scaffolding logic)
- extension-builder documents three flows with copy-paste bash commands
- extension-optimizer documents tiered validation with severity table
- All three link to references/marketplace-schema.md
- Clean separation preserved: starter = decision, builder = execution, optimizer = validation
- No skill mentions scripts outside its responsibility tier
</success_criteria>

<output>
After completion, create `.planning/phases/01-marketplace-support/01-05-SUMMARY.md` with: the three sections added (one per skill), the cross-link graph between starter/builder/optimizer, and confirmation of clean separation.
</output>
