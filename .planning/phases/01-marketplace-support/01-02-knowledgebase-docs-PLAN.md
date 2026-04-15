---
phase: 01-marketplace-support
plan: 02
type: execute
wave: 2
depends_on: [01]
files_modified:
  - references/marketplace-schema.md
  - README.md
autonomous: true
requirements: []
must_haves:
  truths:
    - "A new shared reference references/marketplace-schema.md exists documenting the canonical marketplace.json schema"
    - "README.md contains a Marketplace primer explaining standalone vs umbrella layouts with install examples for both"
    - "The one-level invariant (marketplace.json lives at exactly one level per tree) is documented prominently"
    - "Install instructions use real /plugin marketplace add <path> examples for both layouts"
  artifacts:
    - path: "references/marketplace-schema.md"
      provides: "Canonical marketplace.json schema reference, consumed by extension-builder and extension-optimizer"
      min_lines: 80
      contains: "standalone vs umbrella layout explanation, required fields table, source types table, reserved names list"
    - path: "README.md"
      provides: "Top-level marketplace primer section"
      contains: "Marketplace Support header, standalone example, umbrella example, install commands"
  key_links:
    - from: "references/marketplace-schema.md"
      to: "data/version-manifest.json"
      via: "schema facts are derived from schemas.marketplace_manifest/marketplace_plugin_entry"
      pattern: "marketplace_manifest|marketplace_plugin_entry"
    - from: "README.md"
      to: "references/marketplace-schema.md"
      via: "link in Marketplace Support section"
      pattern: "references/marketplace-schema"
---

<objective>
Create the new shared reference `references/marketplace-schema.md` (canonical schema documentation) and add a Marketplace Support primer to README.md covering both standalone (flat) and umbrella layouts. Both documents are derived from the corrected data/version-manifest.json produced by Plan 01 and the verified schema in RESEARCH.md.

Purpose: The knowledgebase layer is the steering input for skills + validator + scaffolder. Correct, user-facing docs here unlock downstream skill integration (Plan 05) and give end users a place to land.

