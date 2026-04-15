---
title: Standalone → umbrella promotion flow
trigger_condition: A user asks to convert a standalone plugin into an umbrella marketplace, or creates a second plugin adjacent to an existing standalone and wants them unified
planted_date: 2026-04-16
---

# Standalone → umbrella promotion flow

Deferred from the initial marketplace-support phase. Handle when real demand surfaces.

## Scope when triggered

- Create umbrella dir (or detect one the user points at)
- Move the standalone plugin into `umbrella/plugin-name/`
- Merge the plugin's root marketplace.json entry into the umbrella's marketplace.json
- Delete the now-inner plugin-level marketplace.json (enforce the one-level invariant)
- Handle git boundaries: plugin-as-repo vs plugin-as-subdir vs submodule
- Update any references (README install instructions, etc.)

## Open questions at trigger time

- CLI/skill entry point: new command, or option on `extension-builder`?
- Dry-run mode? Promotion touches multiple files + possibly git state — rehearsal matters.
- Does the toolkit rewrite the existing plugin's docs to reference the new umbrella path?

## Why deferred

No concrete user need yet. The three clean-case flows (standalone, new umbrella, register-into-existing) cover greenfield work. Promotion is a migration, and migrations are easier to design against a real example than in the abstract.
