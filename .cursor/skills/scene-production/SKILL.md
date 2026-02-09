---
name: scene-production
description: Produce scene briefs and scene plans for short-form comedy: beat sheets, shot plans, character placement, and render notes. Use when designing scene structure, staging, shot plans, or AI render prompts from a script; when the user asks about scene_brief, scene_plan, or production constraints.
---

# Scene Production

Two phases: **Scene Brief** (lock intent and dialogue budget for the writer) then **Scene Plan** (executable plan for rendering). Scene authority is structure and staging only; no dialogue writing.

## Phase 1 — scene_brief.md (required first)

Lock before script writing:

- Characters present, tension pattern, pressure source, release target
- **Dialogue budget** (total lines, preferred speakers, silence encouraged?)
- Notes for the writer (tone, what the line must accomplish — not wording)
- Notes for production (required beats, visual storytelling, runtime target)

Do **not** write dialogue in the brief.

### scene_brief.md structure

```markdown
# scene_brief.md
## Title
## Scene Intent
## Characters Present (role, emotional state entering, integrity bounds)
## Tension Pattern
## Pressure Source
## Release Target
## Dialogue Budget
## Notes for Lena
## Notes for Rowan
```

## Phase 2 — scene_plan.md (after script)

Consume scene_brief + script. Produce an executable plan.

### scene_plan.md structure

```markdown
## {Title}
### Mode — sketch | vignette-capable
### Beat Sheet (3–7 beats)
### Character Placement (on-screen, off-screen, integrity notes)
### Environment & Props (minimal)
### Shot Plan (wide/medium/close, what happens, duration; max ~5 shots)
### Dialogue Slots (speaker, function, constraint, timing) — what the line does, not wording
### Render Notes — lighting mood, movement level; avoid exaggerated expressions, cartoonish motion, fantasy styling
### Continuity Check — escalation risk? works standalone?
```

## Non-Negotiables

- Do **not** write dialogue.
- Do **not** change dialogue intent after the writer; if something breaks, revise the brief and request new dialogue.
- Do **not** invent story arcs or sequel dependence.
- Do **not** force characters to "act funny."
- Keep scenes minimal: few beats, few props, few moving parts.
- Do **not** add beats unsupported by the brief.

## Render / Assembly Notes (for Evan)

- **Style:** Grounded realism; natural motion, believable timing, restrained expressions.
- **Avoid:** Animation, fantasy, "internet skit" energy, trending sounds unless requested.
- **Defects:** Iterate prompts to fix; do not hide defects with fast cuts.
- **Deliverables:** final.mp4, voice.wav if VO, subs.srt if used, prompt bundle (shot_01.txt, voice.txt, edit_notes.md).

## Character Integrity (Rowan checklist)

Before finalizing:
1. Is any character acting "for the joke" instead of from temperament?
2. Is the character more extreme than prior appearances?
3. Does the scene require prior episodes to land?
4. Are we repeating a bit verbatim?
5. Is anyone’s dignity compromised?

If any is yes → revise or reject.
