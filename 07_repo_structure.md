# 07_repository_structure.md
# Repository & Artifact Layout (v1)

This document defines how files are organized so the system stays legible.

---

## Root
```
stephanie-project/
├─ design/
│  ├─ 01_workflow_architecture.md
│  ├─ 02_agent_definitions.md
│  ├─ 03_character_bible.md
│  ├─ 04_ai_production_playbook.md
│  ├─ 05_trend_scout.md
│  ├─ 06_trend_usage_rules.md
│  └─ 07_repository_structure.md
│
├─ agents/
│  ├─ theo.prompt.md
│  ├─ mabel.prompt.md
│  ├─ lena.prompt.md
│  ├─ rowan.prompt.md
│  ├─ render.prompt.md
│  └─ parker.prompt.md
│
├─ runs/
│  ├─ YYYY-MM/
│  │  ├─ YYYY-MM-DD_slug/
│  │  │  ├─ trend_brief.md
│  │  │  ├─ ideas.md
│  │  │  ├─ approved_ideas.md
│  │  │  ├─ scene_brief.md   ← NEW
│  │  │  ├─ scripts.md
│  │  │  ├─ scene_plan.md
│  │  │  ├─ qc_report.md
│  │  │  └─ post_bundle/

│
├─ assets/
│  ├─ characters/
│  ├─ styles/
│  └─ references/
│
└─ archive/
   └─ published/
```

---

## Rules
- Every run has a dated folder.
- No agent writes outside its assigned artifact.
- Prompts are versioned separately from outputs.
- Published assets are immutable once archived.

---

## Benefits
- Easy rollback
- Clear provenance of decisions
- Simple diffing of agent behavior over time

---
