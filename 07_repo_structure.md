# 07_repository_structure.md
# Repository & Artifact Layout (v1)

> **Doc type:** MECHANICS
> Canonical: `docs/MECHANICS.md` (artifacts/gates/state) • `docs/POLICY.md` (taste/scope/trends)

This document defines how files are organized so the system stays legible.

---

## Root (current)
```
stephanie-project/
├─ project.yaml
├─ requirements.txt
├─ README.md
├─ 01_workflow_architecture.md
├─ 02_agent_definitions.md
├─ 03_character_bible.md
├─ 04_ai_production_playbook.md
├─ 06_trend_rules.md
├─ 08_agent_platforms.md
├─ 09_scope_boundaries.md
├─ 10_scene_brief.md
│
├─ docs/
│  ├─ MECHANICS.md
│  └─ POLICY.md
│
├─ agents/
│  ├─ trend_scout.prompt.md
│  ├─ theo.prompt.md
│  ├─ mabel.prompt.md
│  ├─ lena.prompt.md
│  ├─ rowan.prompt.md
│  ├─ evan.prompt.md
│  ├─ qc.prompt.md
│  └─ parker.prompt.md
│
├─ contracts/
│  ├─ artifact_contracts.yaml
│  └─ README.md
│
├─ scripts/
│  ├─ run_pipeline.py
│  ├─ artifact_contracts.py
│  ├─ gates.py
│  └─ provenance.py
│
├─ templates/
│  └─ curator_decision.template.md
│
├─ runs/
│  ├─ YYYY-MM/
│  │  ├─ YYYY-MM-DD_slug/
│  │  │  ├─ trend_brief.md
│  │  │  ├─ ideas.md
│  │  │  ├─ approved_ideas.md
│  │  │  ├─ scene_brief.md
│  │  │  ├─ scripts.md
│  │  │  ├─ scene_plan.md
│  │  │  ├─ render_report.md
│  │  │  ├─ render_prompts/
│  │  │  ├─ qc_report.md
│  │  │  ├─ curator_decision.md
│  │  │  ├─ READY_FOR_CURATOR.md
│  │  │  ├─ STOPPED_QC_FAIL.md (only on QC failure)
│  │  │  ├─ run_manifest.yaml
│  │  │  └─ post_bundle/

└─ design/
   └─ stephanie_taste_profile.md
```

For the authoritative execution contract (artifacts, gates, and run state), see `docs/MECHANICS.md`.

---

## Rules
- Every run has a dated folder.
- No agent writes outside its assigned artifact.
- Prompts are versioned separately from outputs.
- Published outputs should be treated as immutable once shared externally.

---

## Benefits
- Easy rollback
- Clear provenance of decisions
- Simple diffing of agent behavior over time

---