Output: New references/marketplace-schema.md; updated README.md with marketplace primer section.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/phases/01-marketplace-support/01-CONTEXT.md
@.planning/phases/01-marketplace-support/01-RESEARCH.md
@.planning/phases/01-marketplace-support/01-01-SUMMARY.md
@.planning/notes/marketplace-support-design.md
@data/version-manifest.json
@references/marketplaces.md
@README.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create references/marketplace-schema.md</name>
  <files>references/marketplace-schema.md</files>
  <read_first>
    - data/version-manifest.json (corrected by Plan 01 — read schemas.marketplace_manifest and schemas.marketplace_plugin_entry)
    - .planning/phases/01-marketplace-support/01-RESEARCH.md (Canonical marketplace.json Schema section, lines 21-102; Code Examples section, lines 310-425)
    - .planning/notes/marketplace-support-design.md (layout decisions)
    - references/marketplaces.md (existing adjacent reference — do NOT duplicate CLI/auth content; link to it instead)
  </read_first>
  <action>
    Create a new file `references/marketplace-schema.md`. This is the schema-focused companion to existing `references/marketplaces.md` (which covers CLI/auth/caching). This file focuses on the JSON shape and the two layout patterns.

    Use this exact skeleton (fill prose where indicated; preserve every heading and every code block verbatim):

    ```markdown
    # Marketplace Schema Reference

    Canonical JSON shape for `.claude-plugin/marketplace.json` and the two supported layout patterns.

    Canonical docs: https://code.claude.com/docs/en/plugin-marketplaces
    Companion: `references/marketplaces.md` (CLI, auth, caching, settings integration)

    ## Two Layouts

    `marketplace.json` lives at **exactly one level** per tree — never both at the plugin root and an ancestor umbrella root simultaneously.

    ### Standalone (flat)

    A plugin that is also its own single-entry marketplace. Directly installable.

    ```
    my-plugin/
    ├── .claude-plugin/
    │   ├── plugin.json
    │   └── marketplace.json   # single entry points at "./"
    ├── skills/
    └── README.md
    ```

    Install:
    ```bash
    /plugin marketplace add ./my-plugin
    /plugin install my-plugin@my-plugin
    ```

    Use when: shipping one plugin, no aggregation needed, fastest path to installable.

    ### Umbrella (aggregating)

    A directory containing N plugin subdirs, aggregated by a single marketplace.json at the umbrella root.

    ```
    my-marketplace/
    ├── .claude-plugin/
    │   └── marketplace.json   # aggregates plugin-a, plugin-b, ...
    ├── plugin-a/
    │   └── .claude-plugin/plugin.json
    └── plugin-b/
        └── .claude-plugin/plugin.json
    ```

    Install:
    ```bash
    /plugin marketplace add ./my-marketplace
    /plugin install plugin-a@my-marketplace
    /plugin install plugin-b@my-marketplace
    ```

    Use when: shipping multiple related plugins, shared owner/metadata, discovery-friendly.

    ### The invariant

    A plugin directory under an umbrella MUST NOT have its own `.claude-plugin/marketplace.json`. Promotion (standalone → umbrella) is a separate flow: move the plugin under the umbrella and delete its inner marketplace.json.

    ## Top-Level Schema

    Required and optional top-level fields:

    | Field | Type | Required | Description |
    |-------|------|----------|-------------|
    | `name` | string | yes | Marketplace identifier (kebab-case). Visible in `/plugin install X@<name>`. Must not collide with reserved names (see below). |
    | `owner` | object | yes | `{name: string (required), email?: string}` |
    | `plugins` | array | yes | List of plugin entry objects |
    | `metadata` | object | no | `{description?, version?, pluginRoot?}` |

    `metadata.pluginRoot` is prepended to relative plugin `source` paths. With `pluginRoot: "./plugins"`, a plugin with `source: "formatter"` resolves to `./plugins/formatter`.

    ## Plugin Entry Schema

    Required:

    | Field | Type | Description |
    |-------|------|-------------|
    | `name` | string | Plugin identifier (kebab-case) |
    | `source` | string or object | See Source Types below |

    Optional:

    | Field | Type | Description |
    |-------|------|-------------|
    | `description` | string | Brief plugin description |
    | `version` | string | Semver; **`plugin.json` version silently wins if both set** |
    | `author` | object | `{name: string, email?: string}` (object, not string) |
    | `homepage` | string | Homepage or docs URL |
    | `repository` | string | Source code URL |
    | `license` | string | SPDX identifier (e.g. `MIT`, `Apache-2.0`) |
    | `keywords` | array | Discovery tags (synonym of `tags`) |
    | `category` | string | Plugin category |
    | `tags` | array | Searchability tags |
    | `strict` | boolean | Default `true`; see Strict Mode |
    | `commands`, `agents`, `skills`, `hooks`, `mcpServers`, `outputStyles`, `lspServers` | string or object | Override/supplement plugin.json component definitions |

    Deprecated:

    | Field | Replacement | Severity |
    |-------|-------------|----------|
    | `path` | `source` | warning |

    ## Source Types

    | Type | Value shape | Required fields |
    |------|-------------|-----------------|
    | Relative path | string `"./name"` | must start with `./`, no `../` |
    | GitHub | object `{source: "github", repo, ref?, sha?}` | `repo` (e.g. `owner/name`) |
    | URL | object `{source: "url", url, ref?, sha?}` | `url` (https://, git@, Azure DevOps, CodeCommit) |
    | Git subdir | object `{source: "git-subdir", url, path, ref?, sha?}` | `url`, `path` |
    | npm | object `{source: "npm", package, version?, registry?}` | `package` |

    Relative paths resolve against the marketplace root (the directory containing `.claude-plugin/`). `../` is disallowed.

    ## Reserved Marketplace Names

    Do NOT use these names (reserved for official Anthropic marketplaces):

    - `claude-code-marketplace`
    - `claude-code-plugins`
    - `claude-plugins-official`
    - `anthropic-marketplace`
    - `anthropic-plugins`
    - `agent-skills`
    - `knowledge-work-plugins`
    - `life-sciences`

    ## Strict Mode

    | Value | Behavior |
    |-------|----------|
    | `true` (default) | `plugin.json` is authority; marketplace entry supplements |
    | `false` | Marketplace entry is the entire definition; plugin MUST NOT also declare components in `plugin.json` (conflict → load failure) |

    Use the default unless you specifically need marketplace-only component definitions.

    ## Minimal Valid marketplace.json

    ```json
    {
      "name": "my-marketplace",
      "owner": { "name": "Your Name" },
      "plugins": [
        { "name": "my-plugin", "source": "./my-plugin" }
      ]
    }
    ```

    ## Full Example

    ```json
    {
      "name": "company-tools",
      "owner": { "name": "DevTools Team", "email": "devtools@example.com" },
      "metadata": {
        "description": "Company internal plugins",
        "version": "1.0.0",
        "pluginRoot": "./plugins"
      },
      "plugins": [
        {
          "name": "formatter",
          "source": "formatter",
          "description": "Code formatting on save",
          "version": "2.1.0",
          "author": { "name": "DevTools Team" },
          "homepage": "https://example.com/formatter",
          "license": "MIT",
          "keywords": ["formatting", "style"]
        },
        {
          "name": "deploy-tools",
          "source": {
            "source": "github",
            "repo": "company/deploy-plugin",
            "ref": "v1.0.0"
          }
        }
      ]
    }
    ```

    ## Common Pitfalls

    - `../` in relative source paths → rejected at validation time. Plugins must be inside the marketplace root.
    - Setting `version` in both `plugin.json` and the marketplace entry → `plugin.json` wins silently.
    - Using a reserved marketplace name → fails at `/plugin marketplace add` time with no prior warning. Check the list above before naming.
    - URL-distributed marketplace + relative source paths → fails at install (URL distribution only fetches the JSON, not plugin dirs). Use URL distribution only with remote `source` types.
    - `strict: false` + plugin has a component-declaring `plugin.json` → load failure. Leave `strict` at default.

    ## Where This Schema Is Enforced

    | Facet | Enforced by |
    |-------|-------------|
    | JSON syntax, required fields | `claude plugin validate` (built-in) |
    | Reserved names, path-exists, author object shape, metadata wrapper shape | `scripts/marketplace_manager.py validate` |
    | Schema drift vs toolkit version | `data/version-manifest.json` `schemas.marketplace_manifest` / `marketplace_plugin_entry` |

    See `references/marketplaces.md` for CLI commands, auth tokens, caching, and settings integration.
    ```

    Write exactly this content. Do not paraphrase headings. The file should be around 150-180 lines.
  </action>
  <verify>
    <automated>
      test -f references/marketplace-schema.md &&
      grep -q "^# Marketplace Schema Reference" references/marketplace-schema.md &&
      grep -q "^## Two Layouts" references/marketplace-schema.md &&
      grep -q "^### Standalone (flat)" references/marketplace-schema.md &&
      grep -q "^### Umbrella (aggregating)" references/marketplace-schema.md &&
      grep -q "^## Reserved Marketplace Names" references/marketplace-schema.md &&
      grep -q '`claude-code-marketplace`' references/marketplace-schema.md &&
      grep -q '`life-sciences`' references/marketplace-schema.md &&
      grep -q '/plugin marketplace add ./my-plugin' references/marketplace-schema.md &&
      grep -q '/plugin marketplace add ./my-marketplace' references/marketplace-schema.md &&
      grep -q 'exactly one level' references/marketplace-schema.md &&
      [ $(wc -l < references/marketplace-schema.md) -ge 80 ]
    </automated>
  </verify>
  <acceptance_criteria>
    - File exists and is at least 80 lines.
    - Contains sections `## Two Layouts`, `### Standalone (flat)`, `### Umbrella (aggregating)`, `## Top-Level Schema`, `## Plugin Entry Schema`, `## Source Types`, `## Reserved Marketplace Names`, `## Strict Mode`, `## Minimal Valid marketplace.json`, `## Full Example`, `## Common Pitfalls`, `## Where This Schema Is Enforced`.
    - Lists all 8 reserved names exactly as in CONTEXT.md.
    - States "exactly one level" invariant verbatim.
    - Source types table lists `git-subdir` (with hyphen), does NOT list `pip`.
    - `author` is shown as object `{name, email?}` in schema table and example.
    - Install examples use `/plugin marketplace add ./my-plugin` and `/plugin marketplace add ./my-marketplace`.
    - No broken markdown (tables render, code fences matched).
  </acceptance_criteria>
  <done>File created, all grep assertions pass, renders cleanly as markdown.</done>
