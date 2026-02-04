# Mechanics (Execution Contract)

> **Doc type:** MECHANICS
> This file is the canonical source of truth for artifacts, gates, and run state.

This document is the **runtime contract** for the orchestrator: artifacts, gates, and run state.

If you change anything here, assume it impacts determinism and reproducibility; prefer a version bump.

## Orchestrator
- Entry point: `scripts/run_pipeline.py`
- Config: `project.yaml`
- Outputs: `runs/YYYY-MM/YYYY-MM-DD_slug/`

## Provider integration
- Contract (how to wire a real model provider): `docs/PROVIDER_CONTRACT.md`

## Canonical Workflow (Phase 1)
1) `trend_scout` → `trend_brief.md`
2) `theo` → `ideas.md`
3) `mabel` → `approved_ideas.md`
4) `rowan` (phase 1) → `scene_brief.md`
5) `lena` → `scripts.md`
6) `rowan` (phase 2) → `scene_plan.md`
7) `evan` → `render_report.md` + `render_prompts/`
8) `qc` → `qc_report.md`
9) Human curator → `curator_decision.md`
10) `parker` (resume-only) → `post_bundle/post_plan.md`

Selection points exist at steps 3, 4, 5, and 6 (shortlist, chosen idea,
scripted idea(s), planned scene(s)). Each selection must be recorded in
the downstream artifact via explicit "source" and "selection notes"
sections to preserve provenance and prevent silent drift.

## Canonical Artifact Inventory (v1)
The workflow is artifact-driven. Each artifact is owned by a single agent
or the controller and is validated after write.

| Artifact key | File / path | Owner | Purpose |
| --- | --- | --- | --- |
| trend_brief | trend_brief.md | trend_scout | Topic brief for human behavior, not memes |
| ideas | ideas.md | theo | Idea list with pressure/release |
| approved_ideas | approved_ideas.md | mabel | Shortlist + rejections + selection notes |
| scene_brief | scene_brief.md | rowan | Coordination brief + chosen idea reference |
| scripts | scripts.md | lena | Dialogue + silent variant tied to brief |
| scene_plan | scene_plan.md | rowan | Executable beat/shot plan tied to script |
| render_report | render_report.md | evan | Render output report + source inputs |
| render_prompts | render_prompts/* | evan | Prompt bundle per version (v1, v2, final) |
| qc_report | qc_report.md | qc | PASS/FAIL gate + findings |
| curator_decision | curator_decision.md | human | Approval gate + notes |
| post_bundle | post_bundle/post_plan.md | parker | Publishing assets (resume-only) |
| run_manifest | run_manifest.yaml | controller | Provenance + hashes + gate outcomes |

Operational markers:
- READY_FOR_CURATOR.md (created after QC pass)
- STOPPED_QC_FAIL.md (created if QC FAIL and stop_on_qc_fail=true)

## Required Source References (anti-drift)
To make selections and handoffs inspectable:
- `approved_ideas.md` MUST include a global shortlist rationale.
- `scene_brief.md` MUST cite the exact approved idea title chosen.
- `scripts.md` MUST cite the scene brief title it is honoring.
- `scene_plan.md` MUST cite both the scene brief and the script title.
- `render_report.md` MUST cite the scene_plan + scripts used, and the
  prompt bundle version path.

## Artifacts and Contracts
Artifact contracts live in `contracts/artifact_contracts.yaml`.

Validation behavior:
- Each artifact is written to disk and then validated.
- Contract violations create `CONTRACT_VIOLATION.md` in the run folder and stop the run.

## Gates (Hard Semantics)
### QC gate
- Source: `qc_report.md`
- Required line: `- **Status:** PASS` or `- **Status:** FAIL`
- Enforcement:
  - If FAIL and `run_defaults.stop_on_qc_fail: true`, the run stops and writes `STOPPED_QC_FAIL.md`.

### Curator gate (resume flow)
- Source: `curator_decision.md`
- Required line: `Approved: yes/no` (also accepts true/false)
- Enforcement:
  - Only APPROVED runs proceed to Parker.

## Run State Model (Phase 1)
States are tracked in the run manifest for auditability.

Primary states:
- DRAFT (artifact generation in progress)
- RENDERING (Evan step active)
- QC (QC gate active)
- READY_FOR_CURATOR (awaiting curator decision)
- CURATOR_VETOED (explicit "no")
- APPROVED (explicit "yes")
- POST_BUNDLE_READY (Parker outputs prepared)
- STOPPED_QC_FAIL (QC failure with stop_on_qc_fail=true)

State transitions are recorded in `run.state_history`.

## Provenance (Run Manifest)
- File: `run_manifest.yaml` in each run folder
- Purpose: capture inputs (config, contracts, prompts, policy, provider),
  outputs (hashes), and gate outcomes for rollback and audit.

The manifest is updated after each artifact step and includes:
- `inputs.config`, `inputs.contracts`, `inputs.prompts`
- `inputs.policy` (taste profile, trend rules, character bible, scope)
- `inputs.provider` + `inputs.routing`
- `outputs` (per artifact file hash + size)
- `gates` (QC + curator outcomes)
- `run.state` + `run.state_history`
