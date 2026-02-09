# Stephanie Project — Agent Skills

These skills encode domain knowledge from the agent prompts (`agents/*.prompt.md`) so that Cursor (or other agent runtimes) can apply them when working on comedy, scripts, scene production, curation, QC, or publishing.

## Skills Overview

| Skill | Purpose | Primary agents |
|-------|---------|----------------|
| **comedy-ideas** | Premise-level comedy: pressure/release, contrast, tone bounds | Theo, Mabel |
| **script-writing** | Dialogue, silent beats, punchlines, subtitle text from scene brief | Lena |
| **scene-production** | Scene brief → scene plan, beat sheet, shot plan, render notes | Rowan, Evan |
| **taste-curation** | Shortlist/reject against taste profile; reflection pass | Mabel |
| **qc-gate** | Technical and tone review; pass/fail with fixes | QC |
| **publishing-bundle** | Post assets after approval; captions, variants | Parker |

## Usage

- Skills are **project-scoped** (`.cursor/skills/`). They apply when the conversation involves the described tasks (e.g., "write a sketch premise," "turn this into a scene plan").
- Each skill’s `description` in SKILL.md is used for discovery; keep it specific and include trigger terms.
- Canonical agent behavior and artifact contracts remain in `agents/`, `contracts/`, and `docs/`. These skills summarize and align with that behavior for reuse in Cursor.

## Source

Content is derived from:

- `02_agent_definitions.md`
- `agents/*.prompt.md`
- `03_character_bible.md`
- `design/stephanie_taste_profile.md`
- `10_scene_brief.md`