</task>

<task type="auto">
  <name>Task 2: Add Marketplace Support primer section to README.md</name>
  <files>README.md</files>
  <read_first>
    - README.md (entire current file — find a sensible insertion point; likely after the install/overview section, before or near the "Shared References" or "Scripts" section)
    - references/marketplace-schema.md (just created in Task 1 — link to it from README)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (specifics section with install command examples)
  </read_first>
  <action>
    Edit `README.md`. Add a new top-level section titled `## Marketplace Support`. Insert it after whichever existing section makes sense (look for a section on installation, usage, or shared references; place the primer adjacent).

    Use this exact content for the section (preserve headings and code blocks verbatim):

    ```markdown
    ## Marketplace Support

    Plugins built with this toolkit are consumable via Claude Code's local marketplace system. Two layouts are supported:

    ### Standalone (flat)

    One plugin directory that is also its own single-entry marketplace. Fastest path to installable.

    ```
    my-plugin/
    └── .claude-plugin/
        ├── plugin.json
        └── marketplace.json   # auto-created by extension-builder
    ```

    Install:
    ```bash
    /plugin marketplace add ./my-plugin
    /plugin install my-plugin@my-plugin
    ```

    The toolkit's `extension-builder` scaffolds standalone layouts by default — the generated plugin is installable immediately with no extra wiring.

    ### Umbrella (aggregating)

    One marketplace directory containing N plugin subdirs. Ideal when shipping a related plugin set.

    ```
    my-marketplace/
    ├── .claude-plugin/marketplace.json   # aggregates plugin-a, plugin-b
    ├── plugin-a/.claude-plugin/plugin.json
    └── plugin-b/.claude-plugin/plugin.json
    ```

    Install:
    ```bash
    /plugin marketplace add ./my-marketplace
    /plugin install plugin-a@my-marketplace
    ```

    When you scaffold a new plugin inside an umbrella, `extension-builder` detects the ancestor marketplace.json via upward search and registers the new plugin into it — no inner marketplace.json is created.

    ### The one-level invariant

    `marketplace.json` lives at exactly one level per tree — either the plugin root (standalone) or the umbrella root (umbrella), never both. Promotion (standalone → umbrella) is a separate migration flow, not yet automated; see `.planning/seeds/marketplace-promotion-flow.md`.

    ### Schema reference

    Full schema, source types, reserved names, and pitfalls: [`references/marketplace-schema.md`](references/marketplace-schema.md)
    Companion CLI/auth/caching reference: [`references/marketplaces.md`](references/marketplaces.md)
    ```

    Requirements:
    - Place this section at a reasonable location in the README (after install/overview, before deep reference tables). If the README has an existing "Marketplace" mention, consolidate — do not create duplication.
    - Do NOT alter unrelated sections.
    - Keep existing table of contents (if any) consistent; if TOC lists sections, add "Marketplace Support" in the right alphabetical/structural slot.
  </action>
  <verify>
    <automated>
      grep -q "^## Marketplace Support" README.md &&
      grep -q "^### Standalone (flat)" README.md &&
      grep -q "^### Umbrella (aggregating)" README.md &&
      grep -q "^### The one-level invariant" README.md &&
      grep -q '/plugin marketplace add ./my-plugin' README.md &&
      grep -q '/plugin marketplace add ./my-marketplace' README.md &&
      grep -q 'references/marketplace-schema.md' README.md &&
      grep -q 'exactly one level' README.md
    </automated>
  </verify>
  <acceptance_criteria>
    - `## Marketplace Support` H2 section exists in README.md.
    - Contains H3 subsections: `Standalone (flat)`, `Umbrella (aggregating)`, `The one-level invariant`, `Schema reference`.
    - Both install command examples (`./my-plugin` and `./my-marketplace`) appear.
    - Links to `references/marketplace-schema.md` and `references/marketplaces.md` present.
    - "exactly one level" phrase appears verbatim.
    - No duplicate Marketplace sections (if one existed before, consolidated).
  </acceptance_criteria>
  <done>README.md renders with new Marketplace Support section; all grep assertions pass.</done>
</task>

</tasks>

<verification>
Run both task verifications. Additionally, spot-check rendered markdown: `head -60 references/marketplace-schema.md` and verify that tables/code fences are well-formed. Confirm README.md section placement is sensible by reading ~30 lines around the new section.
</verification>

<success_criteria>
- references/marketplace-schema.md exists with canonical schema, two-layout explanation, reserved names, pitfalls
- README.md contains Marketplace Support section with standalone + umbrella examples and one-level invariant
- Both documents link to each other and to references/marketplaces.md
- Schema facts match data/version-manifest.json (corrected by Plan 01) — no pip, 8 reserved names, author as object
</success_criteria>

<output>
After completion, create `.planning/phases/01-marketplace-support/01-02-SUMMARY.md` with: file sizes, headings outline, link graph between the three reference docs.
</output>
