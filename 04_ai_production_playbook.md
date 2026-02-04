# AI-Only Production Playbook (Render Pipeline) (v1)

> **Doc type:** MECHANICS
> Canonical: `docs/MECHANICS.md` (artifacts/gates/state) • `docs/POLICY.md` (taste/scope/trends)

Canonical references:
- Mechanics (artifacts/gates/run state): `docs/MECHANICS.md`
- Policy (taste/scope/trend constraints): `docs/POLICY.md`

This playbook replaces human filming/acting with AI generation.

## Output Targets
- **Default format:** 9:16 vertical, 1080x1920
- **Length:** 15–45 seconds (default 20–30)
- **Style:** grounded, realistic, slice-of-life (no cartoon/anime/fantasy)
- **Comedy:** one beat, minimal escalation

## Inputs Required (from upstream)
- Rowan `scene_plan.md` (beats + shot plan + character placement)
- Lena script (or silent variant)
- Character cards (integrity bounds)
- Style guide (visual + voice)

## Render Agent Responsibilities
1. Convert scene plan into generation prompts:
   - per shot prompt
   - continuity notes (wardrobe/lighting/location)
2. Generate visuals/video clips.
3. Generate VO (if needed) in a natural style; otherwise prefer silence + ambient sound.
4. Assemble edit:
   - keep cuts tight
   - preserve pauses that are the joke
5. Create subtitles (optional but consistent).
6. Export final MP4 + store prompt bundle for reproducibility.
7. Write `render_report.md` with source inputs and bundle path.

## Quality Gates (must pass before Stephanie review)
### Technical
- No obvious facial warping or limb artifacts
- No unreadable on-screen text
- Audio intelligible, no clipping
- Subtitles match spoken words

### Tone
- No meanness, humiliation, cruelty
- No trend dependency (sounds, meme references)
- No over-acting; keep naturalism

### Structure
- One comedic turn
- No recap, no “part 2” hook
- Ends cleanly

## Prompt Bundle Format
Store prompts in a folder per asset:
- `render_prompts/{YYYY-MM-DD}_{slug}/`
  - `shot_01.txt`
  - `shot_02.txt`
  - `voice.txt`
  - `edit_notes.md`
  - `subs.srt` (if used)

## Versioning
- `v1` = first assembly
- `v2` = fixes after QC
- `final` = approved for posting

## Escalation Policy (prevent “sitcom drift”)
- If a character becomes more extreme to “make it funnier,” roll back.
- If the joke relies on remembering earlier content, reject.
- If the render tool pushes the style toward animation, re-prompt toward realism.

## Deferred Until System Stability
- Long-form episodes (>2 min)
- Planned arcs
- Multi-part cliffhangers
- Multi-platform syndication automation

---
